Setup
=====

Once the module has been activated you can start using it by including the
``password_totp`` authentication method in the `[session] authentications
<https://docs.tryton.org/projects/server/en/latest/topics/configuration.html#authentications>`_
configuration option.

.. warning::

    Remember to remove the ``password`` authentication method from the
    ``[session] authentications`` option when enabling time-based one-time
    passwords.  If the list of authentications is set to 
    ``password_totp,password`` a user will be able to login without entering a
    valid TOTP access code.  This is because each authentication method is
    tried in turn.  So when the ``password_totp`` authentication fails the
    system will then try the ``password`` authentication, which will succeed.


Configuration Options
---------------------

This module will work without any additional setup, however it does add a few
configuration options that allow you to adjust its behaviour to fit your
deployment.  All these configuration options should be set inside the
``[authentication_totp]`` section of your `configuration file
<https://docs.tryton.org/projects/server/en/latest/topics/configuration.html>`_.

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

        The `Passlib AppWallet documentation
        <https://passlib.readthedocs.io/en/stable/lib/passlib.totp.html#appwallet>`_
        contains further information.

    Default value: ``None``

issuer
    The issuer is a name that is included in the QR codes used with
    authenticator apps.  It helps the users know which TOTP is for which
    service.  It is formatted before it is used, and can include the name
    of the user's main company.  Note, use without the ``company`` module is
    supported.

    Default value: ``{company} Tryton``

key_length
    This configuration option allows you to change the length of the keys that
    are generated when a new TOTP secret is required.  The `RFC 4226
    <https://tools.ietf.org/html/rfc4226.html>`_ (which is what TOTP
    `RFC 6238 <https://tools.ietf.org/html/rfc6238.html>`_ is based on)
    suggests that keys should be at least 128 bits long, and recommends using
    160 bit keys.

    Default value: ``160``
