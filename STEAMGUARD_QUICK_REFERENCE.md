# 🔍 Справочник SteamGuard - Быстрая шпаргалка

## 📌 Ключевые концепции

### shared_secret
- **Что это:** Главный ключ для генерирования 2FA кодов
- **Формат:** Base64 (20 байт)
- **Где хранится:** В mafile, в БД (зашифрован)
- **Использование:** `HMAC-SHA1(shared_secret, time_counter)`
- **Пример:** `sM3/3L0pXvfXhY2ZvB7cK9mN4pQ6rS8tU1wV2xY3zA=`

### identity_secret
- **Что это:** Ключ для генерирования хешей подтверждений
- **Формат:** Base64 (20 байт)
- **Где хранится:** В mafile, в БД (зашифрован)
- **Использование:** `HMAC-SHA1(identity_secret, time_bytes + tag)`
- **Пример:** `aBcDeFgHiJkLmNoPqRsTuVwXyZ1A2B3C4D5E6F7G=`

### revocation_code
- **Что это:** Резервный код для отключения 2FA
- **Формат:** XXXXX-XXXXX-XXXXX (5-3-5 символов)
- **Где хранится:** В mafile, в БД, выписывается пользователю
- **Использование:** Если потеряли доступ к shared_secret
- **Пример:** `A1B2C-D3E4F-G5H6I`

### maFile
- **Что это:** JSON файл с данными Steam Guard аккаунта
- **Формат:** `{account_name}.maFile`
- **Где хранится:** `mafiles/` папка
- **Содержит:** shared_secret, identity_secret, account_name, revocation_code
- **Минимум для работы:** shared_secret + account_name

---

## ⚡ Быстрые команды

### Генерирование 2FA кода

```python
from app.steam_utils import SteamGuardUtil

code = SteamGuardUtil.generate_steam_guard_code(shared_secret)
print(code)  # "12345"
```

### Создание mafile

```python
from app.steam_guard import SteamGuardManager

manager = SteamGuardManager()
path = manager.create_mafile_from_dict({
    'shared_secret': 'FhkMQfG2w3Z9nBvK7xL2mN4pQ6rS8tU1wV2xY3zA=',
    'account_name': 'myaccount'
})
```

### Импорт mafile

```python
manager = SteamGuardManager()
data = manager.import_mafile('mafiles/myaccount.maFile')
# {'account_name': '...', 'shared_secret': '...', ...}
```

### Валидация mafile

```python
from app.steam_utils import MafileValidator

is_valid = MafileValidator.validate_mafile(mafile_data)
```

### Генерирование хеша подтверждения

```python
from app.steam_utils import SteamAPIAuth

hash = SteamAPIAuth.generate_confirmation_hash(
    identity_secret,
    tag='conf'  # или 'details', 'allow', 'cancel'
)
```

### Работа с Manifest

```python
from app.steam_guard import ManifestManager

manifest = ManifestManager('mafiles')

# Получить все аккаунты
accounts = manifest.get_all_accounts()

# Добавить аккаунт
manifest.add_account_to_manifest('myaccount', 'myaccount.maFile')

# Обновить
manifest.update_account_in_manifest('myaccount', {
    'last_used': int(time.time()),
    'last_code': '12345'
})
```

---

## 🔐 Алгоритмы

### TOTP (Time-based One-Time Password)

```
1. Декодировать secret из Base64
2. time_counter = current_time // 30  (30-сек периоды)
3. time_bytes = big_endian(time_counter)
4. hmac_hash = HMAC-SHA1(secret, time_bytes)
5. index = hmac_hash[-1] & 0x0f
6. four_bytes = hmac_hash[index:index+4]
7. code = (four_bytes % 100000).to_string().zfill(5)
```

### Confirmation Hash

```
1. Декодировать identity_secret из Base64
2. time_counter = current_time // 30
3. time_bytes = big_endian(time_counter)
4. tag_bytes = tag.encode('utf-8')
5. data = time_bytes + tag_bytes
6. hmac_hash = HMAC-SHA1(identity_secret, data)
7. hash = Base64(hmac_hash)
```

---

## 📁 Структура файлов

```
steam_auth/
├── app/
│   ├── steam_guard.py          # SteamGuardManager, MafileCreator
│   ├── steam_auth.py           # SteamAuthenticator
│   ├── steam_utils.py          # SteamGuardUtil, SteamAPIAuth
│   ├── database.py             # Database, учет аккаунтов
│   ├── encryption.py           # Шифрование secrets
│   ├── logger.py               # Логирование
│   └── config.py               # Конфигурация
├── mafiles/                    # Mafiles папка
│   ├── account1.maFile
│   ├── account2.maFile
│   └── manifest.json
├── requirements.txt
└── main.py
```

---

## 🔗 Основные классы

### SteamGuardManager

```python
manager = SteamGuardManager()

manager.create_mafile_from_dict(data)  # Создать mafile
manager.import_mafile(path)             # Импортировать
manager.get_steam_guard_code(secret)    # Получить код
manager.get_confirmation_operations()   # Получить операции
manager.confirm_operation()             # Подтвердить
```

### SteamAuthenticator

```python
auth = get_authenticator()

auth.login(account, password)           # Войти
auth.send_code()                        # Отправить код
auth.confirm_code(code)                 # Подтвердить
auth.get_mafile_data()                  # Получить данные
auth.reset()                            # Сбросить
```

