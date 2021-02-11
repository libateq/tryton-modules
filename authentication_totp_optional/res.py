# This file is part of the authentication_totp_optional Tryton module.
# Please see the COPYRIGHT and README.rst files at the top level of this
# package for full copyright notices, license terms and support information.
from re import split

from trytond.config import config
from trytond.model import ModelView, fields
from trytond.modules.authentication_totp.res import QRCode, User as TOTPUser
from trytond.pool import Pool, PoolMeta
from trytond.pyson import Eval, PYSONEncoder
from trytond.transaction import Transaction
from trytond.wizard import Button, StateTransition, StateView, Wizard

_totp_required = 'totp' in split('[,+]', config.get(
    'session', 'authentications', default='password'))


class User(metaclass=PoolMeta):
    __name__ = 'res.user'

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
        cls._buttons.update({
            'setup_totp_secret': {},
            'clear_totp_secret': {
                'invisible': _totp_required,
                },
            })

    def get_totp_update_pending(self, name=None):
        return False

    @classmethod
    def _get_totp_setup_wizard(cls):
        pool = Pool()
        Action = pool.get('ir.action')
        ModelData = pool.get('ir.model.data')
        data_id = ModelData.get_id(
            'authentication_totp_optional', 'wizard_user_setup_totp')
        return Action.get_action_id(data_id)

    @ModelView.button_change('actions')
    def update_totp_secret(self):
        setup_wizard = self._get_totp_setup_wizard()
        self.actions += (setup_wizard,)
        self.totp_update_pending = True

    @ModelView.button_change()
    def clear_totp_secret(self):
        self.totp_key = None
        self.totp_secret = None
        self.totp_qrcode = None

    @classmethod
    @ModelView.button_action(
        'authentication_totp_optional.wizard_user_setup_totp')
    def setup_totp_secret(cls, users):
        pass

    @classmethod
    def run_totp_setup_wizard_on_login(cls, users, trigger=None):
        setup_wizard = cls._get_totp_setup_wizard()
        if setup_wizard:
            for user in users:
                user.actions += (setup_wizard,)
        cls.save(users)

    @classmethod
    def _login_totp_optional(cls, login, parameters):
        pool = Pool()
        User = pool.get('res.user')

        user_id = cls._get_login(login)[0]
        if not user_id:
            return

        user = User(user_id)
        if user.totp_key:
            return cls._login_totp(login, parameters)
        return user_id

    @classmethod
    def _ModelView__view_look_dom(
            cls, element, type, fields_width=None, _fields_attrs=None):
        result = super()._ModelView__view_look_dom(
            element, type, fields_width, _fields_attrs)
        name = element.get('name')
        if name in {'clear_totp_secret', 'setup_totp_secret'}:
            encoder = PYSONEncoder()
            states = cls._buttons[name]
            element.set('states', encoder.encode(states))
        return result


class UserSetupTOTPStart(ModelView):
    "Setup TOTP Authentication"
    __name__ = 'res.user.setup_totp.start'

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
    totp_qrcode_disabled = fields.Boolean(
        "TOTP QR Code Disabled",
        states={
            'invisible': bool(QRCode),
            })

    @classmethod
    def __setup__(cls):
        super().__setup__()
        cls.totp_secret.help = TOTPUser.totp_secret.help
        cls.totp_qrcode.help = TOTPUser.totp_qrcode.help


class UserSetupTOTPSkipped(ModelView):
    "Setup TOTP Authentication"
    __name__ = 'res.user.setup_totp.skipped'


class UserSetupTOTPDone(ModelView):
    "Setup TOTP Authentication"
    __name__ = 'res.user.setup_totp.done'


class UserSetupTOTP(Wizard):
    "Setup TOTP Authentication"
    __name__ = 'res.user.setup_totp'

    start = StateView(
        'res.user.setup_totp.start',
        'authentication_totp_optional.user_setup_totp_start_view_form', [
            Button("Not Now", 'end', None),
            Button("Skip", 'skip', 'tryton-cancel'),
            Button("OK", 'save', 'tryton-ok', default=True),
            ])
    skip = StateTransition()
    save = StateTransition()
    skipped = StateView(
        'res.user.setup_totp.skipped',
        'authentication_totp_optional.user_setup_totp_skipped_view_form', [
            Button("OK", 'end', 'tryton-ok', default=True),
            ])
    done = StateView(
        'res.user.setup_totp.done',
        'authentication_totp_optional.user_setup_totp_done_view_form', [
            Button("OK", 'end', 'tryton-ok', default=True),
            ])

    @classmethod
    def get_totp_setup_wizards(cls):
        pool = Pool()
        WizardAction = pool.get('ir.action.wizard')
        wizards = WizardAction.search([
            ('wiz_name', 'in', [
                'res.user.setup_totp',
                ])])
        return [w.id for w in wizards]

    def default_start(self, fields=None):
        pool = Pool()
        User = pool.get('res.user')
        transaction = Transaction()
        user = User(transaction.context.get('activate_id', transaction.user))
        result = {
            'user': user.id,
            'totp_secret': user.generate_totp_secret(),
            'totp_qrcode': user.totp_qrcode,
            'totp_qrcode_disabled': not user.totp_qrcode,
            }
        return result

    def transition_save(self):
        pool = Pool()
        User = pool.get('res.user')
        user = self.start.user
        User.write([user], {
            'totp_secret': self.start.totp_secret,
            'actions': [('remove', self.get_totp_setup_wizards())],
            })
        return 'done'

    def transition_skip(self):
        pool = Pool()
        User = pool.get('res.user')
        user = self.start.user
        User.write([user], {
            'actions': [('remove', self.get_totp_setup_wizards())],
            })
        return 'skipped' if not user.totp_secret else 'end'
