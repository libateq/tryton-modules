Setup
=====

Once the module has been activated you can start using it by including the
``totp``, ``totp_optional``, ``password_totp`` or ``password_totp_optional``
authentication methods in the `[session] authentications`_ configuration
option.

The methods that start with ``password`` will first ask for the user's
password before requesting a TOTP code from the user.  This then provides
2 factor authentication for users that have a *TOTP Secret* setup.

The difference between the optional and non-optional authentication methods is
that the ``totp`` methods always require the user to enter a code to verify
their identity, so a code must be setup for the user before they first login.
Whereas the ``totp_optional`` methods only require a code if the user has
already setup a *TOTP Secret*.

.. _`[session] authentications`: https://docs.tryton.org/projects/server/en/latest/topics/configuration.html#authentications


Configuration Options
---------------------

This module will work without any additional setup, however it does add a few
configuration options that allow you to adjust its behaviour to fit your
deployment.  All these configuration options should be set inside the
``[authentication_totp]`` section of your `configuration file`_.

.. _`configuration file`: https://docs.tryton.org/projects/server/en/latest/topics/configuration.html

application_secrets_file
    This is the path to a file that contains secrets that are used to encrypt
    and decrypt the TOTP keys when they are stored and retrieved from the
    database.  The file should contain lines of the form ``tag: secret``.
    It is recommended to either incremental counters (``1``, ``2``, ...) or
    ISO dates (``2020-05-04``, ``2020-07-21``, ...) as the ``tag``.  Take care
    to ensure the secrets have sufficient entropy.

    Suitable lines can be created as follows:

    .. code-block:: bash

        python3 -c "
        from passlib.totp import generate_secret
        from datetime import date
        print('{}: {}'.format(date.today(), generate_secret()))"

    This configuration option is not set by default.  This means the TOTP keys
    are stored unencrypted in the database.  It is **strongly recommended**
    that you setup a suitable secrets file and use it, especially on production
    systems.

    .. seealso::

        The `Passlib AppWallet documentation`_ contains further information.

        .. _`Passlib AppWallet documentation`: https://passlib.readthedocs.io/en/stable/lib/passlib.totp.html#appwallet

    Default value: ``None``

issuer
    The issuer is a name that is included in the QR codes used with
    authenticator apps.  It helps the users know which TOTP is for which
    service.  It is formatted before it is used, and can include the name
    of the user's main company.  Note, use without activating the ``company``
    module is supported, in which case the ``company`` is left blank.

    Default value: ``{company} Tryton``

key_length
    This configuration option allows you to change the length of the keys that
    are generated when a new TOTP secret is required.  The `RFC 4226`_ (which
    is what TOTP `RFC 6238`_ is based on) suggests that keys should be at least
    128 bits long, and recommends using 160 bit keys.

    .. _`RFC 4226`: https://tools.ietf.org/html/rfc4226.html
    .. _`RFC 6238`: https://tools.ietf.org/html/rfc6238.html

    Default value: ``160``


Prompting Users to Setup TOTP
-----------------------------

You can prompt users to setup TOTP by adding the *Setup Time-based One-Time
Password Authentication* wizard to their login *Actions*.  To help make this
process simpler a trigger is provided that will automatically do this when
a new user is created.  This trigger can easily be deactivated if desired.

With this action in place, the wizard will run when the user logs in.  This
will automatically generate a new secret for the user and will help them add
it to their authenticator app.
