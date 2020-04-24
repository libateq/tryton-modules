# This file is part of the account_uk_vat_analysis Tryton module.
# Please see the COPYRIGHT and README.rst files at the top level of this
# package for full copyright notices, license terms and support information.
from unittest import TestLoader()

from trytond.tests.test_tryton import ModuleTestCase, suite as test_suite


class AccountUkVatAnalysisTestCase(ModuleTestCase):
    "Test Account UK VAT Analysis module"
    module = 'account_uk_vat_analysis'


def suite():
    suite = test_suite()
    suite.addTests(TestLoader().loadTestsFromTestCase(
        AccountUkVatAnalysisTestCase))
    return suite
