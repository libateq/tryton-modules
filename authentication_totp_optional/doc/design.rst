******
Design
******

.. _model-res.user:

User
====

The *Authentication TOTP Optional Module* extends the *User* concept to allow
users who do not have a :abbr:`TOTP (Time-based One Time Passwords)` secret to
login without needing to enter in an authentication token.

.. seealso::

   The `User <trytond:model-res.user>` concept is introduced by the
   :doc:`Res Module <trytond:modules/res/index>`.

   The TOTP authentication method is introduced by the
   :doc:`Authentication TOTP Module <authentication_totp:index>`.

Wizards
-------

.. _wizard-res.user.setup_totp:

Setup TOTP Authentication
^^^^^^^^^^^^^^^^^^^^^^^^^

The *Setup TOTP Authentication* wizard guides a user through the steps required
to enable TOTP authentication on their user account.
It will generate a TOTP secret, and with the right Python packages
:doc:`installed <installation>` it can be used to share it with an
authenticator app via a :abbr:`QR (Quick Response)` code.
