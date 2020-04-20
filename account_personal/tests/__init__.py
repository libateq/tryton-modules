# This file is part of the account_personal Tryton module.
# Please see the COPYRIGHT and README.rst files at the top level of this
# package for full copyright notices, license terms and support information.
try:
    from trytond.modules.account_personal.tests.test_account_personal import suite  # noqa: E501
except ImportError:
    from .test_account_personal import suite

__all__ = ['suite']
