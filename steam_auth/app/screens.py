from kivy.app import App
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.image import Image
from kivy.garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg
from kivy.core.window import Window
from kivy.uix.filechooser import FileChooserListView
import os

from app.database import Database
from app.steam_guard import SteamGuardManager, MafileCreator
from app.steam_auth import get_authenticator, AuthStatus

# Установить размер окна для эмуляции мобильного устройства
Window.size = (360, 800)


class HomeScreen(Screen):
    """Главный экран приложения"""
    
    def __init__(self, db: Database, **kwargs):
        super().__init__(**kwargs)
        self.db = db
        self.build_ui()
    
    def build_ui(self):
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Заголовок
        title = Label(text='Steam Auth Manager', size_hint_y=0.15, bold=True, font_size='20sp')
        layout.add_widget(title)
        
        # Кнопка со счетчиком аккаунтов
        account_count = self.db.count_accounts()
        accounts_btn = Button(
            text=f'Accounts : {account_count}',
            size_hint_y=0.2,
            font_size='18sp'
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
    
    def on_enter(self):
        # Обновить счетчик при возврате на главный экран
        self.clear_widgets()
        self.build_ui()
    
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
        
        scroll.add_widget(items_layout)
        list_layout.add_widget(scroll)
        layout.add_widget(list_layout)
        
        # Кнопки управления (30% высоты)
        control_layout = BoxLayout(orientation='horizontal', size_hint_y=0.2, spacing=5)
        
        back_btn = Button(text='Back')
        back_btn.bind(on_press=self.go_back)
        control_layout.add_widget(back_btn)
        
        add_btn = Button(text='Add Account', background_color=(0.2, 0.8, 0.2, 1))
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
        info_layout = BoxLayout(orientation='vertical', size_hint_y=0.3, spacing=5)
        info_layout.add_widget(Label(text=f'Account: {account["account_name"]}', bold=True))
        info_layout.add_widget(Label(text=f'2FA Code: {self.guard_manager.get_steam_guard_code(account["shared_secret"])}', font_size='16sp', bold=True, color=(0.2, 0.8, 0.2, 1)))
        info_layout.add_widget(Label(text='Created: ' + str(account['created_at']).split()[0]))
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
        
        # Место для дополнительного контента
        layout.add_widget(Label(size_hint_y=0.1))
        
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
        content = BoxLayout(orientation='vertical')
        content.add_widget(Label(text='Вы уверены что хотите удалить\nэтот аккаунт?'))
        
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
        form_layout = GridLayout(cols=1, spacing=10, size_hint_y=0.8, padding=10)
        
        # Account Name
        form_layout.add_widget(Label(text='Account Name:', size_hint_y=None, height=30))
        self.account_name_input = TextInput(
            text=account['account_name'],
            multiline=False,
            size_hint_y=None,
            height=40
        )
        form_layout.add_widget(self.account_name_input)
        
        # Password
        form_layout.add_widget(Label(text='Password:', size_hint_y=None, height=30))
        self.password_input = TextInput(
            text=account['password'],
            password=True,
            multiline=False,
            size_hint_y=None,
            height=40
        )
        form_layout.add_widget(self.password_input)
        
        # Shared Secret
        form_layout.add_widget(Label(text='Shared Secret:', size_hint_y=None, height=30))
        self.shared_secret_input = TextInput(
            text=account['shared_secret'],
            multiline=False,
            size_hint_y=None,
            height=40
        )
        form_layout.add_widget(self.shared_secret_input)
        
        layout.add_widget(form_layout)
        
        # Кнопки
        btn_layout = BoxLayout(size_hint_y=0.1, spacing=5)
        
        save_btn = Button(text='Save', background_color=(0.2, 0.8, 0.2, 1))
        save_btn.bind(on_press=self.save_account)
        btn_layout.add_widget(save_btn)
        
        cancel_btn = Button(text='Cancel')
        cancel_btn.bind(on_press=self.go_back)
        btn_layout.add_widget(cancel_btn)
        
        layout.add_widget(btn_layout)
        
        self.add_widget(layout)
    
    def save_account(self, instance):
        self.db.update_account(
            self.account_id,
            account_name=self.account_name_input.text,
            password=self.password_input.text,
            shared_secret=self.shared_secret_input.text
        )
        
        # Показать сообщение об успехе
        content = BoxLayout(orientation='vertical')
        content.add_widget(Label(text='Account updated successfully!'))
        btn = Button(text='OK', size_hint_y=0.3)
        
        popup = Popup(title='Success', content=content, size_hint=(0.9, 0.3))
        btn.bind(on_press=popup.dismiss)
        btn.bind(on_press=self.go_back)
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
        self.confirmations = []
    
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
            text=f'Confirmations for {account["account_name"]}',
            size_hint_y=0.1,
            bold=True
        ))
        
        # Список подтверждений
        self.confirmations = self.guard_manager.get_confirmation_operations(
            account.get('identity_secret', ''),
            account['shared_secret']
        )
        
        conf_layout = BoxLayout(orientation='vertical', size_hint_y=0.75)
        scroll = ScrollView(size_hint=(1, 1))
        
        items_layout = GridLayout(cols=1, spacing=5, size_hint_y=None, padding=5)
        items_layout.bind(minimum_height=items_layout.setter('height'))
        
        if self.confirmations:
            for conf in self.confirmations:
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
        
        # Кнопка назад (15% высоты)
        back_btn = Button(text='Back', size_hint_y=0.15)
        back_btn.bind(on_press=self.go_back)
        layout.add_widget(back_btn)
        
        self.add_widget(layout)
    
    def confirm_operation(self, instance):
        account = self.db.get_account(self.account_id)
        self.guard_manager.confirm_operation(
            instance.conf_id,
            account.get('identity_secret', ''),
            account['shared_secret'],
            confirm=True
        )
        self.on_enter()  # Обновить экран
    
    def reject_operation(self, instance):
        account = self.db.get_account(self.account_id)
        self.guard_manager.confirm_operation(
            instance.conf_id,
            account.get('identity_secret', ''),
            account['shared_secret'],
            confirm=False
        )
        self.on_enter()  # Обновить экран
    
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
        
        create_btn = Button(
            text='Create Mafile',
            background_color=(0.4, 0.8, 0.6, 1),
            size_hint_y=None,
            height=60
        )
        create_btn.bind(on_press=self.go_to_create_mafile)
        buttons_layout.add_widget(create_btn)
        
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
    
    def go_to_create_mafile(self, instance):
        self.manager.current = 'create_mafile'
    
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
        layout.add_widget(Label(text='Add Account Manually', size_hint_y=0.1, bold=True, font_size='16sp'))
        
        # Форма
        form_layout = GridLayout(cols=1, spacing=10, size_hint_y=0.75, padding=10)
        
        # Account Name
        form_layout.add_widget(Label(text='Account Name:', size_hint_y=None, height=30))
        self.account_name_input = TextInput(
            hint_text='Steam account name',
            multiline=False,
            size_hint_y=None,
            height=40
        )
        form_layout.add_widget(self.account_name_input)
        
        # Password
        form_layout.add_widget(Label(text='Password:', size_hint_y=None, height=30))
        self.password_input = TextInput(
            hint_text='Password',
            password=True,
            multiline=False,
            size_hint_y=None,
            height=40
        )
        form_layout.add_widget(self.password_input)
        
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
            account_id = self.db.add_account(
                account_name=self.account_name_input.text,
                password=self.password_input.text,
                shared_secret=self.shared_secret_input.text
            )
            
            content = BoxLayout(orientation='vertical')
            content.add_widget(Label(text='Account added successfully!'))
            btn = Button(text='OK', size_hint_y=0.3)
            
            popup = Popup(title='Success', content=content, size_hint=(0.9, 0.3))
            btn.bind(on_press=popup.dismiss)
            btn.bind(on_press=self.go_to_accounts)
            content.add_widget(btn)
            popup.open()
        except Exception as e:
            content = BoxLayout(orientation='vertical')
            content.add_widget(Label(text=f'Error: {str(e)}'))
            btn = Button(text='OK', size_hint_y=0.3)
            
            popup = Popup(title='Error', content=content, size_hint=(0.9, 0.3))
            btn.bind(on_press=popup.dismiss)
            content.add_widget(btn)
            popup.open()
    
    def go_back(self, instance):
        self.manager.current = 'add_account'
    
    def go_to_accounts(self, instance):
        self.manager.current = 'accounts'


