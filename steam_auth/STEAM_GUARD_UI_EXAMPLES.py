"""
Примеры интеграции Steam Guard функционала в Kivy UI
Демонстрирует как использовать SteamGuardManager в экранах приложения
"""

# ============================================================================
# ПРИМЕР 1: AddAccountScreen - Добавление нового аккаунта
# ============================================================================

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.garden.spinner import Spinner
from kivy.uix.progressbar import ProgressBar
from kivy.core.window import Window
from kivy.uix.screenmanager import Screen
from kivy.uix.scrollview import ScrollView

from steam_guard import SteamGuardManager
import threading


class AddAccountScreen(Screen):
    """Экран добавления нового аккаунта через Steam Web API"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.guard = SteamGuardManager()
        self.setup_ui()
    
    def setup_ui(self):
        """Построить UI"""
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Заголовок
        title = Label(
            text='[b]Добавить новый Steam аккаунт[/b]',
            markup=True,
            size_hint_y=0.1
        )
        layout.add_widget(title)
        
        # Форма ввода
        form = GridLayout(cols=2, spacing=10, size_hint_y=0.4)
        
        # Имя пользователя
        form.add_widget(Label(text='Steam Username:', size_hint_x=0.3))
        self.username_input = TextInput(
            hint_text='Your Steam username',
            multiline=False,
            size_hint_x=0.7
        )
        form.add_widget(self.username_input)
        
        # Пароль
        form.add_widget(Label(text='Password:', size_hint_x=0.3))
        self.password_input = TextInput(
            hint_text='Your Steam password',
            password=True,
            multiline=False,
            size_hint_x=0.7
        )
        form.add_widget(self.password_input)
        
        # Номер телефона
        form.add_widget(Label(text='Phone Number:', size_hint_x=0.3))
        self.phone_input = TextInput(
            hint_text='+1234567890',
            multiline=False,
            size_hint_x=0.7
        )
        form.add_widget(self.phone_input)
        
        layout.add_widget(form)
        
        # Статус
        self.status_label = Label(
            text='Готов к добавлению аккаунта',
            size_hint_y=0.2
        )
        layout.add_widget(self.status_label)
        
        # Прогресс
        self.progress = ProgressBar(max=100, value=0, size_hint_y=0.1)
        layout.add_widget(self.progress)
        
        # Кнопки
        buttons = BoxLayout(size_hint_y=0.2, spacing=10)
        
        btn_add = Button(text='Add Account')
        btn_add.bind(on_press=self.on_add_account)
        buttons.add_widget(btn_add)
        
        btn_cancel = Button(text='Cancel')
        btn_cancel.bind(on_press=lambda x: self.on_cancel())
        buttons.add_widget(btn_cancel)
        
        layout.add_widget(buttons)
        
        self.add_widget(layout)
    
    def on_add_account(self, instance):
        """Обработать нажатие кнопки добавления"""
        username = self.username_input.text.strip()
        password = self.password_input.text
        phone = self.phone_input.text.strip()
        
        if not username or not password:
            self.status_label.text = '[color=ff0000]Username и password обязательны[/color]'
            return
        
        # Запустить добавление в отдельном потоке
        self.status_label.text = 'Подключение к Steam Web API...'
        self.progress.value = 25
        
        def add_account_thread():
            try:
                # Шаг 1: Аутентификация
                self.status_label.text = 'Аутентификация...'
                self.progress.value = 50
                
                # Шаг 2: Привязка 2FA
                self.status_label.text = 'Привязка Steam Guard...'
                self.progress.value = 75
                
                account_data = self.guard.add_account_with_login(
                    username=username,
                    password=password,
                    phone_number=phone if phone else None
                )
                
                if account_data:
                    self.status_label.text = (
                        f'[color=00ff00]Аккаунт добавлен!\n'
                        f'Steam ID: {account_data["steam_id"]}\n'
                        f'Revocation Code: {account_data["revocation_code"]}[/color]'
                    )
                    self.progress.value = 100
                    
                    # Показать popup с revocation code
                    self.show_revocation_code_popup(account_data["revocation_code"])
                else:
                    self.status_label.text = '[color=ff0000]Ошибка при добавлении аккаунта[/color]'
                    self.progress.value = 0
                
            except Exception as e:
                self.status_label.text = f'[color=ff0000]Ошибка: {str(e)}[/color]'
                self.progress.value = 0
        
        thread = threading.Thread(target=add_account_thread)
        thread.daemon = True
        thread.start()
    
    def show_revocation_code_popup(self, revocation_code):
        """Показать popup с кодом восстановления"""
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        content.add_widget(Label(
            text='[b]ВАЖНО: Сохраните код восстановления![/b]',
            markup=True
        ))
        
        content.add_widget(Label(
            text=f'Этот код позволит вам восстановить доступ к аккаунту\nесли вы потеряете доступ к 2FA:\n\n[b]{revocation_code}[/b]',
            markup=True
        ))
        
        btn = Button(text='OK', size_hint_y=0.3)
        content.add_widget(btn)
        
        popup = Popup(
            title='Revocation Code',
            content=content,
            size_hint=(0.9, 0.6)
        )
        
        btn.bind(on_press=popup.dismiss)
        popup.open()
    
    def on_cancel(self):
        """Отменить добавление"""
        self.manager.current = 'main'


# ============================================================================
# ПРИМЕР 2: AccountListScreen - Список аккаунтов и 2FA коды
# ============================================================================

class AccountListScreen(Screen):
    """Экран со списком аккаунтов и 2FA кодов"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.guard = SteamGuardManager()
        self.setup_ui()
    
    def setup_ui(self):
        """Построить UI"""
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Заголовок
        title = Label(
            text='[b]Ваши Steam аккаунты[/b]',
            markup=True,
            size_hint_y=0.1
        )
        layout.add_widget(title)
        
        # Список аккаунтов (в ScrollView)
        scroll = ScrollView(size_hint=(1, 0.7))
        self.accounts_layout = GridLayout(cols=1, spacing=10, size_hint_y=None)
        self.accounts_layout.bind(minimum_height=self.accounts_layout.setter('height'))
        scroll.add_widget(self.accounts_layout)
        layout.add_widget(scroll)
        
        # Кнопки
        buttons = BoxLayout(size_hint_y=0.2, spacing=10)
        
        btn_refresh = Button(text='Refresh Codes')
        btn_refresh.bind(on_press=lambda x: self.refresh_accounts())
        buttons.add_widget(btn_refresh)
        
        btn_add = Button(text='Add Account')
        btn_add.bind(on_press=lambda x: self.on_add_account())
        buttons.add_widget(btn_add)
        
        layout.add_widget(buttons)
        
        self.add_widget(layout)
        
        # Загрузить аккаунты при открытии
        self.on_enter = self.refresh_accounts
    
    def refresh_accounts(self, *args):
        """Обновить список аккаунтов и 2FA коды"""
        self.accounts_layout.clear_widgets()
        
        accounts = self.guard.get_all_accounts()
        
        if not accounts:
            self.accounts_layout.add_widget(Label(
                text='Нет аккаунтов. Нажмите "Add Account" для добавления.',
                size_hint_y=None,
                height=50
            ))
            return
        
        for account in accounts:
            self.add_account_widget(account)
    
    def add_account_widget(self, account):
        """Добавить виджет аккаунта"""
        account_box = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=200,
            padding=10,
            spacing=5
        )
        account_box.canvas.before.clear()
        
        # Имя аккаунта
        name_label = Label(
            text=f"[b]{account['account_name']}[/b]",
            markup=True,
            size_hint_y=0.2
        )
        account_box.add_widget(name_label)
        
        # 2FA код
        try:
            entry = self.guard.manifest.get_entry(account['steam_id'])
            mafile_path = f"{self.guard.MAFILES_DIR}/{entry.filename}"
            
            import json
            with open(mafile_path, 'r') as f:
                mafile_data = json.load(f)
            
            code, time_left = self.guard.get_steam_guard_code(
                mafile_data['shared_secret']
            )
            
            code_label = Label(
                text=f"[b][size=32]{code}[/size][/b]\n({time_left}s)",
                markup=True,
                size_hint_y=0.4
            )
            account_box.add_widget(code_label)
        except Exception as e:
            account_box.add_widget(Label(
                text=f'[color=ff0000]Ошибка: {str(e)}[/color]',
                markup=True
            ))
        
        # Статус шифрования
        encrypted_text = "🔒 Encrypted" if account['is_encrypted'] else "🔓 Not encrypted"
        status_label = Label(
            text=encrypted_text,
            size_hint_y=0.2
        )
        account_box.add_widget(status_label)
        
        # Действия
        actions = BoxLayout(size_hint_y=0.2, spacing=5)
        
        btn_copy = Button(text='Copy Code')
        btn_copy.bind(on_press=lambda x: self.copy_code(code))
        actions.add_widget(btn_copy)
        
        btn_encrypt = Button(text='Encrypt' if not account['is_encrypted'] else 'Decrypt')
        btn_encrypt.bind(on_press=lambda x: self.on_toggle_encryption(account))
        actions.add_widget(btn_encrypt)
        
        btn_delete = Button(text='Delete')
        btn_delete.bind(on_press=lambda x: self.on_delete_account(account))
        actions.add_widget(btn_delete)
        
        account_box.add_widget(actions)
        
        self.accounts_layout.add_widget(account_box)
    
    def copy_code(self, code):
        """Скопировать код в буфер обмена"""
        # Kivy: нужно использовать соответствующий модуль для платформы
        try:
            import subprocess
            subprocess.Popen(['xclip', '-selection', 'clipboard'], 
                           stdin=subprocess.PIPE).communicate(code.encode())
        except:
            # На мобильных устройствах может потребоваться другой подход
            pass
    
    def on_toggle_encryption(self, account):
        """Переключить шифрование для аккаунта"""
        if account['is_encrypted']:
            self.show_decrypt_dialog(account)
        else:
            self.show_encrypt_dialog(account)
    
    def show_encrypt_dialog(self, account):
        """Показать диалог шифрования"""
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        content.add_widget(Label(text='Enter encryption password:'))
        
        password_input = TextInput(
            hint_text='Password',
            password=True,
            multiline=False
        )
        content.add_widget(password_input)
        
        buttons = BoxLayout(size_hint_y=0.3, spacing=10)
        
        def encrypt_account():
            password = password_input.text
            if password:
                if self.guard.encrypt_mafile(account['steam_id'], password):
                    popup.dismiss()
                    self.refresh_accounts()
        
        btn_encrypt = Button(text='Encrypt')
        btn_encrypt.bind(on_press=lambda x: encrypt_account())
        buttons.add_widget(btn_encrypt)
        
        btn_cancel = Button(text='Cancel')
        btn_cancel.bind(on_press=lambda x: popup.dismiss())
        buttons.add_widget(btn_cancel)
        
        content.add_widget(buttons)
        
        popup = Popup(
            title='Encrypt Account',
            content=content,
            size_hint=(0.9, 0.6)
        )
        popup.open()
    
    def show_decrypt_dialog(self, account):
        """Показать диалог расшифровки"""
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        content.add_widget(Label(text='Enter encryption password:'))
        
        password_input = TextInput(
            hint_text='Password',
            password=True,
            multiline=False
        )
        content.add_widget(password_input)
        
        buttons = BoxLayout(size_hint_y=0.3, spacing=10)
        
        def decrypt_account():
            password = password_input.text
            mafile_data = self.guard.decrypt_mafile(account['steam_id'], password)
            if mafile_data:
                # Расшифровать успешно - теперь нужно сохранить как расшифрованный
                popup.dismiss()
                self.refresh_accounts()
            else:
                # Ошибка при расшифровке
                pass
        
        btn_decrypt = Button(text='Decrypt')
        btn_decrypt.bind(on_press=lambda x: decrypt_account())
        buttons.add_widget(btn_decrypt)
        
        btn_cancel = Button(text='Cancel')
        btn_cancel.bind(on_press=lambda x: popup.dismiss())
        buttons.add_widget(btn_cancel)
        
        content.add_widget(buttons)
        
        popup = Popup(
            title='Decrypt Account',
            content=content,
            size_hint=(0.9, 0.6)
        )
        popup.open()
    
    def on_delete_account(self, account):
        """Удалить аккаунт"""
        # TODO: Показать confirmation dialog
        self.guard.remove_account(account['steam_id'])
        self.refresh_accounts()
    
    def on_add_account(self):
        """Перейти на экран добавления"""
        self.manager.current = 'add_account'


