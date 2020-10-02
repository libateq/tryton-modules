# This file is part of the account_chart_variant Tryton module.
# Please see the COPYRIGHT and README.rst files at the top level of this
# package for full copyright notices, license terms and support information.
from trytond.model import fields
from trytond.pool import Pool
from trytond.transaction import Transaction


class VariantMixin:

    variant_names = fields.Function(
        fields.Char("Variants"),
        'on_change_with_variant_names')

    @fields.depends('variants')
    def on_change_with_variant_names(self, name=None):
        if self.variants:
            values = [v.rec_name for v in self.variants[:3]]
            if self.variants[3:]:
                values.append("...")
            return ', '.join(values)

    @classmethod
    def _get_chart_records(cls, template_id):
        raise NotImplementedError

    @classmethod
    def get_chart_variants(cls, template):
        variants = set()
        records = cls._get_chart_records(template.id)
        while records:
            variants |= set(v.id for r in records for v in r.variants)
            records = sum((getattr(r, 'childs', ()) for r in records), ())
        return variants

    @classmethod
    def _get_excluded(cls, records):
        pool = Pool()
        ChartVariant = pool.get('account.chart_variant')

        transaction = Transaction()
        variants = set(ChartVariant.browse(
            transaction.context.get('variants', [])))

        excluded = {}
        while records:
            excluded.update({
                r.id: r for r in records
                if ((r.variants and not(set(r.variants) & variants))
                    or (getattr(r, 'parent', None)
                        and r.parent.id in excluded))})
            records = sum((getattr(r, 'childs', ()) for r in records), ())

        return excluded

    @classmethod
    def _get_excluded_lines(cls, records):
        return sum((e.lines for e in cls._get_excluded(records).values()), ())
