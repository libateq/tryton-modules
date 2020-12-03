# This file is part of the sale_direct Tryton module.
# Please see the COPYRIGHT and README.rst files at the top level of this
# package for full copyright notices, license terms and support information.
from trytond.i18n import gettext
from trytond.model import fields
from trytond.pool import Pool, PoolMeta
from trytond.pyson import And, Eval, Or

from .exception import MissingVisitLocationParentError


class Move(metaclass=PoolMeta):
    __name__ = 'stock.move'

    @classmethod
    def _get_origin(cls):
        return super()._get_origin() + ['sale.direct.visit']

    @classmethod
    def get_visit_moves(
            cls, visit, sales_material, from_location, to_location):
        moves = []
        for item in sales_material:
            moves.append(cls(
                    product=item.product.id,
                    quantity=item.quantity,
                    uom=item.unit,
                    from_location=from_location,
                    to_location=to_location,
                    origin=visit,
                    effective_date=visit.time.date(),
                    ))
        return moves


class Location(metaclass=PoolMeta):
    __name__ = 'stock.location'

    is_visit_location = fields.Function(
        fields.Boolean("Is Visit Location"),
        'get_is_visit_location')

    @classmethod
    def __setup__(cls):
        super().__setup__()
        cls.address.states['invisible'] = And(
            cls.address.states.get('invisible', True),
            ~Eval('is_visit_location', False))
        cls.address.states['required'] = Or(
            cls.address.states.get('required', False),
            Eval('is_visit_location', False))
        cls.address.depends.append('is_visit_location')

    def get_is_visit_location(self, name=None):
        pool = Pool()
        Configuration = pool.get('sale.configuration')

        if self.parent and self.type == 'storage':
            config = Configuration(1)
            return self.parent == config.visit_location_parent

    @classmethod
    def get_visit_location(cls, address):
        pool = Pool()
        Configuration = pool.get('sale.configuration')

        config = Configuration(1)
        if not config.visit_location_parent:
            raise MissingVisitLocationParentError(gettext(
                    'sale_direct.msg_missing_visit_location_parent'))

        location = cls(
            name=address.building_address,
            address=address,
            type='storage',
            parent=config.visit_location_parent,
            )
        location.save()
        return location

    @classmethod
    def find_visit_location(cls, address):
        pool = Pool()
        Configuration = pool.get('sale.configuration')

        config = Configuration(1)
        if not config.visit_location_parent:
            return

        locations = cls.search([
                ('parent', '=', config.visit_location_parent.id),
                ('type', '=', 'storage'),
                ('address', '=', address),
            ], limit=1)
        if locations:
            return locations[0]
