# 📋 Структура SteamGuard Mafile - Полное руководство

## 📚 Оглавление

1. [Структура JSON](#структура-json)
2. [Обязательные и опциональные поля](#обязательные-и-опциональные-поля)
3. [Генерация Secrets](#генерация-secrets)
4. [Классы и методы](#классы-и-методы)
5. [Загрузка и сохранение](#загрузка-и-сохранение)
6. [2FA генерация (TOTP)](#2fa-генерация-totp)
7. [Подтверждение операций](#подтверждение-операций)
8. [Примеры кода](#примеры-кода)

---

## Структура JSON

### Полная структура mafile

```json
{
  "shared_secret": "base64_encoded_string",
  "identity_secret": "base64_encoded_string",
  "revocation_code": "XXXXX-XXXXX-XXXXX",
  "account_name": "steamusername",
  "uri": "steam://account/username",
  "server_time": 1234567890,
  "account_name_hmac": "base64_hmac_hash",
  "session_id": "session_identifier",
  "fully_enrolled": true
}
```

### Минимальная валидная структура

Для работы **абсолютно необходимы только**:
```json
{
  "shared_secret": "base64_encoded_string",
  "account_name": "steamusername"
}
```

---

## Обязательные и опциональные поля

### ✅ ОБЯЗАТЕЛЬНЫЕ ПОЛЯ (Required)

| Поле | Тип | Описание | Пример |
|------|-----|---------|--------|
| `shared_secret` | string (base64) | Секретный ключ для генерации 2FA кодов. **КРИТИЧЕСКИ ВАЖНО!** Хранится в base64 формате | `FhkMQfG2w3Z...` (20 байт, закодированных base64) |
| `account_name` | string | Имя Steam аккаунта (как вводится при входе в Steam) | `"mysteamaccount"` |

### ⚙️ ОПЦИОНАЛЬНЫЕ ПОЛЯ (Optional)

| Поле | Тип | Описание | Примечание |
|------|-----|---------|-----------|
| `identity_secret` | string (base64) | Используется для подтверждения торговли и рыночных операций. Если пусто - подтверждения не будут работать | `6 months of trade confirmations` |
| `revocation_code` | string | Резервный код для отключения 2FA если потеряли доступ. Формат: `XXXXX-XXXXX-XXXXX` | `"A1B2C-D3E4F-G5H6I"` |
| `uri` | string | URI для импорта (совместимость). Обычно пусто или `steam://account/{username}` | `""` |
| `server_time` | integer (timestamp) | Время последнего сохранения mafile (Unix timestamp) | `1705330800` |
| `account_name_hmac` | string (base64) | HMAC хеш имени аккаунта (для проверки целостности) | `""` или хеш |
| `session_id` | string | ID сессии (для мобильного приложения) | `""` или session ID |
| `fully_enrolled` | boolean | Флаг полной регистрации в Steam Guard | `true` |

---

## Генерация Secrets

### 📌 Как генерируются secrets в коде

```python
import os
import base64

# Генерирование shared_secret (20 байт)
shared_secret_bytes = os.urandom(20)
shared_secret = base64.b64encode(shared_secret_bytes).decode('utf-8')

# Генерирование identity_secret (20 байт)
identity_secret_bytes = os.urandom(20)
identity_secret = base64.b64encode(identity_secret_bytes).decode('utf-8')

# Результат (примеры):
# shared_secret: "FhkMQfG2w3Z9nBvK7xL2mN4pQ6rS8tU..." (27-28 символов)
# identity_secret: "AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPp..." (27-28 символов)
```

### 🔐 Особенности секретов

1. **shared_secret** - обязательный ключ
   - Длина: 20 байт (до кодирования)
   - Кодирование: Base64
   - Использование: HMAC-SHA1 для генерации 2FA кодов
   - Формула: `HMAC-SHA1(shared_secret, time_counter)`

2. **identity_secret** - для операций
   - Длина: 20 байт (до кодирования)
   - Кодирование: Base64
   - Использование: Генерация хешей для подтверждений
   - Формула: `HMAC-SHA1(identity_secret, time_counter + tag)`

### Генерирование revocation_code

```python
import random
import string

chars = string.ascii_uppercase + string.digits

# Формат: XXXXX-XXXXX-XXXXX (5-3-5 символов)
code = '-'.join(
    ''.join(random.choice(chars) for _ in range(5))
    for _ in range(3)
)

# Пример результата: "A1B2C-D3E4F-G5H6I"
```

---

## Классы и методы

### 1️⃣ SteamGuardManager

```python
class SteamGuardManager:
    """Менеджер для работы с Steam Guard и mafiles"""
    
    MAFILES_DIR = "mafiles"  # Директория хранения
    
    def create_mafile_from_dict(self, account_data: Dict[str, Any]) -> str:
        """
        Создает и сохраняет mafile из словаря
        
        Параметры:
            account_data: Словарь с ключами:
                - shared_secret (обязателен)
                - identity_secret (опционально)
                - revocation_code (опционально)
                - account_name (обязателен)
        
        Возвращает:
            Путь к сохраненному mafile
        """
        # Создает файл: {MAFILES_DIR}/{account_name}.maFile
        # Возвращает: /path/to/mafiles/myaccount.maFile
```

### 2️⃣ SteamGuardUtil

```python
class SteamGuardUtil:
    """Утилиты для работы с Steam Guard TOTP"""
    
    @staticmethod
    def generate_totp(shared_secret: str, time_offset: int = 0) -> str:
        """
        Генерирует TOTP код (5 цифр) из shared secret
        
        Алгоритм:
        1. Декодировать shared_secret из Base64
        2. Получить текущее время в 30-секундных интервалах
        3. Вычислить HMAC-SHA1(secret, time_counter)
        4. Взять последние 4 байта и преобразовать в число
        5. Модуль 100000 для получения 5 цифр
        
        Возвращает:
            "12345" - 5-значный код
        """
    
    @staticmethod
    def get_code_time_remaining() -> int:
        """Получить количество секунд до смены кода (максимум 30)"""
```

### 3️⃣ SteamAuthenticator

```python
class SteamAuthenticator:
    """Аутентификатор для создания mafile (SDA-подобный)"""
    
    def login(self, account_name: str, password: str) -> Tuple[bool, str]:
        """Попытка входа"""
    
    def send_code(self) -> Tuple[bool, str]:
        """Отправить код подтверждения на email/SMS"""
    
    def confirm_code(self, code: str) -> Tuple[bool, str]:
        """Подтвердить код и создать mafile"""
    
    def _generate_secrets(self):
        """Автоматически генерирует все secrets"""
    
    def get_mafile_data(self) -> Optional[Dict]:
        """Получить готовый словарь для mafile"""
```

### 4️⃣ MafileValidator

```python
class MafileValidator:
    """Валидация структуры mafile"""
    
    REQUIRED_FIELDS = ['shared_secret', 'account_name']
    OPTIONAL_FIELDS = ['identity_secret', 'revocation_code', ...]
    
    @classmethod
    def validate_mafile(cls, mafile_data: Dict) -> bool:
        """
        Проверяет структуру mafile
        
        Проверки:
        - Наличие обязательных полей
        - Валидность Base64 кодирования secrets
        """
```

### 5️⃣ SteamAPIAuth

```python
class SteamAPIAuth:
    """Работа с Steam API для подтверждений"""
    
    @staticmethod
    def generate_confirmation_hash(identity_secret: str, tag: str = 'conf') -> str:
        """
        Генерирует хеш для запроса подтверждений
        
        Алгоритм:
        1. Декодировать identity_secret
        2. Получить текущее время: time_counter = server_time // 30
        3. Комбинировать: data = time_bytes + tag_bytes
        4. Вычислить: HMAC-SHA1(identity_secret, data)
        5. Закодировать результат в Base64
        
        Теги:
        - 'conf' - для получения списка подтверждений
        - 'details' - для получения деталей
        - 'allow' - для подтверждения
        - 'cancel' - для отклонения
        """
```

---

## Загрузка и сохранение

### Сохранение mafile

```python
from app.steam_guard import SteamGuardManager

manager = SteamGuardManager()

account_data = {
    'shared_secret': 'FhkMQfG2w3Z9nBvK7xL2mN4pQ6rS8tU...',
    'identity_secret': 'AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPp...',
    'revocation_code': 'A1B2C-D3E4F-G5H6I',
    'account_name': 'mysteamaccount'
}

mafile_path = manager.create_mafile_from_dict(account_data)
# Результат: 'mafiles/mysteamaccount.maFile'
```

### Структура сохраняемого файла

```
mafiles/
├── mysteamaccount.maFile
├── anotheraccount.maFile
└── ...
```

**Внутри mysteamaccount.maFile:**
```json
{
  "shared_secret": "FhkMQfG2w3Z9nBvK7xL2mN4pQ6rS8tU...",
  "identity_secret": "AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPp...",
  "revocation_code": "A1B2C-D3E4F-G5H6I",
  "account_name": "mysteamaccount",
  "uri": "",
  "server_time": 1705330800,
  "account_name_hmac": "",
  "session_id": "",
  "fully_enrolled": true
}
```

### Загрузка mafile

```python
mafile_data = manager.import_mafile('mafiles/mysteamaccount.maFile')

# Возвращает:
# {
#     'account_name': 'mysteamaccount',
#     'shared_secret': 'FhkMQfG2w3Z9...',
#     'identity_secret': 'AaBbCc...',
#     'revocation_code': 'A1B2C-...'
# }
```

---

## 2FA генерация (TOTP)

### Алгоритм TOTP (Time-based One-Time Password)

```python
import hmac
import hashlib
import struct
import base64
import time

def generate_steam_guard_code(shared_secret: str) -> str:
    """
    Генерирует Steam Guard код
    
    Этапы:
    1. Декодировать shared_secret из Base64
    2. Получить текущее время в 30-секундных интервалах
    3. Вычислить HMAC-SHA1
    4. Преобразовать в 5-значный код
    """
    
    # Шаг 1: Декодировать secret
    secret_bytes = base64.b64decode(shared_secret)
    
    # Шаг 2: Получить time counter
    server_time = int(time.time())
    time_counter = server_time // 30
    time_bytes = struct.pack('>Q', time_counter)  # Big-endian, 8 байт
    
    # Шаг 3: HMAC-SHA1
    hmac_hash = hmac.new(secret_bytes, time_bytes, hashlib.sha1).digest()
    
    # Шаг 4: Преобразование
    last_byte = hmac_hash[-1] & 0x0f  # Получить индекс из последних 4 бит
    four_bytes = struct.unpack('>I', hmac_hash[last_byte:last_byte + 4])[0]
    
    # Шаг 5: Модуль 100000
    code = str(four_bytes % 100000).zfill(5)
    
    return code

# Пример использования:
code = generate_steam_guard_code("FhkMQfG2w3Z9nBvK7xL2mN4pQ6rS8tU...")
print(code)  # "12345"
```

### Временные интервалы

```
Время        | Time Counter | Код
-------------|--------------|-------
00:00-00:29  | counter=0    | код A
00:30-00:59  | counter=1    | код B
01:00-01:29  | counter=2    | код C
...
30 сек = новый код
```

### Текущий оставшийся время кода

```python
remaining_seconds = 30 - (int(time.time()) % 30)
# Возвращает: количество секунд до смены кода (1-30)
```

---

## Подтверждение операций

### Процесс подтверждения

```
1. Пользователь видит операцию (торговля, маркетплейс)
   ↓
2. Система генерирует confirmation_hash используя identity_secret
   ↓
3. Система отправляет запрос на Steam с хешом
   ↓
4. Steam подтверждает операцию
```

### Генерирование хеша подтверждения

```python
from app.steam_utils import SteamAPIAuth

# Генерировать хеш для списка подтверждений
conf_hash = SteamAPIAuth.generate_confirmation_hash(
    identity_secret="AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPp...",
    tag='conf'  # или 'details', 'allow', 'cancel'
)

# Создать URL для запроса
url = SteamAPIAuth.get_confirmations_url(
    steam_id=76561198123456789,
    identity_secret="AaBbCc...",
    access_token="token123"
)
```

### Структура URL подтверждения

```
Base URL: https://steamcommunity.com/mobileconf/getlist

Параметры:
- p=0                      # Страница (всегда 0)
- a={steam_id}            # 64-bit Steam ID
- k={confirmation_hash}    # Хеш для подтверждения
- t={server_time}         # Текущее время
- m=react                 # Мобильный клиент
- tag=conf                # Тег (conf/details/allow/cancel)

Полный URL:
https://steamcommunity.com/mobileconf/getlist?p=0&a=76561198123456789&k=XXXXXX&t=1705330800&m=react&tag=conf
```

### Типы операций для подтверждения

```python
operations = [
    {
        'id': '123456',
        'type': 'trade',           # Торговля
        'description': 'Trade offer from user',
        'timestamp': 1705330800,
        'status': 'pending'
    },
    {
        'id': '123457',
        'type': 'market',          # Маркетплейс
        'description': 'Sell item for 100 ₽',
        'timestamp': 1705330801,
        'status': 'pending'
    },
    {
        'id': '123458',
        'type': 'listing',         # Выставление лота
        'description': 'List item for sale',
        'timestamp': 1705330802,
        'status': 'pending'
    }
]
```

---

## Примеры кода

### Пример 1: Полный процесс создания mafile

```python
from app.steam_auth import get_authenticator
from app.steam_guard import SteamGuardManager
from app.database import Database

# Шаг 1: Аутентификация
auth = get_authenticator()
success, msg = auth.login("mysteamaccount", "mypassword123")

if not success and "code_needed" in msg:
    auth.send_code()
    code = input("Enter confirmation code: ")
    success, msg = auth.confirm_code(code)

# Шаг 2: Получить данные mafile
if success:
    mafile_data = auth.get_mafile_data()
    
    # Шаг 3: Создать и сохранить mafile
    manager = SteamGuardManager()
    mafile_path = manager.create_mafile_from_dict(mafile_data)
    
    # Шаг 4: Добавить в БД
    db = Database()
    account_id = db.add_account(
        account_name=mafile_data['account_name'],
        password="mypassword123",
        shared_secret=mafile_data['shared_secret'],
        identity_secret=mafile_data.get('identity_secret'),
        revocation_code=mafile_data.get('revocation_code')
    )
    
    print(f"✓ Mafile создан и сохранен")
    print(f"  Path: {mafile_path}")
    print(f"  Account ID: {account_id}")
else:
    print(f"✗ Ошибка: {msg}")

auth.reset()  # Очистить состояние
```

### Пример 2: Генерирование 2FA кода

```python
from app.steam_utils import SteamGuardUtil
import time

account = db.get_account_by_name("mysteamaccount")

# Получить текущий код
code = SteamGuardUtil.generate_steam_guard_code(account['shared_secret'])
remaining = SteamGuardUtil.get_code_time_remaining()

print(f"Текущий код: {code}")
print(f"Осталось: {remaining} секунд")

# Через 5 секунд
time.sleep(5)
remaining = SteamGuardUtil.get_code_time_remaining()
print(f"Осталось: {remaining} секунд")

# Новый код будет через {remaining} секунд
```

### Пример 3: Импорт существующего mafile

```python
from app.steam_guard import SteamGuardManager
from app.database import Database

manager = SteamGuardManager()
db = Database()

# Импортировать mafile
mafile_data = manager.import_mafile('path/to/mysteamaccount.maFile')

if mafile_data:
    # Добавить в БД
    account_id = db.add_account(
        account_name=mafile_data['account_name'],
        password="password123",
        shared_secret=mafile_data['shared_secret'],
        identity_secret=mafile_data.get('identity_secret'),
        revocation_code=mafile_data.get('revocation_code')
    )
    
    print(f"✓ Mafile импортирован")
else:
    print("✗ Ошибка при импорте")
```

### Пример 4: Валидация mafile

```python
from app.steam_utils import MafileValidator
import json

with open('mafiles/myaccount.maFile', 'r') as f:
    mafile_data = json.load(f)

if MafileValidator.validate_mafile(mafile_data):
    print("✓ Mafile валидный")
else:
    print("✗ Mafile поврежден или неполный")
```

### Пример 5: Подтверждение операций

```python
from app.steam_utils import SteamAPIAuth
from app.steam_guard import SteamGuardManager

account = db.get_account_by_name("mysteamaccount")
manager = SteamGuardManager()

# Получить список подтверждений
confirmations = manager.get_confirmation_operations(
    identity_secret=account['identity_secret'],
    shared_secret=account['shared_secret']
)

print("Ожидающие операции:")
for conf in confirmations:
    print(f"  - {conf['type']}: {conf['description']}")

# Подтвердить операцию
operation_id = confirmations[0]['id']
result = manager.confirm_operation(
    operation_id=operation_id,
    identity_secret=account['identity_secret'],
    shared_secret=account['shared_secret'],
    confirm=True  # True - подтвердить, False - отклонить
)

print(f"Результат: {'✓' if result else '✗'}")
```

---

## 🔐 Безопасность

### ⚠️ Критичные моменты

1. **Никогда не хранить in plaintext**
   - Шифровать shared_secret и identity_secret перед сохранением
   - Использовать encryption.py модуль

2. **Защита от брутфорса**
   - Ограничить попытки входа
   - Добавить задержку после неудачных попыток

3. **Revocation code**
   - Хранить отдельно от других данных
   - Показывать пользователю только один раз при создании

4. **Логирование**
   - Не логировать shared_secret, identity_secret, пароли
   - Логировать только события и ошибки

### 🛡️ Рекомендации

```python
# НЕПРАВИЛЬНО ❌
print(f"Shared secret: {shared_secret}")

# ПРАВИЛЬНО ✓
print(f"Shared secret: {shared_secret[:8]}...")
logger.info(f"Account {account_name} created")
```

---

## 📌 Резюме

| Компонент | Описание |
|-----------|---------|
| **shared_secret** | Главный ключ для 2FA (HMAC-SHA1, Base64) |
| **identity_secret** | Ключ для подтверждений операций (HMAC-SHA1, Base64) |
| **revocation_code** | Резервный отключение 2FA (формат: XXXXX-XXXXX-XXXXX) |
| **TOTP Algorithm** | 30-секундные интервалы, HMAC-SHA1, 5 цифр |
| **Confirmation Hash** | HMAC-SHA1(identity_secret, time + tag), Base64 |
| **maFile Format** | JSON с обязательными shared_secret и account_name |