# ============================================================================
# ПРИМЕР 3: ImportMaFileScreen - Импорт mafile
# ============================================================================

class ImportMaFileScreen(Screen):
    """Экран импорта mafile из другого источника"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.guard = SteamGuardManager()
        self.setup_ui()
    
    def setup_ui(self):
        """Построить UI"""
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        layout.add_widget(Label(
            text='[b]Импортировать mafile[/b]',
            markup=True,
            size_hint_y=0.1
        ))
        
        # Выбор файла (на мобильных устройствах это будет другой механизм)
        self.file_path_label = Label(
            text='Файл не выбран',
            size_hint_y=0.2
        )
        layout.add_widget(self.file_path_label)
        
        btn_browse = Button(text='Browse Files', size_hint_y=0.15)
        btn_browse.bind(on_press=self.on_browse_files)
        layout.add_widget(btn_browse)
        
        # Пароль (если mafile зашифрован)
        layout.add_widget(Label(text='Encryption Password (if needed):', size_hint_y=0.1))
        
        self.password_input = TextInput(
            hint_text='Leave empty if not encrypted',
            password=True,
            multiline=False,
            size_hint_y=0.15
        )
        layout.add_widget(self.password_input)
        
        # Статус
        self.status_label = Label(text='', size_hint_y=0.2)
        layout.add_widget(self.status_label)
        
        # Кнопки
        buttons = BoxLayout(size_hint_y=0.15, spacing=10)
        
        btn_import = Button(text='Import')
        btn_import.bind(on_press=self.on_import)
        buttons.add_widget(btn_import)
        
        btn_cancel = Button(text='Cancel')
        btn_cancel.bind(on_press=lambda x: self.manager.current = 'accounts')
        buttons.add_widget(btn_cancel)
        
        layout.add_widget(buttons)
        
        self.add_widget(layout)
        
        self.selected_file = None
    
    def on_browse_files(self, instance):
        """Открыть файловый браузер"""
        # На мобильных устройствах нужно использовать соответствующий API
        # Например, android.storage или filechooser
        pass
    
    def on_import(self, instance):
        """Импортировать выбранный mafile"""
        if not self.selected_file:
            self.status_label.text = '[color=ff0000]Выберите файл[/color]'
            return
        
        password = self.password_input.text.strip()
        
        self.status_label.text = 'Импорт...'
        
        def import_thread():
            success = self.guard.import_and_register_mafile(
                self.selected_file,
                password=password if password else None
            )
            
            if success:
                self.status_label.text = '[color=00ff00]Аккаунт успешно импортирован![/color]'
            else:
                self.status_label.text = '[color=ff0000]Ошибка при импорте[/color]'
        
        thread = threading.Thread(target=import_thread)
        thread.daemon = True
        thread.start()


# ============================================================================
# ПРИМЕЧАНИЯ ДЛЯ ИНТЕГРАЦИИ
# ============================================================================

"""
1. ИНИЦИАЛИЗАЦИЯ В ГЛАВНОМ ПРИЛОЖЕНИИ:
   
   from steam_auth import SteamGuardManager
   from screens import AddAccountScreen, AccountListScreen
   
   class SteamAuthApp(App):
       def build(self):
           sm = ScreenManager()
           sm.add_widget(AccountListScreen(name='accounts'))
           sm.add_widget(AddAccountScreen(name='add_account'))
           return sm

2. ПОТОКОБЕЗОПАСНОСТЬ:
   - Все долгие операции (Steam Web API) должны быть в отдельных потоках
   - Используйте threading.Thread или asyncio для асинхронных операций
   - Обновляйте UI только из главного потока

3. БЕЗОПАСНОСТЬ:
   - Не храните пароли в памяти дольше необходимого
   - Используйте шифрование для чувствительных данных
   - На мобильных устройствах используйте secure storage

4. ANDROID СПЕЦИФИКА:
   - Для выбора файлов используйте android.filechooser или аналог
   - Проверьте WRITE_EXTERNAL_STORAGE и READ_EXTERNAL_STORAGE permissions
   - Используйте app-specific directories для сохранения файлов

5. ОБНОВЛЕНИЕ КОДОВ:
   - Обновляйте 2FA коды примерно каждые 2-3 секунды
   - Используйте Timer для периодического обновления
   - Показывайте оставшееся время до смены кода
"""
