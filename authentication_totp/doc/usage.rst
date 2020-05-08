General Usage
=============

Time-based One-Time Passwords (TOTP) are useful as an additional means of
authentication.  This module allows them to be used with Tryton.

Once activated and :doc:`setup` the main TOTP settings can be found under the
*Authentications* tab in your preferences.  Administrators can view and change
users TOTP settings from the `Administration > Users > Users
<https://demo.tryton.org/model/res.user;name="Users">`_ menu.


Using Time-based One-Time Passwords
-----------------------------------

There are plenty of TOTP apps available for both Android and iOS that can be
used with this module.  The TOTP secret needs to be shared between Tryton and
your authenticator app.  In the app it is normally easiest to read the secret
from a QR code.  This module supports this if the right python packages are
installed.  More information on this is available in the :doc:`installation`
guide.


Setting the TOTP Secret
-----------------------

Your TOTP secret is found in the *Authentications* tab in your preferences.
Here the secret can be manually changed if required, or the *Update Secret*
button can be used to run the *Setup Time-based One-Time Password
Authentication* wizard when the preferences window is closed.
If available the QR code for the secret can also be displayed, and this allows
the secret to be easily re-entered into your authenticator app.


Prompting Users to Setup TOTP
-----------------------------

You can prompt users to setup TOTP by adding the *Setup Time-based One-Time
Password Authentication* wizard to their login *Actions*.  To help make this
process simpler a trigger is provided that will automatically do this when
a new user is created.  This trigger can easily be deactivated if desired.

With this action in place, the wizard will run when the user logs in.  This
will automatically generate a new secret for the user and will help them add
it to their authenticator app.


Requiring Users to Use TOTP
---------------------------

Administrators can force users to use TOTP with their account by ticking the
*TOTP Required* checkbox.  To force existing users to setup TOTP the *Setup
Required Time-based One-Time Password Authentication* wizard should be added
to their login *Actions*.  This will ensure a TOTP secret is created for these
users the next time that they login.

.. note::

    Make sure users are prepared for this change.  With this setting they will
    not be able to use the system until they have setup TOTP or they may end
    up locking themselves out if they proceed without recording the TOTP
    secret in their authenticator app.
