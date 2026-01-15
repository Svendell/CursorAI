"""
Дополнительные утилиты для работы со Steam API и Guard
"""

import hmac
import hashlib
import struct
import time
import base64
import json
from typing import Optional, Dict, Any


class SteamGuardUtil:
    """Утилиты для работы с Steam Guard TOTP"""
    
    # Steam использует этот алгоритм для генерации кодов
    STEAM_GUARD_CODE_CHARS = '23456789BCDFGHJKMNPQRTVW'
    
    @staticmethod
    def generate_totp(shared_secret: str, time_offset: int = 0) -> str:
        """
        Генерирует TOTP код из shared secret
        
        Args:
            shared_secret: Base64-encoded shared secret из Steam
            time_offset: Смещение времени в секундах (для тестирования)
        
        Returns:
            5-значный код Steam Guard
        """
        try:
            # Декодировать secret из base64
            secret_bytes = base64.b64decode(shared_secret)
            
            # Получить текущее время в 30-секундных интервалах
            server_time = int(time.time()) + time_offset
            time_counter = server_time // 30
            
            # Преобразовать в bytes (big-endian)
            time_bytes = struct.pack('>Q', time_counter)
            
            # Вычислить HMAC-SHA1
            hmac_hash = hmac.new(secret_bytes, time_bytes, hashlib.sha1).digest()
            
            # Получить индекс от последних 4 бит
            last_byte = hmac_hash[-1] & 0x0f
            four_bytes = struct.unpack('>I', hmac_hash[last_byte:last_byte + 4])[0]
            
            # Получить последние 5 цифр
            code = str(four_bytes % 100000).zfill(5)
            
            return code
        except Exception as e:
            print(f"Ошибка при генерации TOTP: {e}")
            return "00000"
    
    @staticmethod
    def generate_steam_guard_code(shared_secret: str, time_offset: int = 0) -> str:
        """
        Генерирует Steam Guard код (как в приложении Steam)
        
        Args:
            shared_secret: Base64-encoded shared secret
            time_offset: Смещение времени
        
        Returns:
            5-значный Steam Guard код
        """
        try:
            secret_bytes = base64.b64decode(shared_secret)
            server_time = int(time.time()) + time_offset
            time_counter = server_time // 30
            
            time_bytes = struct.pack('>Q', time_counter)
            hmac_hash = hmac.new(secret_bytes, time_bytes, hashlib.sha1).digest()
            
            # Steam использует свой метод для конвертации
            last_byte = hmac_hash[-1] & 0x0f
            four_bytes = struct.unpack('>I', hmac_hash[last_byte:last_byte + 4])[0]
            
            code = str(four_bytes % 100000).zfill(5)
            return code
        except Exception as e:
            print(f"Ошибка: {e}")
            return "00000"
    
    @staticmethod
    def get_code_time_remaining() -> int:
        """Получить количество секунд до смены кода"""
        return 30 - (int(time.time()) % 30)
    
    @staticmethod
    def get_next_code_time() -> int:
        """Получить время до следующего кода в секундах"""
        return 30 - (int(time.time()) % 30)


