# This file is part of the account_chart_variant Tryton module.
# Please see the COPYRIGHT and README.rst files at the top level of this
# package for full copyright notices, license terms and support information.
from trytond.model import ModelSQL, fields
from trytond.pool import Pool, PoolMeta

from .common import VariantMixin


class TaxTemplateVariant(ModelSQL):
    "Tax Template - Chart Variant"
    __name__ = 'account.tax.template-account.chart_variant'

    tax = fields.Many2One(
        'account.tax.template', "Tax", required=True, ondelete='CASCADE')
    variant = fields.Many2One(
        'account.chart_variant', "Variant", required=True, ondelete='CASCADE')


class TaxTemplate(VariantMixin, metaclass=PoolMeta):
    __name__ = 'account.tax.template'

    variants = fields.Many2Many(
        'account.tax.template-account.chart_variant', 'tax', 'variant',
        "Variants")

    @classmethod
    def _get_chart_records(cls, template_id):
        return cls.search([
                ('account', '=', template_id),
                ('parent', '=', None),
                ])

    @classmethod
    def create_tax(
            cls, account_id, company_id, template2account, template2tax=None):
        if template2tax is None:
            template2tax = {}
        taxes = cls._get_chart_records(account_id)
        template2tax.update({e: None for e in cls._get_excluded(taxes)})
        super().create_tax(
            account_id, company_id, template2account, template2tax)


class TaxCodeTemplateVariant(ModelSQL):
    "Tax Code Template - Chart Variant"
    __name__ = 'account.tax.code.template-account.chart_variant'

    tax_code = fields.Many2One(
        'account.tax.code.template', "Tax Code", required=True,
        ondelete='CASCADE')
    variant = fields.Many2One(
        'account.chart_variant', "Variant", required=True, ondelete='CASCADE')


class TaxCodeTemplate(VariantMixin, metaclass=PoolMeta):
    __name__ = 'account.tax.code.template'

    variants = fields.Many2Many(
        'account.tax.code.template-account.chart_variant',
        'tax_code', 'variant', "Variants")

    @classmethod
    def _get_chart_records(cls, template_id):
        return cls.search([
                ('account', '=', template_id),
                ('parent', '=', None),
                ])

    @classmethod
    def create_tax_code(cls, account_id, company_id, template2tax_code=None):
        if template2tax_code is None:
            template2tax_code = {}
        tax_codes = cls._get_chart_records(account_id)
        template2tax_code.update(
            {e: None for e in cls._get_excluded(tax_codes)})
        super().create_tax_code(account_id, company_id, template2tax_code)


class TaxCodeLineTemplateVariant(ModelSQL):
    "Tax Code Line Template - Chart Variant"
    __name__ = 'account.tax.code.line.template-account.chart_variant'

    tax_code_line = fields.Many2One(
        'account.tax.code.line.template', "Tax Code Line", required=True,
        ondelete='CASCADE')
    variant = fields.Many2One(
        'account.chart_variant', "Variant", required=True, ondelete='CASCADE')


class TaxCodeLineTemplate(VariantMixin, metaclass=PoolMeta):
    __name__ = 'account.tax.code.line.template'

    variants = fields.Many2Many(
        'account.tax.code.line.template-account.chart_variant',
        'tax_code_line', 'variant', "Variants")

    @classmethod
    def _get_chart_records(cls, template_id):
        return cls.search([
                ('code.account', '=', template_id),
                ])

    @classmethod
    def create_tax_code_line(
            cls, account_id, template2tax, template2tax_code,
            template2tax_code_line=None):
        pool = Pool()
        TaxCodeTemplate = pool.get('account.tax.code.template')

        if template2tax_code_line is None:
            template2tax_code_line = {}

        tax_code_lines = cls._get_chart_records(account_id)
        template2tax_code_line.update(
            {e: None for e in cls._get_excluded(tax_code_lines)})

        tax_codes = TaxCodeTemplate._get_chart_records(account_id)
        template2tax_code_line.update(
            {e: None for e in cls._get_excluded_lines(tax_codes)})

        super().create_tax_code_line(
            account_id, template2tax, template2tax_code,
            template2tax_code_line)


class TaxRuleTemplateVariant(ModelSQL):
    "Tax Rule Template - Chart Variant"
    __name__ = 'account.tax.rule.template-account.chart_variant'

    tax_rule = fields.Many2One(
        'account.tax.rule.template', "Tax Rule", required=True,
        ondelete='CASCADE')
    variant = fields.Many2One(
        'account.chart_variant', "Variant", required=True, ondelete='CASCADE')


class TaxRuleTemplate(VariantMixin, metaclass=PoolMeta):
    __name__ = 'account.tax.rule.template'

    variants = fields.Many2Many(
        'account.tax.rule.template-account.chart_variant',
        'tax_rule', 'variant', "Variants")

    @classmethod
    def _get_chart_records(cls, template_id):
        return cls.search([
                ('account', '=', template_id),
                ])

    @classmethod
    def create_rule(cls, account_id, company_id, template2rule=None):
        if template2rule is None:
            template2rule = {}
        tax_rules = cls._get_chart_records(account_id)
        template2rule.update({e: None for e in cls._get_excluded(tax_rules)})
        super().create_rule(account_id, company_id, template2rule)


class TaxRuleLineTemplateVariant(ModelSQL):
    "Tax Rule Line Template - Chart Variant"
    __name__ = 'account.tax.rule.line.template-account.chart_variant'

    tax_rule_line = fields.Many2One(
        'account.tax.rule.line.template', "Tax Rule Line", required=True,
        ondelete='CASCADE')
    variant = fields.Many2One(
        'account.chart_variant', "Variant", required=True, ondelete='CASCADE')


class TaxRuleLineTemplate(VariantMixin, metaclass=PoolMeta):
    __name__ = 'account.tax.rule.line.template'

    variants = fields.Many2Many(
        'account.tax.rule.line.template-account.chart_variant',
        'tax_rule_line', 'variant', "Variants")

    @classmethod
    def _get_chart_records(cls, template_id):
        return cls.search([
                ('rule.account', '=', template_id),
                ])

    @classmethod
    def create_rule_line(
            cls, account_id, template2tax, template2rule,
            template2rule_line=None):
        pool = Pool()
        TaxRuleTemplate = pool.get('account.tax.rule.template')

        if template2rule_line is None:
            template2rule_line = {}

        tax_rule_lines = cls._get_chart_records(account_id)
        template2rule_line.update(
            {e: None for e in cls._get_excluded(tax_rule_lines)})

        tax_rules = TaxRuleTemplate._get_chart_records(account_id)
        template2rule_line.update(
            {e: None for e in cls._get_excluded_lines(tax_rules)})

        super().create_rule_line(
            account_id, template2tax, template2rule, template2rule_line)
