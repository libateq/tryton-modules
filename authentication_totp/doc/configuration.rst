*************
Configuration
*************

The *Authentication TOTP Module* has a few configuration options that allow
you to adjust its behaviour to fit your deployment.
All these configuration options should be set inside the
``[authentication_totp]`` section of
:doc:`configuration file <trytond:topics/configuration>`.

.. _config-authentication_totp.application_secrets_file:

``application_secrets_file``
============================

This is the path to a file that contains secrets that are used to encrypt
and decrypt the TOTP keys when they are stored and retrieved from the
database.
The file should contain lines of the form ``tag: secret``.
It is recommended to either incremental counters (``1``, ``2``, ...) or
ISO dates (``2020-05-04``, ``2020-07-21``, ...) as the ``tag``.
Take care to ensure the secrets have sufficient entropy.

Suitable lines can be created as follows:

.. code-block:: bash

   python3 -c "
   from passlib.totp import generate_secret
   from datetime import date
   print('{}: {}'.format(date.today(), generate_secret()))"

.. note::

   This configuration option is not set by default.
   This means the TOTP keys are stored unencrypted in the database.
   It is **strongly recommended** that you setup a suitable secrets file
   and use it, especially on production systems.

.. seealso::

   The `Passlib AppWallet documentation`__ contains further information.

   __ https://passlib.readthedocs.io/en/stable/lib/passlib.totp.html#appwallet

The default value is: ``None``

.. _config-authentication_totp.issuer:

``issuer``
==========

The issuer is a name that is included in the QR codes used with authenticator
apps.
It helps the `Users <model-res.user>` know which TOTP key is for which service.
It is formatted before it is used, and can include the name of the user's main
`Company <company:model-company.company>`.

.. note::

   The *Authentication TOTP Module* can be activated without the
   :doc:`Company Module <company:index>` module being activated.
   In this case the ``{company}`` part of the issuer is left blank.

The default value is: ``{company} Tryton``

.. _config-authentication_totp.key_length:

``key_length``
==============

This configuration option allows you to change the length of the keys that
are generated when a new TOTP secret is required.

.. note::

   The :rfc:4226 (which is what TOTP :rfc:6238 is based on) suggests that keys
   should be at least 128 bits long, and recommends using 160 bit keys.

The default value is: ``160``
