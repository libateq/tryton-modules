************
Installation
************

Prerequisites
=============

* Python 3.6 or later (http://www.python.org/)
* See the :file:`setup.py` file for Python package dependencies.
* See the :file:`tryton.cfg` file for Tryton module dependencies.

Using ``pip``
=============

The easiest way to install this module and it's dependencies is directly from
the Python Package Index:

.. code-block:: bash

   pip3 install trytonlq_authentication_totp

If you want to display :abbr:`QR (Quick Response)` codes for use with
authenticator apps, then you will need some additional packages installed on
your system.
This is done automatically if you run:

.. code-block:: bash

   pip3 install trytonlq_authentication_totp[qrcode]

Using sources
=============

Alternatively, you can clone the *tryton-modules* repository, and install the
module from there:

.. code-block:: bash

   git clone https://bitbucket.org/libateq/tryton-modules
   cd tryton-modules/authentication_totp
   python3 setup.py install

Other Information
=================

You may need administrator/root privileges to perform the installation, as the
install commands will by default attempt to install the module to the system
wide Python site-packages directory on your system.

For advanced options, please refer to the standard Python packaging and
installation documentation:

* https://docs.python.org/3/installing/index.html

To use without installation, extract the archive into :file:`trytond/modules`
with the directory name :file:`authentication_totp`.
