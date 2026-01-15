#!/usr/bin/env python3
"""
Тестирование реализации Steam Guard функционала
Демонстрирует:
- Добавление новых аккаунтов через Steam Web API (симуляция)
- Создание и управление mafiles
- Генерацию Steam Guard 2FA кодов
- Работу с Manifest файлом
- Шифрование и расшифровку mafiles
"""

import os
import sys
import json
import base64

# Добавить путь к модулям
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from steam_guard import SteamGuardManager, FileEncryptor, Manifest


def test_add_account_with_login():
    """Тест: Добавить новый аккаунт через Steam Web API"""
    print("\n" + "="*60)
    print("ТЕСТ 1: Добавление нового аккаунта")
    print("="*60)
    
    guard = SteamGuardManager()
    
    # Добавить новый аккаунт
    account_data = guard.add_account_with_login(
        username="testuser",
        password="password123",
        phone_number="+1234567890"
    )
    
    if account_data:
        print("✓ Аккаунт успешно добавлен!")
        print(f"  Steam ID: {account_data['steam_id']}")
        print(f"  Revocation Code: {account_data['revocation_code']}")
        print(f"  Shared Secret: {account_data['shared_secret'][:20]}...")
        return True
    else:
        print("✗ Ошибка при добавлении аккаунта")
        return False


def test_steam_guard_code():
    """Тест: Генерация Steam Guard 2FA кода"""
    print("\n" + "="*60)
    print("ТЕСТ 2: Генерация Steam Guard 2FA кода")
    print("="*60)
    
    guard = SteamGuardManager()
    
    # Получить все аккаунты
    accounts = guard.get_all_accounts()
    
    if not accounts:
        print("✗ Нет аккаунтов для тестирования")
        return False
    
    account = accounts[0]
    print(f"Тестирование аккаунта: {account['account_name']}")
    
    # Прочитать mafile
    entry = guard.manifest.get_entry(account['steam_id'])
    mafile_path = os.path.join(guard.MAFILES_DIR, entry.filename)
    
    with open(mafile_path, 'r', encoding='utf-8') as f:
        mafile_data = json.load(f)
    
    # Получить 2FA код
    code, time_remaining = guard.get_steam_guard_code(mafile_data['shared_secret'])
    
    print(f"✓ Steam Guard код: {code}")
    print(f"  Время остаток: {time_remaining} секунд")
    
    # Получить только код
    code_only = guard.get_steam_guard_code_only(mafile_data['shared_secret'])
    print(f"✓ Код (только): {code_only}")
    
    return True


def test_mafile_encryption():
    """Тест: Шифрование mafile"""
    print("\n" + "="*60)
    print("ТЕСТ 3: Шифрование и расшифровка mafile")
    print("="*60)
    
    guard = SteamGuardManager()
    
    accounts = guard.get_all_accounts()
    if not accounts:
        print("✗ Нет аккаунтов для тестирования")
        return False
    
    account = accounts[0]
    steam_id = account['steam_id']
    password = "myencryptionkey123"
    
    print(f"Шифрование аккаунта: {account['account_name']}")
    
    # Зашифровать
    if guard.encrypt_mafile(steam_id, password):
        print("✓ Mafile успешно зашифрован!")
    else:
        print("✗ Ошибка при шифровании")
        return False
    
    # Проверить что файл зашифрован
    entry = guard.manifest.get_entry(steam_id)
    if entry.salt and entry.iv:
        print(f"✓ Salt: {entry.salt[:20]}...")
        print(f"✓ IV: {entry.iv[:20]}...")
    
    # Расшифровать
    decrypted = guard.decrypt_mafile(steam_id, password)
    if decrypted:
        print(f"✓ Mafile успешно расшифрован!")
        print(f"  Account Name: {decrypted.get('account_name')}")
        print(f"  Shared Secret: {decrypted.get('shared_secret')[:20]}...")
        return True
    else:
        print("✗ Ошибка при расшифровании")
        return False


def test_import_mafile():
    """Тест: Импорт mafile"""
    print("\n" + "="*60)
    print("ТЕСТ 4: Импорт mafile")
    print("="*60)
    
    guard = SteamGuardManager()
    
    accounts = guard.get_all_accounts()
    if not accounts:
        print("✗ Нет аккаунтов для тестирования")
        return False
    
    account = accounts[0]
    entry = guard.manifest.get_entry(account['steam_id'])
    mafile_path = os.path.join(guard.MAFILES_DIR, entry.filename)
    
    # Импортировать
    mafile_data = guard.import_mafile(mafile_path)
    
    if mafile_data:
        print("✓ Mafile успешно импортирован!")
        print(f"  Account: {mafile_data['account_name']}")
        print(f"  Steam ID: {mafile_data['steam_id']}")
        print(f"  Has Identity Secret: {bool(mafile_data['identity_secret'])}")
        print(f"  Revocation Code: {mafile_data['revocation_code']}")
        return True
    else:
        print("✗ Ошибка при импорте mafile")
        return False


