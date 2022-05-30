# This file is part of the {{ cookiecutter.module_name }} Tryton module.
# Please see the COPYRIGHT and README.rst files at the top level of this
# package for full copyright notices, license terms and support information.
from trytond.pool import Pool


def register():
    Pool.register(
        module='{{ cookiecutter.module_name }}', type_='model')
    Pool.register(
        module='{{ cookiecutter.module_name }}', type_='wizard')
    Pool.register(
        module='{{ cookiecutter.module_name }}', type_='report')
