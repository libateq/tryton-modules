# This file is part of the account_uk_variants Tryton module.
# Please see the COPYRIGHT and README.rst files at the top level of this
# package for full copyright notices, license terms and support information.
from trytond.pool import Pool


def register():
    Pool.register(
        module='account_uk_variants', type_='model')
    Pool.register(
        module='account_uk_variants', type_='report')
    Pool.register(
        module='account_uk_variants', type_='wizard')
