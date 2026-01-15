# 📁 Примеры Mafile и тестовый код

## 📊 Пример 1: Минимальный валидный mafile

```json
{
  "shared_secret": "sM3/3L0pXvfXhY2ZvB7cK9mN4pQ6rS8tU1wV2xY3zA=",
  "account_name": "mysteamaccount"
}
```

**Размер:** 124 байта  
**Валидные операции:** только генерирование 2FA кодов

---

## 📊 Пример 2: Полный mafile с подтверждениями

```json
{
  "shared_secret": "sM3/3L0pXvfXhY2ZvB7cK9mN4pQ6rS8tU1wV2xY3zA=",
  "identity_secret": "aBcDeFgHiJkLmNoPqRsTuVwXyZ1A2B3C4D5E6F7G=",
  "revocation_code": "A1B2C-D3E4F-G5H6I",
  "account_name": "mysteamaccount",
  "uri": "",
  "server_time": 1705330800,
  "account_name_hmac": "",
  "session_id": "",
  "fully_enrolled": true
}
```

**Размер:** 420 байт  
**Валидные операции:** генерирование кодов + подтверждения операций

---

## 📊 Пример 3: Mafile со всеми заполненными полями

```json
{
  "shared_secret": "sM3/3L0pXvfXhY2ZvB7cK9mN4pQ6rS8tU1wV2xY3zA=",
  "identity_secret": "aBcDeFgHiJkLmNoPqRsTuVwXyZ1A2B3C4D5E6F7G=",
  "revocation_code": "A1B2C-D3E4F-G5H6I",
  "account_name": "mysteamaccount",
  "uri": "steam://account/mysteamaccount",
  "server_time": 1705330800,
  "account_name_hmac": "iOjPqRsTuVwXyZ1A2B3C4D5E6F7G8H9I=",
  "session_id": "SessionID123456789",
  "fully_enrolled": true
}
```

---

## 🧪 Тестовый код для работы с mafile

### Тест 1: Создание и валидация mafile

```python
import json
import base64
import os
from typing import Dict, Any

def test_create_and_validate_mafile():
    """Тестирование создания и валидации mafile"""
    
    # Создать тестовый mafile
    test_data = {
        'shared_secret': 'sM3/3L0pXvfXhY2ZvB7cK9mN4pQ6rS8tU1wV2xY3zA=',
        'account_name': 'test_account',
        'identity_secret': 'aBcDeFgHiJkLmNoPqRsTuVwXyZ1A2B3C4D5E6F7G=',
        'revocation_code': 'A1B2C-D3E4F-G5H6I'
    }
    
    # Создать структуру mafile
    mafile = {
        'shared_secret': test_data['shared_secret'],
        'identity_secret': test_data.get('identity_secret', ''),
        'revocation_code': test_data.get('revocation_code', ''),
        'account_name': test_data['account_name'],
        'uri': '',
        'server_time': int(time.time()),
        'account_name_hmac': '',
        'session_id': '',
        'fully_enrolled': True
    }
    
    # Сохранить в файл
    test_path = 'test_mafile.json'
    with open(test_path, 'w') as f:
        json.dump(mafile, f, indent=2)
    
    # Загрузить и проверить
    with open(test_path, 'r') as f:
        loaded_mafile = json.load(f)
    
    # Валидация
    assert loaded_mafile['account_name'] == 'test_account'
    assert loaded_mafile['shared_secret'] == test_data['shared_secret']
    assert loaded_mafile['identity_secret'] == test_data['identity_secret']
    
    # Валидация Base64
    try:
        base64.b64decode(loaded_mafile['shared_secret'])
        print("✓ shared_secret - валидный Base64")
    except Exception:
        print("✗ shared_secret - невалидный Base64")
        return False
    
    try:
        base64.b64decode(loaded_mafile['identity_secret'])
        print("✓ identity_secret - валидный Base64")
    except Exception:
        print("✗ identity_secret - невалидный Base64")
        return False
    
    # Очистка
    os.remove(test_path)
    
    print("✓ Тест создания и валидации mafile пройден")
    return True

if __name__ == '__main__':
    test_create_and_validate_mafile()
```

### Тест 2: Генерирование 2FA кодов

