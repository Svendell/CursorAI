"""
Модуль для работы с конфигурацией приложения
"""

import os
import configparser
from typing import Any, Optional


class Config:
    """Менеджер конфигурации приложения"""
    
    DEFAULT_CONFIG_FILE = 'config.ini'
    
    # Значения по умолчанию
    DEFAULTS = {
        'APP': {
            'name': 'Steam Auth Manager',
            'version': '1.0.0',
            'developer': 'Steam Auth Manager Team'
        },
        'UI': {
            'window_width': '360',
            'window_height': '800',
            'items_per_page': '4',
            'list_height_percent': '70'
        },
        'DATABASE': {
            'db_path': '',
            'auto_backup': 'true',
            'backup_dir': 'backups/'
        },
        'SECURITY': {
            'encrypt_passwords': 'false',
            'pbkdf2_iterations': '100000',
            'require_master_password': 'false'
        },
        'STEAM': {
            'mafiles_dir': 'mafiles/',
            'auto_export_mafiles': 'true',
            'export_format': 'json'
        },
        'LOGGING': {
            'log_level': '1',
            'log_file': 'logs/steamauth.log',
            'max_log_size': '10',
            'backup_count': '3'
        },
        'FEATURES': {
            'enable_confirmations': 'true',
            'enable_json_export': 'true',
            'enable_mafile_import': 'true',
            'enable_mafile_creation': 'true'
        },
        'ADVANCED': {
            'dark_theme': 'true',
            'language': 'ru',
            'timezone': 'UTC',
            'use_biometric': 'true',
            'session_timeout': '30'
        }
    }
    
    def __init__(self, config_file: str = DEFAULT_CONFIG_FILE):
        """
        Инициализирует конфигурацию
        
        Args:
            config_file: Путь к файлу конфигурации
        """
        self.config_file = config_file
        self.config = configparser.ConfigParser()
        self.load()
    
    def load(self):
        """Загрузить конфигурацию из файла"""
        if os.path.exists(self.config_file):
            self.config.read(self.config_file)
        else:
            # Использовать значения по умолчанию
            for section, options in self.DEFAULTS.items():
                if not self.config.has_section(section):
                    self.config.add_section(section)
                for key, value in options.items():
                    self.config.set(section, key, value)
            self.save()
    
    def save(self):
        """Сохранить конфигурацию в файл"""
        with open(self.config_file, 'w') as f:
            self.config.write(f)
    
    def get(self, section: str, option: str, fallback: Any = None) -> Any:
        """
        Получить значение опции
        
        Args:
            section: Раздел конфигурации
            option: Опция
            fallback: Значение по умолчанию
        
        Returns:
            Значение опции
        """
        try:
            if self.config.has_option(section, option):
                return self.config.get(section, option)
        except (configparser.NoSectionError, configparser.NoOptionError):
            pass
        
        # Попробовать получить из дефолтов
        if section in self.DEFAULTS and option in self.DEFAULTS[section]:
            return self.DEFAULTS[section][option]
        
        return fallback
    
    def get_int(self, section: str, option: str, fallback: int = 0) -> int:
        """Получить целое число"""
        value = self.get(section, option)
        try:
            return int(value)
        except (ValueError, TypeError):
            return fallback
    
    def get_float(self, section: str, option: str, fallback: float = 0.0) -> float:
        """Получить число с плавающей точкой"""
        value = self.get(section, option)
        try:
            return float(value)
        except (ValueError, TypeError):
            return fallback
    
    def get_bool(self, section: str, option: str, fallback: bool = False) -> bool:
        """Получить булево значение"""
        value = self.get(section, option, 'false').lower()
        return value in ('true', '1', 'yes', 'on')
    
    def set(self, section: str, option: str, value: Any):
        """
        Установить значение опции
        
        Args:
            section: Раздел конфигурации
            option: Опция
            value: Значение
        """
        if not self.config.has_section(section):
            self.config.add_section(section)
        self.config.set(section, option, str(value))
    
    def get_all(self, section: str) -> dict:
        """
        Получить все опции раздела
        
        Args:
            section: Раздел конфигурации
        
        Returns:
            Словарь опций
        """
        if self.config.has_section(section):
            return dict(self.config.items(section))
        return {}
    
    def print_config(self):
        """Вывести всю конфигурацию"""
        for section in self.config.sections():
            print(f"[{section}]")
            for option, value in self.config.items(section):
                print(f"  {option} = {value}")
            print()


# Глобальный экземпляр конфигурации
_config_instance = None


def get_config(config_file: str = Config.DEFAULT_CONFIG_FILE) -> Config:
    """
    Получить глобальный экземпляр конфигурации
    
    Args:
        config_file: Путь к файлу конфигурации
    
    Returns:
        Экземпляр Config
    """
    global _config_instance
    if _config_instance is None:
        _config_instance = Config(config_file)
    return _config_instance


# Вспомогательные функции для удобства
def get_str(section: str, option: str, fallback: str = '') -> str:
    """Получить строку из глобальной конфигурации"""
    return get_config().get(section, option, fallback)


def get_int(section: str, option: str, fallback: int = 0) -> int:
    """Получить целое число из глобальной конфигурации"""
    return get_config().get_int(section, option, fallback)


def get_bool(section: str, option: str, fallback: bool = False) -> bool:
    """Получить булево значение из глобальной конфигурации"""
    return get_config().get_bool(section, option, fallback)


# Тестирование
if __name__ == '__main__':
    config = Config()
    config.print_config()
    
    # Примеры использования
    print("\n=== Примеры использования ===")
    print(f"Название приложения: {config.get('APP', 'name')}")
    print(f"Ширина окна: {config.get_int('UI', 'window_width')}")
    print(f"Шифровать пароли: {config.get_bool('SECURITY', 'encrypt_passwords')}")
    print(f"Язык: {config.get('ADVANCED', 'language')}")
