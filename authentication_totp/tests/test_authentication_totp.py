# This file is part of the authentication_totp Tryton module.
# Please see the COPYRIGHT and README.rst files at the top level of this
# package for full copyright notices, license terms and support information.
from time import time
from passlib.totp import TOTP
from unittest import TestLoader, skipIf

from trytond.config import config
from trytond.exceptions import LoginException, UserError
from trytond.modules.company.tests import create_company
from trytond.pool import Pool
from trytond.tests.test_tryton import (
    ModuleTestCase, activate_module, with_transaction, suite as test_suite)
from trytond.transaction import Transaction

from ..res import QRCode

TOTP_SECRET_KEY = 'GE3D-AYRA-KRHV-IUBA-KNSW-G4TF-OQQE-WZLZ'


def current_timestamp():
    return int(time())


class AuthenticationTOTPTestCase(ModuleTestCase):
    "Test Authentication TOTP module - totp Authentication Method"
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
    def test_user_set_totp_secret(self):
        pool = Pool()
        User = pool.get('res.user')
        user = User(name='totp', login='totp')
        user.save()

        user.totp_secret = TOTP_SECRET_KEY
        user.save()
        with Transaction().set_user(0):
            user = User(user.id)
            self.assertEqual(user.totp_secret, TOTP_SECRET_KEY)

        user.totp_secret = None
        user.save()
        with Transaction().set_user(0):
            user = User(user.id)
            self.assertIsNone(user.totp_secret)

        with self.assertRaises(UserError):
            user.totp_secret = 'an_invalid_key'
            user.save()

        with self.assertRaises(UserError):
            user.totp_secret = TOTP_SECRET_KEY[:19]
            user.save()

    @with_transaction()
    def test_user_get_totp_issuer(self):
        pool = Pool()
        User = pool.get('res.user')
        user = User(name='totp', login='totp', totp_secret=TOTP_SECRET_KEY)
        user.save()
        with Transaction().set_user(0):
            user = User(user.id)
            self.assertIn('Tryton', user.totp_url)

    @with_transaction()
    @skipIf(not QRCode, "qrcode not available")
    def test_user_get_totp_qrcode(self):
        pool = Pool()
        User = pool.get('res.user')
        user = User(name='totp', login='totp', totp_secret=TOTP_SECRET_KEY)
        user.save()
        qrcode = user.totp_qrcode
        self.assertGreater(len(qrcode), 0)


class AuthenticationTOTPCompanyTestCase(ModuleTestCase):
    "Test Authentication TOTP Module with Company"
    module = 'authentication_totp'
    extras = ['company']

    def setUp(self):
        super().setUp()
        activate_module('company')

        methods = config.get('session', 'authentications', default='')
        config.set('session', 'authentications', 'totp')
        self.addCleanup(config.set, 'session', 'authentications', methods)

    @with_transaction()
    def test_user_get_totp_issuer_company(self):
        pool = Pool()
        User = pool.get('res.user')
        company = create_company()
        user = User(
            name='totp', login='totp', totp_secret=TOTP_SECRET_KEY)
        user.companies = [company]
        user.company = company
        user.save()
        with Transaction().set_user(0):
            user = User(user.id)
            self.assertIn('issuer=Dunder%20Mifflin%20Tryton', user.totp_url)


class UserLoginTOTPTestCase(ModuleTestCase):
    "Test Authentication TOTP Module - User Login TOTP Model"
    module = 'authentication_totp'

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
    suite.addTests(TestLoader().loadTestsFromTestCase(
        AuthenticationTOTPCompanyTestCase))
    suite.addTests(TestLoader().loadTestsFromTestCase(
        UserLoginTOTPTestCase))
    return suite
