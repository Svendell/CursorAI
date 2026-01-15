"""Kivy Screens для Steam Auth Manager приложения"""

from kivy.app import App
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.core.window import Window
import os

from app.database import Database
from app.steam_guard import SteamGuardManager, MafileCreator, get_guard_manager
from app.steam_auth import get_authenticator, AuthStatus

Window.size = (360, 800)


class HomeScreen(Screen):
    """Главный экран приложения"""
    
    def __init__(self, db: Database, **kwargs):
        super().__init__(**kwargs)
        self.db = db
    
    def on_enter(self):
        self.build_ui()
    
    def build_ui(self):
        self.clear_widgets()
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Заголовок
        title = Label(text='Steam Guard Manager', size_hint_y=0.15, bold=True, font_size='20sp')
        layout.add_widget(title)
        
        # Кнопка со счетчиком аккаунтов
        account_count = self.db.count_accounts()
        accounts_btn = Button(
            text=f'Accounts : {account_count}',
            size_hint_y=0.2,
            font_size='18sp',
            background_color=(0.2, 0.6, 0.8, 1)
        )
        accounts_btn.bind(on_press=self.go_to_accounts)
        layout.add_widget(accounts_btn)
        
        # Дополнительные кнопки
        settings_btn = Button(text='Settings', size_hint_y=0.2, font_size='18sp')
        layout.add_widget(settings_btn)
        
        about_btn = Button(text='About', size_hint_y=0.2, font_size='18sp')
        layout.add_widget(about_btn)
        
        # Пустое место
        layout.add_widget(Label(size_hint_y=0.25))
        
        self.add_widget(layout)
    
    def go_to_accounts(self, instance):
        self.manager.current = 'accounts'


class AccountsScreen(Screen):
    """Экран со списком аккаунтов"""
    
    def __init__(self, db: Database, **kwargs):
        super().__init__(**kwargs)
        self.db = db
        self.current_page = 0
        self.items_per_page = 4
    
    def on_enter(self):
        self.build_ui()
    
    def build_ui(self):
        self.clear_widgets()
        
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Заголовок
        title = Label(text='Accounts', size_hint_y=0.1, bold=True, font_size='18sp')
        layout.add_widget(title)
        
        # Список аккаунтов (70% высоты)
        accounts = self.db.get_all_accounts()
        self.accounts = accounts
        
        list_layout = BoxLayout(orientation='vertical', size_hint_y=0.7)
        scroll = ScrollView(size_hint=(1, 1))
        
        items_layout = GridLayout(cols=1, spacing=5, size_hint_y=None, padding=5)
        items_layout.bind(minimum_height=items_layout.setter('height'))
        
        # Показать элементы текущей страницы
        start_idx = self.current_page * self.items_per_page
        end_idx = start_idx + self.items_per_page
        page_accounts = accounts[start_idx:end_idx]
        
        for account in page_accounts:
            btn = Button(
                text=account['account_name'],
                size_hint_y=None,
                height=50,
                background_color=(0.2, 0.6, 0.8, 1)
            )
            btn.account_id = account['id']
            btn.bind(on_press=self.open_account)
            items_layout.add_widget(btn)
        
        if not page_accounts:
            items_layout.add_widget(Label(
                text='No accounts yet',
                size_hint_y=None,
                height=50
            ))
        
        scroll.add_widget(items_layout)
        list_layout.add_widget(scroll)
        layout.add_widget(list_layout)
        
        # Кнопки управления (20% высоты)
        control_layout = BoxLayout(orientation='horizontal', size_hint_y=0.2, spacing=5)
        
        back_btn = Button(text='Back')
        back_btn.bind(on_press=self.go_back)
        control_layout.add_widget(back_btn)
        
        add_btn = Button(text='+ Add', background_color=(0.2, 0.8, 0.2, 1))
        add_btn.bind(on_press=self.go_to_add_account)
        control_layout.add_widget(add_btn)
        
        layout.add_widget(control_layout)
        
        self.add_widget(layout)
    
    def open_account(self, instance):
        account_screen = self.manager.get_screen('account')
        account_screen.account_id = instance.account_id
        self.manager.current = 'account'
    
    def go_to_add_account(self, instance):
        self.manager.current = 'add_account'
    
    def go_back(self, instance):
        self.manager.current = 'home'


