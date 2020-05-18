# This file is part of the sequence_common Tryton module.
# Please see the COPYRIGHT and README.rst files at the top level of this
# package for full copyright notices, license terms and support information.
try:
    from trytond.modules.sequence_common.tests.test_sequence_common import suite  # noqa: E501
except ImportError:
    from .test_sequence_common import suite

__all__ = ['suite']
