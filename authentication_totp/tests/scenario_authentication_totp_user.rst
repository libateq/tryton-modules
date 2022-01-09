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

Create some users with TOTP secrets::

    >>> User = Model.get('res.user')
    >>> admin, = User.find([('login', '=', 'admin')])

    >>> user = User()
    >>> user.login = 'totp_user'
    >>> user.totp_secret = TOTP_SECRET_KEY
    >>> user.save()

    >>> user_other = User()
    >>> user_other.login = 'totp_user_other'
    >>> user_other.totp_secret = TOTP_SECRET_KEY
    >>> user_other.save()

The user can see their own TOTP details::

    >>> set_user(user)
    >>> user.totp_secret == TOTP_SECRET_KEY
    True
    >>> user.totp_url
    'otpauth://totp/Tryton:totp_user?secret=GE3DAYRAKRHVIUBAKNSWG4TFOQQEWZLZ&issuer=Tryton'
    >>> if QRCode:
    ...     bool(len(user.totp_qrcode))
    ... else:
    ...     bool("QRCode not available: Test skipped")
    True

But cannot see another user's TOTP details::

    >>> user_other.totp_key
    >>> user_other.totp_secret
    >>> user_other.totp_qrcode
    >>> user_other.totp_url

Create a company::

    >>> set_user(admin)
    >>> _ = create_company()
    >>> company = get_company()
    >>> user.company = company
    >>> user.save()

TOTP urls include the company, if the user has one::

    >>> set_user(user)
    >>> user.totp_url
    'otpauth://totp/Dunder%20Mifflin%20Tryton:totp_user?secret=GE3DAYRAKRHVIUBAKNSWG4TFOQQEWZLZ&issuer=Dunder%20Mifflin%20Tryton'

A user can generate a new random TOTP secret::

    >>> new = User.update_totp_secret([user], config.context)[0]
    >>> new['totp_secret'] != user.totp_secret
    True

And save a new TOTP secret in their preferences::

    >>> User.set_preferences(
    ...     {'totp_secret': new['totp_secret']}, config.context)
    >>> user.reload()
    >>> user.totp_secret != TOTP_SECRET_KEY
    True

But not to an invalid value::

    >>> User.set_preferences(
    ...     {'totp_secret': 'an_invalid_key'}, config.context)  # doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
       ...
    TOTPInvalidSecretError: ...

    >>> User.set_preferences(
    ...     {'totp_secret': 'an_invalid_key'}, config.context)  # doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
       ...
    TOTPInvalidSecretError: ...
