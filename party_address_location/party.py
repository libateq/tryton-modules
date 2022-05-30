# This file is part of the party_address_location Tryton module.
# Please see the COPYRIGHT and README.rst files at the top level of this
# package for full copyright notices, license terms and support information.
from math import asin, cos, radians, sqrt

from sql import Literal, Null
from sql.conditionals import Case, Coalesce
from sql.functions import Asin, Cos, Radians, Sqrt

from trytond.config import config
from trytond.model import fields
from trytond.pool import Pool, PoolMeta
from trytond.transaction import Transaction

_earth_radius = config.getfloat(
    'party_address_location', 'earth_radius', default=3959.0)


def calculate_distance(latitude1, longitude1, latitude2, longitude2):
    if None in (latitude1, longitude1, latitude2, longitude2):
        return None

    delta_longitude = radians(longitude2 - longitude1)
    delta_latitude = radians(latitude2 - latitude1)

    hav_latitude = (1 - cos(delta_latitude)) / 2
    hav_longitude = (1 - cos(delta_longitude)) / 2

    return 2 * _earth_radius * asin(sqrt(
        hav_latitude
        + (cos(radians(latitude1)) * cos(radians(latitude2)) * hav_longitude)))


def calculate_distance_column(latitude1, longitude1, latitude2, longitude2):
    latitude1 = Coalesce(latitude1, 0)
    longitude1 = Coalesce(longitude1, 0)
    latitude2 = Coalesce(latitude2, 0)
    longitude2 = Coalesce(longitude2, 0)

    delta_longitude = Radians(longitude2 - longitude1)
    delta_latitude = Radians(latitude2 - latitude1)

    hav_latitude = (Literal(1) - Cos(delta_latitude)) / Literal(2)
    hav_longitude = (Literal(1) - Cos(delta_longitude)) / Literal(2)

    column = Literal(2 * _earth_radius) * Asin(Sqrt(
        hav_latitude
        + (Cos(Radians(latitude1)) * Cos(Radians(latitude2)) * hav_longitude)))

    return Case(
        ((latitude1 is Null) | (longitude1 is Null)
            | (latitude2 is Null) | (longitude2 is Null), Null),
        else_=column)


class Address(metaclass=PoolMeta):
    __name__ = 'party.address'

    latitude = fields.Float("Latitude")
    longitude = fields.Float("Longitude")
    distance = fields.Function(
        fields.Float("Distance", digits=(5, 0)),
        'get_distance', searcher='search_distance')

    @classmethod
    def __setup__(cls):
        super().__setup__()
        cls._order.insert(0, ('distance', 'ASC NULLS LAST'))

    @fields.depends('postal_code')
    def on_change_postal_code(self):
        pool = Pool()
        PostalCode = pool.get('country.postal_code')

        self.latitude = None
        self.longitude = None
        if self.postal_code:
            postal_codes = PostalCode.search(
                [('postal_code', '=', self.postal_code)], limit=1)
            if postal_codes:
                postal_code, = postal_codes
                self.latitude = postal_code.latitude
                self.longitude = postal_code.longitude

    @classmethod
    def get_distance(cls, addresses, name):
        context = Transaction().context
        result = {}
        for address in addresses:
            result[address.id] = calculate_distance(
                context.get('latitude'), context.get('longitude'),
                address.latitude, address.longitude)
        return result

    @classmethod
    def _address_distance_query(cls, latitude, longitude):
        address = cls.__table__()
        return address.select(
            address.id.as_('id'),
            calculate_distance_column(
                address.latitude, address.longitude,
                Literal(latitude), Literal(longitude)).as_('distance'))

    @classmethod
    def search_distance(cls, name, clause):
        context = Transaction().context
        if context.get('latitude') is None or context.get('longitude') is None:
            return [('id', '=', 0)]

        _, operator, value = clause
        Operator = fields.SQL_OPERATORS[operator]
        address_distance = cls._address_distance_query(
            context['latitude'], context['longitude'])
        query = address_distance.select(
            address_distance.id,
            where=Operator(address_distance.distance, value))

        return [('id', 'in', query)]

    @classmethod
    def order_distance(cls, tables):
        address, _ = tables[None]

        context = Transaction().context
        if context.get('latitude') is None or context.get('longitude') is None:
            return [address.postal_code]

        key = 'address_distance'
        if key not in tables:
            address_distance = cls._address_distance_query(
                context['latitude'], context['longitude'])
            query = address.join(
                address_distance, 'LEFT',
                condition=address.id == address_distance.id)
            tables[key] = {
                None: (query.right, query.condition),
                }
        else:
            address_distance, _ = tables[key][None]

        return [address_distance.distance]

    @classmethod
    def _get_postal_codes(cls, *args):
        pool = Pool()
        PostalCode = pool.get('country.postal_code')

        if len(args) < 2:
            postal_codes = {
                v['postal_code'] for v in args[0]
                if (v.get('postal_code')
                    and not v.get('latitude') and not v.get('longitude'))}
        else:
            actions = iter(args)
            postal_codes = {
                v['postal_code'] for s, v in zip(actions, actions) for a in s
                if (not a.latitude and not a.longitude
                    and v.get('postal_code')
                    and not v.get('latitude') and not v.get('longitude'))}

        country_postal_codes = PostalCode.search([
            ('postal_code', 'in', postal_codes),
            ])
        return {z.postal_code: z for z in country_postal_codes}

    @classmethod
    def _located_values(cls, values, postal_codes):
        if (values.get('postal_code') in postal_codes
                and not values.get('latitude')
                and not values.get('longitude')):
            values = values.copy()
            values.update({
                'latitude': postal_codes[values['postal_code']].latitude,
                'longitude': postal_codes[values['postal_code']].longitude,
                })

        return values

    @classmethod
    def create(cls, vlist):
        postal_codes = cls._get_postal_codes(vlist)
        return super().create(
            [cls._located_values(v, postal_codes) for v in vlist])

    @classmethod
    def write(cls, *args):
        postal_codes = cls._get_postal_codes(*args)

        to_write = []
        actions = iter(args)
        for addresses, values in zip(actions, actions):
            if (not values.get('postal_code')
                    or values['postal_code'] not in postal_codes
                    or values.get('latitude') or values.get('longitude')):
                to_write.extend([addresses, values])
            else:
                for address in addresses:
                    if address.longitude or address.latitude:
                        to_write.extend([[address], values])
                    else:
                        to_write.extend([
                                [address],
                                cls._located_values(values, postal_codes)])

        super().write(*to_write)
