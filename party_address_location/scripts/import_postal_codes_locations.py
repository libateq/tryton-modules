#!/usr/bin/env python3
# This file is part of the party_address_location Tryton module.
# Please see the COPYRIGHT and README.rst files at the top level of this
# package for full copyright notices, license terms and support information.
import csv
import sys
from io import StringIO

from proteus import Model

from trytond.modules.country.scripts import import_postal_codes

try:
    from progressbar import ETA, Bar, ProgressBar, SimpleProgress
except ImportError:
    ProgressBar = None


def import_(data):
    PostalCode = Model.get('country.postal_code')
    Country = Model.get('country.country')
    Subdivision = Model.get('country.subdivision')
    print('Importing', file=sys.stderr)

    def get_country(code):
        country = countries.get(code)
        if not country:
            country, = Country.find([('code', '=', code)])
            countries[code] = country
        return country
    countries = {}

    def get_subdivision(country, code):
        code = '%s-%s' % (country, code)
        subdivision = subdivisions.get(code)
        if not subdivision:
            try:
                subdivision, = Subdivision.find([('code', '=', code)])
            except ValueError:
                return
            subdivisions[code] = subdivision
        return subdivision
    subdivisions = {}

    if ProgressBar:
        pbar = ProgressBar(
            widgets=[SimpleProgress(), Bar(), ETA()])
    else:
        pbar = iter
    f = StringIO(data.decode('utf-8'))
    postal_codes = []
    for row in pbar(list(csv.DictReader(
                    f, fieldnames=import_postal_codes._fieldnames,
                    delimiter='\t'))):
        country = get_country(row['country'])
        for code in ['code1', 'code2', 'code3']:
            subdivision = get_subdivision(row['country'], row[code])
            if code == 'code1' or subdivision:
                postal_codes.append(
                    PostalCode(
                        country=country, subdivision=subdivision,
                        postal_code=row['postal'], city=row['place'],
                        latitude=float(row['latitude']),
                        longitude=float(row['longitude'])))
    PostalCode.save(postal_codes)


import_postal_codes.import_ = import_


if __name__ == '__main__':
    import_postal_codes.run()
