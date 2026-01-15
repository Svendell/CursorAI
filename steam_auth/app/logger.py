"""
Модуль логирования приложения
"""

import logging
import logging.handlers
import os
from app.config import get_config


class AppLogger:
    """Менеджер логирования для приложения"""
    
    _instance = None
    _logger = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AppLogger, cls).__new__(cls)
            cls._instance._init_logger()
        return cls._instance
    
    def _init_logger(self):
        """Инициализировать логгер"""
        config = get_config()
        
        # Создать логгер
        self._logger = logging.getLogger('steam_auth_manager')
        
        # Получить уровень логирования
        log_level_int = config.get_int('LOGGING', 'log_level', 1)
        levels = {
            0: logging.ERROR,
            1: logging.INFO,
            2: logging.DEBUG
        }
        log_level = levels.get(log_level_int, logging.INFO)
        self._logger.setLevel(log_level)
        
        # Консольный обработчик
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        console_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(console_formatter)
        self._logger.addHandler(console_handler)
        
        # Файловый обработчик (если указан)
        log_file = config.get('LOGGING', 'log_file')
        if log_file:
            # Создать папку для логов если не существует
            log_dir = os.path.dirname(log_file)
            if log_dir and not os.path.exists(log_dir):
                os.makedirs(log_dir)
            
            # Максимальный размер файла в байтах
            max_bytes = config.get_int('LOGGING', 'max_log_size', 10) * 1024 * 1024
            backup_count = config.get_int('LOGGING', 'backup_count', 3)
            
            file_handler = logging.handlers.RotatingFileHandler(
                log_file,
                maxBytes=max_bytes,
                backupCount=backup_count
            )
            file_handler.setLevel(log_level)
            file_formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            file_handler.setFormatter(file_formatter)
            self._logger.addHandler(file_handler)
    
    def get_logger(self):
        """Получить логгер"""
        return self._logger


def get_logger():
    """Получить логгер приложения"""
    return AppLogger().get_logger()


def log_debug(message: str):
    """Логирование debug"""
    get_logger().debug(message)


def log_info(message: str):
    """Логирование info"""
    get_logger().info(message)


def log_warning(message: str):
    """Логирование warning"""
    get_logger().warning(message)


def log_error(message: str, exception: Exception = None):
    """Логирование error"""
    if exception:
        get_logger().error(message, exc_info=True)
    else:
        get_logger().error(message)


def log_critical(message: str):
    """Логирование critical"""
    get_logger().critical(message)


# Примеры использования
if __name__ == '__main__':
    logger = get_logger()
    
    log_debug("Debug сообщение")
    log_info("Info сообщение")
    log_warning("Warning сообщение")
    log_error("Error сообщение")
    log_critical("Critical сообщение")
    
    # С исключением
    try:
        1 / 0
    except Exception as e:
        log_error("Произошла ошибка", e)
