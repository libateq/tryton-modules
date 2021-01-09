*****
Setup
*****

.. _Enabling optional TOTP authentication:

Enabling optional TOTP authentication
=====================================

Once the *Authentication TOTP Optional Module* has been activated you can start
using it by including the ``totp_optional`` authentication method in the
`authentications <trytond:config-session.authentications>` setting in the
``session`` section of the
:doc:`configuration file <trytond:topics/configuration>`.

You will also need to make sure you have correctly setup the
:doc:`Authentication TOTP Module <authentication_totp:index>` as well.

.. _Prompting users to setup TOTP:

Prompting users to setup TOTP
=============================

You can prompt users to setup :abbr:`TOTP (Time-based One Time Passwords)` by
adding the `Setup TOTP Authentication <wizard-res.user.setup_totp>` wizard to
their login :guilabel:`Actions`.
This will automatically run the wizard when the user logs in.

To help make this process simpler a `Trigger <trytond:model-ir.trigger>` is
provided that automatically does this when a new user is created.

.. tip::

   The trigger that puts the *Setup TOTP Authentication* wizard in a user's
   login :guilabel:`Actions` can easily be deactivated if desired from the
   [:menuselection:`Administration --> Models --> Triggers`] menu.
