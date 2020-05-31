Setup
=====

Once the module has been activated you can start using it by including the
``totp_optional`` authentication method in the `[session] authentications`_
configuration option.

You will also need to make sure you have correctly setup the
authentication_totp_ module as well.

.. _`[session] authentications`: https://docs.tryton.org/projects/server/en/latest/topics/configuration.html#authentications
.. _authentication_totp: https://bitbucket.org/libateq/tryton-modules/src/development/authentication_totp/


Prompting Users to Setup TOTP
-----------------------------

You can prompt users to setup TOTP by adding the *Setup Time-based One-Time
Password Authentication* wizard to their login *Actions*.  To help make this
process simpler a trigger is provided that will automatically do this when
a new user is created.  This trigger can easily be deactivated if desired.

With this action in place, the wizard will run when the user logs in.  This
will automatically generate a new secret for the user and will help them add
it to their authenticator app.
