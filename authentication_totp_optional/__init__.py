# This file is part of the authentication_totp_optional Tryton module.
# Please see the COPYRIGHT and README.rst files at the top level of this
# package for full copyright notices, license terms and support information.
from trytond.pool import Pool

from . import ir
from . import res


def register():
    Pool.register(
        ir.Trigger,
        res.User,
        res.UserSetupTOTPStart,
        res.UserSetupTOTPSkipped,
        res.UserSetupTOTPDone,
        module='authentication_totp_optional', type_='model')
    Pool.register(
        res.UserSetupTOTP,
        module='authentication_totp_optional', type_='wizard')