```python
import hmac
import hashlib
import struct
import base64
import time

def test_totp_generation():
    """Тестирование генерирования TOTP кодов"""
    
    # Тестовый shared_secret
    test_secret = 'sM3/3L0pXvfXhY2ZvB7cK9mN4pQ6rS8tU1wV2xY3zA='
    
    def generate_code(secret: str, offset: int = 0) -> str:
        """Генерировать 2FA код"""
        secret_bytes = base64.b64decode(secret)
        server_time = int(time.time()) + offset
        time_counter = server_time // 30
        
        time_bytes = struct.pack('>Q', time_counter)
        hmac_hash = hmac.new(secret_bytes, time_bytes, hashlib.sha1).digest()
        
        last_byte = hmac_hash[-1] & 0x0f
        four_bytes = struct.unpack('>I', hmac_hash[last_byte:last_byte + 4])[0]
        
        code = str(four_bytes % 100000).zfill(5)
        return code
    
    # Получить коды для разных моментов времени
    code_now = generate_code(test_secret)
    code_in_15_sec = generate_code(test_secret, 15)
    code_in_30_sec = generate_code(test_secret, 30)  # Новый код
    code_in_45_sec = generate_code(test_secret, 45)  # Такой же как code_in_30_sec
    
    print(f"Текущий код (0 сек):    {code_now}")
    print(f"Код через 15 сек:       {code_in_15_sec}")
    print(f"Код через 30 сек:       {code_in_30_sec}")
    print(f"Код через 45 сек:       {code_in_45_sec}")
    
    # Проверка
    assert code_now == code_in_15_sec, "Коды в одном периоде должны совпадать"
    assert code_in_30_sec == code_in_45_sec, "Коды в одном периоде должны совпадать"
    
    if code_now != code_in_30_sec:
        print("✓ Коды меняются каждые 30 секунд")
    
    # Проверка формата
    assert len(code_now) == 5, f"Код должен быть 5 цифр, а это {code_now}"
    assert code_now.isdigit(), f"Код должен состоять только из цифр, а это {code_now}"
    
    print("✓ Тест генерирования TOTP пройден")
    return True

if __name__ == '__main__':
    test_totp_generation()
```

### Тест 3: Генерирование хешей подтверждений

```python
import hmac
import hashlib
import struct
import base64
import time

def test_confirmation_hash_generation():
    """Тестирование генерирования хешей для подтверждений"""
    
    test_identity_secret = 'aBcDeFgHiJkLmNoPqRsTuVwXyZ1A2B3C4D5E6F7G='
    
    def generate_confirmation_hash(identity_secret: str, tag: str = 'conf') -> str:
        """Генерировать хеш подтверждения"""
        secret_bytes = base64.b64decode(identity_secret)
        server_time = int(time.time())
        
        time_bytes = struct.pack('>Q', server_time // 30)
        tag_bytes = tag.encode('utf-8')
        
        data = time_bytes + tag_bytes
        
        hmac_hash = hmac.new(secret_bytes, data, hashlib.sha1).digest()
        hash_b64 = base64.b64encode(hmac_hash).decode('utf-8')
        
        return hash_b64
    
    # Генерировать хеши с разными тегами
    conf_hash = generate_confirmation_hash(test_identity_secret, 'conf')
    details_hash = generate_confirmation_hash(test_identity_secret, 'details')
    allow_hash = generate_confirmation_hash(test_identity_secret, 'allow')
    cancel_hash = generate_confirmation_hash(test_identity_secret, 'cancel')
    
    print(f"conf hash:     {conf_hash[:20]}...")
    print(f"details hash:  {details_hash[:20]}...")
    print(f"allow hash:    {allow_hash[:20]}...")
    print(f"cancel hash:   {cancel_hash[:20]}...")
    
    # Проверка что хеши разные
    assert conf_hash != details_hash, "Хеши с разными тегами должны быть разные"
    assert details_hash != allow_hash, "Хеши с разными тегами должны быть разные"
    
    # Проверка что это валидный Base64
    try:
        base64.b64decode(conf_hash)
        print("✓ Хеш - валидный Base64")
    except Exception:
        print("✗ Хеш - невалидный Base64")
        return False
    
    # Проверка длины (HMAC-SHA1 = 20 байт, Base64 = ~27 символов)
    expected_length = 28  # 20 байт -> 28 символов в Base64
    actual_length = len(conf_hash)
    assert actual_length == expected_length, \
        f"Длина Base64 хеша должна быть {expected_length}, а это {actual_length}"
    
    print("✓ Тест генерирования хешей подтверждений пройден")
    return True

if __name__ == '__main__':
    test_confirmation_hash_generation()
```

### Тест 4: Работа с файлами mafile

