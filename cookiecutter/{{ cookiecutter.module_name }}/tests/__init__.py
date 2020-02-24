# This file is part of the {{ cookiecutter.module_name }} Tryton module.
# Please see the COPYRIGHT and README files at the top level of this repository
# for full copyright notices, license terms and support information.
try:
    from trytond.modules.{{ cookiecutter.module_name }}.tests.test_{{ cookiecutter.module_name }} import suite{% if cookiecutter.module_name|length > 14 %}  # noqa: E501{% endif %}
except ImportError:
    from .test_{{ cookiecutter.module_name }} import suite

__all__ = ['suite']
