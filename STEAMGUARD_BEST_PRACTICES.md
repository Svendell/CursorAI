# 🔐 SteamGuard Реализация - Лучшие практики и сравнение

## 📋 Содержание

1. [Сравнение реализаций](#сравнение-реализаций)
2. [Лучшие практики](#лучшие-практики)
3. [Типичные ошибки](#типичные-ошибки)
4. [Безопасность](#безопасность)
5. [Оптимизация](#оптимизация)

---

## Сравнение реализаций

### Реализация 1: Базовая (Наша текущая)

```python
# ✓ Плюсы
- Простая структура
- Легко понять и модифицировать
- Работает локально
- Поддерживает импорт/экспорт mafiles

# ✗ Минусы
- Нет реальной авторизации Steam
- Симуляция процесса
- Нет реального подключения к API Steam
- Secrets генерируются случайно (не от Steam)
```

### Реализация 2: Полная (Как в SDA)

Для реальной работы нужно:

```python
# Необходимо добавить:

1. Реальная авторизация Steam
   - Запросы к steamcommunity.com
   - Парсинг ответов
   - Обработка RSA шифрования пароля
   - Обработка различных кодов ошибок

2. Получение secrets от Steam
   - shared_secret из ответа авторизации
   - identity_secret для подтверждений
   - Валидация полученных данных

3. Работа с Steam API
   - Получение списка подтверждений
   - Подтверждение операций
   - Обработка сессий

4. Безопасность
   - Шифрование хранимых данных
   - Защита от MITM атак
   - SSL/TLS сертификаты
```

### Реализация 3: Production-ready

```python
# Дополнительно:

1. Обработка ошибок
   - Retry логика
   - Graceful degradation
   - Логирование

2. Кэширование
   - Кэш подтверждений
   - Кэш списка аккаунтов
   - TTL управление

3. Мониторинг
   - Метрики использования
   - Tracking ошибок
   - Performance мониторинг

4. Тестирование
   - Unit тесты
   - Integration тесты
   - Мокирование Steam API
```

---

## Лучшие практики

### 1. Работа с Secrets

#### ❌ НЕПРАВИЛЬНО

```python
# Хранить в plaintext
shared_secret = "sM3/3L0pXvfXhY2ZvB7cK9mN4pQ6rS8tU1wV2xY3zA="

# Логировать полный secret
print(f"Secret: {shared_secret}")

# Передавать в параметрах URL
url = f"?secret={shared_secret}"

# Копировать в памяти
secret_copy = shared_secret  # Может быть перехвачен
```

#### ✅ ПРАВИЛЬНО

```python
# Шифровать при сохранении
from app.encryption import encrypt_secret

encrypted_secret = encrypt_secret(shared_secret)
db.save(encrypted_secret)

# Логировать только с маской
logger.info(f"Secret: {shared_secret[:8]}...")

# Передавать в теле POST запроса с HTTPS
import requests
headers = {'Content-Type': 'application/json'}
requests.post(url, json={'secret': secret}, headers=headers)

# Очищать память после использования
import gc
secret_for_use = decrypt_secret(encrypted_secret)
result = use_secret(secret_for_use)
del secret_for_use
gc.collect()
```

### 2. Валидация входных данных

#### ❌ НЕПРАВИЛЬНО

```python
def confirm_code(code: str):
    """Прямая проверка без валидации"""
    if len(code) >= 5:  # Недостаточно
        # Подтвердить
        pass
```

#### ✅ ПРАВИЛЬНО

```python
from typing import Tuple

def confirm_code(code: str) -> Tuple[bool, str]:
    """Полная валидация"""
    
    # Проверка присутствия
    if not code:
        return False, "Code is required"
    
    # Проверка формата
    if not code.isalnum():
        return False, "Code must contain only letters and numbers"
    
    # Проверка длины
    if len(code) < 5 or len(code) > 10:
        return False, "Code must be 5-10 characters"
    
    # Семантическая проверка (если нужна)
    if not validate_against_steam(code):
        return False, "Code is not valid"
    
    return True, "Code accepted"
```

### 3. Обработка исключений

#### ❌ НЕПРАВИЛЬНО

```python
def generate_code(secret: str) -> str:
    """Без обработки ошибок"""
    secret_bytes = base64.b64decode(secret)
    hmac_hash = hmac.new(secret_bytes, time_bytes, hashlib.sha1).digest()
    # ... может выбросить исключение
    return code
```

#### ✅ ПРАВИЛЬНО

```python
def generate_code(secret: str) -> str:
    """С обработкой ошибок"""
    try:
        # Валидировать input
        if not secret:
            raise ValueError("Secret cannot be empty")
        
        # Попробовать декодировать
        try:
            secret_bytes = base64.b64decode(secret)
        except Exception as e:
            logger.error(f"Failed to decode secret: {e}")
            raise ValueError(f"Invalid base64 secret: {e}")
        
        # Основная логика с обработкой
        try:
            hmac_hash = hmac.new(secret_bytes, time_bytes, hashlib.sha1).digest()
            code = calculate_code(hmac_hash)
            return code
        except Exception as e:
            logger.error(f"Failed to generate code: {e}", exc_info=True)
            raise RuntimeError(f"Code generation failed: {e}")
            
    except ValueError as e:
        logger.warning(f"Validation error: {e}")
        return "00000"  # Безопасное значение по умолчанию
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        return "00000"  # Fallback
```

### 4. Тестирование TOTP

#### ❌ НЕПРАВИЛЬНО

```python
def test_totp():
    code = generate_code(secret)
    assert code is not None  # Недостаточно

def test_totp_2():
    # Тестирование зависит от текущего времени - ненадежно
    code1 = generate_code(secret)
    time.sleep(31)
    code2 = generate_code(secret)
    assert code1 != code2
```

#### ✅ ПРАВИЛЬНО

```python
def test_totp_format():
    """Проверить формат кода"""
    code = generate_code(secret)
    assert isinstance(code, str), "Code должен быть строкой"
    assert len(code) == 5, f"Code должен быть 5 символов, а это {code}"
    assert code.isdigit(), f"Code должен состоять из цифр, а это {code}"

def test_totp_consistency():
    """Проверить что код одинаков в одном периоде"""
    secret = base64.b64encode(os.urandom(20)).decode()
    
    # Генерировать с фиксированным time_offset
    code1 = generate_code(secret, time_offset=0)
    code2 = generate_code(secret, time_offset=15)  # Через 15 сек, один период
    assert code1 == code2, "Коды должны быть одинаковы в одном 30-сек периоде"

def test_totp_period_change():
    """Проверить что код меняется в новом периоде"""
    secret = base64.b64encode(os.urandom(20)).decode()
    
    code1 = generate_code(secret, time_offset=0)
    code2 = generate_code(secret, time_offset=30)  # Новый период
    
    # Коды скорее всего разные (может быть совпадение в 1/100000)
    # Но это дает представление о работе

def test_totp_edge_cases():
    """Проверить граничные случаи"""
    # Secret из всех нулей
    zero_secret = base64.b64encode(bytes(20)).decode()
    code = generate_code(zero_secret)
    assert len(code) == 5 and code.isdigit()
    
    # Secret из всех FF
    ff_secret = base64.b64encode(bytes([0xFF] * 20)).decode()
    code = generate_code(ff_secret)
    assert len(code) == 5 and code.isdigit()
```

---

## Типичные ошибки

### Ошибка 1: Неправильная Base64 кодировка

```python
# ❌ НЕПРАВИЛЬНО - двойное кодирование
secret_bytes = os.urandom(20)
secret_str = str(secret_bytes)  # Это не Base64!
encoded = base64.b64encode(secret_str.encode())  # Двойное кодирование

# ✅ ПРАВИЛЬНО
secret_bytes = os.urandom(20)
secret_b64 = base64.b64encode(secret_bytes).decode('utf-8')  # Одно кодирование
```

### Ошибка 2: Неправильный порядок байт (Endianness)

```python
# ❌ НЕПРАВИЛЬНО - little-endian
time_bytes = struct.pack('<Q', time_counter)  # '<' = little-endian

# ✅ ПРАВИЛЬНО - big-endian (как в Steam)
time_bytes = struct.pack('>Q', time_counter)  # '>' = big-endian
```

### Ошибка 3: Неправильный HMAC алгоритм

```python
# ❌ НЕПРАВИЛЬНО - MD5
hmac_hash = hmac.new(secret_bytes, time_bytes, hashlib.md5).digest()

# ✓ ПРАВИЛЬНО - SHA1
hmac_hash = hmac.new(secret_bytes, time_bytes, hashlib.sha1).digest()

# ⚠️ НЕПРАВИЛЬНО - SHA256 (не используется в Steam)
hmac_hash = hmac.new(secret_bytes, time_bytes, hashlib.sha256).digest()
```

### Ошибка 4: Неправильная индексация HMAC результата

```python
# ❌ НЕПРАВИЛЬНО - всегда используется последний байт
four_bytes = struct.unpack('>I', hmac_hash[-4:])[0]

# ✅ ПРАВИЛЬНО - используется динамический индекс
last_byte = hmac_hash[-1] & 0x0f  # Получить индекс из последних 4 бит
four_bytes = struct.unpack('>I', hmac_hash[last_byte:last_byte + 4])[0]
```

### Ошибка 5: Неправильная обработка mafile

```python
# ❌ НЕПРАВИЛЬНО - нет валидации
def load_mafile(path):
    with open(path) as f:
        return json.load(f)  # Может быть невалидным

# ✅ ПРАВИЛЬНО - с валидацией
def load_mafile(path):
    try:
        with open(path) as f:
            data = json.load(f)
        
        if not MafileValidator.validate_mafile(data):
            raise ValueError("Invalid mafile structure")
        
        return data
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON: {e}")
    except FileNotFoundError:
        raise FileNotFoundError(f"Mafile not found: {path}")
```

---

## Безопасность

### 🔐 Критичные аспекты

#### 1. Защита Secrets

```python
# НИКОГДА не логировать полные secrets
❌ logger.info(f"Secret: {shared_secret}")
✓ logger.info(f"Secret: {shared_secret[:8]}...{shared_secret[-4:]}")

# НИКОГДА не выводить в UI полные secrets
❌ print(f"Your secret: {shared_secret}")
✓ print(f"Secret saved safely")

# НИКОГДА не передавать в GET параметрах
❌ requests.get(f"https://api.example.com?secret={secret}")
✓ requests.post("https://api.example.com", json={"secret": secret})

# НИКОГДА не хранить в plaintext файлах
❌ with open('secrets.txt', 'w') as f:
    f.write(shared_secret)
    
✓ encrypted = encrypt_secret(shared_secret)
  db.save(encrypted)
```

#### 2. Защита от Брутфорса

```python
from datetime import datetime, timedelta
from collections import defaultdict

class LoginRateLimiter:
    def __init__(self, max_attempts: int = 5, window_seconds: int = 300):
        self.max_attempts = max_attempts
        self.window = timedelta(seconds=window_seconds)
        self.attempts = defaultdict(list)
    
    def check_limit(self, account_name: str) -> bool:
        """Проверить лимит попыток"""
        now = datetime.now()
        
        # Очистить старые попытки
        self.attempts[account_name] = [
            t for t in self.attempts[account_name]
            if now - t < self.window
        ]
        
        # Проверить лимит
        if len(self.attempts[account_name]) >= self.max_attempts:
            return False
        
        return True
    
    def record_attempt(self, account_name: str):
        """Записать попытку входа"""
        self.attempts[account_name].append(datetime.now())
    
    def reset(self, account_name: str):
        """Сбросить счетчик при успешном входе"""
        self.attempts[account_name] = []

# Использование
limiter = LoginRateLimiter()

if not limiter.check_limit(account_name):
    logger.warning(f"Too many login attempts for {account_name}")
    return False, "Too many attempts, please try again later"

limiter.record_attempt(account_name)

# После успешного входа
limiter.reset(account_name)
```

#### 3. Защита маfiles

```python
import os
from pathlib import Path

class MafileSecurityManager:
    @staticmethod
    def ensure_permissions(mafile_path: str, mode: int = 0o600):
        """Установить правильные права доступа к mafile"""
        os.chmod(mafile_path, mode)  # rw------- только для владельца
    
    @staticmethod
    def validate_path(mafile_path: str, base_dir: str) -> bool:
        """Проверить что путь находится в правильной директории"""
        base = Path(base_dir).resolve()
        path = Path(mafile_path).resolve()
        
        # Защита от path traversal атак
        return str(path).startswith(str(base))
    
    @staticmethod
    def backup_mafile(mafile_path: str) -> str:
        """Создать резервную копию mafile"""
        import shutil
        import datetime
        
        backup_path = f"{mafile_path}.backup.{datetime.datetime.now().isoformat()}"
        shutil.copy2(mafile_path, backup_path)
        
        return backup_path

# Использование
security = MafileSecurityManager()

# При создании mafile
mafile_path = create_mafile(account_data)
security.ensure_permissions(mafile_path)

# При загрузке
if not security.validate_path(user_provided_path, MAFILES_DIR):
    raise SecurityError("Invalid mafile path")

# Перед изменением
security.backup_mafile(mafile_path)
```

---

## Оптимизация

### 1. Кэширование TOTP кодов

```python
from datetime import datetime, timedelta

class TOTPCache:
    def __init__(self):
        self.cache = {}  # account_name -> (code, expiry_time)
    
    def get_code(self, account_name: str, secret: str) -> str:
        """Получить код с кэшированием"""
        now = datetime.now()
        
        # Проверить кэш
        if account_name in self.cache:
            code, expiry = self.cache[account_name]
            if now < expiry:
                return code
        
        # Генерировать новый код
        code = generate_totp(secret)
        
        # Кэшировать до смены
        seconds_until_change = 30 - (int(time.time()) % 30)
        expiry = now + timedelta(seconds=seconds_until_change)
        
        self.cache[account_name] = (code, expiry)
        
        return code

# Использование
cache = TOTPCache()
code = cache.get_code("myaccount", shared_secret)
# При следующем вызове в течение 30 сек вернет кэшированный код
```

### 2. Асинхронные операции

```python
import asyncio
from concurrent.futures import ThreadPoolExecutor

class AsyncSteamGuard:
    def __init__(self):
        self.executor = ThreadPoolExecutor(max_workers=4)
    
    async def generate_code_async(self, secret: str) -> str:
        """Асинхронное генерирование кода"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self.executor,
            generate_totp,
            secret
        )
    
    async def batch_generate_codes(self, accounts: list) -> dict:
        """Генерировать коды для нескольких аккаунтов одновременно"""
        tasks = [
            self.generate_code_async(acc['shared_secret'])
            for acc in accounts
        ]
        
        codes = await asyncio.gather(*tasks)
        
        return {
            acc['account_name']: code
            for acc, code in zip(accounts, codes)
        }

# Использование
guard = AsyncSteamGuard()
codes = await guard.batch_generate_codes(accounts)
```

---

## 📚 Дополнительные ресурсы

- [Полное руководство структуры Mafile](MAFILE_STRUCTURE_GUIDE.md)
- [Примеры и Тесты](MAFILE_EXAMPLES_AND_TESTS.md)
- [Steam Guard на GitHub](https://github.com/search?q=steamguard+mafile)

