{{ '#' * (cookiecutter.module_title|length + 7) }}
{{ cookiecutter.module_title }} Module
{{ '#' * (cookiecutter.module_title|length + 7) }}

{{ ('The *' + cookiecutter.module_title '* ' + cookiecutter.purpose + '.') | wordwrap }}

.. toctree::
   :maxdepth: 2

   installation
   setup
   usage
   configuration
   design
   support
   license
