# This file is part of the authentication_totp Tryton module.
# Please see the COPYRIGHT and README.rst files at the top level of this
# package for full copyright notices, license terms and support information.
import os
from binascii import Error as BinAsciiError
from datetime import date
from io import BytesIO
from math import ceil

from passlib.exc import TokenError, UsedTokenError
from passlib.totp import TOTP, generate_secret
from sql import Null
from sql.aggregate import Max

try:
    from qrcode import QRCode
    from qrcode.image.pil import PilImage
except ImportError:
    QRCode = None

from trytond.config import config
from trytond.i18n import gettext
from trytond.model import ModelSQL, ModelView, fields
from trytond.model.exceptions import AccessError
from trytond.pool import Pool, PoolMeta
from trytond.pyson import Eval
from trytond.transaction import Transaction
from trytond.wizard import Button, StateTransition, StateView, Wizard

from .exception import (
    TOTPAccessCodeReuseError, TOTPInvalidSecretError, TOTPKeyTooShortError,
    TOTPLoginException, TOTPTokenIncorrect)


def get_application_secrets_file():
    secrets_file = os.path.join(
        config.get(
            'authentication_totp', 'application_secrets_dir',
            default=config.get('database', 'path')),
        config.get(
            'authentication_totp', 'application_secrets_file',
            default='application.secrets'))
    if not os.path.exists(secrets_file):
        flags = os.O_WRONLY | os.O_CREAT
        with open(os.open(secrets_file, flags, mode=0o600), 'w') as file:
            file.write('{}: {}\n'.format(date.today(), generate_secret()))
    return secrets_file


_algorithm = config.get('authentication_totp', 'algorithm', default='sha1')
_application_secrets_file = get_application_secrets_file()
_digits = config.getint('authentication_totp', 'digits', default=6)
_issuer = config.get(
    'authentication_totp', 'issuer', default='{company} Tryton')
_key_length = config.get('authentication_totp', 'key_length', default=160)
_period = config.getint('authentication_totp', 'period', default=30)
_window = config.getint('authentication_totp', 'window', default=_period)
_skew = config.getint('authentication_totp', 'skew', default=0)


def get_totp(source=None, **kwargs):
    totp = TOTP.using(
        secrets_path=_application_secrets_file, digits=_digits,
        alg=_algorithm, period=_period)
    if source:
        return totp.from_source(source=source)
    else:
        kwargs.setdefault('size', ceil(_key_length / 8))
        return totp(**kwargs)


class QRCodeMixin:
    __slots__ = ()

    totp_qrcode = fields.Function(
        fields.Binary(
            "TOTP QR Code",
            states={
                'invisible': ~Eval('totp_secret', '') | (not QRCode),
                },
            depends=['totp_secret'],
            help="The QR code that contains the details of the TOTP secret."),
        'on_change_with_totp_qrcode')
    totp_url = fields.Function(
        fields.Char(
            "TOTP URL",
            states={
                'invisible': ~Eval('totp_secret', ''),
                },
            depends=['totp_secret'],
            help="The URL that contains the details of the TOTP secret."),
        'on_change_with_totp_url')

    @fields.depends('login')
    def _get_totp_url_fields(self):
        return {
            'label': self.login,
            'company': "",
            }

    @fields.depends('totp_secret', methods=['_get_totp_url_fields'])
    def on_change_with_totp_url(self, name=None):
        if not self.totp_secret:
            return

        url_fields = self._get_totp_url_fields()
        issuer = _issuer.format(**url_fields).strip()
        try:
            totp = get_totp(key=self.totp_secret)
        except BinAsciiError:
            return
        return totp.to_uri(label=url_fields['label'], issuer=issuer)

    @fields.depends('totp_secret', methods=['on_change_with_totp_url'])
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


class User(QRCodeMixin, metaclass=PoolMeta):
    __name__ = 'res.user'

    totp_key = fields.Char("TOTP Key")
    totp_secret = fields.Function(fields.Char(
            "TOTP Secret",
            help="Secret key used for time-based one-time password (TOTP) "
            "user authentication."),
        'get_totp_secret', setter='set_totp_secret')

    @classmethod
    def __setup__(cls):
        super().__setup__()
        cls._preferences_fields.extend([
            'totp_secret',
            ])
        cls._buttons.update({
            'update_totp_secret': {},
            })

    def get_totp_secret(self, name):
        if self.totp_key:
            return get_totp(source=self.totp_key).pretty_key()

    @classmethod
    def set_totp_secret(cls, users, name, value):
        for user in users:
            if value:
                try:
                    user.totp_key = get_totp(key=value).to_json()
                except BinAsciiError:
                    raise TOTPInvalidSecretError(gettext(
                        'authentication_totp.msg_user_invalid_totp_secret',
                        login=user.login))
            else:
                user.totp_key = None
        cls.save(users)

    @classmethod
    def generate_totp_secret(cls):
        return get_totp(new=True).pretty_key()

    @classmethod
    @ModelView.button_action('authentication_totp.update_totp_secret_wizard')
    def update_totp_secret(cls, users):
        pass

    @classmethod
    def read(cls, ids, fields_names):
        result = super().read(ids, fields_names)
        user_id = Transaction().user
        if user_id == 0:
            return result

        clean_fields = ['totp_key', 'totp_secret', 'totp_qrcode', 'totp_url']
        if fields_names:
            clean_fields = list(set(clean_fields) & set(fields_names))
        if clean_fields:
            for id, values in zip(ids, result):
                if id != user_id:
                    for field in clean_fields:
                        values[field] = None
        return result

    @classmethod
    def validate_fields(cls, users, field_names):
        super().validate_fields(users, field_names)
        cls.check_totp_key_length(users, field_names=field_names)

    @classmethod
    def check_totp_key_length(cls, users, field_names=None):
        if field_names and 'totp_key' not in field_names:
            return

        # Rebrowse as root so totp_key is available
        with Transaction().set_user(0):
            users = cls.browse([u.id for u in users])

        min_key_length = _key_length / 8
        for user in users:
            if not user.totp_key:
                continue

            totp = get_totp(source=user.totp_key)
            if len(totp.key) < min_key_length:
                raise TOTPKeyTooShortError(gettext(
                    'authentication_totp.msg_user_totp_too_short',
                    login=user.login))

    @classmethod
    def _login_totp(cls, login, parameters):
        pool = Pool()
        TOTPLogin = pool.get('res.user.login.totp')

        if 'totp_code' not in parameters:
            raise TOTPLoginException('totp_code', login)

        user_id = cls._get_login(login)[0]
        access_code = parameters['totp_code']
        if TOTPLogin.check(user_id, access_code):
            return user_id


