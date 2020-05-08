# This file is part of the authentication_totp Tryton module.
# Please see the COPYRIGHT and README.rst files at the top level of this
# package for full copyright notices, license terms and support information.
from binascii import Error as BinAsciiError
from io import BytesIO
from math import ceil
from passlib.exc import TokenError, UsedTokenError
from passlib.totp import TOTP
from re import split
try:
    from qrcode import QRCode
    from qrcode.image.pil import PilImage
except ImportError:
    QRCode = None

from trytond.config import config
from trytond.i18n import gettext
from trytond.model import ModelSQL, ModelView, fields
from trytond.pool import Pool, PoolMeta
from trytond.pyson import Eval
from trytond.transaction import Transaction
from trytond.wizard import Button, StateView, StateTransition, Wizard

from .exception import (
    TOTPAccessCodeReuseError, TOTPInvalidSecretError, TOTPKeyTooShortError,
    TOTPKeyTooShortWarning, TOTPLoginException)

_totp_issuer = config.get(
    'authentication_totp', 'issuer', default='{company} Tryton')
_totp_key_length = config.get(
    'authentication_totp', 'key_length', default=160)

_totp_required = 'totp' in split('[,+]', config.get(
    'session', 'authentications', default='password'))

_TOTPFactory = TOTP.using(secrets_path=config.get(
    'authentication_totp', 'application_secrets_file', default=None))


# Buttons on models the user cannot write to are made readonly and disabled,
# this hack avoids the button being made readonly in the user preferences.
class _clickable_button_hack(dict):

    def copy(self):
        return self.__class__(self)

    def __setitem__(self, key, value):
        if key == 'readonly':
            return
        return super().__setitem__(key, value)