def test_manifest_operations():
    """Тест: Операции с Manifest"""
    print("\n" + "="*60)
    print("ТЕСТ 5: Операции с Manifest")
    print("="*60)
    
    guard = SteamGuardManager()
    
    print(f"Всего аккаунтов: {len(guard.manifest.entries)}")
    print(f"Зашифрован: {guard.manifest.encrypted}")
    
    # Вывести все записи
    print("\nЗаписи в manifest:")
    for entry in guard.manifest.entries:
        is_encrypted = "🔒" if entry.salt else "🔓"
        print(f"  {is_encrypted} {entry.filename} (SteamID: {entry.steam_id})")
    
    return True


def test_confirmation_key():
    """Тест: Генерация ключа для подтверждений"""
    print("\n" + "="*60)
    print("ТЕСТ 6: Генерация ключа для подтверждений")
    print("="*60)
    
    guard = SteamGuardManager()
    
    accounts = guard.get_all_accounts()
    if not accounts:
        print("✗ Нет аккаунтов для тестирования")
        return False
    
    account = accounts[0]
    entry = guard.manifest.get_entry(account['steam_id'])
    mafile_path = os.path.join(guard.MAFILES_DIR, entry.filename)
    
    with open(mafile_path, 'r', encoding='utf-8') as f:
        mafile_data = json.load(f)
    
    identity_secret = mafile_data.get('identity_secret')
    if not identity_secret:
        print("✗ Нет identity_secret в mafile")
        return False
    
    # Получить ключ для подтверждений
    conf_key = guard.get_confirmation_key(identity_secret, tag="conf")
    
    print(f"✓ Confirmation Key (conf): {conf_key[:30]}...")
    
    # Для разных операций
    allow_key = guard.get_confirmation_key(identity_secret, tag="allow")
    deny_key = guard.get_confirmation_key(identity_secret, tag="deny")
    
    print(f"✓ Confirmation Key (allow): {allow_key[:30]}...")
    print(f"✓ Confirmation Key (deny): {deny_key[:30]}...")
    
    return True


def test_file_encryptor():
    """Тест: Утилиты шифрования файлов"""
    print("\n" + "="*60)
    print("ТЕСТ 7: FileEncryptor утилиты")
    print("="*60)
    
    password = "testpassword123"
    test_data = '{"account_name": "testuser", "shared_secret": "abc123"}'
    
    # Генерировать salt и IV
    salt = FileEncryptor.get_random_salt()
    iv = FileEncryptor.get_random_iv()
    
    print(f"✓ Salt: {salt}")
    print(f"✓ IV: {iv}")
    
    # Зашифровать
    encrypted = FileEncryptor.encrypt_data(password, salt, iv, test_data)
    if encrypted:
        print(f"✓ Encrypted: {encrypted[:50]}...")
    else:
        print("✗ Ошибка при шифровании (требуется cryptography)")
        return False
    
    # Расшифровать
    decrypted = FileEncryptor.decrypt_data(password, salt, iv, encrypted)
    if decrypted == test_data:
        print(f"✓ Decrypted успешно!")
        print(f"  Data: {decrypted}")
        return True
    else:
        print("✗ Ошибка при расшифровании")
        return False


def main():
    """Запустить все тесты"""
    print("\n" + "="*60)
    print("STEAM GUARD РЕАЛИЗАЦИЯ - ПОЛНЫЙ ТЕСТ")
    print("="*60)
    print("\nТестирование функционала на основе Steam Desktop Authenticator")
    print("Дополнительно использованы: steamguard, steampy")
    
    tests = [
        ("Добавление аккаунта", test_add_account_with_login),
        ("Steam Guard 2FA код", test_steam_guard_code),
        ("Manifest операции", test_manifest_operations),
        ("Шифрование mafile", test_mafile_encryption),
        ("Импорт mafile", test_import_mafile),
        ("Confirmation Key", test_confirmation_key),
        ("FileEncryptor", test_file_encryptor),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"\n✗ Исключение в тесте: {e}")
            results.append((test_name, False))
    
    # Итоги
    print("\n" + "="*60)
    print("ИТОГИ")
    print("="*60)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✓ PASSED" if success else "✗ FAILED"
        print(f"{status}: {test_name}")
    
    print(f"\nРезультат: {passed}/{total} тестов пройдено")
    
    if passed == total:
        print("✓ ВСЕ ТЕСТЫ ПРОЙДЕНЫ!")
    else:
        print(f"✗ {total - passed} тест(ов) провалено")
    
    print("\n" + "="*60)


if __name__ == "__main__":
    main()
