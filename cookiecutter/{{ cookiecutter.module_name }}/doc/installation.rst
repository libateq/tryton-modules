************
Installation
************

Prerequisites
=============

* Python 3.7 or later (http://www.python.org/)
* See the :file:`setup.py` file for Python package dependencies.
* See the :file:`tryton.cfg` file for Tryton module dependencies.

Using ``pip``
=============

The easiest way to install this module and it's dependencies is directly from
the Python Package Index:

.. code-block:: bash

   pip3 install {{ cookiecutter.package_name }}

Using sources
=============

Alternatively, you can clone the *{{ cookiecutter.tryton_modules_repository_name }}* repository, and install the
module from there:

.. code-block:: bash

   git clone {{ cookiecutter.tryton_modules_repository_url }}
   cd {{ cookiecutter.tryton_modules_repository_name }}/{{ cookiecutter.module_name }}
   python3 setup.py install

Other information
=================

You may need administrator/root privileges to perform the installation, as the
install commands will by default attempt to install the module to the system
wide Python site-packages directory on your system.

For advanced options, please refer to the standard Python packaging and
installation documentation:

* https://docs.python.org/3/installing/index.html

To use without installation, extract the archive into :file:`trytond/modules`
with the directory name :file:`{{ cookiecutter.module_name }}`.
