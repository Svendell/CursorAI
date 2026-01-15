# 🔐 Steam Authentication Module Guide (v1.1)

## 📌 Обзор

Модуль `app/steam_auth.py` реализует многошаговую аутентификацию Steam, подобно **Steam Desktop Authenticator (SDA)**. Это позволяет пользователям создавать mafiles через процесс, имитирующий реальную Steam авторизацию.

## 🎯 Основной поток

```
1. Пользователь вводит логин и пароль
   ↓
2. Система попытается авторизоваться
   ↓
3. Если требуется 2FA, предложить 2 способа:
   - Отправить код на Email
   - Отправить код на SMS
   ↓
4. Пользователь вводит 5-значный код
   ↓
5. Если код верный - создается Mafile с secrets
```

## 🔧 Основные классы

### AuthStatus (Enum)

Перечисление состояний аутентификации:

```python
from app.steam_auth import AuthStatus

class AuthStatus(Enum):
    IDLE = "idle"                          # Начальное состояние
    LOGGING_IN = "logging_in"              # Попытка входа
    EMAIL_CODE_NEEDED = "email_code_needed"        # Нужен код по email
    SMS_CODE_NEEDED = "sms_code_needed"    # Нужен код по SMS
    AUTHENTICATOR_CODE_NEEDED = "authenticator_code_needed"  # Нужен 2FA код
    DEVICE_CONFIRMATION_NEEDED = "device_confirmation_needed" # Нужно подтвердить устройство
    SUCCESS = "success"                    # Успешная авторизация
    FAILED = "failed"                      # Авторизация не удалась
```

### SteamAuthenticator

Основной класс для управления аутентификацией.

#### Инициализация

```python
from app.steam_auth import get_authenticator

# Получить singleton экземпляр
auth = get_authenticator()
```

#### Методы

##### 1. `login(account_name: str, password: str) -> Tuple[bool, str]`

Попытаться авторизоваться с учетными данными.

**Параметры:**
- `account_name`: Имя Steam аккаунта
- `password`: Пароль аккаунта

**Возвращает:**
- `(True, message)` - если авторизация успешна без 2FA
- `(False, "code_needed:email")` - если нужен код по email
- `(False, "code_needed:sms")` - если нужен код по SMS
- `(False, error_message)` - если произошла ошибка

**Пример:**

```python
success, message = auth.login("mysteamaccount", "mypassword123")

if success:
    print("Авторизация успешна!")
    mafile_data = auth.get_mafile_data()
elif "code_needed" in message:
    print(f"Требуется код: {message}")
    # Перейти на экран ввода кода
else:
    print(f"Ошибка: {message}")
```

##### 2. `send_code() -> None`

Отправить код подтверждения на email или SMS.

**Пример:**

```python
try:
    auth.send_code()
    print("Код отправлен!")
except Exception as e:
    print(f"Ошибка отправки кода: {e}")
```

##### 3. `confirm_code(code: str) -> Tuple[bool, str]`

Подтвердить код подтверждения и создать mafile secrets.

**Параметры:**
- `code`: 5-значный код из email или SMS

**Возвращает:**
- `(True, "Code confirmed")` - если код верный
- `(False, error_message)` - если код неверный

**Пример:**

```python
success, message = auth.confirm_code("12345")

if success:
    print("Код подтвержден!")
    mafile_data = auth.get_mafile_data()
    # Создать mafile с этими данными
else:
    print(f"Неверный код: {message}")
```

##### 4. `confirm_device() -> Tuple[bool, str]`

Альтернативный способ подтверждения через устройство.

**Пример:**

```python
success, message = auth.confirm_device()
if success:
    print("Устройство подтверждено!")
```

##### 5. `get_mafile_data() -> Dict[str, str]`

Получить полные данные mafile после успешной авторизации.

**Возвращает:**
```python
{
    "shared_secret": "abcd1234...",
    "identity_secret": "xyz9876...",
    "revocation_code": "R12345",
    "account_name": "mysteamaccount",
    "session_id": "session123...",
    "web_cookie": "cookie...",
    "timestamp": "1234567890"
}
```

