General Usage
=============

This module allow users to optionally use the Time-based One-Time Passwords
(TOTP) provided by the authentication_totp_ module.

Once activated and :doc:`setup`, if you have set a *TOTP Secret* on your
account, then will need to enter the correct TOTP code when authenticating.
If you do not have a *TOTP Secret* set on your account then the TOTP
authentication will be skipped.

.. _authentication_totp: https://bitbucket.org/libateq/tryton-modules/src/development/authentication_totp/


Setting the TOTP Secret
-----------------------

This module provides a *Setup Time-based One-Time Password Authentication*
wizard which guides you through setting up a TOTP.  Using the *Update Secret*
button in your preferences will run this wizard when the preferences window
is closed.  If available the QR code for the secret will also be displayed,
and this allows the secret to be easily shared with your authenticator app.
