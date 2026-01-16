from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import NumericProperty, ObjectProperty, ListProperty
from db import Database
from steam_wrapper import SteamWrapper
import os

KV_FILE = os.path.join(os.path.dirname(__file__), 'ui.kv')

class MainScreen(Screen):
    pass

class AccountsScreen(Screen):
    page = NumericProperty(0)
    per_page = NumericProperty(4)
    accounts = ListProperty([])

    def on_enter(self):
        self.load()

    def load(self):
        db = Database()
        total = db.count_accounts()
        self.manager.get_screen('main').ids.accounts_count.text = str(total)
        start = self.page * self.per_page
        self.accounts = db.get_accounts_paginated(start, self.per_page)
        # populate grid
        try:
            grid = self.ids.accounts_grid
            grid.clear_widgets()
            from kivy.uix.button import Button
            for a in self.accounts:
                btn = Button(text=f"{a['account_name']}", size_hint_y=None)
                def _open(acc_id, *l):
                    self.manager.get_screen('account').account_id = acc_id
                    self.manager.current = 'account'
                # bind with default arg
                btn.bind(on_release=lambda inst, aid=a['id']: _open(aid))
                grid.add_widget(btn)
        except Exception:
            pass

    def next_page(self):
        db = Database()
        if (self.page + 1) * self.per_page < db.count_accounts():
            self.page += 1
            self.load()

    def prev_page(self):
        if self.page > 0:
            self.page -= 1
            self.load()

class AccountScreen(Screen):
    account_id = NumericProperty(0)

    def on_enter(self):
        self.load()

    def load(self):
        db = Database()
        acc = db.get_account_by_id(self.account_id)
        if acc:
            self.ids.account_name.text = acc['account_name']
            self.ids.account_password.text = acc['password'] or ''
            self.ids.account_shared.text = acc['shared_secret'] or ''
            self._acc = acc

    def delete(self):
        db = Database()
        db.delete_account(self.account_id)
        self.manager.current = 'accounts'

    def edit(self):
        self.manager.get_screen('edit_account').set_account(self._acc)
        self.manager.current = 'edit_account'

    def confirmations(self):
        self.manager.get_screen('confirmations').set_account(self._acc)
        self.manager.current = 'confirmations'

class AddAccountScreen(Screen):
    def on_manual_add(self):
        self.manager.current = 'add_manual'

    def on_create_mafile(self):
        self.manager.current = 'add_manual'

class AddManualScreen(Screen):
    def add_account(self):
        name = self.ids.input_name.text.strip()
        pwd = self.ids.input_password.text.strip()
        shared = self.ids.input_shared.text.strip()
        identity = ''
        if hasattr(self.ids, 'input_identity'):
            identity = self.ids.input_identity.text.strip()
        if not name:
            return
        db = Database()
        acc_id = db.add_account(name, pwd, shared, identity_secret=identity)
        # create mafile and save path
        wrapper = SteamWrapper()
        try:
            path = wrapper.create_mafile({'id': acc_id, 'account_name': name, 'password': pwd, 'shared_secret': shared})
            if path:
                db.set_mafile_path(acc_id, path)
        except Exception:
            pass
        self.manager.current = 'accounts'

class EditAccountScreen(Screen):
    acc = ObjectProperty(None)

    def set_account(self, acc):
        self.acc = acc
        self.ids.edit_name.text = acc['account_name']
        self.ids.edit_password.text = acc['password'] or ''
        self.ids.edit_shared.text = acc['shared_secret'] or ''
        if hasattr(self.ids, 'edit_identity'):
            self.ids.edit_identity.text = acc.get('identity_secret') or ''

    def save(self):
        name = self.ids.edit_name.text.strip()
        pwd = self.ids.edit_password.text.strip()
        shared = self.ids.edit_shared.text.strip()
        identity = ''
        if hasattr(self.ids, 'edit_identity'):
            identity = self.ids.edit_identity.text.strip()
        db = Database()
        db.update_account(self.acc['id'], name, pwd, shared, identity)
        self.manager.current = 'account'

class ConfirmationsScreen(Screen):
    account = ObjectProperty(None)
    confirmations = ListProperty([])

    def set_account(self, acc):
        self.account = acc
        self.load_confirmations()

    def load_confirmations(self):
        wrapper = SteamWrapper()
        try:
            self.confirmations = wrapper.fetch_confirmations(self.account)
        except Exception:
            self.confirmations = []
        # populate confirmations grid
        try:
            grid = self.ids.conf_grid
            grid.clear_widgets()
            from kivy.uix.label import Label
            from kivy.uix.boxlayout import BoxLayout
            from kivy.uix.button import Button
            for i, c in enumerate(self.confirmations):
                box = BoxLayout(size_hint_y=None, height='72dp')
                box.add_widget(Label(text=str(c)))
                b1 = Button(text='Accept', size_hint_x=None, width='100dp')
                b1.bind(on_release=lambda inst, idx=i: self.accept(idx))
                b2 = Button(text='Decline', size_hint_x=None, width='100dp')
                b2.bind(on_release=lambda inst, idx=i: self.decline(idx))
                box.add_widget(b1)
                box.add_widget(b2)
                grid.add_widget(box)
        except Exception:
            pass

    def accept(self, idx):
        wrapper = SteamWrapper()
        wrapper.respond_confirmation(self.account, idx, True)
        self.load_confirmations()

    def decline(self, idx):
        wrapper = SteamWrapper()
        wrapper.respond_confirmation(self.account, idx, False)
        self.load_confirmations()

class AuthApp(App):
    def build(self):
        Builder.load_file(KV_FILE)
        sm = ScreenManager()
        sm.add_widget(MainScreen(name='main'))
        sm.add_widget(AccountsScreen(name='accounts'))
        sm.add_widget(AccountScreen(name='account'))
        sm.add_widget(AddAccountScreen(name='add'))
        sm.add_widget(AddManualScreen(name='add_manual'))
        sm.add_widget(EditAccountScreen(name='edit_account'))
        sm.add_widget(ConfirmationsScreen(name='confirmations'))
        return sm

if __name__ == '__main__':
    AuthApp().run()
