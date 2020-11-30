# This file is part of the sale_direct Tryton module.
# Please see the COPYRIGHT and README.rst files at the top level of this
# package for full copyright notices, license terms and support information.
from trytond.model import fields
from trytond.pool import PoolMeta


class Configuration(metaclass=PoolMeta):
    __name__ = 'sale.configuration'

    general_address_party = fields.Many2One(
        'party.party', "General Address Party",
        help="The party that is used for general addresses that are not "
        "associated with any particular party.")
    visit_location_parent = fields.Many2One(
        'stock.location', "Visit Location Parent",
        domain=[('type', '=', 'storage'), ('flat_childs', '=', True)],
        help="The parent location for stock locations that are used for sales "
        "material left during visits.")
