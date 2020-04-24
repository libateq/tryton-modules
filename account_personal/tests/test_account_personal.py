# This file is part of the account_personal Tryton module.
# Please see the COPYRIGHT and README.rst files at the top level of this
# package for full copyright notices, license terms and support information.
from unittest import TestLoader

from trytond.tests.test_tryton import ModuleTestCase, suite as test_suite


class AccountPersonalTestCase(ModuleTestCase):
    "Test Account Personal module"
    module = 'account_personal'


def suite():
    suite = test_suite()
    suite.addTests(TestLoader().loadTestsFromTestCase(AccountPersonalTestCase))
    return suite
