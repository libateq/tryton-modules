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

