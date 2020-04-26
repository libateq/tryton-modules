# This file is part of the authentication_totp Tryton module.
# Please see the COPYRIGHT and README.rst files at the top level of this
# package for full copyright notices, license terms and support information.
from trytond.pool import PoolMeta


class Trigger(metaclass=PoolMeta):
    __name__ = 'ir.trigger'

    @classmethod
    def __setup__(cls):
        super().__setup__()
        cls.action.selection.append(
            ('res.user|add_totp_setup_wizard_to_actions',
             "Run TOTP Setup Wizard on Login"),
            )
