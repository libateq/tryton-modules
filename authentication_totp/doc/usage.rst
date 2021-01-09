*****
Usage
*****

Time-based One-Time Passwords (TOTP) are useful as an additional means of
authentication.
This module allows them to be used with Tryton.

.. _Viewing and changing user TOTP settings:

Viewing and changing user TOTP settings
=======================================

Your user TOTP settings can be found under the :guilabel:`TOTP` tab in your
preferences.
You can also view and change TOTP settings for `Users <model-res.user>` in
the normal way.

.. _Using time-based one-time passwords:

Using time-based one-time passwords
===================================

There are plenty of TOTP apps available for both Android and iOS that can be
used with this module.
The TOTP secret needs to be shared between Tryton and your authenticator app.
Apps will often have a way of reading the TOTP secret using a QR code.
This module supports this if you have the right Python packages installed.
More information on this is available in the :doc:`installation` guide.

.. _Updating the TOTP secret:

Updating the TOTP secret
========================

Your TOTP secret is found in the :guilabel:`TOTP` tab in your preferences.
Here the secret can be manually changed if required, or the
:guilabel:`Update Secret` button can be used to create a new random TOTP
secret.
You can then use the QR Code, if available, to re-share the secret with your
authenticator app.