class AccountScreen(Screen):
    """Экран информации об аккаунте"""
    
    def __init__(self, db: Database, guard_manager: SteamGuardManager, **kwargs):
        super().__init__(**kwargs)
        self.db = db
        self.guard_manager = guard_manager
        self.account_id = None
    
    def on_enter(self):
        self.build_ui()
    
    def build_ui(self):
        self.clear_widgets()
        
        account = self.db.get_account(self.account_id)
        if not account:
            layout = BoxLayout(orientation='vertical')
            layout.add_widget(Label(text='Account not found'))
            self.add_widget(layout)
            return
        
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Информация об аккаунте
        info_layout = BoxLayout(orientation='vertical', size_hint_y=0.35, spacing=5)
        info_layout.add_widget(Label(text=f'Account: {account["account_name"]}', bold=True, font_size='14sp'))
        
        # Получить 2FA код
        code, time_left = self.guard_manager.get_steam_guard_code(account["shared_secret"])
        info_layout.add_widget(Label(
            text=f'2FA Code: {code} ({time_left}s)',
            font_size='16sp',
            bold=True,
            color=(0.2, 0.8, 0.2, 1)
        ))
        info_layout.add_widget(Label(
            text='Created: ' + str(account['created_at']).split()[0],
            font_size='12sp'
        ))
        layout.add_widget(info_layout)
        
        # Кнопки действия (60% высоты)
        buttons_layout = GridLayout(cols=2, spacing=5, size_hint_y=0.6, padding=5)
        
        confirm_btn = Button(
            text='Confirmations',
            background_color=(0.4, 0.6, 0.8, 1),
            size_hint_y=None,
            height=60
        )
        confirm_btn.bind(on_press=self.go_to_confirmations)
        buttons_layout.add_widget(confirm_btn)
        
        edit_btn = Button(
            text='Edit',
            background_color=(0.8, 0.8, 0.2, 1),
            size_hint_y=None,
            height=60
        )
        edit_btn.bind(on_press=self.go_to_edit)
        buttons_layout.add_widget(edit_btn)
        
        delete_btn = Button(
            text='Delete',
            background_color=(0.8, 0.2, 0.2, 1),
            size_hint_y=None,
            height=60
        )
        delete_btn.bind(on_press=self.delete_account)
        buttons_layout.add_widget(delete_btn)
        
        back_btn = Button(
            text='Back',
            size_hint_y=None,
            height=60
        )
        back_btn.bind(on_press=self.go_back)
        buttons_layout.add_widget(back_btn)
        
        layout.add_widget(buttons_layout)
        layout.add_widget(Label(size_hint_y=0.05))
        
        self.add_widget(layout)
    
    def go_to_confirmations(self, instance):
        conf_screen = self.manager.get_screen('confirmations')
        conf_screen.account_id = self.account_id
        self.manager.current = 'confirmations'
    
    def go_to_edit(self, instance):
        edit_screen = self.manager.get_screen('edit_account')
        edit_screen.account_id = self.account_id
        self.manager.current = 'edit_account'
    
    def delete_account(self, instance):
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        content.add_widget(Label(text='Вы уверены что хотите\nудалить этот аккаунт?'))
        
        btn_layout = BoxLayout(size_hint_y=0.3, spacing=10)
        
        confirm_btn = Button(text='Yes', background_color=(0.8, 0.2, 0.2, 1))
        cancel_btn = Button(text='No')
        
        popup = Popup(title='Delete Account', content=content, size_hint=(0.9, 0.4))
        
        def confirm_delete(btn):
            self.db.delete_account(self.account_id)
            popup.dismiss()
            self.manager.current = 'accounts'
        
        confirm_btn.bind(on_press=confirm_delete)
        cancel_btn.bind(on_press=popup.dismiss)
        
        btn_layout.add_widget(confirm_btn)
        btn_layout.add_widget(cancel_btn)
        content.add_widget(btn_layout)
        
        popup.open()
    
    def go_back(self, instance):
        self.manager.current = 'accounts'


