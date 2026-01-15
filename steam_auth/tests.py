#!/usr/bin/env python3
"""
Тесты для приложения Steam Auth Manager
"""

import unittest
import os
import tempfile
import json
import base64
from app.database import Database
from app.steam_guard import SteamGuardManager, MafileCreator
from app.steam_utils import SteamGuardUtil, MafileValidator, SteamIDConverter
from app.config import Config
from app.encryption import PasswordEncryption


class TestDatabase(unittest.TestCase):
    """Тесты для базы данных"""
    
    def setUp(self):
        """Подготовка к тесту"""
        # Использовать временную БД для тестов
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        self.db = Database(self.temp_db.name)
    
    def tearDown(self):
        """Очистка после теста"""
        if os.path.exists(self.temp_db.name):
            os.unlink(self.temp_db.name)
    
    def test_add_account(self):
        """Тест добавления аккаунта"""
        account_id = self.db.add_account(
            'test_account',
            'test_password',
            'dGVzdF9zaGFyZWRfc2VjcmV0'  # base64
        )
        self.assertIsNotNone(account_id)
        self.assertGreater(account_id, 0)
    
    def test_get_account(self):
        """Тест получения аккаунта"""
        account_id = self.db.add_account(
            'test_account',
            'test_password',
            'dGVzdF9zaGFyZWRfc2VjcmV0'
        )
        
        account = self.db.get_account(account_id)
        self.assertIsNotNone(account)
        self.assertEqual(account['account_name'], 'test_account')
        self.assertEqual(account['password'], 'test_password')
    
    def test_update_account(self):
        """Тест обновления аккаунта"""
        account_id = self.db.add_account(
            'test_account',
            'test_password',
            'dGVzdF9zaGFyZWRfc2VjcmV0'
        )
        
        updated = self.db.update_account(
            account_id,
            account_name='new_account_name',
            password='new_password'
        )
        self.assertTrue(updated)
        
        account = self.db.get_account(account_id)
        self.assertEqual(account['account_name'], 'new_account_name')
        self.assertEqual(account['password'], 'new_password')
    
    def test_delete_account(self):
        """Тест удаления аккаунта"""
        account_id = self.db.add_account(
            'test_account',
            'test_password',
            'dGVzdF9zaGFyZWRfc2VjcmV0'
        )
        
        deleted = self.db.delete_account(account_id)
        self.assertTrue(deleted)
        
        account = self.db.get_account(account_id)
        self.assertIsNone(account)
    
    def test_count_accounts(self):
        """Тест подсчета аккаунтов"""
        initial_count = self.db.count_accounts()
        
        self.db.add_account('account1', 'pass1', 'secret1')
        self.db.add_account('account2', 'pass2', 'secret2')
        
        final_count = self.db.count_accounts()
        self.assertEqual(final_count, initial_count + 2)


