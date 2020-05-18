# This file is part of the authentication_totp Tryton module.
# Please see the COPYRIGHT and README.rst files at the top level of this
# package for full copyright notices, license terms and support information.
from trytond.model import fields
from trytond.pool import Pool, PoolMeta
from trytond.pyson import Eval
from trytond.transaction import Transaction
from trytond.wizard import StateTransition, Wizard


class Sequence(metaclass=PoolMeta):
    __name__ = 'ir.sequence'

    @staticmethod
    def default_padding():
        return 6


class SequenceStrict(metaclass=PoolMeta):
    __name__ = 'ir.sequence.strict'

    @staticmethod
    def default_padding():
        return 6


class SyncSequenceData(Wizard):
    "Sync Sequence Data"
    __name__ = 'ir.sequence.sync_data'

    start = StateTransition()

    def transition_start(self):
        pool = Pool()
        ModelData = pool.get('ir.model.data')

        sequence_data = ModelData.search([
            ('model', 'in', ['ir.sequence', 'ir.sequence.strict']),
            ('out_of_sync', '=', True)])
        ModelData.sync(sequence_data)

        return 'end'
