******
Design
******

The *Authentication TOTP Module* extends the User concept to allow users to
setup and use :abbr:`TOTP (Time-based One Time Passwords)` secrets and tokens.

.. _model-res.user:

User
====

When this module is active a TOTP secret can be generated, or set, for each
*User*.

The TOTP secret must be shared with an authenticator app which can then
generate TOTP tokens based on the secret and the current time.
If :doc:`Setup <setup>` correctly, when the user attempts to login they are
prompted to enter in the Token generated by the authenticator app.
If the correct token is provided then the user passes this stage of
authentication.

.. seealso::

   The `User <trytond:model-res.user>` concept is introduced by the
   :doc:`Res Module <trytond:modules/res/index>`.

.. _model-res.user.login.totp:

User Login TOTP
===============

The *User Login TOTP* concept is used to check that the TOTP token provided
by the user is valid and has not been used before.
