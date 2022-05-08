# This file is part of the authentication_totp Tryton module.
# Please see the COPYRIGHT and README.rst files at the top level of this
# package for full copyright notices, license terms and support information.
from passlib.totp import TOTP
from time import time

from trytond.config import config
from trytond.exceptions import LoginException
from trytond.pool import Pool
from trytond.tests.test_tryton import ModuleTestCase, with_transaction

TOTP_SECRET_KEY = 'GE3D-AYRA-KRHV-IUBA-KNSW-G4TF-OQQE-WZLZ'


def create_user(name='totp', login='totp', totp_secret=None):
    pool = Pool()
    User = pool.get('res.user')
    user = User(name=name, login=login, totp_secret=totp_secret)
    user.save()
    return user


def current_timestamp():
    return int(time())


class AuthenticationTOTPTestCase(ModuleTestCase):
    "Test Authentication TOTP module"
    module = 'authentication_totp'

    def setUp(self):
        super().setUp()
        methods = config.get('session', 'authentications', default='')
        config.set('session', 'authentications', 'totp')
        self.addCleanup(config.set, 'session', 'authentications', methods)

    @with_transaction()
    def test_user_get_login(self):
        pool = Pool()
        User = pool.get('res.user')

        user = create_user(totp_secret=TOTP_SECRET_KEY)
        with self.assertRaises(LoginException) as cm:
            User.get_login('totp', {})
        self.assertEqual(cm.exception.name, 'totp_code')
        self.assertEqual(cm.exception.type, 'char')

        totp_code = TOTP(key=TOTP_SECRET_KEY).generate().token
        user_id = User.get_login('totp', {
                'totp_code': totp_code,
                })
        self.assertEqual(user_id, user.id)

    @with_transaction()
    def test_user_get_login_no_secret(self):
        pool = Pool()
        User = pool.get('res.user')

        create_user()
        with self.assertRaises(LoginException) as cm:
            User.get_login('totp', {})
        self.assertEqual(cm.exception.name, 'totp_code')
        self.assertEqual(cm.exception.type, 'char')

        totp_code = TOTP(key=TOTP_SECRET_KEY).generate().token
        self.assertFalse(User.get_login('totp', {
                'totp_code': totp_code,
                }))

    @with_transaction()
    def test_user_get_login_unknown_user(self):
        pool = Pool()
        User = pool.get('res.user')

        with self.assertRaises(LoginException) as cm:
            User.get_login('unknown', {})
        self.assertEqual(cm.exception.name, 'totp_code')
        self.assertEqual(cm.exception.type, 'char')

    @with_transaction()
    def test_totp_get_last_counter(self):
        pool = Pool()
        TOTPLogin = pool.get('res.user.login.totp')

        user = create_user(totp_secret=TOTP_SECRET_KEY)
        for counter in [123, 45, 678, 90]:
            totp_login = TOTPLogin()
            totp_login.user_id = user.id
            totp_login.counter = counter
            totp_login.save()

        last_counter = TOTPLogin.get_last_counter(user)
        self.assertEqual(last_counter, 678)

    @with_transaction()
    def test_totp_get_last_counter_no_login(self):
        pool = Pool()
        TOTPLogin = pool.get('res.user.login.totp')

        user = create_user(totp_secret=TOTP_SECRET_KEY)
        last_counter = TOTPLogin.get_last_counter(user)
        self.assertIsNone(last_counter)

    @with_transaction()
    def test_totp_mark_counter_used(self):
        pool = Pool()
        TOTPLogin = pool.get('res.user.login.totp')

        counter = 123456
        user = create_user(totp_secret=TOTP_SECRET_KEY)

        TOTPLogin.mark_counter_used(user, counter)

        totp_logins = TOTPLogin.search([('user_id', '=', user.id)])
        counters = [t.counter for t in totp_logins]
        self.assertIn(counter, counters)

    @with_transaction()
    def test_totp_clean_old_counters(self):
        pool = Pool()
        TOTPLogin = pool.get('res.user.login.totp')

        user = create_user(totp_secret=TOTP_SECRET_KEY)
        for counter in [123, 45, 678, 90]:
            totp_login = TOTPLogin()
            totp_login.user_id = user.id
            totp_login.counter = counter
            totp_login.save()

        TOTPLogin.clean_old_counters(user, 678)

        totp_login, = TOTPLogin.search([('user_id', '=', user.id)])
        self.assertEqual(totp_login.counter, 678)

    @with_transaction()
    def test_totp_check(self):
        pool = Pool()
        TOTPLogin = pool.get('res.user.login.totp')

        time = current_timestamp()
        user = create_user(totp_secret=TOTP_SECRET_KEY)
        totp_code = TOTP(key=TOTP_SECRET_KEY).generate(time=time).token

        self.assertFalse(TOTPLogin.check(user.id, '0', _time=time))
        self.assertFalse(TOTPLogin.check(user.id, 'invalid_code', _time=time))
        self.assertFalse(TOTPLogin.check(user.id, '000000', _time=time))

        self.assertTrue(TOTPLogin.check(user.id, totp_code, _time=time))

        # Second check raises warning about replay attack
        with self.assertRaises(LoginException) as cm:
            TOTPLogin.check(user.id, totp_code, _time=time)
        self.assertEqual(cm.exception.name, 'totp_code')
        self.assertRegex(cm.exception.message, r'(?i)warning.*already.*used')


del ModuleTestCase
