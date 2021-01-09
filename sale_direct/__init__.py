# This file is part of the sale_direct Tryton module.
# Please see the COPYRIGHT and README.rst files at the top level of this
# package for full copyright notices, license terms and support information.
from trytond.pool import Pool

from . import address
from . import configuration
from . import sale
from . import stock
from . import visit


def register():
    Pool.register(
        address.Address,
        configuration.Configuration,
        sale.Sale,
        stock.Move,
        stock.Location,
        visit.PerformVisitAddress,
        visit.PerformVisitEvent,
        visit.PerformVisitSalesMaterial,
        visit.Visit,
        visit.VisitEvent,
        visit.VisitEventSalesMaterial,
        module='sale_direct', type_='model')
    Pool.register(
        visit.PerformVisit,
        visit.RegisterOrder,
        module='sale_direct', type_='wizard')
