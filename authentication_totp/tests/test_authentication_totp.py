# This file is part of the authentication_totp Tryton module.
# Please see the COPYRIGHT and README.rst files at the top level of this
# package for full copyright notices, license terms and support information.
from doctest import DocFileSuite, REPORT_ONLY_FIRST_FAILURE
from passlib.totp import TOTP
from time import time
from unittest import TestLoader

from trytond.config import config
from trytond.exceptions import LoginException
from trytond.pool import Pool
from trytond.tests.test_tryton import (
    ModuleTestCase, doctest_checker, doctest_teardown, with_transaction,
    suite as test_suite)

TOTP_SECRET_KEY = 'GE3D-AYRA-KRHV-IUBA-KNSW-G4TF-OQQE-WZLZ'


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
        user = User(name='totp', login='totp', totp_secret=TOTP_SECRET_KEY)
        user.save()

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
        user = User(name='totp', login='totp')
        user.save()

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
    def test_totp_get(self):
        pool = Pool()
        TOTPLogin = pool.get('res.user.login.totp')
        record, = TOTPLogin.create([{'user_id': 1}])
        totp_login = TOTPLogin.get(1)
        self.assertEqual(record, totp_login)

    @with_transaction()
    def test_totp_check(self):
        pool = Pool()
        TOTPLogin = pool.get('res.user.login.totp')
        User = pool.get('res.user')
        user = User(name='totp', login='totp', totp_secret=TOTP_SECRET_KEY)
        user.save()

        time = current_timestamp()
        totp_code = TOTP(key=TOTP_SECRET_KEY).generate(time=time).token
        totp_login, = TOTPLogin.create([{'user_id': user.id}])

        self.assertFalse(totp_login.check('0', _time=time))
        self.assertFalse(totp_login.check('invalid_code', _time=time))
        self.assertFalse(totp_login.check('000000', _time=time))

        self.assertTrue(totp_login.check(totp_code, _time=time))

        # Second check raises warning about replay attack
        with self.assertRaises(LoginException) as cm:
            totp_login.check(totp_code, _time=time)
        self.assertEqual(cm.exception.name, 'totp_code')
        self.assertRegex(cm.exception.message, r'(?i)warning.*already.*used')


def suite():
    suite = test_suite()
    suite.addTests(TestLoader().loadTestsFromTestCase(
        AuthenticationTOTPTestCase))
    suite.addTests(DocFileSuite(
        'scenario_authentication_totp_admin.rst',
        tearDown=doctest_teardown, encoding='utf-8', checker=doctest_checker,
        optionflags=REPORT_ONLY_FIRST_FAILURE))
    suite.addTests(DocFileSuite(
        'scenario_authentication_totp_user.rst',
        tearDown=doctest_teardown, encoding='utf-8', checker=doctest_checker,
        optionflags=REPORT_ONLY_FIRST_FAILURE))
    return suite
