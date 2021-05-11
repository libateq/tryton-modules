# This file is part of the party_address_location Tryton module.
# Please see the COPYRIGHT and README.rst files at the top level of this
# package for full copyright notices, license terms and support information.
try:
    from trytond.modules.party_address_location.tests.test_party_address_location import suite  # noqa: E501
except ImportError:
    from .test_party_address_location import suite

__all__ = ['suite']