class User(metaclass=PoolMeta):
    __name__ = 'res.user'

    totp_key = fields.Char("TOTP Key")
    totp_secret = fields.Function(fields.Char(
            "TOTP Secret",
            help="Secret key used for time-based one-time password (TOTP) "
            "user authentication."),
        'on_change_with_totp_secret', setter='set_totp_secret')
    totp_qrcode = fields.Function(fields.Binary(
            "TOTP QR Code",
            states={
                'invisible': ~Eval('totp_secret', '') or (not QRCode),
                },
            depends=['totp_secret'],
            help="The QR code for the secret key. Used with authenticator "
            "apps."),
        'on_change_with_totp_qrcode')
    totp_url = fields.Function(fields.Char(
            "TOTP URL",
            states={
                'invisible': ~Eval('totp_secret', ''),
                },
            depends=['totp_secret'],
            help="The URL that contains the secret key and which gets encoded "
            "into a QR Code."),
        'on_change_with_totp_url')
    totp_update_pending = fields.Function(
        fields.Boolean(
            "TOTP Update Pending",
            states={
                'invisible': ~Eval('totp_update_pending'),
                },
            depends=['totp_update_pending']),
        'get_totp_update_pending')

    @classmethod
    def __setup__(cls):
        super().__setup__()
        cls._preferences_fields.extend([
            'totp_secret',
            ])
        cls._buttons.update({
            'totp_update_secret': {},
            'totp_update_secret_preferences': _clickable_button_hack(),
            'totp_clear_secret': _clickable_button_hack({
                'invisible': _totp_required,
                }),
            })

    @fields.depends('totp_key')
    def on_change_with_totp_secret(self, name=None):
        if self.totp_key:
            totp = _TOTPFactory.from_json(self.totp_key)
            return totp.pretty_key()

    @classmethod
    def _is_admin(cls):
        ModelAccess = Pool().get('ir.model.access')
        return ModelAccess.check(
            'res.user', mode='write', raise_exception=False)

    @classmethod
    def _key_length_too_short(cls, key):
        if key:
            totp = _TOTPFactory.from_json(key)
            key_length = len(totp.key) * 8
            return key_length < _totp_key_length

    @classmethod
    def set_totp_secret(cls, users, name, value):
        Warning = Pool().get('res.user.warning')

        if value:
            try:
                key = _TOTPFactory(key=value).to_json()
            except BinAsciiError:
                raise TOTPInvalidSecretError(gettext(
                    'authentication_totp.msg_user_invalid_totp_secret',
                    login=users[0].login))
        else:
            key = None

        if cls._is_admin() and cls._key_length_too_short(key):
            warning_name = 'authentication_totp.key_too_short'
            if Warning.check(warning_name):
                raise TOTPKeyTooShortWarning(warning_name, gettext(
                    'authentication_totp.msg_user_totp_too_short',
                    login=users[0].login))

        cls.write(list(users), {
            'totp_key': key,
            })

    def _get_totp_issuer_fields(self):
        return {
            'company': "",
            }

    @fields.depends(
        'login', 'totp_secret', methods=['_get_totp_issuer_fields'])
    def on_change_with_totp_url(self, name=None):
        if not self.totp_secret:
            return
        issuer = _totp_issuer.format(**self._get_totp_issuer_fields())
        issuer = issuer.strip()
        totp = _TOTPFactory(key=self.totp_secret)
        return totp.to_uri(label=self.login, issuer=issuer)

    @fields.depends('totp_secret', 'totp_url')
    def on_change_with_totp_qrcode(self, name=None):
        url = self.on_change_with_totp_url()
        if not url or not QRCode:
            return

        data = BytesIO()
        qr = QRCode(image_factory=PilImage)
        qr.add_data(url)
        image = qr.make_image()
        image.save(data)
        return data.getvalue()

    def get_totp_update_pending(self, name=None):
        return False

    @classmethod
    @ModelView.button_action('authentication_totp.wizard_user_setup_totp')
    def totp_update_secret(cls, users):
        pass

    @ModelView.button_change('actions', 'totp_update_pending')
    def totp_update_secret_preferences(self):
        self.totp_update_pending = True
        self.add_totp_setup_wizard_to_actions([self], save=False)

    @ModelView.button_change('totp_key', 'totp_qrcode', 'totp_secret')
    def totp_clear_secret(self):
        self.totp_key = None
        self.totp_secret = None
        self.totp_qrcode = None

    @classmethod
    def add_totp_setup_wizard_to_actions(cls, users, trigger=None, save=True):
        pool = Pool()
        User = pool.get('res.user')
        WizardAction = pool.get('ir.action.wizard')

        wizards = WizardAction.search([
            ('wiz_name', '=', 'res.user.setup_totp.display')], limit=1)
        if wizards:
            wizard, = wizards
            for user in users:
                user.actions += (wizard.id, )
            if save:
                User.save(users)

    @classmethod
    def validate(cls, users):
        admin = cls._is_admin()
        for user in users:
            if not admin and cls._key_length_too_short(user.totp_key):
                raise TOTPKeyTooShortError(gettext(
                    'authentication_totp.msg_user_totp_too_short',
                    login=user.login))

    @classmethod
    def _login_totp(cls, login, parameters):
        TOTPLogin = Pool().get('res.user.login.totp')

        user_id = cls._get_login(login)[0]
        if not user_id:
            return

        if TOTPLogin.parameter not in parameters:
            raise TOTPLoginException(TOTPLogin.parameter, login)

        access_code = parameters[TOTPLogin.parameter]
        totp_login = TOTPLogin.get(user_id)
        if totp_login.check(access_code):
            return user_id

    @classmethod
    def _login_totp_optional(cls, login, parameters):
        User = Pool().get('res.user')

        user_id = cls._get_login(login)[0]
        if not user_id:
            return

        user = User(user_id)
        if user.totp_key:
            return cls._login_totp(login, parameters)
        return user_id

    @classmethod
    def _login_password_totp(cls, login, parameters):
        user_ids = {cls._login_password(login, parameters)}
        if all(user_ids):
            user_ids.add(cls._login_totp(login, parameters))
            if len(user_ids) == 1:
                return user_ids.pop()

    @classmethod
    def _login_password_totp_optional(cls, login, parameters):
        user_ids = {cls._login_password(login, parameters)}
        if all(user_ids):
            user_ids.add(cls._login_totp_optional(login, parameters))
            if len(user_ids) == 1:
                return user_ids.pop()


class UserCompany(metaclass=PoolMeta):
    __name__ = 'res.user'

    @fields.depends('main_company')
    def _get_totp_issuer_fields(self):
        company = self.main_company.rec_name if self.main_company else ""
        return {
            'company': company,
            }


