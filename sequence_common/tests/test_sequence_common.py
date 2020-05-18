# This file is part of the sequence_common Tryton module.
# Please see the COPYRIGHT and README.rst files at the top level of this
# package for full copyright notices, license terms and support information.
from unittest import TestLoader

from trytond.tests.test_tryton import ModuleTestCase, suite as test_suite


class SequenceCommonTestCase(ModuleTestCase):
    "Test Sequence Common module"
    module = 'sequence_common'


def suite():
    suite = test_suite()
    suite.addTests(TestLoader().loadTestsFromTestCase(
        SequenceCommonTestCase))
    return suite
