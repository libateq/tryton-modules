# This file is part of the sale_direct Tryton module.
# Please see the COPYRIGHT and README.rst files at the top level of this
# package for full copyright notices, license terms and support information.
from trytond.model import fields
from trytond.pool import Pool, PoolMeta


class Party(metaclass=PoolMeta):
    __name__ = 'party.party'

    general_address_party = fields.Function(
        fields.Boolean("General Address Party"),
        'get_general_address_party', searcher='search_general_address_party')

    def get_general_address_party(self, name):
        pool = Pool()
        Configuration = pool.get('sale.configuration')
        config = Configuration(1)
        return config.general_address_party == self

    @classmethod
    def search_general_address_party(cls, name, clause):
        pool = Pool()
        Configuration = pool.get('sale.configuration')

        _, operator, value = clause
        if operator == '=':
            operator = '=' if value else '!='
        elif operator == '!=':
            operator = '!=' if value else '='

        config = Configuration(1)
        try:
            return [('id', operator, config.general_address_party.id)]
        except AttributeError:
            return [('id', operator, 0)]