class UserLoginTOTP(ModelSQL):
    "User Login TOTP"
    __name__ = 'res.user.login.totp'

    user_id = fields.Integer("User ID")
    user = fields.Function(fields.Many2One('res.user', "User"), 'get_user')
    last_counter = fields.Integer("Last Counter")

    parameter = 'totp_code'

    def get_user(self, name):
        return self.user_id

    @classmethod
    def get(cls, user_id):
        records = cls.search([
            ('user_id', '=', user_id),
            ])
        if records:
            record = records.pop()
            if records:
                cls.delete(records)
            return record
        else:
            record = cls(user_id=user_id)
            record.save()
            return record

    def check(self, code, _time=None):
        if not self.user.totp_key:
            return

        try:
            counter, _ = _TOTPFactory.verify(
                code, self.user.totp_key, time=_time,
                last_counter=self.last_counter)
        except UsedTokenError:
            # Warn the user the token has already been used
            raise TOTPAccessCodeReuseError(self.parameter, self.user.login)
        except TokenError:
            return

        self.last_counter = counter
        self.save()

        return True


class UserSetupTOTP(Wizard):
    "Setup Two-Factor Authentication"
    __name__ = 'res.user.setup_totp'

    save = StateTransition()

    start_state = 'save'

    @classmethod
    def get_wizard_ids(cls):
        WizardAction = Pool().get('ir.action.wizard')
        wizards = WizardAction.search([
            ('wiz_name', 'in', [
                'res.user.setup_totp',
                'res.user.setup_totp.display',
                ])])
        return [w.id for w in wizards]

    def get_user(self):
        User = Pool().get('res.user')
        transaction = Transaction()
        return User(transaction.context.get('active_id', transaction.user))

    def get_totp_secret(self):
        size = ceil(_totp_key_length / 8)
        return _TOTPFactory.new(size=size).pretty_key()

    def transition_save(self):
        User = Pool().get('res.user')
        User.write([self.get_user()], {
            'totp_secret': self.get_totp_secret(),
            'actions': [('remove', self.get_wizard_ids())],
            })
        return 'end'


class UserSetupTOTPShow(ModelView):
    "Setup Two-Factor Authentication"
    __name__ = 'res.user.setup_totp.show'

    user = fields.Many2One(
        'res.user', "User",
        states={
            'invisible': True,
            })
    totp_secret = fields.Char("TOTP Secret")
    totp_qrcode = fields.Binary(
        "TOTP QR Code",
        states={
            'invisible': not QRCode,
            })
    totp_qrcode_disabled = fields.Binary(
        "TOTP QR Code Disabled",
        states={
            'invisible': bool(QRCode),
            })

    @classmethod
    def __setup__(cls):
        super().__setup__()
        cls.totp_secret.help = User.totp_secret.help
        cls.totp_qrcode.help = User.totp_qrcode.help

    @fields.depends('totp_secret', 'user')
    def on_change_with_totp_qrcode(self, name=None):
        if self.totp_secret and self.user:
            self.user.totp_secret = self.totp_secret
            return self.user.on_change_with_totp_qrcode()


class UserSetupTOTPSkipped(ModelView):
    "Setup Two-Factor Authentication"
    __name__ = 'res.user.setup_totp.skipped'


class UserSetupTOTPDone(ModelView):
    "Setup Two-Factor Authentication"
    __name__ = 'res.user.setup_totp.done'


class UserSetupTOTPDisplay(UserSetupTOTP):
    "Setup Two-Factor Authentication"
    __name__ = 'res.user.setup_totp.display'

    show = StateView(
        'res.user.setup_totp.show',
        'authentication_totp.user_setup_totp_show_view_form', [
            Button("Not Now", 'end', None),
            Button("Skip", 'skip', 'tryton-cancel'),
            Button("OK", 'save', 'tryton-ok', default=True),
            ])
    skip = StateTransition()
    skipped = StateView(
        'res.user.setup_totp.skipped',
        'authentication_totp.user_setup_totp_skipped_view_form', [
            Button("OK", 'end', 'tryton-ok', default=True),
            ])
    done = StateView(
        'res.user.setup_totp.done',
        'authentication_totp.user_setup_totp_done_view_form', [
            Button("OK", 'end', 'tryton-ok', default=True),
            ])

    start_state = 'show'

    def get_user(self):
        try:
            return self.show.user
        except AttributeError:
            return super().get_user()

    def get_totp_secret(self):
        try:
            return self.show.totp_secret
        except AttributeError:
            return super().get_totp_secret()

    def default_show(self, fields=None):
        return {
            'user': self.get_user().id,
            'totp_secret': self.get_totp_secret(),
            }

    def transition_save(self):
        super().transition_save()
        return 'done'

    def transition_skip(self):
        User = Pool().get('res.user')
        user = self.get_user()
        User.write([user], {
            'actions': [('remove', self.get_wizard_ids())],
            })
        return 'skipped' if not user.totp_secret else 'end'
