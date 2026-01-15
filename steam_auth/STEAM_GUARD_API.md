# 🔐 Steam Guard API Reference

## 📌 Обзор

Модуль `app/steam_guard.py` предоставляет полный API для работы с Steam Guard и mafiles, совместимый с **Steam Desktop Authenticator (SDA)**.

**Версия**: 2.0 (обновлено с официальной реализацией)

## 🏗️ Архитектура

```
SteamGuardManager          MafileCreator
├─ create_mafile()        ├─ create_mafile_from_account()
├─ import_mafile()        ├─ import_and_add_account()
├─ get_steam_guard_code() ├─ get_2fa_code()
├─ get_confirmation_hash()├─ validate_mafile()
├─ confirm_operation()    ├─ list_mafiles()
└─ [internals]            └─ delete_mafile()
```

---

## 📚 SteamGuardManager - Основной класс

### Создание экземпляра

```python
from app.steam_guard import SteamGuardManager

manager = SteamGuardManager()
# Автоматически создает директорию mafiles/
```

### 1. `create_mafile_from_dict(account_data: Dict[str, Any]) -> str`

Создать mafile из словаря данных аккаунта.

**Параметры:**
```python
account_data = {
    'account_name': 'mysteamaccount',      # Обязательно
    'shared_secret': 'FhkMQfG2w3Z9...',   # Обязательно (Base64, 28 символов)
    'identity_secret': 'abcd1234...',     # Опционально (Base64, 44 символа)
    'revocation_code': 'R12345',          # Опционально
    'session_id': '...'                   # Опционально
}
```

**Возвращает:**
- Путь к созданному файлу mafile
- Пример: `/workspaces/CursorAI/steam_auth/mafiles/mysteamaccount.maFile`

**Структура созданного mafile (JSON):**
```json
{
  "shared_secret": "FhkMQfG2w3Z9nBvK7xL2mN4pQ6rS8tU1wV2xY3zA=",
  "account_name": "mysteamaccount",
  "identity_secret": "abcd1234XYZ9...",
  "revocation_code": "R12345",
  "uri": "",
  "server_time": 1705326000,
  "session_id": "",
  "token_gid": "",
  "fully_enrolled": true
}
```

**Пример использования:**
```python
from app.database import Database

db = Database()
account = db.get_account(1)

mafile_path = manager.create_mafile_from_dict(account)
print(f"Mafile создан: {mafile_path}")
```

**Ошибки:**
- `ValueError` - если отсутствуют обязательные поля

---

### 2. `import_mafile(mafile_path: str) -> Optional[Dict[str, Any]]`

Импортировать данные из существующего mafile.

**Параметры:**
- `mafile_path`: Полный путь к файлу mafile

**Возвращает:**
```python
{
    'account_name': 'mysteamaccount',
    'shared_secret': 'FhkMQfG2w3Z9...',
    'identity_secret': 'abcd1234...',
    'revocation_code': 'R12345'
}
```

**Пример:**
```python
mafile_data = manager.import_mafile('/path/to/account.maFile')

if mafile_data:
    print(f"Аккаунт: {mafile_data['account_name']}")
    print(f"Shared Secret: {mafile_data['shared_secret'][:20]}...")
else:
    print("Ошибка при импорте")
```

---

### 3. `get_steam_guard_code(shared_secret: str, timestamp: Optional[int] = None) -> tuple`

Получить 2FA код используя TOTP алгоритм.

**Алгоритм (7 этапов):**
```
1. Base64 decode shared_secret → 20 байт
2. time_counter = текущее_время // 30
3. time_bytes = big-endian преобразование (8 байт)
4. hmac_hash = HMAC-SHA1(shared_secret, time_bytes)
5. index = последние 4 бита последнего байта hmac_hash
6. code = hmac_hash[index:index+4] % 100000
7. Результат: 5-значный код
```

**Параметры:**
- `shared_secret`: Base64-encoded shared secret (28 символов = 20 байт)
- `timestamp`: Unix timestamp (опционально, по умолчанию текущее время)

**Возвращает:**
```python
(code, time_remaining)
# Пример: ("12345", 15)  # Код действителен 15 секунд
```

