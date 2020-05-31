# This file is part of the authentication_totp_optional Tryton module.
# Please see the COPYRIGHT and README.rst files at the top level of this
# package for full copyright notices, license terms and support information.
try:
    from trytond.modules.authentication_totp_optional.tests.test_authentication_totp_optional import suite  # noqa: E501
except ImportError:
    from .test_authentication_totp_optional import suite

__all__ = ['suite']