class CreateMafileScreen(Screen):
    """Экран для создания mafile как в Steam Desktop Authenticator (SDA)
    
    Многошаговый flow:
    1. Ввод логина и пароля
    2. Отправка кода подтверждения (email/SMS)
    3. Ввод кода подтверждения
    4. Создание и сохранение mafile
    """
    
    def __init__(self, db: Database, guard_manager: SteamGuardManager, **kwargs):
        super().__init__(**kwargs)
        self.db = db
        self.guard_manager = guard_manager
        self.authenticator = get_authenticator()
        self.current_step = 'login'  # login, send_code, confirm_code, success
    
    def on_enter(self):
        self.current_step = 'login'
        self.build_ui()
    
    def build_ui(self):
        self.clear_widgets()
        
        if self.current_step == 'login':
            self._build_login_step()
        elif self.current_step == 'send_code':
            self._build_send_code_step()
        elif self.current_step == 'confirm_code':
            self._build_confirm_code_step()
        elif self.current_step == 'success':
            self._build_success_step()
    
    def _build_login_step(self):
        """Шаг 1: Ввод логина и пароля"""
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Заголовок
        layout.add_widget(Label(
            text='Create Mafile',
            size_hint_y=0.1,
            bold=True,
            font_size='18sp'
        ))
        
        # Прогресс-индикатор
        progress = Label(text='Step 1 of 3: Enter Credentials', size_hint_y=0.08, font_size='12sp')
        layout.add_widget(progress)
        
        # Форма
        form_layout = GridLayout(cols=1, spacing=10, size_hint_y=0.65, padding=10)
        
        form_layout.add_widget(Label(
            text='This will create a mafile using Steam authentication.\n'
                 'Your credentials are encrypted and stored securely.',
            size_hint_y=None,
            height=80
        ))
        
        # Account Name
        form_layout.add_widget(Label(text='Steam Account:', size_hint_y=None, height=30))
        self.account_name_input = TextInput(
            hint_text='Your Steam username',
            multiline=False,
            size_hint_y=None,
            height=40
        )
        form_layout.add_widget(self.account_name_input)
        
        # Password
        form_layout.add_widget(Label(text='Password:', size_hint_y=None, height=30))
        self.password_input = TextInput(
            hint_text='Your account password',
            password=True,
            multiline=False,
            size_hint_y=None,
            height=40
        )
        form_layout.add_widget(self.password_input)
        
        layout.add_widget(form_layout)
        
        # Кнопки
        btn_layout = BoxLayout(size_hint_y=0.15, spacing=5)
        
        next_btn = Button(text='Next', background_color=(0.2, 0.8, 0.2, 1))
        next_btn.bind(on_press=self.on_login_pressed)
        btn_layout.add_widget(next_btn)
        
        cancel_btn = Button(text='Cancel')
        cancel_btn.bind(on_press=self.go_back)
        btn_layout.add_widget(cancel_btn)
        
        layout.add_widget(btn_layout)
        
        self.add_widget(layout)
    
    def on_login_pressed(self, instance):
        """Обработка нажатия кнопки Login"""
        account_name = self.account_name_input.text.strip()
        password = self.password_input.text.strip()
        
        if not account_name or not password:
            self._show_error('Please enter both account and password')
            return
        
        # Попытка авторизации
        success, message = self.authenticator.login(account_name, password)
        
        if success:
            # Авторизация успешна
            self.current_step = 'send_code'
            self.build_ui()
        else:
            # Нужен код подтверждения
            self.current_step = 'send_code'
            self.build_ui()
    
    def _build_send_code_step(self):
        """Шаг 2: Отправка кода подтверждения"""
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Заголовок
        layout.add_widget(Label(
            text='Verify Your Account',
            size_hint_y=0.1,
            bold=True,
            font_size='18sp'
        ))
        
        # Прогресс-индикатор
        progress = Label(text='Step 2 of 3: Verify via Email/SMS', size_hint_y=0.08, font_size='12sp')
        layout.add_widget(progress)
        
        # Контент
        content_layout = GridLayout(cols=1, spacing=15, size_hint_y=0.65, padding=10)
        
        content_layout.add_widget(Label(
            text='Steam will send you a verification code.\n'
                 'Please choose how to receive it:',
            size_hint_y=None,
            height=60
        ))
        
        # Кнопки выбора способа получения кода
        method_layout = GridLayout(cols=1, spacing=10, size_hint_y=None, height=100)
        
        email_btn = Button(text='Send Code to Email', size_hint_y=None, height=40)
        email_btn.bind(on_press=self.on_send_code_pressed)
        method_layout.add_widget(email_btn)
        
        sms_btn = Button(text='Send Code via SMS', size_hint_y=None, height=40)
        sms_btn.bind(on_press=self.on_send_code_pressed)
        method_layout.add_widget(sms_btn)
        
        content_layout.add_widget(method_layout)
        
        content_layout.add_widget(Label(
            text='A verification code will be sent to your registered email or phone.',
            size_hint_y=None,
            height=50
        ))
        
        layout.add_widget(content_layout)
        
        # Кнопки
        btn_layout = BoxLayout(size_hint_y=0.15, spacing=5)
        
        back_btn = Button(text='Back')
        back_btn.bind(on_press=self.go_back_step)
        btn_layout.add_widget(back_btn)
        
        cancel_btn = Button(text='Cancel')
        cancel_btn.bind(on_press=self.go_back)
        btn_layout.add_widget(cancel_btn)
        
        layout.add_widget(btn_layout)
        
        self.add_widget(layout)
    
    def on_send_code_pressed(self, instance):
        """Отправить код подтверждения"""
        try:
            self.authenticator.send_code()
            self.current_step = 'confirm_code'
            self.build_ui()
        except Exception as e:
            self._show_error(f'Failed to send code: {str(e)}')
    
    def _build_confirm_code_step(self):
        """Шаг 3: Ввод кода подтверждения"""
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Заголовок
        layout.add_widget(Label(
            text='Enter Verification Code',
            size_hint_y=0.1,
            bold=True,
            font_size='18sp'
        ))
        
        # Прогресс-индикатор
        progress = Label(text='Step 3 of 3: Confirm Code', size_hint_y=0.08, font_size='12sp')
        layout.add_widget(progress)
        
        # Форма
        form_layout = GridLayout(cols=1, spacing=10, size_hint_y=0.65, padding=10)
        
        form_layout.add_widget(Label(
            text='Enter the 5-digit code you received:',
            size_hint_y=None,
            height=40
        ))
        
        # Code input
        self.code_input = TextInput(
            hint_text='00000',
            multiline=False,
            size_hint_y=None,
            height=50,
            input_filter='int'
        )
        form_layout.add_widget(self.code_input)
        
        form_layout.add_widget(Label(
            text='Once you confirm this code, your mafile will be created.',
            size_hint_y=None,
            height=40
        ))
        
        layout.add_widget(form_layout)
        
        # Кнопки
        btn_layout = BoxLayout(size_hint_y=0.15, spacing=5)
        
        confirm_btn = Button(text='Confirm', background_color=(0.2, 0.8, 0.2, 1))
        confirm_btn.bind(on_press=self.on_confirm_code_pressed)
        btn_layout.add_widget(confirm_btn)
        
        cancel_btn = Button(text='Cancel')
        cancel_btn.bind(on_press=self.go_back)
        btn_layout.add_widget(cancel_btn)
        
        layout.add_widget(btn_layout)
        
        self.add_widget(layout)
    
    def on_confirm_code_pressed(self, instance):
        """Обработка подтверждения кода"""
        code = self.code_input.text.strip()
        
        if not code or len(code) != 5:
            self._show_error('Please enter a valid 5-digit code')
            return
        
        try:
            success, message = self.authenticator.confirm_code(code)
            
            if success:
                # Создать mafile
                mafile_data = self.authenticator.get_mafile_data()
                account_id = self.db.add_account(
                    account_name=mafile_data.get('account_name', 'unknown'),
                    password='',  # Пароль уже использован и подтвержден
                    shared_secret=mafile_data.get('shared_secret', ''),
                    identity_secret=mafile_data.get('identity_secret', ''),
                    revocation_code=mafile_data.get('revocation_code', '')
                )
                
                # Создать файл mafile
                account = self.db.get_account(account_id)
                mafile_path = self.guard_manager.create_mafile_from_dict(account)
                
                self.current_step = 'success'
                self.build_ui()
            else:
                self._show_error(f'Invalid code: {message}')
        except Exception as e:
            self._show_error(f'Error: {str(e)}')
    
    def _build_success_step(self):
        """Шаг успеха: mafile создан"""
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        layout.add_widget(Label(
            text='✓ Success!',
            size_hint_y=0.2,
            bold=True,
            font_size='24sp',
            color=(0.2, 0.8, 0.2, 1)
        ))
        
        content = GridLayout(cols=1, spacing=10, size_hint_y=0.65, padding=10)
        
        content.add_widget(Label(
            text='Your mafile has been created successfully!\n\n'
                 'The account has been added to your database\n'
                 'and is ready for 2FA code generation.',
            size_hint_y=None,
            height=120
        ))
        
        layout.add_widget(content)
        
        # Кнопки
        btn_layout = BoxLayout(size_hint_y=0.15, spacing=5)
        
        finish_btn = Button(text='Done', background_color=(0.2, 0.8, 0.2, 1))
        finish_btn.bind(on_press=self.on_finish)
        btn_layout.add_widget(finish_btn)
        
        layout.add_widget(btn_layout)
        
        self.add_widget(layout)
    
    def on_finish(self, instance):
        """Завершить создание mafile"""
        self.authenticator.reset()
        self.manager.current = 'accounts'
    
    def go_back_step(self, instance):
        """Вернуться на предыдущий шаг"""
        if self.current_step == 'send_code':
            self.current_step = 'login'
            self.build_ui()
        elif self.current_step == 'confirm_code':
            self.current_step = 'send_code'
            self.build_ui()
    
    def go_back(self, instance):
        """Отмена и возврат на экран выбора метода добавления"""
        self.authenticator.reset()
        self.manager.current = 'add_account'
    
    def _show_error(self, message):
        """Показать диалог с ошибкой"""
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        content.add_widget(Label(text=message))
        
        btn = Button(text='OK', size_hint_y=0.3)
        content.add_widget(btn)
        
        popup = Popup(title='Error', content=content, size_hint=(0.9, 0.4))
        btn.bind(on_press=popup.dismiss)
        popup.open()