**Пример:**
```python
code, time_left = manager.get_steam_guard_code('FhkMQfG2w3Z9nBvK7xL2mN4pQ6rS8tU1wV2xY3zA=')
print(f"Код: {code}")
print(f"Действителен еще {time_left} сек")
# Вывод:
# Код: 12345
# Действителен еще 18 сек
```

**Проверка кодов разных времен:**
```python
import time

now = int(time.time())

# Текущий код
code_now, _ = manager.get_steam_guard_code(shared_secret, now)

# Следующий код (через 30 сек)
code_next, _ = manager.get_steam_guard_code(shared_secret, now + 30)

# Коды должны быть разные
assert code_now != code_next
```

---

### 4. `get_steam_guard_code_only(shared_secret: str) -> str`

Быстрый метод для получения только кода (без времени).

**Пример:**
```python
code = manager.get_steam_guard_code_only(shared_secret)
print(code)  # "12345"
```

---

### 5. `get_confirmation_hash(timestamp: int, identity_secret: str, tag: str = "conf") -> str`

Получить хеш для подтверждения операции на Steam.

**Параметры:**
- `timestamp`: Unix timestamp подтверждения
- `identity_secret`: Base64-encoded identity secret (44 символа = 32 байта)
- `tag`: Тип операции ("conf", "details", "allow", "cancel")

**Возвращает:**
- Base64-encoded confirmation hash

**Алгоритм:**
```
1. Base64 decode identity_secret → 32 байта
2. message = timestamp + tag (как строки)
3. hash = HMAC-SHA1(identity_secret, message)
4. результат = Base64 encode(hash)
```

**Пример использования:**
```python
import time

timestamp = int(time.time())
identity_secret = "abcd1234XYZ9..."

# Получить хеш для просмотра деталей
hash_conf = manager.get_confirmation_hash(timestamp, identity_secret, "details")
print(f"Hash для деталей: {hash_conf}")

# Хеш для подтверждения
hash_allow = manager.get_confirmation_hash(timestamp, identity_secret, "allow")
print(f"Hash для подтверждения: {hash_allow}")

# Хеш для отклонения
hash_cancel = manager.get_confirmation_hash(timestamp, identity_secret, "cancel")
print(f"Hash для отклонения: {hash_cancel}")
```

---

### 6. `get_confirmation_operations(identity_secret, shared_secret, access_token=None) -> List[Dict]`

Получить список операций, ожидающих подтверждения.

**Возвращает:**
```python
[
    {
        'id': '1',
        'type': 'trade',                    # trade, market_sell, account_recovery
        'description': 'Обмен предметов',
        'timestamp': 1705326000,
        'status': 'pending',
        'has_confirmation': True
    },
    # ... другие операции
]
```

**Примечание:**
В реальном приложении это делается через Steam API:
```
GET https://steamcommunity.com/mobileconf/getlist?
    p=android&
    a={steamid}&
    k={time}&
    t={tag}&
    m=react&
    tag=conf
```

---

### 7. `confirm_operation(operation_id: str, identity_secret: str, shared_secret: str, confirm: bool) -> bool`

Подтвердить или отклонить операцию.

**Параметры:**
- `operation_id`: ID операции из списка операций
- `identity_secret`: Identity secret
- `shared_secret`: Shared secret
- `confirm`: `True` для подтверждения, `False` для отклонения

**Возвращает:**
- `True` - если успешно
- `False` - если ошибка

**Пример:**
```python
# Подтвердить операцию
success = manager.confirm_operation('123456', identity_secret, shared_secret, confirm=True)
if success:
    print("Операция подтверждена")
else:
    print("Ошибка при подтверждении")

# Отклонить операцию
success = manager.confirm_operation('123456', identity_secret, shared_secret, confirm=False)
```

---

## 🔨 MafileCreator - Высокоуровневый API

Удобный класс для работы с mafiles в контексте приложения.

### Инициализация

```python
from app.steam_guard import MafileCreator
from app.database import Database

db = Database()
creator = MafileCreator(db)
```

### 1. `create_mafile_from_account(account_id: int) -> str`

Создать mafile из данных аккаунта в БД.

