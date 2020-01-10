{{ cookiecutter.module_name.replace('_', ' ').title() }} Module
{{ '#' * (cookiecutter.module_name|replace('_', ' ')|title|length + 7) }}

{{ ('A module for the Tryton application platform that ' + cookiecutter.purpose + '.') | wordwrap }}


Contents
========

.. toctree::
    :maxdepth: 2

    installation
    support
    changelog
    license