class UserCompany(metaclass=PoolMeta):
    __name__ = 'res.user'

    @fields.depends('company')
    def _get_totp_url_fields(self):
        result = super()._get_totp_url_fields()
        if self.company:
            result['company'] = self.company.rec_name
        return result


class UserLoginTOTP(ModelSQL):
    "User Login TOTP"
    __name__ = 'res.user.login.totp'

    user_id = fields.Integer("User ID", required=True)
    counter = fields.Integer("Counter", required=True)

    @classmethod
    def __register__(cls, module_name):
        cursor = Transaction().connection.cursor()
        table = cls.__table_handler__(module_name)
        sql_table = cls.__table__()

        # Migration from 6.2: rename last_counter to counter
        if table.column_exist('last_counter'):
            cursor.execute(*sql_table.delete(
                where=(
                    (sql_table.user_id == Null)
                    | (sql_table.last_counter == Null))))
            table.column_rename('last_counter', 'counter')

        super().__register__(module_name)

    @classmethod
    def get_last_counter(cls, user):
        cursor = Transaction().connection.cursor()
        table = cls.__table__()
        cursor.execute(*table.select(
            Max(table.counter),
            where=table.user_id == user.id))
        record = cursor.fetchone()
        if record:
            return record[0]

    @classmethod
    def mark_counter_used(cls, user, counter):
        record = cls()
        record.user_id = user.id
        record.counter = counter
        record.save()

    @classmethod
    def clean_old_counters(cls, user, counter):
        records = cls.search([
            ('user_id', '=', user.id),
            ('counter', '<', counter),
            ])
        cls.delete(records)

    @classmethod
    def check(cls, user_id, code, _time=None):
        pool = Pool()
        User = pool.get('res.user')

        # Use root to allow access to the totp_key
        with Transaction().set_user(0):
            user = User(user_id)
        if not user.totp_key:
            return

        last_counter = cls.get_last_counter(user)
        try:
            counter, _ = get_totp(source=user.totp_key).match(
                code, time=_time, window=_window, skew=_skew,
                last_counter=last_counter)
        except UsedTokenError:
            # Warn the user the token has already been used
            raise TOTPAccessCodeReuseError('totp_code', user.login)
        except TokenError:
            return

        cls.mark_counter_used(user, counter)
        cls.clean_old_counters(user, counter)

        return True


class UpdateSecretStart(QRCodeMixin, ModelView):
    "Update Secret"
    __name__ = 'res.user.update_totp_secret.start'

    user = fields.Many2One('res.user', "User", readonly=True)
    login = fields.Function(
        fields.Char("Login"),
        'on_change_with_login')
    totp_secret = fields.Char(
        "TOTP Secret", required=True,
        help="Secret key used for time-based one-time password (TOTP) "
        "user authentication.")
    totp_token = fields.Char("TOTP Token", required=True)

    @fields.depends('user')
    def on_change_with_login(self, name=None):
        if self.user:
            return self.user.login

    @fields.depends('user')
    def _get_totp_url_fields(self):
        result = super()._get_totp_url_fields()
        if getattr(self.user, 'company', None):
            result['company'] = self.user.company.rec_name
        return result


class UpdateSecret(Wizard):
    "Update Secret"
    __name__ = 'res.user.update_totp_secret'

    start = StateView(
        'res.user.update_totp_secret.start',
        'authentication_totp.update_totp_secret_view_form', [
            Button("Cancel", 'end', 'tryton-cancel'),
            Button("Update", 'update', 'tryton-ok', default=True),
            ])
    update = StateTransition()

    def default_start(self, fields):
        result = {
            'user': self.record.id,
            'totp_secret': self.record.generate_totp_secret(),
            }
        return result

    def transition_update(self):
        self.check_user_access()
        try:
            counter, _ = get_totp(key=self.start.totp_secret).match(
                self.start.totp_token, window=_window, skew=_skew)
        except BinAsciiError:
            raise TOTPInvalidSecretError(gettext(
                'authentication_totp.msg_user_invalid_totp_secret',
                login=self.start.login))
        except TokenError:
            raise TOTPTokenIncorrect(gettext(
                'authentication_totp.msg_incorrect_token'))

        self.record.totp_secret = self.start.totp_secret
        self.record.save()

        return 'end'

    def end(self):
        return 'reload'

    def _execute(self, state_name):
        self.check_user_access()
        return super()._execute(state_name)

    def check_user_access(self):
        pool = Pool()
        Group = pool.get('res.group')
        ModelData = pool.get('ir.model.data')
        User = pool.get('res.user')

        super().check_access()

        user = User(Transaction().user)
        admin_group = Group(ModelData.get_id('res', 'group_admin'))
        if self.record != user and admin_group not in user.groups:
            raise AccessError(gettext(
                'ir.msg_access_wizard_error',
                name=self.__class__.__name__))
