# This file is part of the account_chart_variant Tryton module.
# Please see the COPYRIGHT and README.rst files at the top level of this
# package for full copyright notices, license terms and support information.
from trytond.pool import Pool

from . import account
from . import tax


def register():
    Pool.register(
        account.ChartVariant,
        account.Account,
        account.AccountChartVariant,
        account.AccountTemplate,
        account.AccountTemplateVariant,
        account.TypeTemplate,
        account.TypeTemplateVariant,
        account.CreateChartAccount,
        tax.TaxTemplate,
        tax.TaxTemplateVariant,
        tax.TaxCodeTemplate,
        tax.TaxCodeTemplateVariant,
        tax.TaxCodeLineTemplate,
        tax.TaxCodeLineTemplateVariant,
        tax.TaxRuleTemplate,
        tax.TaxRuleTemplateVariant,
        tax.TaxRuleLineTemplate,
        tax.TaxRuleLineTemplateVariant,
        module='account_chart_variant', type_='model')
    Pool.register(
        account.CreateChart,
        account.UpdateChart,
        module='account_chart_variant', type_='wizard')
