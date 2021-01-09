# This file is part of the sale_direct Tryton module.
# Please see the COPYRIGHT and README.rst files at the top level of this
# package for full copyright notices, license terms and support information.
from trytond.model import fields
from trytond.pool import Pool, PoolMeta
from trytond.transaction import Transaction


class Configuration(metaclass=PoolMeta):
    __name__ = 'sale.configuration'

    visit_location_parent = fields.Many2One(
        'stock.location', "Visit Location Parent",
        domain=[('type', '=', 'storage'), ('flat_childs', '=', True)],
        help="The parent location for stock locations that are used for sales "
        "material left during visits.")

    @classmethod
    def __register__(cls, module_name):
        pool = Pool()
        Address = pool.get('party.address')

        super().__register__(module_name)

        cursor = Transaction().connection.cursor()
        table_handler = cls.__table_handler__(module_name)
        table = cls.__table__()

        # Migration from 5.8: Remove general_address_party
        if table_handler.column_exist('general_address_party'):
            address_handler = Address.__table_handler__(module_name)
            address = Address.__table__()

            address_handler.not_null_action('party', action='remove')

            cursor.execute(*address.update(
                [address.party], [None],
                where=address.party.in_(
                    table.select(table.general_address_party))))

            table_handler.drop_column('general_address_party')