class EditAccountScreen(Screen):
    """Экран редактирования аккаунта"""
    
    def __init__(self, db: Database, **kwargs):
        super().__init__(**kwargs)
        self.db = db
        self.account_id = None
    
    def on_enter(self):
        self.build_ui()
    
    def build_ui(self):
        self.clear_widgets()
        
        account = self.db.get_account(self.account_id)
        if not account:
            self.add_widget(Label(text='Account not found'))
            return
        
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Заголовок
        layout.add_widget(Label(text='Edit Account', size_hint_y=0.1, bold=True, font_size='16sp'))
        
        # Форма
        form_layout = GridLayout(cols=1, spacing=10, size_hint_y=0.75, padding=10)
        
        # Account Name
        form_layout.add_widget(Label(text='Account Name:', size_hint_y=None, height=30))
        self.account_name_input = TextInput(
            text=account['account_name'],
            multiline=False,
            size_hint_y=None,
            height=40
        )
        form_layout.add_widget(self.account_name_input)
        
        # Shared Secret
        form_layout.add_widget(Label(text='Shared Secret:', size_hint_y=None, height=30))
        self.shared_secret_input = TextInput(
            text=account['shared_secret'],
            multiline=True,
            size_hint_y=None,
            height=60
        )
        form_layout.add_widget(self.shared_secret_input)
        
        layout.add_widget(form_layout)
        
        # Кнопки
        btn_layout = BoxLayout(size_hint_y=0.15, spacing=5)
        
        save_btn = Button(text='Save', background_color=(0.2, 0.8, 0.2, 1))
        save_btn.bind(on_press=self.save_account)
        btn_layout.add_widget(save_btn)
        
        cancel_btn = Button(text='Cancel')
        cancel_btn.bind(on_press=self.go_back)
        btn_layout.add_widget(cancel_btn)
        
        layout.add_widget(btn_layout)
        
        self.add_widget(layout)
    
    def save_account(self, instance):
        try:
            self.db.update_account(
                self.account_id,
                account_name=self.account_name_input.text,
                shared_secret=self.shared_secret_input.text
            )
            
            self._show_success('Account updated successfully!')
        except Exception as e:
            self._show_error(f'Error: {str(e)}')
    
    def _show_success(self, message):
        content = BoxLayout(orientation='vertical', padding=10)
        content.add_widget(Label(text=message))
        btn = Button(text='OK', size_hint_y=0.3)
        
        popup = Popup(title='Success', content=content, size_hint=(0.9, 0.3))
        
        def on_ok(b):
            popup.dismiss()
            self.go_back(None)
        
        btn.bind(on_press=on_ok)
        content.add_widget(btn)
        popup.open()
    
    def _show_error(self, message):
        content = BoxLayout(orientation='vertical', padding=10)
        content.add_widget(Label(text=message))
        btn = Button(text='OK', size_hint_y=0.3)
        
        popup = Popup(title='Error', content=content, size_hint=(0.9, 0.3))
        btn.bind(on_press=popup.dismiss)
        content.add_widget(btn)
        popup.open()
    
    def go_back(self, instance):
        self.manager.current = 'account'


class ConfirmationsScreen(Screen):
    """Экран с подтверждениями операций"""
    
    def __init__(self, db: Database, guard_manager: SteamGuardManager, **kwargs):
        super().__init__(**kwargs)
        self.db = db
        self.guard_manager = guard_manager
        self.account_id = None
    
    def on_enter(self):
        self.build_ui()
    
    def build_ui(self):
        self.clear_widgets()
        
        account = self.db.get_account(self.account_id)
        if not account:
            self.add_widget(Label(text='Account not found'))
            return
        
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Заголовок
        layout.add_widget(Label(
            text=f'Confirmations',
            size_hint_y=0.1,
            bold=True
        ))
        
        # Список подтверждений
        confirmations = self.guard_manager.get_confirmation_operations(
            account.get('identity_secret', ''),
            account['shared_secret']
        )
        
        conf_layout = BoxLayout(orientation='vertical', size_hint_y=0.75)
        scroll = ScrollView(size_hint=(1, 1))
        
        items_layout = GridLayout(cols=1, spacing=5, size_hint_y=None, padding=5)
        items_layout.bind(minimum_height=items_layout.setter('height'))
        
        if confirmations:
            for conf in confirmations:
                item_layout = BoxLayout(orientation='vertical', size_hint_y=None, height=80, spacing=5)
                item_layout.padding = 5
                
                item_layout.add_widget(Label(
                    text=f'{conf["type"].upper()}: {conf["description"]}',
                    bold=True,
                    size_hint_y=0.5
                ))
                
                btn_layout = BoxLayout(size_hint_y=0.5, spacing=5)
                
                confirm_btn = Button(
                    text='Accept',
                    background_color=(0.2, 0.8, 0.2, 1)
                )
                confirm_btn.conf_id = conf['id']
                confirm_btn.bind(on_press=self.confirm_operation)
                btn_layout.add_widget(confirm_btn)
                
                reject_btn = Button(
                    text='Reject',
                    background_color=(0.8, 0.2, 0.2, 1)
                )
                reject_btn.conf_id = conf['id']
                reject_btn.bind(on_press=self.reject_operation)
                btn_layout.add_widget(reject_btn)
                
                item_layout.add_widget(btn_layout)
                items_layout.add_widget(item_layout)
        else:
            items_layout.add_widget(Label(
                text='No confirmations',
                size_hint_y=None,
                height=50
            ))
        
        scroll.add_widget(items_layout)
        conf_layout.add_widget(scroll)
        layout.add_widget(conf_layout)
        
        # Кнопка назад
        back_btn = Button(text='Back', size_hint_y=0.15)
        back_btn.bind(on_press=self.go_back)
        layout.add_widget(back_btn)
        
        self.add_widget(layout)
    
    def confirm_operation(self, instance):
        account = self.db.get_account(self.account_id)
        self.guard_manager.confirm_operation(
            instance.conf_id,
            account.get('identity_secret', ''),
            allow=True
        )
        self.on_enter()
    
    def reject_operation(self, instance):
        account = self.db.get_account(self.account_id)
        self.guard_manager.confirm_operation(
            instance.conf_id,
            account.get('identity_secret', ''),
            allow=False
        )
        self.on_enter()
    
    def go_back(self, instance):
        self.manager.current = 'account'


