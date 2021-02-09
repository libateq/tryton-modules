# This file is part of the sale_direct Tryton module.
# Please see the COPYRIGHT and README.rst files at the top level of this
# package for full copyright notices, license terms and support information.
from contextlib import suppress
from datetime import datetime
from sql import Literal, Null
from sql.functions import CurrentTimestamp

from trytond.config import config
from trytond.model import DeactivableMixin, ModelSQL, ModelView, fields
from trytond.pool import Pool
from trytond.pyson import Eval, If, PYSONEncoder
from trytond.transaction import Transaction
from trytond.wizard import (
    Button, StateAction, StateTransition, StateView, Wizard)


class VisitType(DeactivableMixin, ModelSQL, ModelView):
    "Visit Type"
    __name__ = 'sale.direct.visit.type'

    name = fields.Char("Name", required=True)

    default_type = fields.Boolean(
        "Default Type", readonly=True,
        help="Checked if this is the default type for new visits.")

    revisit_time = fields.TimeDelta("Revisit Time")

    leave_sales_material = fields.One2Many(
        'sale.direct.visit.type.sales_material', 'visit_type',
        "Leave Sales Material",
        help="The sales material that is left, by default, during the visit.")
    collect_sales_material = fields.Boolean(
        "Collect Sales Material",
        help="Check to automatically collect the sales material, by default, "
        "during the visit.")
    lost_sales_material = fields.Boolean(
        "Lost Sales Material",
        help="Check to automatically write off the sales material, "
        "by default, after the visit.")

    @classmethod
    def __register__(cls, module_name):
        table_handler = cls.__table_handler__(module_name)

        # Migration from 5.8: Rename from sale.direct.visit.event
        event_table = config.get(
            'table', 'sale.direct.visit.event',
            default='sale.direct.visit.event'.replace('.', '_'))
        if table_handler.table_exist(event_table):
            type_table = config.get(
                'table', 'sale.direct.visit.type',
                default='sale.direct.visit.type'.replace('.', '_'))
            table_handler.table_rename(event_table, type_table)

        # Migration from 5.8: Rename default_event to default_type
        if (table_handler.column_exist('default_event')
                and not table_handler.column_exist('default_type')):
            table_handler.column_rename('default_event', 'default_type')

        super().__register__(module_name)

    @classmethod
    def __setup__(cls):
        super().__setup__()
        cls._buttons.update({
            'set_default_type': {
                'invisible': Eval('default_type', False),
                'depends': ['default_type'],
                },
            })

    @classmethod
    def get_default_type(cls):
        type = cls.search([('default_type', '=', True)], limit=1)
        if type:
            return type[0]

    @classmethod
    @ModelView.button
    def set_default_type(cls, visit_types):
        if visit_types:
            default_type = visit_types[0]
        else:
            default_type = None

        to_write = []
        if default_type:
            to_write.extend([[default_type], {'default_type': True}])

        default_types = cls.search([('default_type', '=', True)])
        with suppress(ValueError):
            default_types.remove(default_type)
        if default_types:
            to_write.extend([default_types, {'default_type': False}])

        if to_write:
            cls.write(*to_write)

        return 'reload'


class SalesMaterialMixin:

    product = fields.Many2One(
        'product.product', "Product", required=True, ondelete='RESTRICT',
        domain=[('type', '=', 'goods')])
    unit = fields.Many2One(
        'product.uom', "Unit", required=True, ondelete='RESTRICT',
        domain=[
            If(Eval('unit_category', False),
                ('category', '=', Eval('unit_category')),
                ('category', '!=', -1)),
        ], depends=['unit_category'])
    unit_digits = fields.Function(
        fields.Integer("Unit Digits"),
        'on_change_with_unit_digits')
    unit_category = fields.Function(
        fields.Many2One('product.uom.category', "Unit Category"),
        'on_change_with_unit_category')

    @fields.depends('product')
    def on_change_with_unit(self, name=None):
        if self.product:
            return self.product.default_uom.id

    @fields.depends('unit')
    def on_change_with_unit_digits(self, name=None):
        if self.unit:
            return self.unit.digits
        return 2

    @fields.depends('product')
    def on_change_with_unit_category(self, name=None):
        if self.product:
            return self.product.default_uom_category.id


