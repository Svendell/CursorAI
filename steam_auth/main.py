from kivy.app import App
from kivy.uix.screenmanager import ScreenManager
from kivy.core.window import Window

from app.database import Database
from app.steam_guard import SteamGuardManager
from app.config import get_config
from app.logger import get_logger, log_info, log_error
from app.screens import (
    HomeScreen, AccountsScreen, AccountScreen, EditAccountScreen,
    ConfirmationsScreen, AddAccountScreen, ManualAddScreen,
    CreateMafileScreen, ImportMafileScreen
)


class SteamAuthApp(App):
    """Главное приложение для управления Steam аккаунтами"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Инициализировать конфигурацию и логирование
        self.app_config = get_config()
        self.logger = get_logger()
        
        log_info("=== Инициализация приложения ===")
        log_info(f"Версия: {self.app_config.get('APP', 'version')}")
        
        # Инициализировать базу данных и менеджер Steam Guard
        try:
            self.db = Database()
            self.guard_manager = SteamGuardManager()
            log_info("База данных и Steam Guard менеджер инициализированы")
        except Exception as e:
            log_error("Ошибка при инициализации", e)
            raise
        
        # Установить параметры приложения
        self.title = self.app_config.get('APP', 'name', 'Steam Auth Manager')
    
    def build(self):
        """Построить интерфейс приложения"""
        # Установить размер окна из конфигурации
        window_width = self.app_config.get_int('UI', 'window_width', 360)
        window_height = self.app_config.get_int('UI', 'window_height', 800)
        Window.size = (window_width, window_height)
        
        log_info(f"Размер окна: {window_width}x{window_height}")
        
        # Создать менеджер экранов
        self.root = ScreenManager()
        
        # Создать все экраны
        try:
            self.root.add_widget(HomeScreen(self.db, name='home'))
            self.root.add_widget(AccountsScreen(self.db, name='accounts'))
            self.root.add_widget(AccountScreen(self.db, self.guard_manager, name='account'))
            self.root.add_widget(EditAccountScreen(self.db, name='edit_account'))
            self.root.add_widget(ConfirmationsScreen(self.db, self.guard_manager, name='confirmations'))
            self.root.add_widget(AddAccountScreen(self.db, self.guard_manager, name='add_account'))
            self.root.add_widget(ManualAddScreen(self.db, name='manual_add'))
            self.root.add_widget(CreateMafileScreen(self.db, self.guard_manager, name='create_mafile'))
            self.root.add_widget(ImportMafileScreen(self.db, self.guard_manager, name='import_mafile'))
            
            log_info("Все экраны успешно созданы")
        except Exception as e:
            log_error("Ошибка при создании экранов", e)
            raise
        
        # Установить начальный экран
        self.root.current = 'home'
        log_info("Приложение готово к работе")
        
        return self.root
    
    def on_stop(self):
        """Вызывается когда приложение закрывается"""
        log_info("Закрытие приложения")
        return True


if __name__ == '__main__':
    try:
        app = SteamAuthApp()
        app.run()
    except Exception as e:
        print(f"Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()