**Пример:**
```python
try:
    mafile_path = creator.create_mafile_from_account(1)
    print(f"Mafile создан: {mafile_path}")
except ValueError as e:
    print(f"Ошибка: {e}")
```

---

### 2. `import_and_add_account(mafile_path: str, password: str) -> int`

Импортировать mafile и добавить аккаунт в БД в одном шаге.

**Пример:**
```python
try:
    account_id = creator.import_and_add_account(
        '/path/to/account.maFile',
        'mypassword123'
    )
    print(f"Аккаунт добавлен с ID: {account_id}")
except ValueError as e:
    print(f"Ошибка: {e}")
```

---

### 3. `get_2fa_code(account_id: int) -> tuple`

Получить текущий 2FA код для аккаунта.

**Пример:**
```python
try:
    code, time_left = creator.get_2fa_code(1)
    print(f"Код: {code} (действителен {time_left} сек)")
except ValueError as e:
    print(f"Ошибка: {e}")
```

---

### 4. `validate_mafile(mafile_path: str) -> bool`

Проверить корректность структуры mafile.

**Проверяет:**
- ✓ Файл существует и читаемый
- ✓ JSON валиден
- ✓ Присутствуют обязательные поля (shared_secret, account_name)
- ✓ shared_secret в формате Base64, 28 символов (20 байт)
- ✓ identity_secret если присутствует: 44 символа (32 байта)

**Пример:**
```python
try:
    is_valid = creator.validate_mafile('/path/to/account.maFile')
    if is_valid:
        print("Mafile валиден")
except ValueError as e:
    print(f"Ошибка: {e}")
    # "Shared secret должен быть 20 байт, получено 19"
    # "Обязательное поле отсутствует: shared_secret"
```

---

### 5. `list_mafiles() -> List[Dict]`

Получить список всех mafiles в приложении.

**Возвращает:**
```python
[
    {
        'filename': 'myaccount.maFile',
        'path': '/path/to/myaccount.maFile',
        'account_name': 'myaccount',
        'has_identity_secret': True,
        'has_revocation_code': True,
        'timestamp': 1705326000.5
    },
    # ... другие mafiles
]
```

**Пример:**
```python
mafiles = creator.list_mafiles()
for mf in mafiles:
    print(f"- {mf['account_name']} ({mf['filename']})")
    if mf['has_identity_secret']:
        print("  ✓ Identity Secret присутствует")
```

---

### 6. `delete_mafile(account_name: str) -> bool`

Удалить mafile аккаунта.

**Пример:**
```python
try:
    deleted = creator.delete_mafile('mysteamaccount')
    if deleted:
        print("Mafile удален")
    else:
        print("Mafile не найден")
except ValueError as e:
    print(f"Ошибка: {e}")
```

---

## 📁 Структура Mafile

### Обязательные поля

| Поле | Тип | Размер | Описание |
|------|-----|--------|---------|
| `shared_secret` | String (Base64) | 28 символов (20 байт) | Для генерирования TOTP кодов |
| `account_name` | String | - | Имя Steam аккаунта |

### Опциональные поля

| Поле | Тип | Размер | Описание |
|------|-----|--------|---------|
| `identity_secret` | String (Base64) | 44 символа (32 байта) | Для подтверждения операций |
| `revocation_code` | String | 5-10 символов | Код для отключения 2FA |
| `session_id` | String | - | ID сессии Steam |
| `uri` | String | - | URI для provisioning |
| `token_gid` | String | - | GID токена |
| `server_time` | Integer | - | Timestamp создания |
| `fully_enrolled` | Boolean | - | Статус регистрации в Steam |

---

## 🧪 Примеры использования

### Пример 1: Получение 2FA кода в реальном времени

```python
from app.steam_guard import SteamGuardManager
import time

manager = SteamGuardManager()
shared_secret = 'FhkMQfG2w3Z9nBvK7xL2mN4pQ6rS8tU1wV2xY3zA='

while True:
    code, time_left = manager.get_steam_guard_code(shared_secret)
    print(f"[{time.strftime('%H:%M:%S')}] Код: {code} ({time_left}s)")
    
    if time_left < 5:  # Обновить перед переходом
        time.sleep(2)
    else:
        time.sleep(1)
```

