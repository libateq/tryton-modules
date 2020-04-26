# This file is part of the authentication_totp Tryton module.
# Please see the COPYRIGHT and README.rst files at the top level of this
# package for full copyright notices, license terms and support information.
try:
    from trytond.modules.authentication_totp.tests.test_authentication_totp import suite  # noqa: E501
except ImportError:
    from .test_authentication_totp import suite

__all__ = ['suite']