**Пример:**

```python
if auth.status == AuthStatus.SUCCESS:
    mafile_data = auth.get_mafile_data()
    
    # Использовать для создания mafile
    from app.database import Database
    
    db = Database()
    account_id = db.add_account(
        account_name=mafile_data.get('account_name'),
        password='',  # Не сохранять пароль после авторизации
        shared_secret=mafile_data.get('shared_secret'),
        identity_secret=mafile_data.get('identity_secret'),
        revocation_code=mafile_data.get('revocation_code')
    )
```

##### 6. `reset() -> None`

Сбросить состояние аутентификации. Используйте перед новой попыткой входа.

**Пример:**

```python
# После завершения процесса авторизации
auth.reset()

# Теперь можно начать новую авторизацию
auth.login("anotheruser", "anotherpassword")
```

### SteamLoginValidator

Класс для валидации входных данных.

```python
from app.steam_auth import SteamLoginValidator

validator = SteamLoginValidator()

# Проверить логин
if validator.validate_account_name("mysteamaccount"):
    print("Логин валиден")
else:
    print("Логин содержит недопустимые символы")

# Проверить пароль
if validator.validate_password("mypassword123"):
    print("Пароль валиден")
else:
    print("Пароль слишком короткий")

# Проверить код
if validator.validate_code("12345"):
    print("Код валиден")
else:
    print("Код должен быть 5 цифр")
```

## 📱 Интеграция с UI (screens.py)

### CreateMafileScreen - Многошаговый процесс

Новый `CreateMafileScreen` реализует 4-шаговый процесс:

**Шаг 1 - Ввод учетных данных**
```python
def _build_login_step(self):
    """Показать форму ввода логина и пароля"""
    # Получить данные
    account_name = self.account_name_input.text
    password = self.password_input.text
    
    # Вызвать login
    success, message = self.authenticator.login(account_name, password)
    
    if success:
        # Перейти на Шаг 2 (отправка кода)
        self.current_step = 'send_code'
    else:
        # Показать ошибку
        self._show_error(message)
```

**Шаг 2 - Отправка кода**
```python
def on_send_code_pressed(self, instance):
    """Отправить код подтверждения"""
    try:
        self.authenticator.send_code()
        # Перейти на Шаг 3 (ввод кода)
        self.current_step = 'confirm_code'
    except Exception as e:
        self._show_error(f'Failed to send code: {str(e)}')
```

**Шаг 3 - Ввод кода подтверждения**
```python
def on_confirm_code_pressed(self, instance):
    """Подтвердить код"""
    code = self.code_input.text
    success, message = self.authenticator.confirm_code(code)
    
    if success:
        # Получить данные и создать mafile
        mafile_data = self.authenticator.get_mafile_data()
        
        # Добавить в БД
        account_id = self.db.add_account(
            account_name=mafile_data.get('account_name'),
            password='',
            shared_secret=mafile_data.get('shared_secret'),
            identity_secret=mafile_data.get('identity_secret'),
            revocation_code=mafile_data.get('revocation_code')
        )
        
        # Создать mafile файл
        account = self.db.get_account(account_id)
        mafile_path = self.guard_manager.create_mafile_from_dict(account)
        
        # Перейти на Шаг 4 (успех)
        self.current_step = 'success'
    else:
        self._show_error(f'Invalid code: {message}')
```

**Шаг 4 - Завершение**
```python
def on_finish(self, instance):
    """Завершить процесс"""
    self.authenticator.reset()
    self.manager.current = 'accounts'
```

## 🔄 Полный пример использования