### SteamGuardUtil

```python
SteamGuardUtil.generate_totp(secret)    # 5-значный код
SteamGuardUtil.generate_steam_guard_code(secret)  # Альтернатива
SteamGuardUtil.get_code_time_remaining()  # Осталось сек
```

### MafileValidator

```python
MafileValidator.validate_mafile(data)   # Проверить структуру
MafileValidator.REQUIRED_FIELDS         # Обязательные поля
MafileValidator.OPTIONAL_FIELDS         # Опциональные
```

### Database

```python
db = Database()

db.add_account(name, password, secret)  # Добавить
db.get_account(id)                      # Получить по ID
db.get_account_by_name(name)           # Получить по имени
db.get_all_accounts()                   # Все аккаунты
db.update_account(id, **kwargs)        # Обновить
db.delete_account(id)                   # Удалить
```

### ManifestManager

```python
manifest = ManifestManager('mafiles')

manifest.load_manifest()                # Загрузить
manifest.add_account_to_manifest()      # Добавить
manifest.remove_account_from_manifest() # Удалить
manifest.get_all_accounts()             # Все аккаунты
manifest.get_account(name)              # Конкретный
manifest.update_account_in_manifest()   # Обновить
manifest.sync_with_filesystem()         # Синхронизировать
```

---

## ✅ Проверочный список

### При создании mafile
- [ ] shared_secret не пусто
- [ ] shared_secret - валидный Base64
- [ ] account_name не пусто
- [ ] account_name соответствует Steam (3-32 символа)
- [ ] Файл сохранен в `mafiles/`
- [ ] Файл добавлен в manifest
- [ ] Файл добавлен в БД

### При использовании кода
- [ ] shared_secret расшифрован (если зашифрован)
- [ ] secret_bytes = base64.b64decode(secret)
- [ ] Используется big-endian (`>Q`)
- [ ] Используется HMAC-SHA1
- [ ] Результат модуль 100000
- [ ] Результат зафиксирован (5 цифр)

### При подтверждении операции
- [ ] identity_secret не пусто
- [ ] Используется правильный tag ('conf', 'details', 'allow', 'cancel')
- [ ] Используется big-endian (`>Q`)
- [ ] Используется HMAC-SHA1
- [ ] Результат закодирован в Base64
- [ ] Используется HTTPS для запроса
- [ ] Обработаны все ошибки

### При подключении к Steam API
- [ ] Используется валидный Steam ID (64-bit)
- [ ] Используется валидный access_token
- [ ] Обработаны таймауты
- [ ] Обработаны ошибки авторизации (401, 403)
- [ ] Обработана rate limiting (429)
- [ ] Используется правильный User-Agent

---

## 🐛 Типичные проблемы

### Ошибка: "Invalid base64 secret"
```python
# ❌ Причина: неправильное кодирование
secret = os.urandom(20)  # Это bytes, не Base64!

# ✅ Решение:
secret = base64.b64encode(os.urandom(20)).decode('utf-8')
```

### Ошибка: "Code never changes"
```python
# ❌ Причина: неправильный порядок байт
time_bytes = struct.pack('<Q', time_counter)  # Little-endian!

# ✅ Решение:
time_bytes = struct.pack('>Q', time_counter)  # Big-endian
```

### Ошибка: "Confirmation always fails"
```python
# ❌ Причина: неправильный steam_id
steam_id = 12345  # 32-bit, не хватает

# ✅ Решение:
steam_id = 76561198123456789  # 64-bit Steam ID
```

### Ошибка: "Secrets are not from Steam"
```python
# ❌ Причина: генерируются случайно в демо режиме
self.shared_secret = base64.b64encode(os.urandom(20))

# ✅ Решение: получить реальные secrets при авторизации Steam
response = steam_api.login(account, password)
self.shared_secret = response['shared_secret']
```

---

## 📚 Документация

| Файл | Содержание |
|------|-----------|
| [MAFILE_STRUCTURE_GUIDE.md](MAFILE_STRUCTURE_GUIDE.md) | Полное руководство по структуре mafile |
| [MAFILE_EXAMPLES_AND_TESTS.md](MAFILE_EXAMPLES_AND_TESTS.md) | Примеры и тестовый код |
| [MANIFEST_AND_OPERATIONS.md](MANIFEST_AND_OPERATIONS.md) | Manifest и управление подтверждениями |
| [STEAMGUARD_BEST_PRACTICES.md](STEAMGUARD_BEST_PRACTICES.md) | Лучшие практики и безопасность |

---

## 🔗 Полезные ссылки

- Steam Community Guard: https://steamcommunity.com/
- Steam Guard Mobile: https://store.steampowered.com/
- SteamGuard на GitHub: https://github.com/search?q=steamguard

---

## 💡 Советы

1. **Всегда шифруйте secrets** при сохранении
2. **Никогда не логируйте полные secrets** (показывайте только начало)
3. **Всегда валидируйте входные данные** перед использованием
4. **Используйте HTTPS** для всех запросов к Steam API
5. **Обработайте все исключения** при работе с файлами
6. **Кэшируйте коды** в течение 30 сек (не пересчитывайте)
7. **Ограничивайте попытки входа** (5 попыток в 5 минут)
8. **Ротируйте access tokens** (обновляйте регулярно)
9. **Резервируйте revocation codes** (в безопасном месте)
10. **Мониторьте ошибки** и логируйте все подозрительное