class ImportMafileScreen(Screen):
    """Экран для импорта mafile"""
    
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
        layout.add_widget(Label(text='Import Mafile', size_hint_y=0.1, bold=True, font_size='16sp'))
        
        # Выбор файла
        file_layout = BoxLayout(orientation='vertical', size_hint_y=0.6)
        
        # В реальном приложении здесь был бы file chooser
        # Для демонстрации используем простой ввод пути
        file_layout.add_widget(Label(text='Mafile Path:', size_hint_y=None, height=30))
        self.file_path_input = TextInput(
            hint_text='/path/to/mafile.maFile',
            multiline=False,
            size_hint_y=None,
            height=40
        )
        file_layout.add_widget(self.file_path_input)
        
        file_layout.add_widget(Label(text='Password:', size_hint_y=None, height=30))
        self.password_input = TextInput(
            hint_text='Password',
            password=True,
            multiline=False,
            size_hint_y=None,
            height=40
        )
        file_layout.add_widget(self.password_input)
        
        layout.add_widget(file_layout)
        
        # Кнопки
        btn_layout = BoxLayout(size_hint_y=0.2, spacing=5)
        
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
            mafile_creator = MafileCreator(self.db)
            account_id = mafile_creator.import_and_add_account(
                self.file_path_input.text,
                self.password_input.text
            )
            
            if account_id:
                content = BoxLayout(orientation='vertical')
                content.add_widget(Label(text='Mafile imported successfully!'))
                btn = Button(text='OK', size_hint_y=0.3)
                
                popup = Popup(title='Success', content=content, size_hint=(0.9, 0.3))
                btn.bind(on_press=popup.dismiss)
                btn.bind(on_press=self.go_to_accounts)
                content.add_widget(btn)
                popup.open()
            else:
                raise Exception('Failed to import mafile')
        except Exception as e:
            content = BoxLayout(orientation='vertical')
            content.add_widget(Label(text=f'Error: {str(e)}'))
            btn = Button(text='OK', size_hint_y=0.3)
            
            popup = Popup(title='Error', content=content, size_hint=(0.9, 0.3))
            btn.bind(on_press=popup.dismiss)
            content.add_widget(btn)
            popup.open()
    
    def go_back(self, instance):
        self.manager.current = 'add_account'
    
    def go_to_accounts(self, instance):
        self.manager.current = 'accounts'
