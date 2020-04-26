# This file is part of the authentication_totp Tryton module.
# Please see the COPYRIGHT and README.rst files at the top level of this
# package for full copyright notices, license terms and support information.
from binascii import Error as BinAsciiError
from io import BytesIO
from math import ceil
from passlib.exc import TokenError, UsedTokenError  # noqa: F401
from passlib.totp import TOTP as PassLibTOTP

from trytond.config import config

try:
    from qrcode import QRCode
    from qrcode.image.pil import PilImage
except ImportError:
    QRCode = None


class TOTP:
    "Time-based One-Time Passwords"

    def __init__(self, *args, **kwargs):
        self.TOTPFactory = PassLibTOTP.using(*args, **kwargs)

    def new_secret(self, length):
        size = ceil(length / 8)
        return self.TOTPFactory.new(size=size).pretty_key()

    def secret_from_key(self, key):
        totp = self.TOTPFactory.from_json(key)
        return totp.pretty_key()

    def key_from_secret(self, secret):
        if secret:
            try:
                totp = self.TOTPFactory(key=secret)
            except BinAsciiError as error:
                raise ValueError from error
            return totp.to_json()

    def length(self, key):
        if key:
            totp = self.TOTPFactory.from_json(key)
            return len(totp.key) * 8
        return 0

    def generate_uri(self, secret, login, issuer):
        if secret:
            totp = self.TOTPFactory(key=secret)
            return totp.to_uri(label=login, issuer=issuer)

    @staticmethod
    def qrcode_available():
        return bool(QRCode)

    def generate_qrcode(self, secret, login, issuer):
        if not secret or not QRCode:
            return
        data = BytesIO()
        qr = QRCode(image_factory=PilImage)
        qr.add_data(self.generate_uri(secret, login, issuer))
        image = qr.make_image()
        image.save(data)
        return data.getvalue()

    def verify(self, *args, **kwargs):
        return self.TOTPFactory.verify(*args, **kwargs)


totp = TOTP(secrets_path=config.get(
    'authentication_totp', 'application_secrets_file', default=None))
