*****
Setup
*****

.. _Enabling TOTP authentication:

Enabling TOTP authentication
============================

After you have activated the *Authentication TOTP Module* you should then set
the TOTP secret for the admin user.
Once this has been done you can then enable
:abbr:`TOTP (Time-based One Time Passwords)` authentication by adding
the ``totp`` method to the
`authentications <trytond:config-session.authentications>` setting in the
``session`` section of the
:doc:`configuration file <trytond:topics/configuration>`.
