# This file is part of the account_uk_variants Tryton module.
# Please see the COPYRIGHT and README.rst files at the top level of this
# package for full copyright notices, license terms and support information.
from unittest import TestLoader

from trytond.tests.test_tryton import ModuleTestCase, suite as test_suite


class AccountUkVariantsTestCase(ModuleTestCase):
    "Test Account Uk Variants module"
    module = 'account_uk_variants'


def suite():
    suite = test_suite()
    suite.addTests(TestLoader().loadTestsFromTestCase(
        AccountUkVariantsTestCase))
    return suite
