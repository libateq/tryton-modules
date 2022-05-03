# This file is part of the authentication_totp Tryton module.
# Please see the COPYRIGHT and README.rst files at the top level of this
# package for full copyright notices, license terms and support information.
from binascii import Error as BinAsciiError
from io import BytesIO
from math import ceil
from passlib.exc import TokenError, UsedTokenError
from passlib.totp import TOTP
try:
    from qrcode import QRCode
    from qrcode.image.pil import PilImage
except ImportError:
    QRCode = None

from trytond.config import config
from trytond.i18n import gettext
from trytond.model import ModelSQL, ModelView, fields
from trytond.pool import Pool, PoolMeta
from trytond.pyson import Eval, PYSONEncoder
from trytond.transaction import Transaction

from .exception import (
    TOTPAccessCodeReuseError, TOTPInvalidSecretError, TOTPKeyTooShortError,
    TOTPLoginException)

_totp_issuer = config.get(
    'authentication_totp', 'issuer', default='{company} Tryton')
_totp_key_length = config.get(
    'authentication_totp', 'key_length', default=160)


class User(metaclass=PoolMeta):
    __name__ = 'res.user'

    totp_key = fields.Char("TOTP Key")
    totp_secret = fields.Function(fields.Char(
            "TOTP Secret",
            help="Secret key used for time-based one-time password (TOTP) "
            "user authentication."),
        'get_totp_secret', setter='set_totp_secret')
    totp_qrcode = fields.Function(fields.Binary(
            "TOTP QR Code",
            states={
                'invisible': ~Eval('totp_secret', '') | (not QRCode),
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
            return self.totp(source=self.totp_key).pretty_key()

    @classmethod
    def set_totp_secret(cls, users, name, value):
        for user in users:
            if value:
                try:
                    user.totp_key = cls.totp(key=value).to_json()
                except BinAsciiError:
                    raise TOTPInvalidSecretError(gettext(
                        'authentication_totp.msg_user_invalid_totp_secret',
                        login=user.login))
            else:
                user.totp_key = None
        cls.save(users)

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
        totp = self.totp(key=self.totp_secret)
        return totp.to_uri(label=self.login, issuer=issuer)

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

    @classmethod
    def _totp_factory(cls):
        return TOTP.using(
            secrets_path=config.get(
                'authentication_totp', 'application_secrets_file',
                default=None),
            digits=config.getint('authentication_totp', 'digits', default=6),
            alg=config.get('authentication_totp', 'algorithm', default='sha1'),
            period=config.getint('authentication_totp', 'period', default=30),
            )

    @classmethod
    def totp(cls, source=None, **kwargs):
        totp = cls._totp_factory()
        if source:
            return totp.from_source(source=source)
        else:
            kwargs.setdefault('size', ceil(_totp_key_length / 8))
            return totp(**kwargs)

    @classmethod
    def generate_totp_secret(cls):
        return cls.totp(new=True).pretty_key()

    @ModelView.button_change(methods=[
            'on_change_with_totp_qrcode', 'on_change_with_totp_url'])
    def update_totp_secret(self):
        self.totp_secret = self.generate_totp_secret()
        self.totp_url = self.on_change_with_totp_url()
        self.totp_qrcode = self.on_change_with_totp_qrcode()

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
    def validate(cls, users):
        # Use root to ensure the totp_secret is available
        with Transaction().set_user(0):
            for user in cls.browse([u.id for u in users]):
                user.check_totp_key_length()

    def check_totp_key_length(self):
        if self.totp_key:
            totp = self.totp(source=self.totp_key)
            key_length = len(totp.key) * 8
            if key_length < _totp_key_length:
                raise TOTPKeyTooShortError(gettext(
                    'authentication_totp.msg_user_totp_too_short',
                    login=self.login))

    @classmethod
    def _login_totp(cls, login, parameters):
        pool = Pool()
        TOTPLogin = pool.get('res.user.login.totp')

        if 'totp_code' not in parameters:
            raise TOTPLoginException('totp_code', login)

        user_id = cls._get_login(login)[0]
        totp_login = TOTPLogin.get(user_id)
        access_code = parameters['totp_code']
        if totp_login.check(access_code):
            return user_id

    @classmethod
    def _ModelView__view_look_dom(
            cls, element, type, fields_width=None, _fields_attrs=None):
        result = super()._ModelView__view_look_dom(
            element, type, fields_width, _fields_attrs)
        if element.get('name') == 'update_totp_secret':
            encoder = PYSONEncoder()
            states = cls._buttons['update_totp_secret']
            element.set('states', encoder.encode(states))
        return result


class UserCompany(metaclass=PoolMeta):
    __name__ = 'res.user'

    @fields.depends('company')
    def _get_totp_issuer_fields(self):
        company = self.company.rec_name if self.company else ""
        return {
            'company': company,
            }


class UserLoginTOTP(ModelSQL):
    "User Login TOTP"
    __name__ = 'res.user.login.totp'

    user_id = fields.Integer("User ID")
    user = fields.Function(fields.Many2One('res.user', "User"), 'get_user')
    last_counter = fields.Integer("Last Counter")

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
        pool = Pool()
        User = pool.get('res.user')

        # Use root to allow access to the totp_secret
        with Transaction().set_user(0):
            user, = User.browse([self.user_id])
        if not user.totp_key:
            return

        window = config.getint('authentication_totp', 'window', default=30)
        skew = config.getint('authentication_totp', 'skew', default=0)
        try:
            counter, _ = User.totp(source=user.totp_key).match(
                code, time=_time, window=window, skew=skew,
                last_counter=self.last_counter)
        except UsedTokenError:
            # Warn the user the token has already been used
            raise TOTPAccessCodeReuseError('totp_code', user.login)
        except TokenError:
            return

        self.last_counter = counter
        self.save()

        return True
