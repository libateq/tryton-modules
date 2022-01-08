============================
TOTP Authentication Scenario
============================

Imports::

    >>> from proteus import Model, Wizard
    >>> from trytond.modules.authentication_totp.res import QRCode
    >>> from trytond.modules.company.tests.tools import (
    ...     create_company, get_company)
    >>> from trytond.tests.tools import activate_modules, set_user

Constants::

    >>> TOTP_SECRET_KEY = 'GE3D-AYRA-KRHV-IUBA-KNSW-G4TF-OQQE-WZLZ'

Activate modules::

    >>> config = activate_modules(['authentication_totp'])

Create a user with a TOTP secret::

    >>> User = Model.get('res.user')
    >>> user = User()
    >>> user.login = 'totp_user'
    >>> user.totp_secret = TOTP_SECRET_KEY
    >>> user.save()
    >>> set_user(user)

The user can generate a new random TOTP secret::

    >>> new = User.update_totp_secret([user], config.context)[0]
    >>> new['totp_secret'] != user.totp_secret
    True

And save it from their preferences::

    >>> User.set_preferences(
    ...     {'totp_secret': new['totp_secret']}, config.context)
    >>> user.reload()
    >>> user.totp_secret != TOTP_SECRET_KEY
    True
