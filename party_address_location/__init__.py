# This file is part of the party_address_location Tryton module.
# Please see the COPYRIGHT and README.rst files at the top level of this
# package for full copyright notices, license terms and support information.
from trytond.pool import Pool

from . import country, party


def register():
    Pool.register(
        country.PostalCode,
        party.Address,
        module='party_address_location', type_='model')
