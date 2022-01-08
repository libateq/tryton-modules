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
    >>> user = User()
    >>> user.login = 'totp_user'
    >>> user.totp_secret = TOTP_SECRET_KEY
    >>> user.company = None
    >>> user.save()

The user's TOTP secret can be changed::

    >>> user.totp_secret = None
    >>> user.save()
    >>> user.totp_secret is None
    True

    >>> user.totp_secret = TOTP_SECRET_KEY
    >>> user.save()
    >>> user.totp_secret == TOTP_SECRET_KEY
    True

It cannot be set to an invalid value::

    >>> user.totp_secret = 'an_invalid_key'  # doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
       ...
    binascii.Error: ...

    >>> user.totp_secret = TOTP_SECRET_KEY[:19]
    >>> user.save()  # doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
       ...
    TOTPKeyTooShortError: ...

    >>> user.reload()

The secret key can be encoded in a url::

    >>> user.totp_url
    'otpauth://totp/Tryton:totp_user?secret=GE3DAYRAKRHVIUBAKNSWG4TFOQQEWZLZ&issuer=Tryton'

This is used in QR codes for importing into the authenticator app::

    >>> if QRCode:
    ...     bool(len(user.totp_qrcode))
    ... else:
    ...     bool('QRCode not available: skip test')
    True

If the user has a company then it is included in the totp_url::

    >>> user.company = company
    >>> user.save()

    >>> user.totp_url
    'otpauth://totp/Dunder%20Mifflin%20Tryton:totp_user?secret=GE3DAYRAKRHVIUBAKNSWG4TFOQQEWZLZ&issuer=Dunder%20Mifflin%20Tryton'

The user can generate a new random TOTP secret::

    >>> set_user(user)
    >>> new = User.update_totp_secret([user], config.context)[0]
    >>> new['totp_secret'] != user.totp_secret
    True

And save it from their preferences::

    >>> User.set_preferences(
    ...     {'totp_secret': new['totp_secret']}, config.context)
    >>> user.reload()
    >>> user.totp_secret != TOTP_SECRET_KEY
    True