class VisitTypeSalesMaterial(SalesMaterialMixin, ModelSQL, ModelView):
    "Visit Type Sales Material"
    __name__ = 'sale.direct.visit.type.sales_material'

    visit_type = fields.Many2One(
        'sale.direct.visit.type', "Visit Type", required=True)
    quantity = fields.Float(
        "Quantity", required=True, digits=(16, Eval('unit_digits', 2)),
        depends=['unit_digits'])

    @classmethod
    def __register__(cls, module_name):
        table_handler = cls.__table_handler__(module_name)

        # Migration from 5.8: Rename sale.direct.visit.event.sales_material
        event_table = config.get(
            'table', 'sale.direct.visit.event.sales_material',
            default='sale.direct.visit.event.sales_material'.replace('.', '_'))
        if table_handler.table_exist(event_table):
            type_table = config.get(
                'table', 'sale.direct.visit.type.sales_material',
                default=(
                    'sale.direct.visit.type.sales_material'.replace('.', '_')))
            table_handler.table_rename(event_table, type_table)

        # Migration from 5.8: Rename visit_event to visit_type
        if (table_handler.column_exist('visit_event')
                and not table_handler.column_exist('visit_type')):
            table_handler.column_rename('visit_event', 'visit_type')

        super().__register__(module_name)


class Visit(ModelSQL, ModelView):
    "Visit"
    __name__ = 'sale.direct.visit'

    address = fields.Many2One(
        'party.address', "Address", required=True, ondelete='RESTRICT')
    time = fields.DateTime("Time", required=True)
    type = fields.Many2One(
        'sale.direct.visit.type', "Type", required=True, ondelete='RESTRICT')

    revisit_time = fields.DateTime("Revisit Time")

    sales = fields.One2Many(
        'sale.sale', 'origin', "Sales", readonly=True,
        states={
            'invisible': ~Eval('sales'),
        }, depends=['sales'])

    sales_material_moves = fields.One2Many(
        'stock.move', 'origin', "Sales Material Moves", readonly=True,
        states={
            'invisible': ~Eval('sales_material_moves'),
        }, depends=['sales_material_moves'])

    notes = fields.Text("Notes")

    @classmethod
    def __register__(cls, module_name):
        table_handler = cls.__table_handler__(module_name)

        # Migration from 5.8: Rename event to type
        if (table_handler.column_exist('event')
                and not table_handler.column_exist('type')):
            table_handler.column_rename('event', 'type')

        super().__register__(module_name)

    @classmethod
    def __setup__(cls):
        super().__setup__()
        cls._order = [
            ('time', 'DESC'),
            ('id', 'DESC'),
            ]
        cls._buttons.update({
            'register_order': {},
            })

    def get_rec_name(self, name):
        if self.address and self.time:
            return ' to '.join([str(self.time), self.address.building_address])
        return '[{}]'.format(self.id)

    @classmethod
    def get_last_street_address(cls):
        visits = cls.search([], order=[('time', 'DESC')], limit=1)
        if visits:
            address = visits[0].address
            return {
                'street': address.street,
                'city': address.city,
                'country': getattr(address.country, 'id', None),
                'subdivision': getattr(address.subdivision, 'id', None),
                }

    @classmethod
    def get_visit(cls, address, event):
        return cls(
            address=address,
            time=event.time,
            type=event.type,
            revisit_time=event.revisit_time,
            notes=event.notes,
            )

    @classmethod
    @ModelView.button_action('sale_direct.register_order_wizard')
    def register_order(cls, visits):
        pass


class PerformVisitAddress(ModelView):
    "Perform Visit Address"
    __name__ = 'sale.direct.visit.perform.address'

    new_address = fields.Boolean("New Address")

    address = fields.Many2One(
        'party.address', "Address", states={
            'invisible': Eval('new_address', False),
        }, depends=['new_address'])

    _states = {
        'invisible': ~Eval('new_address'),
        }
    _depends = ['new_address']

    name = fields.Char(
        "Building Name", states={
            'invisible': ~Eval('new_address', False),
            'required': Eval('new_address', False),
        }, depends=_depends)
    street = fields.Text("Street", states=_states, depends=_depends)
    zip = fields.Char("Zip", states=_states, depends=_depends)
    city = fields.Char("City", states=_states, depends=_depends)
    country = fields.Many2One(
        'country.country', "Country", states=_states, depends=_depends)
    subdivision_types = fields.Function(
        fields.MultiSelection(
            'get_subdivision_types', "Subdivision Types",
            states=_states, depends=_depends),
        'on_change_with_subdivision_types')
    subdivision = fields.Many2One(
        'country.subdivision', "Subdivision",
        domain=[
            ('country', '=', Eval('country', -1)),
            If(Eval('subdivision_types', []),
                ('type', 'in', Eval('subdivision_types', [])),
                ()),
            ],
        states=_states, depends=_depends+['country', 'subdivision_types'])

    del _states, _depends

    @fields.depends('subdivision', 'country')
    def on_change_country(self):
        if (self.subdivision
                and self.subdivision.country != self.country):
            self.subdivision = None

    @classmethod
    def get_subdivision_types(cls):
        pool = Pool()
        Subdivision = pool.get('country.subdivision')
        return Subdivision.fields_get(['type'])['type']['selection']

    @fields.depends('country')
    def on_change_with_subdivision_types(self, name=None):
        pool = Pool()
        Types = pool.get('party.address.subdivision_type')
        return Types.get_types(self.country)