class TestSteamGuard(unittest.TestCase):
    """Тесты для Steam Guard"""
    
    def setUp(self):
        """Подготовка к тесту"""
        self.manager = SteamGuardManager()
        # Создать valid 20-байт secret для тестирования
        self.shared_secret_bytes = b'test_secret_20bytes'  # 19 байт, добавим 1
        self.shared_secret = base64.b64encode(b'0' * 20).decode('utf-8')
        self.identity_secret = base64.b64encode(b'0' * 32).decode('utf-8')
    
    def test_totp_generation(self):
        """Тест генерации TOTP кода"""
        # Код должен быть 5 символов и состоять из цифр
        code, time_left = self.manager.get_steam_guard_code(self.shared_secret)
        
        self.assertEqual(len(code), 5)
        self.assertTrue(code.isdigit())
        self.assertGreater(time_left, 0)
        self.assertLessEqual(time_left, 30)
    
    def test_totp_consistency(self):
        """Тест что один и тот же код генерируется в один временной интервал"""
        import time
        timestamp = int(time.time())
        
        code1, _ = self.manager.get_steam_guard_code(self.shared_secret, timestamp)
        code2, _ = self.manager.get_steam_guard_code(self.shared_secret, timestamp)
        
        # Коды должны быть идентичны при одном временном интервале
        self.assertEqual(code1, code2)
    
    def test_totp_different_intervals(self):
        """Тест что коды разные в разные временные интервалы"""
        import time
        timestamp = int(time.time())
        
        code1, _ = self.manager.get_steam_guard_code(self.shared_secret, timestamp)
        code2, _ = self.manager.get_steam_guard_code(self.shared_secret, timestamp + 30)
        
        # Коды должны быть разные в разных 30-секундных интервалах
        self.assertNotEqual(code1, code2)
    
    def test_confirmation_hash(self):
        """Тест получения confirmation hash"""
        import time
        timestamp = int(time.time())
        
        hash_conf = self.manager.get_confirmation_hash(timestamp, self.identity_secret, "conf")
        
        # Hash должен быть base64 encoded
        self.assertTrue(all(c in 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=' for c in hash_conf))
        self.assertGreater(len(hash_conf), 0)
    
    def test_confirmation_hash_different_tags(self):
        """Тест что разные теги дают разные хеши"""
        import time
        timestamp = int(time.time())
        
        hash1 = self.manager.get_confirmation_hash(timestamp, self.identity_secret, "conf")
        hash2 = self.manager.get_confirmation_hash(timestamp, self.identity_secret, "allow")
        
        # Разные теги должны давать разные хеши
        self.assertNotEqual(hash1, hash2)
    
    def test_mafile_creation(self):
        """Тест создания mafile"""
        account_data = {
            'account_name': 'test_account',
            'shared_secret': self.shared_secret,
            'identity_secret': self.identity_secret,
            'revocation_code': 'TEST-CODE'
        }
        
        mafile_path = self.manager.create_mafile_from_dict(account_data)
        
        try:
            # Проверить что файл создан
            self.assertTrue(os.path.exists(mafile_path))
            
            # Проверить содержимое
            with open(mafile_path, 'r') as f:
                mafile = json.load(f)
            
            self.assertEqual(mafile['account_name'], 'test_account')
            self.assertEqual(mafile['shared_secret'], self.shared_secret)
            self.assertEqual(mafile['identity_secret'], self.identity_secret)
            self.assertEqual(mafile['revocation_code'], 'TEST-CODE')
            self.assertTrue(mafile['fully_enrolled'])
        finally:
            # Очистка
            if os.path.exists(mafile_path):
                os.unlink(mafile_path)
    
    def test_mafile_creation_minimal(self):
        """Тест создания минимального mafile (только обязательные поля)"""
        account_data = {
            'account_name': 'minimal_account',
            'shared_secret': self.shared_secret
        }
        
        mafile_path = self.manager.create_mafile_from_dict(account_data)
        
        try:
            with open(mafile_path, 'r') as f:
                mafile = json.load(f)
            
            # Обязательные поля должны присутствовать
            self.assertIn('shared_secret', mafile)
            self.assertIn('account_name', mafile)
            
            # Опциональные поля должны быть пустыми или по умолчанию
            self.assertEqual(mafile['identity_secret'], '')
            self.assertEqual(mafile['revocation_code'], '')
        finally:
            if os.path.exists(mafile_path):
                os.unlink(mafile_path)
    
    def test_invalid_shared_secret(self):
        """Тест на ошибку при неверном shared_secret"""
        account_data = {
            'account_name': 'test',
            'shared_secret': ''  # Пусто
        }
        
        with self.assertRaises(ValueError):
            self.manager.create_mafile_from_dict(account_data)
    
    def test_import_mafile(self):
        """Тест импорта mafile"""
        # Создать mafile
        account_data = {
            'account_name': 'import_test',
            'shared_secret': self.shared_secret,
            'identity_secret': self.identity_secret,
            'revocation_code': 'IMPORT-CODE'
        }
        
        mafile_path = self.manager.create_mafile_from_dict(account_data)
        
        try:
            # Импортировать его обратно
            imported_data = self.manager.import_mafile(mafile_path)
            
            self.assertIsNotNone(imported_data)
            self.assertEqual(imported_data['account_name'], 'import_test')
            self.assertEqual(imported_data['shared_secret'], self.shared_secret)
            self.assertEqual(imported_data['identity_secret'], self.identity_secret)
            self.assertEqual(imported_data['revocation_code'], 'IMPORT-CODE')
        finally:
            if os.path.exists(mafile_path):
                os.unlink(mafile_path)
    
    def test_get_steam_guard_code_only(self):
        """Тест быстрого метода получения кода"""
        code = self.manager.get_steam_guard_code_only(self.shared_secret)
        
        self.assertEqual(len(code), 5)
        self.assertTrue(code.isdigit())


class TestMafileValidator(unittest.TestCase):
    """Тесты для валидации mafile"""
    
    def test_valid_mafile(self):
        """Тест валидного mafile"""
        mafile = {
            'shared_secret': base64.b64encode(b'0' * 20).decode('utf-8'),
            'account_name': 'test_account'
        }
        
        self.assertTrue(MafileValidator.validate_mafile(mafile))
    
    def test_invalid_mafile_missing_field(self):
        """Тест невалидного mafile (отсутствует поле)"""
        mafile = {
            'shared_secret': base64.b64encode(b'0' * 20).decode('utf-8')
        }
        
        self.assertFalse(MafileValidator.validate_mafile(mafile))
    
    def test_invalid_mafile_bad_base64(self):
        """Тест невалидного mafile (плохой base64)"""
        mafile = {
            'shared_secret': 'not_valid_base64!!!',
            'account_name': 'test_account'
        }
        
        self.assertFalse(MafileValidator.validate_mafile(mafile))


class TestMafileCreator(unittest.TestCase):
    """Тесты для MafileCreator"""
    
    def setUp(self):
        """Подготовка к тесту"""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        self.db = Database(self.temp_db.name)
        self.creator = MafileCreator(self.db)
        
        # Добавить тестовый аккаунт в БД
        self.shared_secret = base64.b64encode(b'0' * 20).decode('utf-8')
        self.identity_secret = base64.b64encode(b'0' * 32).decode('utf-8')
        self.account_id = self.db.add_account(
            'test_account',
            'test_password',
            self.shared_secret,
            self.identity_secret,
            'TEST-CODE'
        )
    
    def tearDown(self):
        """Очистка после теста"""
        if os.path.exists(self.temp_db.name):
            os.unlink(self.temp_db.name)
    
    def test_create_mafile_from_account(self):
        """Тест создания mafile из данных аккаунта"""
        mafile_path = self.creator.create_mafile_from_account(self.account_id)
        
        try:
            self.assertTrue(os.path.exists(mafile_path))
            
            with open(mafile_path, 'r') as f:
                mafile = json.load(f)
            
            self.assertEqual(mafile['account_name'], 'test_account')
            self.assertEqual(mafile['shared_secret'], self.shared_secret)
        finally:
            if os.path.exists(mafile_path):
                os.unlink(mafile_path)
    
    def test_get_2fa_code(self):
        """Тест получения 2FA кода для аккаунта"""
        code, time_left = self.creator.get_2fa_code(self.account_id)
        
        self.assertEqual(len(code), 5)
        self.assertTrue(code.isdigit())
        self.assertGreater(time_left, 0)
        self.assertLessEqual(time_left, 30)
    
    def test_validate_mafile_valid(self):
        """Тест валидации корректного mafile"""
        mafile_path = self.creator.create_mafile_from_account(self.account_id)
        
        try:
            is_valid = self.creator.validate_mafile(mafile_path)
            self.assertTrue(is_valid)
        finally:
            if os.path.exists(mafile_path):
                os.unlink(mafile_path)
    
    def test_validate_mafile_invalid(self):
        """Тест валидации некорректного mafile"""
        # Создать невалидный mafile
        temp_mafile = tempfile.NamedTemporaryFile(mode='w', suffix='.maFile', delete=False)
        json.dump({'account_name': 'test'}, temp_mafile)
        temp_mafile.close()
        
        try:
            with self.assertRaises(ValueError):
                self.creator.validate_mafile(temp_mafile.name)
        finally:
            if os.path.exists(temp_mafile.name):
                os.unlink(temp_mafile.name)
    
    def test_list_mafiles(self):
        """Тест получения списка mafiles"""
        mafile_path = self.creator.create_mafile_from_account(self.account_id)
        
        try:
            mafiles = self.creator.list_mafiles()
            
            self.assertGreater(len(mafiles), 0)
            self.assertTrue(any(mf['account_name'] == 'test_account' for mf in mafiles))
        finally:
            if os.path.exists(mafile_path):
                os.unlink(mafile_path)
    
    def test_delete_mafile(self):
        """Тест удаления mafile"""
        mafile_path = self.creator.create_mafile_from_account(self.account_id)
        
        self.assertTrue(os.path.exists(mafile_path))
        
        # Удалить mafile
        deleted = self.creator.delete_mafile('test_account')
        self.assertTrue(deleted)
        self.assertFalse(os.path.exists(mafile_path))


class TestPasswordEncryption(unittest.TestCase):
    """Тесты для шифрования паролей"""
    
    def test_encrypt_decrypt(self):
        """Тест шифрования и расшифровки"""
        master_password = 'my_master_password'
        plaintext = 'my_secret_password'
        
        encrypted = PasswordEncryption.encrypt(plaintext, master_password)
        decrypted = PasswordEncryption.decrypt(encrypted, master_password)
        
        self.assertEqual(plaintext, decrypted)
    
    def test_wrong_password_decryption(self):
        """Тест расшифровки с неправильным паролем"""
        master_password = 'my_master_password'
        wrong_password = 'wrong_password'
        plaintext = 'my_secret_password'
        
        encrypted = PasswordEncryption.encrypt(plaintext, master_password)
        
        # Должна выбросить исключение
        with self.assertRaises(ValueError):
            PasswordEncryption.decrypt(encrypted, wrong_password)


class TestSteamIDConverter(unittest.TestCase):
    """Тесты для конвертации SteamID"""
    
    def test_to_64bit(self):
        """Тест конвертации в 64-bit"""
        steam_id = 'STEAM_0:1:123456'
        steam_id_64 = SteamIDConverter.to_64bit(steam_id)
        
        self.assertGreater(steam_id_64, 0)
        self.assertIsInstance(steam_id_64, int)
    
    def test_from_64bit(self):
        """Тест конвертации из 64-bit"""
        steam_id_64 = 76561198246875681
        steam_id = SteamIDConverter.from_64bit(steam_id_64)
        
        self.assertTrue(steam_id.startswith('STEAM_'))


class TestConfig(unittest.TestCase):
    """Тесты для конфигурации"""
    
    def setUp(self):
        """Подготовка к тесту"""
        self.temp_config = tempfile.NamedTemporaryFile(delete=False, suffix='.ini')
        self.temp_config.close()
        self.config = Config(self.temp_config.name)
    
    def tearDown(self):
        """Очистка после теста"""
        if os.path.exists(self.temp_config.name):
            os.unlink(self.temp_config.name)
    
    def test_get_default_value(self):
        """Тест получения значения по умолчанию"""
        value = self.config.get('APP', 'name')
        self.assertIsNotNone(value)
        self.assertEqual(value, 'Steam Auth Manager')
    
    def test_get_int(self):
        """Тест получения целого числа"""
        value = self.config.get_int('UI', 'window_width')
        self.assertEqual(value, 360)
        self.assertIsInstance(value, int)
    
    def test_get_bool(self):
        """Тест получения булева значения"""
        value = self.config.get_bool('SECURITY', 'encrypt_passwords')
        self.assertFalse(value)
        self.assertIsInstance(value, bool)
    
    def test_set_value(self):
        """Тест установки значения"""
        self.config.set('TEST', 'option', 'value')
        value = self.config.get('TEST', 'option')
        self.assertEqual(value, 'value')


def run_tests():
    """Запустить все тесты"""
    # Создать набор тестов
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Добавить все тесты
    suite.addTests(loader.loadTestsFromTestCase(TestDatabase))
    suite.addTests(loader.loadTestsFromTestCase(TestSteamGuard))
    suite.addTests(loader.loadTestsFromTestCase(TestMafileCreator))
    suite.addTests(loader.loadTestsFromTestCase(TestMafileValidator))
    suite.addTests(loader.loadTestsFromTestCase(TestPasswordEncryption))
    suite.addTests(loader.loadTestsFromTestCase(TestSteamIDConverter))
    suite.addTests(loader.loadTestsFromTestCase(TestConfig))
    
    # Запустить тесты
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result


if __name__ == '__main__':
    result = run_tests()
    exit(0 if result.wasSuccessful() else 1)
