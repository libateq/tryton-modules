# This file is part of the booking Tryton module.
# Please see the COPYRIGHT and README.rst files at the top level of this
# package for full copyright notices, license terms and support information.
from trytond.exceptions import UserError


class MissingVisitLocationParentError(UserError):
    "Raised when the visit location parent is needed but not configured"