```python
import json
import os
import shutil

def test_mafile_file_operations():
    """Тестирование операций с файлами mafile"""
    
    # Создать тестовую директорию
    test_dir = 'test_mafiles'
    os.makedirs(test_dir, exist_ok=True)
    
    try:
        # Тестовые данные
        accounts = [
            {
                'shared_secret': 'sM3/3L0pXvfXhY2ZvB7cK9mN4pQ6rS8tU1wV2xY3zA=',
                'account_name': 'account1'
            },
            {
                'shared_secret': 'aBcDeFgHiJkLmNoPqRsTuVwXyZ1A2B3C4D5E6F7G=',
                'identity_secret': 'qWeRtYuIoPdFgHjKlZxCvBnMqWeRtYuIoPdFgHjK=',
                'account_name': 'account2'
            }
        ]
        
        # Создать mafiles
        for account in accounts:
            mafile = {
                'shared_secret': account['shared_secret'],
                'identity_secret': account.get('identity_secret', ''),
                'revocation_code': '',
                'account_name': account['account_name'],
                'uri': '',
                'server_time': int(time.time()),
                'account_name_hmac': '',
                'session_id': '',
                'fully_enrolled': True
            }
            
            filepath = os.path.join(test_dir, f"{account['account_name']}.maFile")
            with open(filepath, 'w') as f:
                json.dump(mafile, f, indent=2)
        
        # Проверить что файлы созданы
        files = os.listdir(test_dir)
        assert len(files) == 2, f"Должно быть 2 файла, а там {len(files)}"
        print(f"✓ Создано {len(files)} mafile'ов")
        
        # Загрузить и проверить содержимое
        for account in accounts:
            filepath = os.path.join(test_dir, f"{account['account_name']}.maFile")
            with open(filepath, 'r') as f:
                loaded = json.load(f)
            
            assert loaded['account_name'] == account['account_name']
            assert loaded['shared_secret'] == account['shared_secret']
            print(f"✓ Загружен и проверен {account['account_name']}")
        
        print("✓ Тест операций с файлами mafile пройден")
        return True
        
    finally:
        # Очистка
        shutil.rmtree(test_dir, ignore_errors=True)

if __name__ == '__main__':
    test_mafile_file_operations()
```

### Тест 5: Валидация структуры mafile

```python
def test_mafile_validation():
    """Тестирование валидации структуры mafile"""
    
    from app.steam_utils import MafileValidator
    
    # Валидный mafile
    valid_mafile = {
        'shared_secret': 'sM3/3L0pXvfXhY2ZvB7cK9mN4pQ6rS8tU1wV2xY3zA=',
        'account_name': 'test_account'
    }
    
    # Невалидные mafiles
    invalid_mafiles = [
        # Отсутствует shared_secret
        {
            'account_name': 'test_account'
        },
        # Отсутствует account_name
        {
            'shared_secret': 'sM3/3L0pXvfXhY2ZvB7cK9mN4pQ6rS8tU1wV2xY3zA='
        },
        # Невалидный Base64 shared_secret
        {
            'shared_secret': 'invalid base64!!!',
            'account_name': 'test_account'
        },
        # Невалидный Base64 identity_secret
        {
            'shared_secret': 'sM3/3L0pXvfXhY2ZvB7cK9mN4pQ6rS8tU1wV2xY3zA=',
            'account_name': 'test_account',
            'identity_secret': 'not valid base64!!!'
        }
    ]
    
    # Проверить валидный
    assert MafileValidator.validate_mafile(valid_mafile), \
        "Валидный mafile должен пройти проверку"
    print("✓ Валидный mafile пройден проверку")
    
    # Проверить невалидные
    for i, invalid in enumerate(invalid_mafiles):
        is_valid = MafileValidator.validate_mafile(invalid)
        assert not is_valid, f"Невалидный mafile #{i} должен провалить проверку"
        print(f"✓ Невалидный mafile #{i} провалил проверку (как ожидается)")
    
    print("✓ Тест валидации структуры mafile пройден")
    return True

if __name__ == '__main__':
    test_mafile_validation()
```

---

## 🔍 Проверочный список для mafile

Перед использованием mafile убедитесь:

- [ ] Файл в JSON формате (валидный JSON)
- [ ] Поле `shared_secret` присутствует и не пусто
- [ ] Поле `account_name` присутствует и не пусто
- [ ] `shared_secret` - это валидный Base64 (длина ~28 символов)
- [ ] `identity_secret` (если присутствует) - валидный Base64
- [ ] `revocation_code` (если присутствует) - формат XXXXX-XXXXX-XXXXX
- [ ] Файл защищен от несанкционированного доступа (chmod 600)
- [ ] Файл зашифрован при необходимости

---

## ⚡ Быстрые ссылки

- [Полное руководство](MAFILE_STRUCTURE_GUIDE.md)
- [Исходный код steam_guard.py](steam_auth/app/steam_guard.py)
- [Исходный код steam_utils.py](steam_auth/app/steam_utils.py)
- [Исходный код steam_auth.py](steam_auth/app/steam_auth.py)

