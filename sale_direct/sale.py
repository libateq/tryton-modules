# This file is part of the sale_direct Tryton module.
# Please see the COPYRIGHT and README.rst files at the top level of this
# package for full copyright notices, license terms and support information.
from trytond.pool import PoolMeta


class Sale(metaclass=PoolMeta):
    __name__ = 'sale.sale'

    @classmethod
    def __setup__(cls):
        super().__setup__()
        cls.party.domain = [('general_address_party', '!=', True)]

    @classmethod
    def _get_origin(cls):
        return super()._get_origin() + ['sale.direct.visit']
