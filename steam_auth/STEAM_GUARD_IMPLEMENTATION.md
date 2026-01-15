# Steam Guard & MaFile Реализация - Документация

## Обзор

Реализована полная система управления Steam 2FA (Steam Guard) и mafiles, совместимая со **Steam Desktop Authenticator (SDA)** и использующая лучшие практики из:
- **SteamDesktopAuthenticator** (GitHub: Jessecar96/SteamDesktopAuthenticator) - оригинальная C# реализация
- **steamguard** (PyPI: https://pypi.org/project/steamguard/) - Python библиотека для работы с Steam Guard
- **steampy** - Python Steam Web API клиент

## Архитектура

### 1. **FileEncryptor** - Шифрование mafiles

```python
# Алгоритм шифрования (совместимо с SDA):
- PBKDF2-SHA512: 50,000 итераций
- AES-256-CBC (OpenSSL совместимо)
- Random Salt: 8 байт
- Random IV: 16 байт
```

**Методы:**
- `get_random_salt()` - генерировать случайный salt
- `get_random_iv()` - генерировать случайный IV
- `derive_key(password, salt)` - вывести ключ шифрования
- `encrypt_data(password, salt, iv, data)` - зашифровать данные
- `decrypt_data(password, salt, iv, encrypted_data)` - расшифровать данные

### 2. **ManifestEntry** - Запись в manifest

Структура записи о mafile:
```json
{
    "filename": "123456789.maFile",
    "steamid": "123456789",
    "encryption_salt": "...",
    "encryption_iv": "..."
}
```

### 3. **Manifest** - Управление всеми mafiles

Аналог `Manifest.cs` из SDA. Управляет файлом `manifest.json`:

```json
{
    "encrypted": false,
    "entries": [
        {
            "filename": "123456789.maFile",
            "steamid": "123456789",
            "encryption_salt": null,
            "encryption_iv": null
        }
    ]
}
```

**Основные операции:**
- `load_or_create()` - загрузить или создать новый manifest
- `add_entry(filename, steam_id, salt, iv)` - добавить запись
- `remove_entry(steam_id)` - удалить запись
- `get_entry(steam_id)` - получить запись по steam_id
- `save()` - сохранить manifest

### 4. **SteamGuardManager** - Основной менеджер

#### 4.1 Добавление нового аккаунта (Add Account Flow)

Процесс основан на `LoginForm.cs` и `AuthenticatorLinker.cs` из SDA:

```python
account_data = guard.add_account_with_login(
    username="steamuser",
    password="password123",
    phone_number="+1234567890"
)
```

**Процесс:**
1. **Steam Login** (`_simulate_steam_login`)
   - Отправить username + password на Steam Web API
   - Получить session_id, token_gid, web_cookie
   - Обработать 2FA коды (device_code, email_code)

2. **Add Authenticator** (`_simulate_add_authenticator`)
   - Вызвать IPhoneService/AddAuthenticator
   - Получить shared_secret (20 байт base64)
   - Получить revocation_code ('R' + 5 символов)
   - Отправить номер телефона (PhoneInputForm)
   - Подтвердить SMS код (SMSCodeForm)

3. **Create MaFile** (`_create_mafile`)
   - Создать JSON структуру с критическими полями
   - Сохранить в `mafiles/{steam_id}.maFile`
   - Добавить запись в manifest.json

#### 4.2 MaFile Структура

```json
{
    "shared_secret": "ABC...XYZ=",          // 20 байт base64 для 2FA
    "account_name": "steamuser",             // Имя аккаунта
    "identity_secret": "DEF...UVW=",        // 32 байта base64 для подтверждений
    "revocation_code": "R12345",             // Код восстановления доступа
    "session_id": "...",                     // Cookie для веб-запросов
    "token_gid": "_...",                     // GID токена сессии
    "web_cookie": "...",                     // Дополнительный cookie
    "fully_enrolled": true,                  // Флаг полной регистрации
    "server_time": 1234567890,              // Время синхронизации
    "steam_id": "123456789"                 // ID аккаунта
}
```

#### 4.3 Генерация Steam Guard 2FA кодов

Алгоритм **RFC 6238 TOTP** (как в оригинальной Steam 2FA):

```python
code, time_remaining = guard.get_steam_guard_code(shared_secret)
# Возвращает: ('23456789BC', 15)  # код и секунды до смены
```

**Реализация:**
1. Декодировать shared_secret из base64 → 20 байт
2. Вычислить time_counter = floor(текущее_время / 30)
3. Упаковать time_counter в 8 байт (big-endian)
4. HMAC-SHA1(shared_secret, time_bytes)
5. Dynamic truncation: индекс из последних 4 бит HMAC
6. Извлечь 4 байта из позиции индекса
7. Преобразовать в 5 символов из base-23 алфавита
   - Алфавит: "23456789BCDFGHJKMNPQRTVWXY" (без конфузных символов)

**Особенность Steam:** Коды используют специальный алфавит вместо стандартных цифр!

#### 4.4 Импорт MaFile

```python
# Обычный mafile
mafile_data = guard.import_mafile("path/to/account.maFile")

# Зашифрованный mafile
mafile_data = guard.import_mafile(
    "path/to/encrypted.maFile",
    password="mypassword"
)

# Регистрировать в manifest
guard.import_and_register_mafile("path/to/account.maFile")
```

#### 4.5 Шифрование MaFile

```python
# Зашифровать mafile
guard.encrypt_mafile(steam_id="123456789", password="mykey")

# Расшифровать mafile
mafile_data = guard.decrypt_mafile(steam_id="123456789", password="mykey")
```

#### 4.6 Получение Confirmation Keys

Для подтверждения операций (trades, market):

```python
# Для просмотра подтверждений
conf_key = guard.get_confirmation_key(identity_secret, tag="conf")

# Для подтверждения
allow_key = guard.get_confirmation_key(identity_secret, tag="allow")

# Для отклонения
deny_key = guard.get_confirmation_key(identity_secret, tag="deny")
```

**Алгоритм:**
- HMAC-SHA1(identity_secret, timestamp + tag)
- Результат в base64

#### 4.7 Управление аккаунтами

```python
# Получить все аккаунты
accounts = guard.get_all_accounts()
# [{'account_name': 'user1', 'steam_id': '123', 'is_encrypted': False}, ...]

# Удалить аккаунт
guard.remove_account(steam_id="123456789", delete_file=True)
```

## Интеграция с Database

Для работы с базой данных через `MafileCreator`:

```python
from steam_guard import MafileCreator
from database import Database

db = Database()
creator = MafileCreator(db)

# Создать mafile для аккаунта из БД
mafile_path = creator.create_mafile_from_account(account_id=1)

# Импортировать mafile и добавить в БД
account_id = creator.import_and_add_account(
    mafile_path="path/to/account.maFile",
    password="optional_encryption_key"
)
```

## Константы Steam

- **Base-23 Alphabet**: "23456789BCDFGHJKMNPQRTVWXY" (специальный алфавит Steam)
- **Shared Secret Length**: 20 байт
- **Identity Secret Length**: 32 байта (опционально)
- **TOTP Period**: 30 секунд (стандартный RFC 6238)
- **PBKDF2 Iterations**: 50,000 (как в SDA)
- **Revocation Code Format**: 'R' + 5 символов из "0123456789BCDFGHJKMNPQRTVWXY"

## Требования

```
- cryptography >= 41.0.0  (для AES-256-CBC шифрования)
- base64 (встроенный модуль)
- json (встроенный модуль)
- hmac (встроенный модуль)
- hashlib (встроенный модуль)
```

## Примеры использования

### Пример 1: Добавить новый аккаунт

```python
from steam_guard import SteamGuardManager

guard = SteamGuardManager()

# Добавить аккаунт через Steam Web API (симуляция)
account = guard.add_account_with_login(
    username="mysteamaccount",
    password="mypassword",
    phone_number="+1234567890"
)

if account:
    print(f"Аккаунт добавлен! Revocation Code: {account['revocation_code']}")
    # ВАЖНО: Сохраните revocation_code в безопасном месте!
```

### Пример 2: Получить 2FA код

```python
# Получить текущий Steam Guard код
code, time_left = guard.get_steam_guard_code(shared_secret)
print(f"2FA Код: {code} (осталось {time_left} сек)")
```

### Пример 3: Управление шифрованием

```python
# Зашифровать mafile пароля
guard.encrypt_mafile(steam_id="123456789", password="secretpassword")

# Позже - расшифровать
mafile = guard.decrypt_mafile(steam_id="123456789", password="secretpassword")
```

### Пример 4: Импорт mafile из другого источника

```python
# Импортировать из SDA или другого источника
success = guard.import_and_register_mafile("path/to/exported.maFile")

if success:
    # Аккаунт готов к использованию
    accounts = guard.get_all_accounts()
```

## Ограничения и особенности

1. **Требуется cryptography** для шифрования mafiles
2. **Phone Number** - опционален, но рекомендуется для реального использования
3. **Revocation Code** - КРИТИЧЕН! Потеря кода = потеря доступа к аккаунту
4. **Session Expiration** - session_id и tokens истекают со временем и требуют обновления (функция "Force session refresh" в SDA)
5. **Time Sync** - точная синхронизация времени критична для TOTP кодов
6. **Encrypted Manifest** - поддерживаются зашифрованные mafiles, но требуется пароль для доступа

## Сравнение с Steam Desktop Authenticator

| Функция | SDA | Наша реализация |
|---------|-----|-----------------|
| Добавление аккаунта | ✓ (через UI) | ✓ (симуляция API) |
| MaFile структура | JSON | JSON (совместимо) |
| 2FA генерация | ✓ | ✓ (RFC 6238 TOTP) |
| Шифрование | AES-256-CBC | AES-256-CBC (PBKDF2-SHA512) |
| Подтверждения | ✓ | ✓ (confirmation keys) |
| Импорт/Экспорт | ✓ | ✓ |
| Manifest | C# JSON | Python JSON (совместимо) |
| Мобильная платформа | ✗ | ✓ (Kivy for Android) |

## Дополнительные ресурсы

- **SDA GitHub**: https://github.com/Jessecar96/SteamDesktopAuthenticator
- **steamguard PyPI**: https://pypi.org/project/steamguard/
- **steampy GitHub**: https://github.com/bukson/steampy
- **RFC 6238 TOTP**: https://tools.ietf.org/html/rfc6238
- **Steam Community API**: https://steamcommunity.com/dev/apikey

## Безопасность

⚠️ **ВАЖНО:**
- Никогда не публикуйте shared_secret или identity_secret
- Всегда сохраняйте revocation_code в безопасном месте
- Используйте шифрование для mafiles, если приложение работает с чувствительными данными
- Регулярно обновляйте session tokens (они истекают)
- Используйте HTTPS для всех Steam API запросов в реальной реализации