class AddAccountScreen(Screen):
    """Экран добавления нового аккаунта"""
    
    def __init__(self, db: Database, guard_manager: SteamGuardManager, **kwargs):
        super().__init__(**kwargs)
        self.db = db
        self.guard_manager = guard_manager
    
    def on_enter(self):
        self.build_ui()
    
    def build_ui(self):
        self.clear_widgets()
        
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Заголовок
        layout.add_widget(Label(text='Add Account', size_hint_y=0.1, bold=True, font_size='16sp'))
        
        # Кнопки выбора метода добавления
        buttons_layout = GridLayout(cols=1, spacing=10, size_hint_y=0.7, padding=10)
        
        manual_btn = Button(
            text='Add Manually',
            background_color=(0.4, 0.6, 0.8, 1),
            size_hint_y=None,
            height=60
        )
        manual_btn.bind(on_press=self.go_to_manual_add)
        buttons_layout.add_widget(manual_btn)
        
        import_btn = Button(
            text='Import Mafile',
            background_color=(0.8, 0.6, 0.4, 1),
            size_hint_y=None,
            height=60
        )
        import_btn.bind(on_press=self.go_to_import_mafile)
        buttons_layout.add_widget(import_btn)
        
        layout.add_widget(buttons_layout)
        
        # Кнопка назад
        back_btn = Button(text='Back', size_hint_y=0.2)
        back_btn.bind(on_press=self.go_back)
        layout.add_widget(back_btn)
        
        self.add_widget(layout)
    
    def go_to_manual_add(self, instance):
        self.manager.current = 'manual_add'
    
    def go_to_import_mafile(self, instance):
        self.manager.current = 'import_mafile'
    
    def go_back(self, instance):
        self.manager.current = 'accounts'


class ManualAddScreen(Screen):
    """Экран для ручного добавления аккаунта"""
    
    def __init__(self, db: Database, **kwargs):
        super().__init__(**kwargs)
        self.db = db
    
    def on_enter(self):
        self.build_ui()
    
    def build_ui(self):
        self.clear_widgets()
        
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Заголовок
        layout.add_widget(Label(text='Add Account Manually', size_hint_y=0.1, bold=True, font_size='14sp'))
        
        # Форма
        form_layout = GridLayout(cols=1, spacing=10, size_hint_y=0.75, padding=10)
        
        # Account Name
        form_layout.add_widget(Label(text='Account Name:', size_hint_y=None, height=30))
        self.account_name_input = TextInput(
            hint_text='Your Steam account name',
            multiline=False,
            size_hint_y=None,
            height=40
        )
        form_layout.add_widget(self.account_name_input)
        
        # Shared Secret
        form_layout.add_widget(Label(text='Shared Secret:', size_hint_y=None, height=30))
        self.shared_secret_input = TextInput(
            hint_text='Base64 encoded shared secret',
            multiline=True,
            size_hint_y=None,
            height=80
        )
        form_layout.add_widget(self.shared_secret_input)
        
        layout.add_widget(form_layout)
        
        # Кнопки
        btn_layout = BoxLayout(size_hint_y=0.15, spacing=5)
        
        save_btn = Button(text='Save', background_color=(0.2, 0.8, 0.2, 1))
        save_btn.bind(on_press=self.save_account)
        btn_layout.add_widget(save_btn)
        
        cancel_btn = Button(text='Cancel')
        cancel_btn.bind(on_press=self.go_back)
        btn_layout.add_widget(cancel_btn)
        
        layout.add_widget(btn_layout)
        
        self.add_widget(layout)
    
    def save_account(self, instance):
        try:
            account_name = self.account_name_input.text.strip()
            shared_secret = self.shared_secret_input.text.strip()
            
            if not account_name or not shared_secret:
                raise ValueError('Please fill in all fields')
            
            account_id = self.db.add_account(
                account_name=account_name,
                password='',
                shared_secret=shared_secret
            )
            
            self._show_success('Account added successfully!')
        except Exception as e:
            self._show_error(f'Error: {str(e)}')
    
    def _show_success(self, message):
        content = BoxLayout(orientation='vertical', padding=10)
        content.add_widget(Label(text=message))
        btn = Button(text='OK', size_hint_y=0.3)
        
        popup = Popup(title='Success', content=content, size_hint=(0.9, 0.3))
        
        def on_ok(b):
            popup.dismiss()
            self.manager.current = 'accounts'
        
        btn.bind(on_press=on_ok)
        content.add_widget(btn)
        popup.open()
    
    def _show_error(self, message):
        content = BoxLayout(orientation='vertical', padding=10)
        content.add_widget(Label(text=message))
        btn = Button(text='OK', size_hint_y=0.3)
        
        popup = Popup(title='Error', content=content, size_hint=(0.9, 0.3))
        btn.bind(on_press=popup.dismiss)
        content.add_widget(btn)
        popup.open()
    
    def go_back(self, instance):
        self.manager.current = 'add_account'


