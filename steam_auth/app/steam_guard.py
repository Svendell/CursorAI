import json
import os
from typing import Dict, List, Optional, Any
import base64
import time


class SteamGuardManager:
    """Менеджер для работы с Steam Guard и mafiles"""
    
    MAFILES_DIR = os.path.join(os.path.dirname(__file__), '..', 'mafiles')
    
    def __init__(self):
        os.makedirs(self.MAFILES_DIR, exist_ok=True)
    
    def create_mafile_from_dict(self, account_data: Dict[str, Any]) -> str:
        """Создать mafile из данных аккаунта"""
        account_name = account_data.get('account_name')
        
        # Структура mafile (совместима с Steam Desktop Authenticator)
        mafile_content = {
            "shared_secret": account_data.get('shared_secret'),
            "identity_secret": account_data.get('identity_secret', ''),
            "revocation_code": account_data.get('revocation_code', ''),
            "account_name": account_name,
            "uri": "",
            "server_time": int(time.time()),
            "account_name_hmac": "",
            "session_id": "",
            "fully_enrolled": True
        }
        
        # Сохранить в файл
        mafile_path = os.path.join(self.MAFILES_DIR, f'{account_name}.maFile')
        with open(mafile_path, 'w') as f:
            json.dump(mafile_content, f, indent=2)
        
        return mafile_path
    
    def import_mafile(self, mafile_path: str) -> Optional[Dict[str, Any]]:
        """Импортировать mafile"""
        try:
            with open(mafile_path, 'r') as f:
                mafile_data = json.load(f)
            
            return {
                'account_name': mafile_data.get('account_name'),
                'shared_secret': mafile_data.get('shared_secret'),
                'identity_secret': mafile_data.get('identity_secret'),
                'revocation_code': mafile_data.get('revocation_code'),
            }
        except (json.JSONDecodeError, IOError) as e:
            print(f"Ошибка при импорте mafile: {e}")
            return None
    
    def get_steam_guard_code(self, shared_secret: str) -> str:
        """Получить 2FA код из shared_secret
        
        Использует алгоритм TOTP, как в Steam Guard
        """
        try:
            import hmac
            import hashlib
            import struct
            
            # Декодировать shared_secret из base64
            secret_bytes = base64.b64decode(shared_secret)
            
            # Получить текущее время в 30-секундных интервалах
            server_time = int(time.time())
            time_counter = server_time // 30
            
            # Преобразовать в bytes (big-endian)
            time_bytes = struct.pack('>Q', time_counter)
            
            # Вычислить HMAC-SHA1
            hmac_hash = hmac.new(secret_bytes, time_bytes, hashlib.sha1).digest()
            
            # Получить последние 4 байта и преобразовать в число
            last_byte = hmac_hash[-1] & 0x0f
            four_bytes = struct.unpack('>I', hmac_hash[last_byte:last_byte + 4])[0]
            
            # Получить последние 5 цифр
            code = str(four_bytes % 100000).zfill(5)
            
            return code
        except Exception as e:
            print(f"Ошибка при получении Steam Guard кода: {e}")
            return "00000"
    
    def get_confirmation_operations(self, identity_secret: str, shared_secret: str,
                                    access_token: Optional[str] = None) -> List[Dict[str, Any]]:
        """Получить список предложений для подтверждения
        
        В реальном приложении это должно делать через Steam API
        """
        # Демо список операций (в реальном приложении нужна авторизация)
        return [
            {
                'id': '1',
                'type': 'trade',
                'description': 'Обмен предметов',
                'timestamp': int(time.time()),
                'status': 'pending'
            },
            {
                'id': '2',
                'type': 'market',
                'description': 'Продажа на маркетплейсе',
                'timestamp': int(time.time()),
                'status': 'pending'
            }
        ]
    
    def confirm_operation(self, operation_id: str, identity_secret: str,
                         shared_secret: str, confirm: bool = True) -> bool:
        """Подтвердить или отклонить операцию"""
        # В реальном приложении это должно делать через Steam API
        print(f"{'Подтверждение' if confirm else 'Отклонение'} операции: {operation_id}")
        return True


class MafileCreator:
    """Создатель mafiles с поддержкой создания как в Steam Desktop Authenticator"""
    
    def __init__(self, db_manager: 'Database'):
        self.db_manager = db_manager
        self.guard_manager = SteamGuardManager()
    
    def create_mafile_from_account(self, account_id: int) -> Optional[str]:
        """Создать mafile для существующего аккаунта"""
        account = self.db_manager.get_account(account_id)
        if not account:
            return None
        
        return self.guard_manager.create_mafile_from_dict(account)
    
    def import_and_add_account(self, mafile_path: str, password: str) -> Optional[int]:
        """Импортировать mafile и добавить в БД"""
        mafile_data = self.guard_manager.import_mafile(mafile_path)
        if not mafile_data:
            return None
        
        try:
            account_id = self.db_manager.add_account(
                account_name=mafile_data['account_name'],
                password=password,
                shared_secret=mafile_data['shared_secret'],
                identity_secret=mafile_data.get('identity_secret'),
                revocation_code=mafile_data.get('revocation_code')
            )
            return account_id
        except Exception as e:
            print(f"Ошибка при добавлении аккаунта: {e}")
            return None
