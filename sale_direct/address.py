# This file is part of the sale_direct Tryton module.
# Please see the COPYRIGHT and README.rst files at the top level of this
# package for full copyright notices, license terms and support information.
from collections import defaultdict
from datetime import date, datetime, timedelta
from sql import Literal, Null
from sql.aggregate import Max

from trytond.i18n import gettext
from trytond.model import ModelView, fields
from trytond.pool import Pool, PoolMeta
from trytond.pyson import Eval
from trytond.tools import reduce_ids, grouped_slice
from trytond.transaction import Transaction

from .exception import MissingGeneralAddressPartyError


class Address(metaclass=PoolMeta):
    __name__ = 'party.address'

    building_address = fields.Function(
        fields.Char("Building Address"),
        'get_building_address')

    last_visit_time = fields.Function(
        fields.DateTime("Last Visit Time"),
        'get_last_visit', searcher='search_last_visit')
    last_visit_event = fields.Function(
        fields.Many2One('sale.direct.visit.event', "Last Visit Event"),
        'get_last_visit', searcher='search_last_visit')
    last_visit_notes = fields.Function(
        fields.Text("Last Visit Notes"),
        'get_last_visit', searcher='search_last_visit')

    revisit_required = fields.Function(
        fields.Boolean("Revisit Required"),
        'get_last_visit', searcher='search_last_visit')
    revisit_today = fields.Function(
        fields.Boolean("Revisit Today"),
        'get_last_visit', searcher='search_last_visit')
    revisit_due = fields.Function(
        fields.DateTime("Revisit Due"),
        'get_last_visit', setter='set_revisit_due',
        searcher='search_last_visit')

    general_address = fields.Function(
        fields.Boolean("General Address"),
        'get_general_address')

    @classmethod
    def __setup__(cls):
        super().__setup__()
        cls._buttons.update({
            'visit': {},
            })
        cls.party.states['readonly'] &= ~Eval('general_address', False)
        cls.party.depends.append('general_address')

    def get_building_address(self, name):
        if self.street:
            street, *locality = self.street.splitlines()
            if locality:
                locality = locality[0]
        else:
            street = locality = None
        if self.country:
            country = self.country.code
        else:
            country = None
        result = ', '.join(filter(None, [
                    self.name,
                    street,
                    locality,
                    self.zip,
                    self.city,
                    country]))
        if not result:
            result = self.party.rec_name
        return result

    @classmethod
    def order_building_address(cls, tables):
        address, _ = tables[None]
        return [
            address.country,
            address.subdivision,
            address.city,
            address.street,
            address.name,
            address.party.id,
            ]

    @classmethod
    def get_last_visit(cls, addresses, names):
        address = cls.__table__()
        cursor = Transaction().connection.cursor()

        last_visit = cls.last_visit_query()
        columns = [address.id]
        for name in names:
            columns.append(getattr(last_visit, name))

        result = defaultdict(dict)
        for sub_ids in grouped_slice(addresses):
            red_sql = reduce_ids(address.id, sub_ids)
            cursor.execute(*address.join(
                    last_visit, 'LEFT',
                    condition=address.id == last_visit.address
                ).select(*columns, where=red_sql))
            for row in cursor.fetchall():
                address_id = row[0]
                for count, name in enumerate(names, 1):
                    result[name][address_id] = row[count]

        return result

    @classmethod
    def search_last_visit(cls, name, clause):
        _, operator, value = clause
        Operator = fields.SQL_OPERATORS[operator]
        last_visit = cls.last_visit_query()
        query = last_visit.select(
            last_visit.address,
            where=Operator(getattr(last_visit, name), value))
        return [('id', 'in', query)]

    @classmethod
    def set_revisit_due(cls, addresses, name, value):
        pool = Pool()
        Visit = pool.get('sale.direct.visit')

        to_save = []
        visits = cls.get_last_visit(addresses, ['id'])
        for visit_id in visits['id'].values():
            visit = Visit(visit_id)
            visit.revisit_time = value
            to_save.append(visit)

        if to_save:
            Visit.save(to_save)

    @classmethod
    def order(cls, tables, name):
        address, _ = tables[None]
        key = 'last_visit'
        if key not in tables:
            last_visit = cls.last_visit_query()
            query = address.join(
                last_visit, 'LEFT',
                condition=address.id == last_visit.address)
            tables[key] = {
                None: (query.right, query.condition),
                }
        else:
            last_visit, _ = tables[key][None]
        return [getattr(last_visit, name)]

    @classmethod
    def order_last_visit_time(cls, tables):
        return cls.order(tables, 'last_visit_time')

    @classmethod
    def order_revisit_due(cls, tables):
        return cls.order(tables, 'revisit_due')

    @fields.depends('party')
    def get_general_address(self, name):
        if self.party:
            return self.party.general_address_party

    @classmethod
    def get_visit_address(cls, address):
        pool = Pool()
        Configuration = pool.get('sale.configuration')

        existing_address = cls.search_visit_address(address)
        if existing_address:
            return existing_address

        config = Configuration(1)
        if not config.general_address_party:
            raise MissingGeneralAddressPartyError(gettext(
                    'sale_direct.msg_missing_general_address_party'))

        new_address = cls(
            party=config.general_address_party,
            name=address.name,
            street=address.street,
            city=address.city,
            country=address.country,
            subdivision=address.subdivision,
            )
        new_address.save()
        return new_address

    @classmethod
    def search_visit_address(cls, address):
        domain = []
        for name in {'name', 'street', 'city', 'subdivision', 'country'}:
            value = getattr(address, name, None)
            if hasattr(value, 'id'):
                domain.append((name, '=', getattr(value, 'id')))
            else:
                domain.append((name, '=', value))

        addresses = cls.search(domain, limit=1)
        if addresses:
            return addresses[0]

    @classmethod
    def last_visit_query(cls):
        pool = Pool()
        Visit = pool.get('sale.direct.visit')

        tomorrow = Literal(datetime.combine(
            date.today() + timedelta(days=1), datetime.min.time()))

        visit = Visit.__table__()
        last_visit = visit.select(
            visit.address.as_('address'),
            Max(visit.time).as_('time'),
            group_by=[visit.address],
            )

        visit = Visit.__table__()
        revisit_required = (visit.revisit_time != Null)
        revisit_today = (visit.revisit_time < tomorrow)
        return visit.join(
                last_visit,
                condition=(
                    (visit.address == last_visit.address)
                    & (visit.time == last_visit.time))
            ).select(
                visit.id.as_('id'),
                visit.address.as_('address'),
                visit.time.as_('last_visit_time'),
                visit.event.as_('last_visit_event'),
                visit.notes.as_('last_visit_notes'),
                revisit_required.as_('revisit_required'),
                revisit_today.as_('revisit_today'),
                visit.revisit_time.as_('revisit_due'),
            )

    @classmethod
    @ModelView.button_action('sale_direct.perform_visit_wizard')
    def visit(cls, addresses):
        pass
