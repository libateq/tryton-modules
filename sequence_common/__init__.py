# This file is part of the sequence_common Tryton module.
# Please see the COPYRIGHT and README.rst files at the top level of this
# package for full copyright notices, license terms and support information.
from trytond.pool import Pool

from . import ir


def register():
    Pool.register(
        ir.Sequence,
        ir.SequenceStrict,
        module='sequence_common', type_='model')
    Pool.register(
        ir.SyncSequenceData,
        module='sequence_common', type_='wizard')

