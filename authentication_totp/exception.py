# This file is part of the authentication_totp Tryton module.
# Please see the COPYRIGHT and README.rst files at the top level of this
# package for full copyright notices, license terms and support information.
from trytond.exceptions import LoginException, UserError
from trytond.i18n import gettext


class TOTPLoginException(LoginException):
    "Request the time-based one-time password for the login process."

    def __init__(self, parameter, login, message_id='msg_user_totp_code'):
        super().__init__(
            parameter,
            gettext('authentication_totp.{}'.format(message_id), login=login),
            type='char')


class TOTPAccessCodeReuseError(TOTPLoginException):
    "Displayed when the access code has recently been used"

    def __init__(self, parameter, login):
        super().__init__(parameter, login, 'msg_user_totp_code_reused')


class TOTPTokenIncorrect(UserError):
    "Raised if the token is wrong when trying to update the totp secret"


class TOTPInvalidSecretError(UserError):
    "Raised when the secret is not of the right form"


class TOTPKeyTooShortError(UserError):
    "Raised when the TOTP secret key is too short"
