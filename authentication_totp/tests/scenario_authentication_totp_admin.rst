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

    >>> config = activate_modules(['authentication_totp', 'company'])

Create a company::

    >>> _ = create_company()
    >>> company = get_company()

Create a user with a TOTP secret::

    >>> User = Model.get('res.user')
    >>> admin, = User.find([('login', '=', 'admin')])

    >>> user = User()
    >>> user.login = 'totp_user'
    >>> user.totp_secret = TOTP_SECRET_KEY
    >>> user.save()

    >>> set_user(user)
    >>> user.totp_secret == TOTP_SECRET_KEY
    True
    >>> set_user(admin)
    >>> user.reload()

The admin user cannot see other user's TOTP details::

    >>> user.totp_key
    >>> user.totp_secret
    >>> user.totp_qrcode
    >>> user.totp_url

The admin user can set TOTP secrets::

    >>> user.totp_secret = None
    >>> user.save()
    >>> set_user(user)
    >>> user.totp_secret is None
    True
    >>> set_user(admin)

    >>> user.totp_secret = TOTP_SECRET_KEY
    >>> user.save()
    >>> set_user(user)
    >>> user.totp_secret == TOTP_SECRET_KEY
    True
    >>> set_user(admin)
    >>> user.reload()

Unless it is to an invalid value::

    >>> user.totp_secret = 'an_invalid_key'
    >>> user.save()  # doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
       ...
    TOTPInvalidSecretError: ...

    >>> user.totp_secret = TOTP_SECRET_KEY[:19]
    >>> user.save()  # doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
       ...
    TOTPKeyTooShortError: ...
