# This file is part of the account_uk_variants Tryton module.
# Please see the COPYRIGHT and README.rst files at the top level of this
# package for full copyright notices, license terms and support information.
try:
    from trytond.modules.account_uk_variants.tests.test_account_uk_variants import suite  # noqa: E501
except ImportError:
    from .test_account_uk_variants import suite

__all__ = ['suite']
