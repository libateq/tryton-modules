{{ cookiecutter.module_name.replace('_', ' ').title() }} Tryton Module
{{ '#' * (cookiecutter.module_name|replace('_', ' ')|title|length + 14) }}

{{ ('A module for the Tryton application platform that ' + cookiecutter.purpose + '.') | wordwrap }}

.. start-of-readme-only-text

Installation
============

.. code:: python

    pip3 install {{ cookiecutter.package_name|replace('_', '-') }}
