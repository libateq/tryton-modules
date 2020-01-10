# This file is part of the account_personal Tryton module.
# Please see the COPYRIGHT and README files at the top level of this repository
# for full copyright notices, license terms and support information.
try:
    from trytond.modules.account_personal.tests.test_account_personal import suite  # noqa
except ImportError:
    from .test_account_personal import suite

__all__ = ['suite']
