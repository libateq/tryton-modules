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

.. _config-authentication_totp.window:

``window``
==========

The number of seconds forwards and backwards in time to search when checking
whether the TOTP code matches.
This can be used to account for transmission delays and small amounts of skew
in the client's clock.

.. note::

   The default value is normally more than enough to account for transmission
   delays and user TOTP code entry times, if client and server clocks are both
   using a reliable time source such as NTP__.

   __ https://en.wikipedia.org/wiki/Network_Time_Protocol

The default value is: The period_ value

.. _config-authentication_totp.skew:

``skew``
========

The number of seconds to adjust the time by before checking whether the TOTP
code matches.
Negative skew is used to account for the client clock running behind the server
clock.
Positive skew indicates the client clock is running ahead of the server clock.

.. tip::

   For most use cases this setting should be left at ``0``.
   It is normally best to account for clock skew and transmission delays
   by using the window_ parameter.

The default value is: ``0``

.. _config-authentication_totp.digits:

``digits``
==========

The number of digits in the generated and/or accepted tokens.
Must be between 6 and 10 inclusive.

.. warning::

   Changing this value from the default may cause problems with some OTP
   client programs which may not support alternative values.

.. warning::

   Due to a limitation of the HOTP algorithm the 10th digit can only contain
   values 0 to 2, and so offers very little extra security.

The default value is: ``6``

.. _config-authentication_totp.algorithm:

``algorithm``
=============

The name of the hash algorithm to use.
This, as defined in :rfc:6238, can be one of ``sha1``, ``sha256`` or
``sha512``.

.. warning::

   Changing this value from the default may cause problems with some OTP
   client programs which may not support alternative values.

The default value is: ``sha1``

.. _config-authentication_totp.period:

``period``
==========

How often, in seconds, the generated token changes.

.. warning::

   Changing this value from the default may cause problems with some OTP
   client programs which may not support alternative values.

The default value is: ``30``
