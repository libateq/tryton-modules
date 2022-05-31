============================
TOTP Authentication Scenario
============================

Imports::

    >>> from passlib.totp import TOTP
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

    >>> Group = Model.get('res.group')
    >>> update_secret_group, = Group.find(
    ...     [('name', '=', 'Update TOTP Secret')])

    >>> user = User()
    >>> user.login = 'totp_user'
    >>> user.totp_secret = TOTP_SECRET_KEY
    >>> user.groups.append(Group(update_secret_group.id))
    >>> user.save()

    >>> user_other = User()
    >>> user_other.login = 'totp_user_other'
    >>> user_other.totp_secret = TOTP_SECRET_KEY
    >>> user_other.groups.append(Group(update_secret_group.id))
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

A user can start to update their TOTP secret to a new one::

    >>> update_secret = Wizard('res.user.update_totp_secret', [user])
    >>> update_secret.form.totp_secret != user.totp_secret
    True

But they must enter in the correct token to save the new secret::

    >>> update_secret.form.totp_token = 'INCORRECT TOKEN'
    >>> update_secret.execute('update')  # doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
       ...
    TOTPTokenIncorrect: ...

    >>> token = TOTP(key=update_secret.form.totp_secret).generate().token
    >>> update_secret.form.totp_token = token
    >>> update_secret.execute('update')

A user cannot update other user's TOTP secrets::

    >>> update_secret = Wizard('res.user.update_totp_secret', [user_other])  # doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
       ...
    AccessError: ...

And manually save a new TOTP secret in their preferences::

    >>> User.set_preferences(
    ...     {'totp_secret': TOTP(new=True).pretty_key()}, config.context)
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
