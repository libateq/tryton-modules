# This file is part of the {{ cookiecutter.module_name }} Tryton module.
# Please see the COPYRIGHT and README.rst files at the top level of this
# package for full copyright notices, license terms and support information.
from trytond.tests.test_tryton import ModuleTestCase


class {{ cookiecutter.module_name.replace('_', ' ').title().replace(' ', '') }}TestCase(ModuleTestCase):
    "Test {{ cookiecutter.module_name.replace('_', ' ').title() }} module"
    module = '{{ cookiecutter.module_name }}'


del ModuleTestCase
