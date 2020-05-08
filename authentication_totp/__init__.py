# This file is part of the authentication_totp Tryton module.
# Please see the COPYRIGHT and README.rst files at the top level of this
# package for full copyright notices, license terms and support information.
from trytond.pool import Pool

from . import ir
from . import res


def register():
    Pool.register(
        ir.Trigger,
        res.User,
        res.UserLoginTOTP,
        res.UserSetupTOTPDone,
        res.UserSetupTOTPShow,
        res.UserSetupTOTPSkipped,
        module='authentication_totp', type_='model')
    Pool.register(
        res.UserCompany,
        module='authentication_totp', type_='model', depends=['company'])
    Pool.register(
        res.UserSetupTOTP,
        res.UserSetupTOTPDisplay,
        module='authentication_totp', type_='wizard')
