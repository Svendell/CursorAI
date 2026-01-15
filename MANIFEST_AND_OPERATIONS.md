# 🗂️ Manifest и Структура Аккаунтов SteamGuard

## 📋 Содержание

1. [Что такое Manifest](#что-такое-manifest)
2. [Структура Manifest файла](#структура-manifest-файла)
3. [Работа с несколькими mafiles](#работа-с-несколькими-mafiles)
4. [Операции и подтверждения](#операции-и-подтверждения)
5. [Загрузка и сохранение Manifest](#загрузка-и-сохранение-manifest)

---

## Что такое Manifest

### Определение

**Manifest** - это метаданные файл, который содержит информацию обо всех mafiles в приложении. Подобно каталогу - он помогает приложению быстро найти и загрузить нужные mafiles без сканирования всех файлов.

### Назначение

```
Структура папки:
mafiles/
├── account1.maFile
├── account2.maFile
├── account3.maFile
└── manifest.json  ← Manifest файл
```

**Manifest.json** помогает:
1. Быстро получить список всех аккаунтов
2. Хранить дополнительные метаданные
3. Управлять порядком отображения
4. Отслеживать последние изменения
5. Синхронизировать с облаком (если нужно)

---

## Структура Manifest файла

### Базовая структура

```json
{
  "accounts": [
    {
      "account_name": "account1",
      "filename": "account1.maFile",
      "timestamp": 1705330800,
      "last_used": 1705330900,
      "enabled": true
    },
    {
      "account_name": "account2",
      "filename": "account2.maFile",
      "timestamp": 1705331000,
      "last_used": 1705331100,
      "enabled": true
    }
  ],
  "version": 1,
  "created": 1705330800,
  "updated": 1705331100
}
```

### Полная структура с метаданными

```json
{
  "version": 1,
  "created_at": 1705330800,
  "updated_at": 1705331100,
  "total_accounts": 3,
  "encrypted": false,
  "encryption_key_hash": "",
  
  "accounts": [
    {
      "account_name": "myaccount",
      "filename": "myaccount.maFile",
      "steam_id": 76561198123456789,
      "display_name": "My Account",
      "created_at": 1705330800,
      "updated_at": 1705330900,
      "last_used": 1705330950,
      "last_code": "12345",
      "last_code_time": 1705330900,
      "enabled": true,
      "favorite": false,
      "notes": "Main account",
      "confirmations_enabled": true,
      "last_confirmations_check": 1705330905,
      "pending_confirmations": 2,
      "status": "healthy"  // healthy, warning, error, offline
    },
    {
      "account_name": "altaccount",
      "filename": "altaccount.maFile",
      "steam_id": 76561198987654321,
      "display_name": "Alt Account",
      "created_at": 1705331000,
      "updated_at": 1705331100,
      "last_used": 1705331050,
      "last_code": "67890",
      "last_code_time": 1705331000,
      "enabled": true,
      "favorite": true,
      "notes": "",
      "confirmations_enabled": true,
      "last_confirmations_check": 1705331005,
      "pending_confirmations": 0,
      "status": "healthy"
    }
  ],
  
  "settings": {
    "auto_refresh_interval": 30,
    "notifications_enabled": true,
    "clipboard_copy_enabled": true,
    "lock_timeout_minutes": 5
  }
}
```

### Поля в Manifest

| Поле | Тип | Описание |
|------|-----|---------|
| `version` | int | Версия формата manifest (для совместимости) |
| `created_at` | int | Unix timestamp создания manifest |
| `updated_at` | int | Unix timestamp последнего обновления |
| `total_accounts` | int | Количество аккаунтов |
| `encrypted` | bool | Зашифрован ли manifest |
| `accounts` | array | Массив метаданных аккаунтов |

### Поля Account в Manifest

| Поле | Тип | Обязателен | Описание |
|------|-----|-----------|---------|
| `account_name` | string | ✓ | Имя Steam аккаунта |
| `filename` | string | ✓ | Имя mafile файла |
| `steam_id` | int | ✗ | 64-bit Steam ID |
| `created_at` | int | ✗ | Когда добавлен mafile |
| `updated_at` | int | ✗ | Когда последний раз обновлен |
| `last_used` | int | ✗ | Когда последний раз использовался |
| `last_code` | string | ✗ | Последний сгенерированный код |
| `enabled` | bool | ✗ | Активен ли аккаунт |
| `favorite` | bool | ✗ | Избранный ли аккаунт |
| `confirmations_enabled` | bool | ✗ | Включены ли подтверждения |
| `status` | string | ✗ | Статус (healthy, warning, error) |

---

## Работа с несколькими mafiles

### Класс ManifestManager

```python
import json
import os
import time
from typing import List, Dict, Optional, Any

class ManifestManager:
    """Управление manifest файлом"""
    
    def __init__(self, mafiles_dir: str):
        self.mafiles_dir = mafiles_dir
        self.manifest_path = os.path.join(mafiles_dir, 'manifest.json')
        self._ensure_manifest_exists()
    
    def _ensure_manifest_exists(self):
        """Убедиться что manifest существует"""
        if not os.path.exists(self.manifest_path):
            self.create_empty_manifest()
    
    def create_empty_manifest(self):
        """Создать пустой manifest"""
        manifest = {
            'version': 1,
            'created_at': int(time.time()),
            'updated_at': int(time.time()),
            'total_accounts': 0,
            'encrypted': False,
            'encryption_key_hash': '',
            'accounts': [],
            'settings': {
                'auto_refresh_interval': 30,
                'notifications_enabled': True,
                'clipboard_copy_enabled': True,
                'lock_timeout_minutes': 5
            }
        }
        
        self._save_manifest(manifest)
    
    def load_manifest(self) -> Dict[str, Any]:
        """Загрузить manifest"""
        try:
            with open(self.manifest_path, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            self.create_empty_manifest()
            return self.load_manifest()
    
    def _save_manifest(self, manifest: Dict[str, Any]):
        """Сохранить manifest"""
        manifest['updated_at'] = int(time.time())
        manifest['total_accounts'] = len(manifest.get('accounts', []))
        
        with open(self.manifest_path, 'w') as f:
            json.dump(manifest, f, indent=2)
    
    def add_account_to_manifest(self, account_name: str, filename: str,
                               steam_id: Optional[int] = None) -> bool:
        """Добавить аккаунт в manifest"""
        manifest = self.load_manifest()
        
        # Проверить дубликаты
        if any(acc['account_name'] == account_name for acc in manifest['accounts']):
            return False
        
        # Добавить новый аккаунт
        account_entry = {
            'account_name': account_name,
            'filename': filename,
            'steam_id': steam_id,
            'created_at': int(time.time()),
            'updated_at': int(time.time()),
            'last_used': None,
            'last_code': '',
            'last_code_time': None,
            'enabled': True,
            'favorite': False,
            'notes': '',
            'confirmations_enabled': True,
            'last_confirmations_check': None,
            'pending_confirmations': 0,
            'status': 'healthy'
        }
        
        manifest['accounts'].append(account_entry)
        self._save_manifest(manifest)
        
        return True
    
    def remove_account_from_manifest(self, account_name: str) -> bool:
        """Удалить аккаунт из manifest"""
        manifest = self.load_manifest()
        
        original_count = len(manifest['accounts'])
        manifest['accounts'] = [
            acc for acc in manifest['accounts']
            if acc['account_name'] != account_name
        ]
        
        if len(manifest['accounts']) < original_count:
            self._save_manifest(manifest)
            return True
        
        return False
    
    def update_account_in_manifest(self, account_name: str,
                                  updates: Dict[str, Any]) -> bool:
        """Обновить данные аккаунта в manifest"""
        manifest = self.load_manifest()
        
        for account in manifest['accounts']:
            if account['account_name'] == account_name:
                account.update(updates)
                account['updated_at'] = int(time.time())
                self._save_manifest(manifest)
                return True
        
        return False
    
    def get_all_accounts(self) -> List[Dict[str, Any]]:
        """Получить все аккаунты из manifest"""
        manifest = self.load_manifest()
        return manifest.get('accounts', [])
    
    def get_account(self, account_name: str) -> Optional[Dict[str, Any]]:
        """Получить конкретный аккаунт"""
        manifest = self.load_manifest()
        
        for account in manifest['accounts']:
            if account['account_name'] == account_name:
                return account
        
        return None
    
    def update_last_used(self, account_name: str):
        """Обновить время последнего использования"""
        self.update_account_in_manifest(
            account_name,
            {'last_used': int(time.time())}
        )
    
    def update_last_code(self, account_name: str, code: str):
        """Обновить последний сгенерированный код"""
        self.update_account_in_manifest(
            account_name,
            {
                'last_code': code,
                'last_code_time': int(time.time())
            }
        )
    
    def set_favorite(self, account_name: str, is_favorite: bool) -> bool:
        """Установить/снять флаг избранного"""
        return self.update_account_in_manifest(
            account_name,
            {'favorite': is_favorite}
        )
    
    def sync_with_filesystem(self) -> List[str]:
        """Синхронизировать manifest с файловой системой"""
        manifest = self.load_manifest()
        
        # Получить все .maFile файлы
        existing_files = {
            f[:-7] for f in os.listdir(self.mafiles_dir)
            if f.endswith('.maFile')
        }
        
        # Получить аккаунты из manifest
        manifest_accounts = {acc['account_name'] for acc in manifest['accounts']}
        
        # Найти отсутствующие файлы
        missing_files = manifest_accounts - existing_files
        
        # Удалить отсутствующие из manifest
        for account_name in missing_files:
            self.remove_account_from_manifest(account_name)
        
        # Найти новые файлы
        new_files = existing_files - manifest_accounts
        
        # Добавить новые в manifest
        for account_name in new_files:
            filename = f"{account_name}.maFile"
            self.add_account_to_manifest(account_name, filename)
        
        return missing_files
```

### Пример использования ManifestManager

```python
# Инициализация
manifest_mgr = ManifestManager('mafiles')

# Добавить новый аккаунт
manifest_mgr.add_account_to_manifest(
    account_name='myaccount',
    filename='myaccount.maFile',
    steam_id=76561198123456789
)

# Получить все аккаунты
accounts = manifest_mgr.get_all_accounts()
print(f"Всего аккаунтов: {len(accounts)}")

# Обновить при использовании
manifest_mgr.update_last_used('myaccount')
manifest_mgr.update_last_code('myaccount', '12345')

# Установить избранное
manifest_mgr.set_favorite('myaccount', True)

# Синхронизировать с файловой системой
missing = manifest_mgr.sync_with_filesystem()
if missing:
    print(f"Удаленные маfiles: {missing}")

# Получить конкретный аккаунт
account = manifest_mgr.get_account('myaccount')
print(f"Статус: {account['status']}")
print(f"Ожидающих подтверждений: {account['pending_confirmations']}")
```

---

## Операции и подтверждения

### Типы операций (Confirmation Types)

```python
class ConfirmationType:
    """Типы операций для подтверждения"""
    
    TRADE = 2          # Торговля (trade offer)
    MARKET = 3         # Маркетплейс (community market)
    LISTING = 6        # Выставление лота
    ACCOUNT = 7        # Операции с аккаунтом
    PROFILE_CHANGE = 11 # Изменение профиля
```

### Структура Operation

```python
@dataclass
class ConfirmationOperation:
    """Операция для подтверждения"""
    
    # Обязательные
    confirmation_id: str              # ID подтверждения
    confirmation_key: str             # Ключ подтверждения
    operation_type: int               # Тип (2=trade, 3=market и т.д.)
    
    # Метаданные
    timestamp: int                    # Unix timestamp
    received_at: int                  # Когда получено подтверждение
    
    # Информация об операции
    other_account_name: Optional[str] # Имя другого участника
    other_steam_id: Optional[int]    # Steam ID другого участника
    item_description: str             # Описание предмета/операции
    
    # Статус
    status: str                       # pending, confirmed, declined, expired
    expires_at: int                   # Когда истекает
```

### Класс для управления подтверждениями

```python
import requests
from datetime import datetime, timedelta

class ConfirmationManager:
    """Управление подтверждениями"""
    
    BASE_URL = 'https://steamcommunity.com/mobileconf'
    
    def __init__(self, account: Dict[str, Any]):
        self.account = account
        self.identity_secret = account['identity_secret']
        self.steam_id = account.get('steam_id')
    
    def _get_confirmations_url(self, tag: str = 'conf') -> str:
        """Создать URL для получения подтверждений"""
        server_time = int(time.time())
        
        # Генерировать хеш
        from app.steam_utils import SteamAPIAuth
        conf_hash = SteamAPIAuth.generate_confirmation_hash(
            self.identity_secret, tag
        )
        
        url = (
            f'{self.BASE_URL}/getlist'
            f'?p=0'
            f'&a={self.steam_id}'
            f'&k={conf_hash}'
            f'&t={server_time}'
            f'&m=react'
            f'&tag={tag}'
        )
        
        return url
    
    def fetch_confirmations(self) -> List[ConfirmationOperation]:
        """Получить список подтверждений"""
        try:
            url = self._get_confirmations_url('conf')
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
                'Accept': 'application/json'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            confirmations = []
            for conf in data.get('confirmations', []):
                operation = ConfirmationOperation(
                    confirmation_id=conf['id'],
                    confirmation_key=conf['key'],
                    operation_type=int(conf['type']),
                    timestamp=int(conf['creation_time']),
                    received_at=int(time.time()),
                    other_account_name=conf.get('creator_name', ''),
                    other_steam_id=conf.get('creator', None),
                    item_description=conf.get('multi', [{}])[0].get(
                        'description', ''
                    ) if conf.get('multi') else '',
                    status='pending',
                    expires_at=int(conf['creation_time']) + 86400 * 15
                )
                
                confirmations.append(operation)
            
            return confirmations
        
        except Exception as e:
            logger.error(f"Failed to fetch confirmations: {e}")
            return []
    
    def confirm_operation(self, confirmation_id: str,
                         confirmation_key: str) -> bool:
        """Подтвердить операцию"""
        try:
            server_time = int(time.time())
            
            from app.steam_utils import SteamAPIAuth
            allow_hash = SteamAPIAuth.generate_confirmation_hash(
                self.identity_secret, 'allow'
            )
            
            url = (
                f'{self.BASE_URL}/ajaxop'
                f'?op=allow'
                f'&p=0'
                f'&a={self.steam_id}'
                f'&k={allow_hash}'
                f'&t={server_time}'
                f'&m=react'
                f'&tag=allow'
            )
            
            data = {
                'confid': confirmation_id,
                'key': confirmation_key,
                'op': 'allow'
            }
            
            response = requests.post(url, data=data, timeout=10)
            return response.status_code == 200
        
        except Exception as e:
            logger.error(f"Failed to confirm: {e}")
            return False
    
    def cancel_operation(self, confirmation_id: str,
                        confirmation_key: str) -> bool:
        """Отклонить операцию"""
        try:
            server_time = int(time.time())
            
            from app.steam_utils import SteamAPIAuth
            cancel_hash = SteamAPIAuth.generate_confirmation_hash(
                self.identity_secret, 'cancel'
            )
            
            url = (
                f'{self.BASE_URL}/ajaxop'
                f'?op=cancel'
                f'?p=0'
                f'&a={self.steam_id}'
                f'&k={cancel_hash}'
                f'&t={server_time}'
                f'&m=react'
                f'&tag=cancel'
            )
            
            data = {
                'confid': confirmation_id,
                'key': confirmation_key,
                'op': 'cancel'
            }
            
            response = requests.post(url, data=data, timeout=10)
            return response.status_code == 200
        
        except Exception as e:
            logger.error(f"Failed to cancel: {e}")
            return False
```

---

## Загрузка и сохранение Manifest

### Сохранение Manifest

```python
def save_manifest(manifest: Dict, path: str):
    """Сохранить manifest с валидацией"""
    
    # Валидировать структуру
    required_fields = ['version', 'created_at', 'updated_at', 'accounts']
    for field in required_fields:
        if field not in manifest:
            raise ValueError(f"Missing required field: {field}")
    
    # Обновить timestamp
    manifest['updated_at'] = int(time.time())
    manifest['total_accounts'] = len(manifest['accounts'])
    
    # Сохранить
    with open(path, 'w') as f:
        json.dump(manifest, f, indent=2)
    
    # Установить права доступа
    os.chmod(path, 0o600)  # rw------- только для владельца
```

### Загрузка Manifest

```python
def load_manifest(path: str) -> Dict:
    """Загрузить manifest с валидацией"""
    
    try:
        with open(path, 'r') as f:
            manifest = json.load(f)
        
        # Валидировать версию
        if manifest.get('version', 1) != 1:
            raise ValueError("Unsupported manifest version")
        
        # Убедиться в наличии accounts
        if 'accounts' not in manifest:
            manifest['accounts'] = []
        
        return manifest
    
    except FileNotFoundError:
        # Вернуть пустой manifest
        return {
            'version': 1,
            'created_at': int(time.time()),
            'updated_at': int(time.time()),
            'total_accounts': 0,
            'accounts': []
        }
```

---

## 📌 Резюме

| Компонент | Назначение |
|-----------|-----------|
| **Manifest** | Метаданные всех mafiles |
| **Account Entry** | Информация об одном аккаунте |
| **ConfirmationManager** | Управление подтверждениями |
| **ConfirmationOperation** | Одна операция для подтверждения |
| **ManifestManager** | API для работы с manifest |

