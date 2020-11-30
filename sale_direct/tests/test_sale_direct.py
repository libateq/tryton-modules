# This file is part of the sale_direct Tryton module.
# Please see the COPYRIGHT and README.rst files at the top level of this
# package for full copyright notices, license terms and support information.
from unittest import TestLoader

from trytond.tests.test_tryton import ModuleTestCase, suite as test_suite


class SaleDirectTestCase(ModuleTestCase):
    "Test Sale Direct module"
    module = 'sale_direct'


def suite():
    suite = test_suite()
    suite.addTests(TestLoader().loadTestsFromTestCase(
        SaleDirectTestCase))
    return suite