class ImportMafileScreen(Screen):
    """Экран для импорта mafile"""
    
    def __init__(self, db: Database, guard_manager: SteamGuardManager, **kwargs):
        super().__init__(**kwargs)
        self.db = db
        self.guard_manager = guard_manager
        self.mafile_creator = MafileCreator(db)
    
    def on_enter(self):
        self.build_ui()
    
    def build_ui(self):
        self.clear_widgets()
        
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Заголовок
        layout.add_widget(Label(text='Import Mafile', size_hint_y=0.1, bold=True, font_size='14sp'))
        
        # Форма
        form_layout = GridLayout(cols=1, spacing=10, size_hint_y=0.75, padding=10)
        
        # Mafile Path
        form_layout.add_widget(Label(text='Mafile Path:', size_hint_y=None, height=30))
        self.mafile_path_input = TextInput(
            hint_text='/path/to/mafile.maFile',
            multiline=False,
            size_hint_y=None,
            height=40
        )
        form_layout.add_widget(self.mafile_path_input)
        
        # Password (опционально)
        form_layout.add_widget(Label(text='Password (optional):', size_hint_y=None, height=30))
        self.password_input = TextInput(
            hint_text='Password if encrypted',
            password=True,
            multiline=False,
            size_hint_y=None,
            height=40
        )
        form_layout.add_widget(self.password_input)
        
        layout.add_widget(form_layout)
        
        # Кнопки
        btn_layout = BoxLayout(size_hint_y=0.15, spacing=5)
        
        import_btn = Button(text='Import', background_color=(0.2, 0.8, 0.2, 1))
        import_btn.bind(on_press=self.import_mafile)
        btn_layout.add_widget(import_btn)
        
        cancel_btn = Button(text='Cancel')
        cancel_btn.bind(on_press=self.go_back)
        btn_layout.add_widget(cancel_btn)
        
        layout.add_widget(btn_layout)
        
        self.add_widget(layout)
    
    def import_mafile(self, instance):
        try:
            mafile_path = self.mafile_path_input.text.strip()
            password = self.password_input.text.strip()
            
            if not mafile_path:
                raise ValueError('Please enter mafile path')
            
            if not os.path.exists(mafile_path):
                raise ValueError(f'File not found: {mafile_path}')
            
            # Импортировать mafile
            account_id = self.mafile_creator.import_and_add_account(
                mafile_path,
                password
            )
            
            if account_id:
                self._show_success('Mafile imported successfully!')
            else:
                raise ValueError('Failed to import mafile')
        except Exception as e:
            self._show_error(f'Error: {str(e)}')
    
    def _show_success(self, message):
        content = BoxLayout(orientation='vertical', padding=10)
        content.add_widget(Label(text=message))
        btn = Button(text='OK', size_hint_y=0.3)
        
        popup = Popup(title='Success', content=content, size_hint=(0.9, 0.3))
        
        def on_ok(b):
            popup.dismiss()
            self.manager.current = 'accounts'
        
        btn.bind(on_press=on_ok)
        content.add_widget(btn)
        popup.open()
    
    def _show_error(self, message):
        content = BoxLayout(orientation='vertical', padding=10)
        content.add_widget(Label(text=message))
        btn = Button(text='OK', size_hint_y=0.3)
        
        popup = Popup(title='Error', content=content, size_hint=(0.9, 0.3))
        btn.bind(on_press=popup.dismiss)
        content.add_widget(btn)
        popup.open()
    
    def go_back(self, instance):
        self.manager.current = 'add_account'
