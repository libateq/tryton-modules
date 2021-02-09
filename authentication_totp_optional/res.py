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
    @ModelView.button_action(
        'authentication_totp_optional.wizard_user_setup_totp')
    def setup_totp_secret(cls, users):
        pass

    @ModelView.button_change(methods=['run_totp_setup_wizard_on_login'])
    def update_totp_secret(self):
        self.totp_update_pending = True
        self.run_totp_setup_wizard_on_login([self], save=False)

    @ModelView.button_change('totp_key', 'totp_qrcode', 'totp_secret')
    def clear_totp_secret(self):
        self.totp_key = None
        self.totp_secret = None
        self.totp_qrcode = None

    @classmethod
    def run_totp_setup_wizard_on_login(cls, users, trigger=None, save=True):
        pool = Pool()
        User = pool.get('res.user')
        WizardAction = pool.get('ir.action.wizard')

        wizards = WizardAction.search([
            ('wiz_name', '=', 'res.user.setup_totp')], limit=1)
        if wizards:
            wizard, = wizards
            for user in users:
                user.actions += (wizard.id, )
            if save:
                User.save(users)

    @classmethod
    def _login_totp_optional(cls, login, parameters):
        User = Pool().get('res.user')

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
    totp_qrcode_disabled = fields.Binary(
        "TOTP QR Code Disabled",
        states={
            'invisible': bool(QRCode),
            })

    @classmethod
    def __setup__(cls):
        super().__setup__()
        cls.totp_secret.help = TOTPUser.totp_secret.help
        cls.totp_qrcode.help = TOTPUser.totp_qrcode.help

    @fields.depends('totp_secret', 'user')
    def on_change_with_totp_qrcode(self, name=None):
        if self.totp_secret and self.user:
            self.user.totp_secret = self.totp_secret
            return self.user.on_change_with_totp_qrcode()


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
    def get_wizard_ids(cls):
        WizardAction = Pool().get('ir.action.wizard')
        wizards = WizardAction.search([
            ('wiz_name', 'in', [
                'res.user.setup_totp',
                ])])
        return [w.id for w in wizards]

    def default_start(self, fields=None):
        User = Pool().get('res.user')
        transaction = Transaction()
        return {
            'user': transaction.context.get('active_id', transaction.user),
            'totp_secret': User.generate_totp_secret(),
            }

    def transition_save(self):
        User = Pool().get('res.user')
        user = self.start.user
        User.write([user], {
            'totp_secret': self.start.totp_secret,
            'actions': [('remove', self.get_wizard_ids())],
            })
        return 'done'

    def transition_skip(self):
        User = Pool().get('res.user')
        user = self.start.user
        User.write([user], {
            'actions': [('remove', self.get_wizard_ids())],
            })
        return 'skipped' if not user.totp_secret else 'end'