```python
from app.steam_auth import get_authenticator, AuthStatus

# Получить authenticator
auth = get_authenticator()

# Шаг 1: Авторизоваться
print("Step 1: Login")
success, message = auth.login("myaccount", "mypassword")
print(f"Result: {success}, {message}")

# Шаг 2: Отправить код
if not success:
    print("\nStep 2: Send Code")
    auth.send_code()
    print("Code sent to email/SMS")
    
    # Шаг 3: Подтвердить код
    print("\nStep 3: Confirm Code")
    code = input("Enter code: ")
    success, message = auth.confirm_code(code)
    print(f"Result: {success}, {message}")
    
    # Шаг 4: Получить данные
    if success:
        print("\nStep 4: Get Mafile Data")
        mafile_data = auth.get_mafile_data()
        
        print(f"Account: {mafile_data.get('account_name')}")
        print(f"Shared Secret: {mafile_data.get('shared_secret')[:20]}...")
        print(f"Identity Secret: {mafile_data.get('identity_secret')[:20]}...")
        print(f"Revocation Code: {mafile_data.get('revocation_code')}")

# Сбросить для следующей авторизации
auth.reset()
```

## 🧪 Тестирование

### Unit тесты

```python
import unittest
from app.steam_auth import SteamAuthenticator, SteamLoginValidator, AuthStatus

class TestSteamAuth(unittest.TestCase):
    def setUp(self):
        self.auth = SteamAuthenticator()
        self.validator = SteamLoginValidator()
    
    def test_login_success(self):
        """Тест успешной авторизации"""
        success, message = self.auth.login("testaccount", "testpassword")
        self.assertTrue(success or "code_needed" in message)
    
    def test_invalid_credentials(self):
        """Тест неверных учетных данных"""
        success, message = self.auth.login("", "")
        self.assertFalse(success)
        self.assertIn("invalid", message.lower())
    
    def test_code_validation(self):
        """Тест валидации кода"""
        self.assertTrue(self.validator.validate_code("12345"))
        self.assertFalse(self.validator.validate_code("123"))  # Слишком короткий
        self.assertFalse(self.validator.validate_code("abcde"))  # Не числа
    
    def test_reset(self):
        """Тест сброса состояния"""
        self.auth.login("test", "test")
        self.auth.reset()
        self.assertEqual(self.auth.status, AuthStatus.IDLE)
```

## 📝 Обработка ошибок

### Валидация входных данных

```python
from app.steam_auth import SteamLoginValidator

validator = SteamLoginValidator()

account_name = "myaccount"
password = "mypassword"

if not validator.validate_account_name(account_name):
    print("Invalid account name")
elif not validator.validate_password(password):
    print("Password too short")
else:
    auth.login(account_name, password)
```

### Обработка исключений

```python
try:
    auth.send_code()
except ConnectionError:
    print("No internet connection")
except TimeoutError:
    print("Request timeout")
except Exception as e:
    print(f"Unknown error: {e}")
```

## 🔐 Безопасность

- **Пароли не сохраняются** - после авторизации пароль не записывается в БД
- **Secrets генерируются** - shared_secret, identity_secret и т.д. генерируются как при реальной авторизации Steam
- **Коды валидируются** - входные данные проверяются перед обработкой
- **Состояние изолировано** - каждый authenticator имеет свое состояние

## 📊 Статистика модуля

```
app/steam_auth.py:
- Строк кода: 348
- Классов: 3 (AuthStatus, SteamAuthenticator, SteamLoginValidator)
- Методов: 15+
- Статусов: 8
- Способов авторизации: 3 (email, sms, device)
```

## 🎓 Дальнейшее развитие

Возможные улучшения:

1. **Real Steam API** - интеграция с реальным Steam API вместо имитации
2. **Recovery Codes** - поддержка recovery кодов для 2FA
3. **Remember Device** - опция "Remember this device"
4. **Multi-factor** - поддержка других способов 2FA (Authy, Microsoft Authenticator)
5. **Rate Limiting** - защита от brute-force атак

## 📚 Связанные файлы

- [screens.py](app/screens.py#L649) - CreateMafileScreen использует steam_auth.py
- [database.py](app/database.py) - хранение данных аккаунтов
- [steam_guard.py](app/steam_guard.py) - создание и управление mafiles
- [encryption.py](app/encryption.py) - шифрование данных