class PerformVisitSalesMaterial(SalesMaterialMixin, ModelView, ModelSQL):
    "Perform Visit Sales Material"
    __name__ = 'sale.direct.visit.perform.sales_material'

    product_name = fields.Function(
        fields.Char("Product"),
        'on_change_with_product_name')
    unit_name = fields.Function(
        fields.Char("Unit"),
        'on_change_with_unit_name')

    quantity = fields.Function(
        fields.Float(
            "Quantity", required=True, digits=(16, Eval('unit_digits', 2)),
            depends=['unit_digits']),
        'get_quantity', setter='set_quantity')

    @classmethod
    def table_query(cls):
        pool = Pool()
        Product = pool.get('product.product')
        Template = pool.get('product.template')

        product = Product.__table__()
        template = Template.__table__()
        return product.join(
                template,
                condition=product.template == template.id,
            ).select(
                product.id.as_('id'),
                Literal(0).as_('create_uid'),
                CurrentTimestamp().as_('create_date'),
                cls.write_uid.sql_cast(Literal(Null)).as_('write_uid'),
                cls.write_date.sql_cast(Literal(Null)).as_('write_date'),
                product.id.as_('product'),
                template.default_uom.as_('unit'),
            )

    @fields.depends('product')
    def get_quantity(self, name):
        if self.product:
            return self.product.quantity

    @classmethod
    def set_quantity(cls, sales_material, name, value):
        pass

    @fields.depends('product')
    def on_change_with_product_name(self, name=None):
        if self.product:
            return self.product.rec_name

    @fields.depends('unit')
    def on_change_with_unit_name(self, name=None):
        if self.unit:
            return self.unit.rec_name


class PerformVisitEvent(ModelView):
    "Perform Visit"
    __name__ = 'sale.direct.visit.perform.event'

    address = fields.Many2One('party.address', "Address", readonly=True)
    type = fields.Many2One('sale.direct.visit.type', "Type", required=True)
    time = fields.DateTime("Time", required=True)

    revisit_time = fields.DateTime("Revisit Time")

    notes = fields.Text("Notes")

    warehouse = fields.Many2One(
        'stock.location', "Warehouse", domain=[('type', '=', 'warehouse')],
        states={
            'required': (
                Eval('sales_material_left')
                | Eval('sales_material_collected')
                | Eval('sales_material_lost')),
        }, depends=[
            'sales_material_left', 'sales_material_collected',
            'sales_material_lost'])
    location = fields.Many2One('stock.location', "Location", readonly=True)
    sales_material_left = fields.One2Many(
        'sale.direct.visit.perform.sales_material', None,
        "Sales Material Left",
        add_remove=[],
        context={
            'locations': If(Eval('warehouse'), [Eval('warehouse')], []),
        },
        depends=['warehouse'])
    sales_material_collected = fields.One2Many(
        'sale.direct.visit.perform.sales_material', None,
        "Sales Material Collected",
        add_remove=[],
        context={
            'locations': If(Eval('location'), [Eval('location')], []),
        },
        depends=['location'])
    sales_material_lost = fields.One2Many(
        'sale.direct.visit.perform.sales_material', None,
        "Sales Material Lost",
        add_remove=[],
        context={
            'locations': If(Eval('location'), [Eval('location')], []),
        },
        depends=['location'])

    @classmethod
    def default_time(cls):
        return datetime.now()

    @classmethod
    def default_warehouse(cls):
        pool = Pool()
        Location = pool.get('stock.location')
        return Location.get_default_warehouse()

    @fields.depends('type')
    def on_change_with_revisit_time(self, name=None):
        if self.type and self.type.revisit_time:
            return datetime.now() + self.type.revisit_time

    @fields.depends('type')
    def on_change_with_sales_material_left(self, name=None):
        if self.type and self.type.leave_sales_material:
            return [{
                'product': s.product.id,
                'product_name': s.product.rec_name,
                'quantity': s.quantity,
                'unit': s.unit.id,
                'unit_name': s.unit.rec_name,
                } for s in self.type.leave_sales_material]
        return []

    def _sales_material_at(self, location):
        pool = Pool()
        Product = pool.get('product.product')

        if not location:
            return []

        with Transaction().set_context(locations=[location]):
            products = Product.search([('quantity', '>', 0)])
        return [{
            'product': p.id,
            'product_name': p.rec_name,
            'quantity': p.quantity,
            'unit': p.default_uom.id,
            'unit_name': p.default_uom.rec_name,
            } for p in products]

    @fields.depends('type', 'location')
    def on_change_with_sales_material_collected(self, name=None):
        if self.type and self.type.collect_sales_material:
            return self._sales_material_at(self.location)
        return []

    @fields.depends('type', 'location')
    def on_change_with_sales_material_lost(self, name=None):
        if self.type and self.type.lost_sales_material:
            return self._sales_material_at(self.location)
        return []