class SteamAPIAuth:
    """Работа с Steam API для подтверждений"""
    
    STEAM_API_BASE = 'https://api.steampowered.com'
    STEAMCOMMUNITY_API_BASE = 'https://steamcommunity.com'
    
    @staticmethod
    def generate_confirmation_hash(identity_secret: str, tag: str = 'conf') -> str:
        """
        Генерирует хеш для запроса подтверждений
        
        Args:
            identity_secret: Identity secret из аккаунта
            tag: Тег для хеша ('conf', 'details', или 'allow')
        
        Returns:
            Хеш для использования в запросе
        """
        try:
            secret_bytes = base64.b64decode(identity_secret)
            server_time = int(time.time())
            
            time_bytes = struct.pack('>Q', server_time // 30)
            tag_bytes = tag.encode('utf-8')
            
            # Комбинировать данные
            data = time_bytes + tag_bytes
            
            # Вычислить HMAC-SHA1
            hmac_hash = hmac.new(secret_bytes, data, hashlib.sha1).digest()
            
            # Закодировать в base64
            hash_b64 = base64.b64encode(hmac_hash).decode('utf-8')
            
            return hash_b64
        except Exception as e:
            print(f"Ошибка при генерации хеша: {e}")
            return ""
    
    @staticmethod
    def get_confirmations_url(steam_id: int, identity_secret: str, access_token: str) -> str:
        """
        Создает URL для получения списка подтверждений
        
        Args:
            steam_id: SteamID 64-bit
            identity_secret: Identity secret
            access_token: Access token из refresh token
        
        Returns:
            URL для запроса
        """
        confirmation_hash = SteamAPIAuth.generate_confirmation_hash(identity_secret)
        server_time = int(time.time())
        
        url = (
            f'{SteamAPIAuth.STEAMCOMMUNITY_API_BASE}/mobileconf/getlist'
            f'?p=0'
            f'&a={steam_id}'
            f'&k={confirmation_hash}'
            f'&t={server_time}'
            f'&m=react'
            f'&tag=conf'
        )
        
        return url
    
    @staticmethod
    def get_confirmation_details_url(steam_id: int, confirmation_id: str,
                                     identity_secret: str) -> str:
        """
        Создает URL для получения деталей подтверждения
        
        Args:
            steam_id: SteamID 64-bit
            confirmation_id: ID подтверждения
            identity_secret: Identity secret
        
        Returns:
            URL для запроса
        """
        details_hash = SteamAPIAuth.generate_confirmation_hash(identity_secret, 'details')
        server_time = int(time.time())
        
        url = (
            f'{SteamAPIAuth.STEAMCOMMUNITY_API_BASE}/mobileconf/details/{confirmation_id}'
            f'?p=0'
            f'&a={steam_id}'
            f'&k={details_hash}'
            f'&t={server_time}'
            f'&m=react'
            f'&tag=details'
        )
        
        return url


class MafileValidator:
    """Валидация и работа с mafiles"""
    
    REQUIRED_FIELDS = [
        'shared_secret',
        'account_name'
    ]
    
    OPTIONAL_FIELDS = [
        'identity_secret',
        'revocation_code',
        'uri',
        'server_time',
        'account_name_hmac',
        'session_id',
        'fully_enrolled'
    ]
    
    @classmethod
    def validate_mafile(cls, mafile_data: Dict[str, Any]) -> bool:
        """
        Валидирует структуру mafile
        
        Args:
            mafile_data: Данные из mafile
        
        Returns:
            True если валидный, False иначе
        """
        # Проверить обязательные поля
        for field in cls.REQUIRED_FIELDS:
            if field not in mafile_data:
                print(f"Отсутствует обязательное поле: {field}")
                return False
        
        # Проверить shared_secret это валидный base64
        try:
            base64.b64decode(mafile_data['shared_secret'])
        except Exception:
            print("Invalid shared_secret format")
            return False
        
        # Проверить identity_secret если присутствует
        if 'identity_secret' in mafile_data and mafile_data['identity_secret']:
            try:
                base64.b64decode(mafile_data['identity_secret'])
            except Exception:
                print("Invalid identity_secret format")
                return False
        
        return True
    
    @classmethod
    def create_mafile(cls, account_name: str, shared_secret: str,
                     identity_secret: Optional[str] = None,
                     revocation_code: Optional[str] = None) -> Dict[str, Any]:
        """
        Создает структуру mafile
        
        Args:
            account_name: Имя аккаунта
            shared_secret: Base64 shared secret
            identity_secret: Base64 identity secret (опционально)
            revocation_code: Revocation code (опционально)
        
        Returns:
            Структура mafile
        """
        mafile = {
            'shared_secret': shared_secret,
            'identity_secret': identity_secret or '',
            'revocation_code': revocation_code or '',
            'account_name': account_name,
            'uri': '',
            'server_time': int(time.time()),
            'account_name_hmac': '',
            'session_id': '',
            'fully_enrolled': True
        }
        
        return mafile


class SteamIDConverter:
    """Конвертация между разными форматами SteamID"""
    
    @staticmethod
    def to_64bit(steam_id: str) -> int:
        """
        Конвертирует SteamID (STEAM_0:...) в 64-bit формат
        
        Args:
            steam_id: SteamID в формате STEAM_0:X:XXXXXX
        
        Returns:
            64-bit SteamID
        """
        try:
            # Парсить STEAM_0:X:Y
            parts = steam_id.replace('STEAM_', '').split(':')
            y = int(parts[1])
            x = int(parts[2])
            
            # Вычислить 32-bit ID
            steam_id_32 = (x << 1) | y
            
            # Конвертировать в 64-bit
            steam_id_64 = (steam_id_32 & 0xffffffff) | 0x0110000100000000
            
            return steam_id_64
        except Exception as e:
            print(f"Ошибка при конвертации SteamID: {e}")
            return 0
    
    @staticmethod
    def from_64bit(steam_id_64: int) -> str:
        """
        Конвертирует 64-bit SteamID в стандартный формат
        
        Args:
            steam_id_64: 64-bit SteamID
        
        Returns:
            SteamID в формате STEAM_0:X:Y
        """
        try:
            # Извлечь 32-bit ID
            steam_id_32 = steam_id_64 & 0xffffffff
            
            # Вычислить X и Y
            y = steam_id_32 & 1
            x = steam_id_32 >> 1
            
            return f'STEAM_0:{y}:{x}'
        except Exception as e:
            print(f"Ошибка при конвертации SteamID: {e}")
            return ''
