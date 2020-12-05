# This file is part of the sale_direct Tryton module.
# Please see the COPYRIGHT and README.rst files at the top level of this
# package for full copyright notices, license terms and support information.
from trytond.model import fields
from trytond.pool import PoolMeta
from trytond.pyson import Eval, If


class Sale(metaclass=PoolMeta):
    __name__ = 'sale.sale'

    origin_model = fields.Function(fields.Selection(
        'get_origin_models', "Origin Model"),
        'on_change_with_origin_model')

    @classmethod
    def __setup__(cls):
        super().__setup__()
        cls.party.domain = [('general_address_party', '!=', True)]
        cls.origin.domain = [
            cls.origin.domain,
            If(Eval('origin_model') == 'sale.direct.visit',
                [
                    ('address', 'in', [
                        Eval('invoice_address', -1),
                        Eval('shipment_address', -1)]),
                ],
                [])]
        cls.origin.depends.extend([
            'origin_model',
            'invoice_address',
            'shipment_address'])

    @classmethod
    def _get_origin(cls):
        return super()._get_origin() + ['sale.direct.visit']

    @classmethod
    def get_origin_models(cls):
        return cls.get_origin()

    @fields.depends('origin')
    def on_change_with_origin_model(self, name=None):
        if self.origin:
            return self.origin.__name__