class PerformVisit(Wizard):
    "Perform Visit"
    __name__ = 'sale.direct.visit.perform'

    start = StateTransition()
    address = StateView(
        'sale.direct.visit.perform.address',
        'sale_direct.perform_visit_address_view_form', [
            Button("Cancel", 'end', 'tryton-cancel'),
            Button("Next", 'event', 'tryton-forward', default=True),
            ])
    event = StateView(
        'sale.direct.visit.perform.event',
        'sale_direct.perform_visit_event_view_form', [
            Button("Cancel", 'end', 'tryton-cancel'),
            Button("Done", 'process_visit', 'tryton-forward', default=True),
            ])
    process_visit = StateTransition()

    def transition_start(self):
        if self.get_address():
            return 'event'
        return 'address'

    def get_address(self):
        pool = Pool()
        Address = pool.get('party.address')

        if isinstance(self.record, Address):
            return self.record

        address = getattr(self.address, 'address', None)
        if address:
            return address

        return Address.search_visit_address(self.address)

    def default_address(self, fields):
        pool = Pool()
        Visit = pool.get('sale.direct.visit')

        address = self.get_address()
        if address:
            return {
                'new_address': False,
                'address': address.id,
                }

        result = {
            'new_address': True,
            }
        address_details = Visit.get_last_street_address()
        if address_details:
            result.update(address_details)

        return result

    def default_event(self, fields):
        pool = Pool()
        Location = pool.get('stock.location')
        VisitType = pool.get('sale.direct.visit.type')

        defaults = {}
        address = self.get_address()
        if address:
            defaults['address'] = address.id

        type = VisitType.get_default_type()
        if type and (not address or not address.revisit_required):
            defaults['type'] = type.id

        location = Location.find_visit_location(address)
        if location:
            defaults['location'] = location.id

        return defaults

    def transition_process_visit(self):
        pool = Pool()
        Address = pool.get('party.address')
        Location = pool.get('stock.location')
        Move = pool.get('stock.move')

        address = self.get_address()
        if not address:
            address = Address.get_visit_address(self.address)

        visit = Visit.get_visit(address, self.event)
        visit.save()

        moves = []
        location = self.event.location
        warehouse = self.event.warehouse
        if self.event.sales_material_left:
            if not location:
                location = Location.get_visit_location(address)
            moves.extend(Move.get_visit_moves(
                visit, self.event.sales_material_left,
                warehouse.storage_location, location))

        if self.event.sales_material_collected:
            if not location:
                location = Location.get_visit_location(address)
            moves.extend(Move.get_visit_moves(
                visit, self.event.sales_material_collected,
                location, warehouse.storage_location))

        if self.event.sales_material_lost:
            if not location:
                location = Location.get_visit_location(address)
            moves.extend(Move.get_visit_moves(
                visit, self.event.sales_material_lost,
                location, warehouse.lost_found_location))

        if moves:
            Move.save(moves)
            # TODO: Add a shipment style assign/force assign stage
            Move.do(moves)

        return 'end'


class RegisterOrder(Wizard):
    "Register Order"
    __name__ = 'sale.direct.visit.register_order'

    start = StateTransition()
    create_party = StateTransition()
    create_order = StateAction('sale.act_sale_form')

    def _get_address(self):
        if self.model.__name__ == 'sale.direct.visit':
            return self.record.address
        if self.model.__name__ == 'party.address':
            return self.record

    def _get_visit(self):
        pool = Pool()
        Address = pool.get('party.address')
        Visit = pool.get('sale.direct.visit')

        if self.model.__name__ == 'sale.direct.visit':
            return self.record

        if self.model.__name__ == 'party.address':
            last_visits = Address.get_last_visit([self.record], ['id'])
            if last_visits['id'][self.record.id]:
                return Visit(last_visits['id'][self.record.id])

    def transition_start(self):
        if self._get_address().party is None:
            return 'create_party'
        return 'create_order'

    def transition_create_party(self):
        pool = Pool()
        Party = pool.get('party.party')

        party = Party()
        party.addresses = [self._get_address()]
        party.save()

        return 'create_order'

    def do_create_order(self, action):
        pool = Pool()
        Sale = pool.get('sale.sale')

        address = self._get_address()
        visit = self._get_visit()

        sale = Sale()
        sale.party = address.party
        sale.invoice_address = address
        sale.shipment_address = address
        if visit:
            sale.sale_date = visit.time.date()
            sale.origin = visit
        sale.save()

        encoder = PYSONEncoder()
        action['views'].reverse()
        action['domains'] = []
        action['pyson_domain'] = encoder.encode([
                ('id', '=', sale.id),
                ])
        return action, {
            'res_id': [sale.id],
            }
