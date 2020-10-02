# This file is part of the account_chart_variant Tryton module.
# Please see the COPYRIGHT and README.rst files at the top level of this
# package for full copyright notices, license terms and support information.
from trytond.model import ModelSQL, ModelView, fields
from trytond.pool import Pool, PoolMeta
from trytond.pyson import Bool, Eval
from trytond.transaction import Transaction

from .common import VariantMixin


class ChartVariant(ModelSQL, ModelView):
    "Chart Variant"
    __name__ = 'account.chart_variant'

    name = fields.Char("Name")


class AccountChartVariant(ModelSQL):
    "Account - Chart Variant"
    __name__ = 'account.account-account.chart_variant'

    account = fields.Many2One(
        'account.account', "Account", domain=[('parent', '=', None)],
        required=True, ondelete='CASCADE')
    variant = fields.Many2One(
        'account.chart_variant', "Variant", required=True, ondelete='CASCADE')


class Account(metaclass=PoolMeta):
    __name__ = 'account.account'

    variants = fields.Many2Many(
        'account.account-account.chart_variant', 'account', 'variant',
        "Variants",
        states={
            'invisible': Bool(Eval('parent')),
        }, depends=['parent'])

    @classmethod
    def create(cls, vlist):
        accounts = super().create(vlist)

        variants = Transaction().context.get('variants', None)
        root_accounts = [a for a in accounts if a.parent is None]
        if root_accounts and variants is not None:
            for root_account in root_accounts:
                root_account.variants = variants
            cls.save(root_accounts)

        return accounts


class AccountTemplateVariant(ModelSQL):
    "Account Template - Chart Variant"
    __name__ = 'account.account.template-account.chart_variant'

    account = fields.Many2One(
        'account.account.template', "Account", required=True,
        ondelete='CASCADE')
    variant = fields.Many2One(
        'account.chart_variant', "Variant", required=True, ondelete='CASCADE')


class AccountTemplate(VariantMixin, metaclass=PoolMeta):
    __name__ = 'account.account.template'

    variants = fields.Many2Many(
        'account.account.template-account.chart_variant', 'account',
        'variant', "Variants")

    @classmethod
    def _get_chart_records(cls, template_id):
        return [cls(template_id)]

    def create_account(
            self, company_id, template2account=None, template2type=None):
        if template2account is None:
            template2account = {}
        template2account.update({e: None for e in self._get_excluded([self])})
        super().create_account(company_id, template2account, template2type)

    def update_account2(
            self, template2account, template2tax, template_done=None):
        if template_done is None:
            template_done = []
        template_done.extend(self._get_excluded([self]))
        super().update_account2(template2account, template2tax, template_done)


class TypeTemplateVariant(ModelSQL):
    "Account Type Template - Chart Variant"
    __name__ = 'account.account.type.template-account.chart_variant'

    account_type = fields.Many2One(
        'account.account.type.template', "Account Type", required=True,
        ondelete='CASCADE')
    variant = fields.Many2One(
        'account.chart_variant', "Variant", required=True, ondelete='CASCADE')


class TypeTemplate(VariantMixin, metaclass=PoolMeta):
    __name__ = 'account.account.type.template'

    variants = fields.Many2Many(
        'account.account.type.template-account.chart_variant',
        'account_type', 'variant', "Variants")

    @classmethod
    def _get_chart_records(cls, template_id):
        pool = Pool()
        AccountTemplate = pool.get('account.account.template')
        return [AccountTemplate(template_id).type]

    def create_type(self, company_id, template2type=None):
        if template2type is None:
            template2type = {}
        template2type.update({e: None for e in self._get_excluded([self])})
        super().create_type(company_id, template2type)


class CreateChartAccount(metaclass=PoolMeta):
    __name__ = 'account.create_chart.account'

    variants = fields.Many2Many(
        'account.chart_variant', None, None, "Variants",
        domain=[('id', 'in', Eval('chart_variants'))],
        depends=['chart_variants'])
    chart_variants = fields.Function(
        fields.Many2Many(
            'account.chart_variant', None, None, "Chart Variants"),
        'on_change_with_chart_variants')

    @fields.depends('account_template')
    def on_change_with_chart_variants(self, name=None):
        pool = Pool()
        AccountTemplate = pool.get('account.account.template')
        TypeTemplate = pool.get('account.account.type.template')
        TaxTemplate = pool.get('account.tax.template')
        TaxCodeTemplate = pool.get('account.tax.code.template')
        TaxCodeLineTemplate = pool.get('account.tax.code.line.template')
        TaxRuleTemplate = pool.get('account.tax.rule.template')
        TaxRuleLineTemplate = pool.get('account.tax.rule.line.template')

        variants = set()
        template = self.account_template
        if template:
            variants |= AccountTemplate.get_chart_variants(template)
            variants |= TypeTemplate.get_chart_variants(template)
            variants |= TaxTemplate.get_chart_variants(template)
            variants |= TaxCodeTemplate.get_chart_variants(template)
            variants |= TaxCodeLineTemplate.get_chart_variants(template)
            variants |= TaxRuleTemplate.get_chart_variants(template)
            variants |= TaxRuleLineTemplate.get_chart_variants(template)

        return list(variants)


class CreateChart(metaclass=PoolMeta):
    __name__ = 'account.create_chart'

    def transition_create_account(self):
        variants = [v.id for v in self.account.variants]
        with Transaction().set_context(variants=variants):
            return super().transition_create_account()

    # TODO: Remove once https://bugs.tryton.org/issue9657 has been fixed
    def default_properties(self, fields):
        pool = Pool()
        Account = pool.get('account.account')

        defaults = {
            'company': self.account.company.id,
            }

        receivable_accounts = Account.search([
                ('type.receivable', '=', True),
                ], limit=2)
        payable_accounts = Account.search([
                ('type.payable', '=', True),
                ], limit=2)

        if len(receivable_accounts) == 1:
            defaults['account_receivable'] = receivable_accounts[0].id
        if len(payable_accounts) == 1:
            defaults['account_payable'] = payable_accounts[0].id

        return defaults


class UpdateChart(metaclass=PoolMeta):
    __name__ = 'account.update_chart'

    def transition_update(self):
        variants = [v.id for v in self.start.account.variants]
        with Transaction().set_context(variants=variants):
            return super().transition_update()

    # TODO: Remove once https://bugs.tryton.org/issue9663 has been fixed
    def default_start(self, fields):
        pool = Pool()
        Account = pool.get('account.account')

        defaults = {}
        charts = Account.search([
                ('parent', '=', None),
                ], limit=2)
        if len(charts) == 1:
            defaults['account'] = charts[0].id
        return defaults