### Пример 2: Импорт нескольких mafiles

```python
from app.steam_guard import MafileCreator
from app.database import Database
import os

db = Database()
creator = MafileCreator(db)

mafiles_folder = '/path/to/mafiles'
password = 'default_password'

for filename in os.listdir(mafiles_folder):
    if filename.endswith('.maFile'):
        mafile_path = os.path.join(mafiles_folder, filename)
        try:
            account_id = creator.import_and_add_account(mafile_path, password)
            print(f"✓ {filename} импортирован (ID: {account_id})")
        except Exception as e:
            print(f"✗ {filename}: {e}")
```

### Пример 3: Получение кодов для всех аккаунтов

```python
from app.steam_guard import MafileCreator
from app.database import Database

db = Database()
creator = MafileCreator(db)

accounts = db.get_all_accounts()
for account in accounts:
    try:
        code, time_left = creator.get_2fa_code(account['id'])
        print(f"{account['account_name']:20} | {code} ({time_left:2}s)")
    except Exception as e:
        print(f"{account['account_name']:20} | ОШИБКА: {e}")
```

---

## ⚠️ Частые ошибки и их решение

### Ошибка 1: "Shared secret должен быть 20 байт"

**Причина:** Неверный формат shared_secret

**Решение:**
```python
import base64

# Неверно (не Base64)
shared_secret = "abcd1234"

# Верно (Base64, 28 символов)
secret_bytes = b'12345678901234567890'  # 20 байт
shared_secret = base64.b64encode(secret_bytes).decode('utf-8')
# Результат: "MTIzNDU2Nzg5MDEyMzQ1Njc4OTA="
```

### Ошибка 2: "Обязательное поле отсутствует"

**Причина:** Неполная структура mafile

**Решение:**
```python
# Минимальная корректная структура
mafile = {
    "shared_secret": "MTIzNDU2Nzg5MDEyMzQ1Njc4OTA=",
    "account_name": "mysteamaccount"
}

# Полная структура
mafile = {
    "shared_secret": "MTIzNDU2Nzg5MDEyMzQ1Njc4OTA=",
    "account_name": "mysteamaccount",
    "identity_secret": "abcd1234...",  # 44 символа
    "revocation_code": "R12345",
    "uri": "",
    "server_time": 1705326000,
    "session_id": "",
    "token_gid": "",
    "fully_enrolled": True
}
```

### Ошибка 3: Неверный 2FA код

**Причина:** Неправильный shared_secret или time sync

**Решение:**
```python
# Проверить что shared_secret валиден
try:
    code, time_left = manager.get_steam_guard_code(shared_secret)
    print(f"Код: {code}")  # Должен быть 5 цифр
except ValueError as e:
    print(f"Ошибка: {e}")

# Убедиться что время синхронизировано
import time
print(f"Текущее время: {int(time.time())}")
print(f"Время на сервере Steam: {int(time.time())}")  # Должны быть близки
```

---

## 📖 Дополнительные ресурсы

- [STEAM_AUTH_GUIDE.md](STEAM_AUTH_GUIDE.md) - Руководство по многошаговой аутентификации
- [README.md](README.md) - Основная документация приложения
- [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md) - Руководство разработчика
- [GitHub: Jessecar96/SteamGuard](https://github.com/Jessecar96/SteamGuard) - Оригинальная реализация

---

## 🔄 История изменений

### v2.0 (текущая версия)
- ✅ Полная переделка на основе официальной реализации
- ✅ Правильный TOTP алгоритм (7 этапов)
- ✅ Поддержка confirmation hash
- ✅ Расширенная валидация mafile
- ✅ Методы для работы со списками операций
- ✅ Улучшенная обработка ошибок

### v1.0 (старая версия)
- Базовая поддержка mafile
- Простая генерирование кодов
- Минимальная функциональность

---

## 📞 Поддержка

Если у вас возникнут проблемы:

1. Проверьте [FAQ в README.md](README.md#FAQ)
2. Посмотрите [примеры в example.py](example.py)
3. Запустите [тесты в tests.py](tests.py)
4. Изучите исходный код в [app/steam_guard.py](app/steam_guard.py)
