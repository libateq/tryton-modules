# This file is part of the account_personal Tryton module.
# Please see the COPYRIGHT and README files at the top level of this repository
# for full copyright notices, license terms and support information.
import unittest


from trytond.tests.test_tryton import ModuleTestCase
from trytond.tests.test_tryton import suite as test_suite


class AccountPersonalTestCase(ModuleTestCase):
    'Test Account Personal module'
    module = 'account_personal'


def suite():
    suite = test_suite()
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(
        AccountPersonalTestCase))
    return suite
