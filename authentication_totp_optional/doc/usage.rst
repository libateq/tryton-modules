*****
Usage
*****

This module allow users to optionally use the Time-based One-Time Passwords
(TOTP) provided by the
:doc:`Authentication TOTP Module <authentication_totp:index>`.

.. _Optionally using TOTP authentication:

Optionally using TOTP authentication
====================================

Once activated and :doc:`setup`, if you have set a TOTP secret on your
user account, then will need to enter the correct TOTP token from your
authenticator app when logging in.
If you do not have a TOTP secret set on your account then the TOTP
authentication will be skipped.

.. _Setting your TOTP secret:

Setting your TOTP secret
------------------------

This module provides a `Setup TOTP Authentication <wizard-res.user.setup_totp>`
wizard which guides you through setting up a TOTP secret and sharing it with
an authenticator app.

The :guilabel:`Update Secret` button in your preferences will run this wizard
when the preferences window is closed.
If available a QR code for the secret will also be displayed, and this allows
the secret to be easily shared with your authenticator app.
