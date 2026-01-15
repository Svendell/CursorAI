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
    
    def test_totp_generation(self):
        """Тест генерации TOTP кода"""
        # Использовать известный shared secret для тестирования
        # Это должен быть валидный base64 encoded string
        shared_secret = base64.b64encode(b'0' * 20).decode('utf-8')
        
        code = SteamGuardUtil.generate_totp(shared_secret)
        
        # Код должен быть 5 символов и состоять из цифр
        self.assertEqual(len(code), 5)
        self.assertTrue(code.isdigit())
    
    def test_time_remaining(self):
        """Тест получения времени до смены кода"""
        time_remaining = SteamGuardUtil.get_code_time_remaining()
        
        self.assertGreater(time_remaining, 0)
        self.assertLessEqual(time_remaining, 30)
    
    def test_mafile_creation(self):
        """Тест создания mafile"""
        manager = SteamGuardManager()
        
        account_data = {
            'account_name': 'test_account',
            'shared_secret': base64.b64encode(b'0' * 20).decode('utf-8'),
            'identity_secret': base64.b64encode(b'0' * 20).decode('utf-8'),
            'revocation_code': 'TEST-CODE'
        }
        
        mafile_path = manager.create_mafile_from_dict(account_data)
        
        # Проверить что файл создан
        self.assertTrue(os.path.exists(mafile_path))
        
        # Проверить содержимое
        with open(mafile_path, 'r') as f:
            mafile = json.load(f)
        
        self.assertEqual(mafile['account_name'], 'test_account')
        self.assertEqual(mafile['shared_secret'], account_data['shared_secret'])
        
        # Очистка
        os.unlink(mafile_path)


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
