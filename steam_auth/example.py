#!/usr/bin/env python3
"""
Пример использования приложения Steam Auth Manager
"""

import sys
import os

# Добавить текущую папку в path
sys.path.insert(0, os.path.dirname(__file__))

from app.database import Database
from app.steam_guard import SteamGuardManager, MafileCreator
from app.steam_utils import SteamGuardUtil, MafileValidator


def example_add_account():
    """Пример добавления аккаунта вручную"""
    print("=== Добавление аккаунта ===")
    
    db = Database()
    
    # Пример данных
    account_name = "my_steam_account"
    password = "my_password"
    shared_secret = "base64_encoded_shared_secret_here"  # Это должен быть реальный shared secret
    
    try:
        account_id = db.add_account(account_name, password, shared_secret)
        print(f"✓ Аккаунт добавлен с ID: {account_id}")
    except Exception as e:
        print(f"✗ Ошибка: {e}")


def example_get_totp_code():
    """Пример получения TOTP кода"""
    print("\n=== Получение 2FA кода ===")
    
    # Это должен быть реальный shared secret в base64
    shared_secret = "base64_shared_secret_here"
    
    try:
        code = SteamGuardUtil.generate_totp(shared_secret)
        time_remaining = SteamGuardUtil.get_code_time_remaining()
        print(f"2FA код: {code}")
        print(f"Осталось секунд: {time_remaining}")
    except Exception as e:
        print(f"✗ Ошибка: {e}")


def example_list_accounts():
    """Пример получения списка всех аккаунтов"""
    print("\n=== Список аккаунтов ===")
    
    db = Database()
    accounts = db.get_all_accounts()
    
    if accounts:
        for account in accounts:
            print(f"- {account['account_name']} (ID: {account['id']})")
            print(f"  Создан: {account['created_at']}")
    else:
        print("Аккаунтов не найдено")


def example_create_mafile():
    """Пример создания mafile"""
    print("\n=== Создание Mafile ===")
    
    db = Database()
    guard_manager = SteamGuardManager()
    
    # Пример добавления аккаунта и создания mafile
    account_name = "test_account"
    password = "test_password"
    shared_secret = "base64_shared_secret_here"
    identity_secret = "base64_identity_secret_here"
    
    try:
        # Добавить аккаунт
        account_id = db.add_account(
            account_name,
            password,
            shared_secret,
            identity_secret
        )
        
        # Получить аккаунт
        account = db.get_account(account_id)
        
        # Создать mafile
        mafile_path = guard_manager.create_mafile_from_dict(account)
        print(f"✓ Mafile создан: {mafile_path}")
        
        # Показать содержимое
        import json
        with open(mafile_path, 'r') as f:
            mafile_data = json.load(f)
        print(f"Содержимое mafile:")
        print(json.dumps(mafile_data, indent=2))
        
    except Exception as e:
        print(f"✗ Ошибка: {e}")


def example_import_mafile():
    """Пример импорта mafile"""
    print("\n=== Импорт Mafile ===")
    
    db = Database()
    mafile_creator = MafileCreator(db)
    
    # Путь к mafile (измените на реальный путь)
    mafile_path = "/path/to/mafile.maFile"
    password = "account_password"
    
    try:
        account_id = mafile_creator.import_and_add_account(mafile_path, password)
        if account_id:
            print(f"✓ Mafile импортирован, ID аккаунта: {account_id}")
        else:
            print("✗ Ошибка при импорте mafile")
    except Exception as e:
        print(f"✗ Ошибка: {e}")


def example_validate_mafile():
    """Пример валидации mafile"""
    print("\n=== Валидация Mafile ===")
    
    # Корректный mafile
    valid_mafile = {
        'shared_secret': 'dGhpcyBpcyBhIGJhc2U2NCBlbmNvZGVkIHN0cmluZw==',  # base64
        'identity_secret': 'dGhpcyBpcyBhIGJhc2U2NCBlbmNvZGVkIHN0cmluZw==',
        'account_name': 'test_account'
    }
    
    # Некорректный mafile (отсутствует поле)
    invalid_mafile = {
        'shared_secret': 'dGhpcyBpcyBhIGJhc2U2NCBlbmNvZGVkIHN0cmluZw=='
    }
    
    if MafileValidator.validate_mafile(valid_mafile):
        print("✓ Валидный mafile")
    else:
        print("✗ Невалидный mafile")
    
    if MafileValidator.validate_mafile(invalid_mafile):
        print("✓ Валидный mafile")
    else:
        print("✗ Невалидный mafile (ожидаемо)")


def show_help():
    """Показать справку"""
    print("""
Steam Auth Manager - Примеры использования

Использование:
    python example.py [команда]

Доступные команды:
    add          - Добавить аккаунт
    list         - Список аккаунтов
    totp         - Получить 2FA код
    create       - Создать mafile
    import       - Импортировать mafile
    validate     - Валидировать mafile
    all          - Запустить все примеры
    help         - Показать эту справку

Примеры:
    python example.py add      # Добавить новый аккаунт
    python example.py list     # Показать все аккаунты
    python example.py all      # Запустить все примеры
    """)


def main():
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == 'add':
            example_add_account()
        elif command == 'list':
            example_list_accounts()
        elif command == 'totp':
            example_get_totp_code()
        elif command == 'create':
            example_create_mafile()
        elif command == 'import':
            example_import_mafile()
        elif command == 'validate':
            example_validate_mafile()
        elif command == 'all':
            example_list_accounts()
            example_validate_mafile()
            example_get_totp_code()
        elif command == 'help':
            show_help()
        else:
            print(f"Неизвестная команда: {command}")
            show_help()
    else:
        show_help()


if __name__ == '__main__':
    main()
