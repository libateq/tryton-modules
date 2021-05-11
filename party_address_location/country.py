# This file is part of the party_address_location Tryton module.
# Please see the COPYRIGHT and README.rst files at the top level of this
# package for full copyright notices, license terms and support information.
from trytond.model import fields
from trytond.pool import PoolMeta


class PostalCode(metaclass=PoolMeta):
    __name__ = 'country.postal_code'

    latitude = fields.Float("Latitude")
    longitude = fields.Float("Longitude")
