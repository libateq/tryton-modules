# This file is part of the account_chart_variant Tryton module.
# Please see the COPYRIGHT and README.rst files at the top level of this
# package for full copyright notices, license terms and support information.
from unittest import TestLoader

from trytond.tests.test_tryton import ModuleTestCase, suite as test_suite


class AccountChartVariantTestCase(ModuleTestCase):
    "Test Account Chart Variant module"
    module = 'account_chart_variant'


def suite():
    suite = test_suite()
    suite.addTests(TestLoader().loadTestsFromTestCase(
        AccountChartVariantTestCase))
    return suite
