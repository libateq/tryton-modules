# This file is part of the {{ cookiecutter.module_name }} Tryton module.
# Please see the COPYRIGHT and README.rst files at the top level of this
# package for full copyright notices, license terms and support information.
from unittest import TestLoader
{%- if cookiecutter.test_with_scenario.lower().startswith('y') %}
from doctest import DocFileSuite, REPORT_ONLY_FIRST_FAILURE
{%- endif %}

{% if cookiecutter.test_with_scenario.lower().startswith('y') -%}
from trytond.tests.test_tryton import (
    ModuleTestCase, doctest_checker, doctest_teardown, suite as test_suite)
{%- else -%}
from trytond.tests.test_tryton import ModuleTestCase, suite as test_suite
{%- endif %}


class {{ cookiecutter.module_name.replace('_', ' ').title().replace(' ', '') }}TestCase(ModuleTestCase):
    "Test {{ cookiecutter.module_name.replace('_', ' ').title() }} module"
    module = '{{ cookiecutter.module_name }}'


def suite():
    suite = test_suite()
    suite.addTests(TestLoader().loadTestsFromTestCase(
        {{ cookiecutter.module_name.replace('_', ' ').title().replace(' ', '') }}TestCase))
    {%- if cookiecutter.test_with_scenario.lower().startswith('y') %}
    suite.addTests(DocFileSuite(
        'scenario_{{ cookiecutter.module_name }}.rst',
        tearDown=doctest_teardown, encoding='utf-8', checker=doctest_checker,
        optionflags=REPORT_ONLY_FIRST_FAILURE))
    {%- endif %}
    return suite
