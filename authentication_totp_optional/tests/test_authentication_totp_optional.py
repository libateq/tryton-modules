# This file is part of the authentication_totp_optional Tryton module.
# Please see the COPYRIGHT and README.rst files at the top level of this
# package for full copyright notices, license terms and support information.
from time import time
from passlib.totp import TOTP
from unittest import TestLoader

from trytond.config import config
from trytond.exceptions import LoginException
from trytond.pool import Pool
from trytond.tests.test_tryton import (
    ModuleTestCase, suite as test_suite, with_transaction)
from trytond.transaction import Transaction

TOTP_SECRET_KEY = 'GE3D-AYRA-KRHV-IUBA-KNSW-G4TF-OQQE-WZLZ'


def current_timestamp():
    return int(time())


class AuthenticationTotpOptionalTestCase(ModuleTestCase):
    "Test Authentication Totp Optional module"
    module = 'authentication_totp_optional'

    def setUp(self):
        super().setUp()
        methods = config.get('session', 'authentications', default='')
        config.set('session', 'authentications', 'totp_optional')
        self.addCleanup(config.set, 'session', 'authentications', methods)

    def run_trigger_tasks(self):
        pool = Pool()
        Queue = pool.get('ir.queue')
        transaction = Transaction()
        self.assertTrue(transaction.tasks)
        while transaction.tasks:
            task = Queue(transaction.tasks.pop())
            task.run()

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

        user_id = User.get_login('totp', {})
        self.assertEqual(user_id, user.id)

    @with_transaction()
    def test_user_create_action(self):
        pool = Pool()
        User = pool.get('res.user')
        user = User(name='totp', login='totp')
        user.save()
        self.run_trigger_tasks()
        self.assertEqual(len(user.actions), 1)
        self.assertEqual(
            user.actions[0].get_action_value()['wiz_name'],
            'res.user.setup_totp')

    @with_transaction()
    def test_user_create_action_with_secret(self):
        pool = Pool()
        User = pool.get('res.user')
        user = User(name='totp', login='totp', totp_secret=TOTP_SECRET_KEY)
        user.save()
        self.run_trigger_tasks()
        self.assertEqual(len(user.actions), 0)

    @with_transaction()
    def test_clear_secret(self):
        pool = Pool()
        User = pool.get('res.user')
        user = User(name='totp', login='totp', totp_secret=TOTP_SECRET_KEY)
        user.save()

        user.clear_totp_secret()
        user.save()

        self.assertFalse(user.totp_secret)


def suite():
    suite = test_suite()
    suite.addTests(TestLoader().loadTestsFromTestCase(
        AuthenticationTotpOptionalTestCase))
    return suite
