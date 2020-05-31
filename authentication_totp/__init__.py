# This file is part of the authentication_totp Tryton module.
# Please see the COPYRIGHT and README.rst files at the top level of this
# package for full copyright notices, license terms and support information.
from trytond.pool import Pool

from . import res


def register():
    Pool.register(
        res.User,
        res.UserLoginTOTP,
        module='authentication_totp', type_='model')
    Pool.register(
        res.UserCompany,
        module='authentication_totp', type_='model', depends=['company'])
