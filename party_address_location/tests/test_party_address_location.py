# This file is part of the party_address_location Tryton module.
# Please see the COPYRIGHT and README.rst files at the top level of this
# package for full copyright notices, license terms and support information.
from doctest import DocFileSuite, REPORT_ONLY_FIRST_FAILURE
from unittest import TestLoader

from trytond.tests.test_tryton import (
    ModuleTestCase, doctest_checker, doctest_teardown, suite as test_suite)


class PartyAddressLocationTestCase(ModuleTestCase):
    "Test Party Address Location module"
    module = 'party_address_location'


def suite():
    suite = test_suite()
    suite.addTests(TestLoader().loadTestsFromTestCase(
        PartyAddressLocationTestCase))
    suite.addTests(DocFileSuite(
        'scenario_party_address_location.rst',
        tearDown=doctest_teardown, encoding='utf-8', checker=doctest_checker,
        optionflags=REPORT_ONLY_FIRST_FAILURE))
    return suite
