"""
Модуль для шифрования и безопасного хранения паролей
"""

import os
import base64
from Cryptodome.Cipher import AES
from Cryptodome.Random import get_random_bytes
from Cryptodome.Protocol.KDF import PBKDF2
import hashlib


class PasswordEncryption:
    """Шифрование паролей с использованием AES"""
    
    # Используется AES-256-CBC
    KEY_SIZE = 32  # 256 bits
    IV_SIZE = 16   # 128 bits
    ITERATIONS = 100000  # для PBKDF2
    
    @staticmethod
    def derive_key(password: str, salt: bytes) -> bytes:
        """
        Производит ключ из пароля используя PBKDF2
        
        Args:
            password: Мастер пароль пользователя
            salt: Salt для PBKDF2
        
        Returns:
            Производный ключ
        """
        return PBKDF2(
            password,
            salt,
            dkLen=PasswordEncryption.KEY_SIZE,
            count=PasswordEncryption.ITERATIONS,
            hmac_hash_module=hashlib.sha256
        )
    
    @staticmethod
    def encrypt(plaintext: str, master_password: str) -> str:
        """
        Шифрует текст используя мастер пароль
        
        Args:
            plaintext: Текст для шифрования
            master_password: Мастер пароль пользователя
        
        Returns:
            Base64 закодированный зашифрованный текст
        """
        # Генерировать salt и IV
        salt = get_random_bytes(16)
        iv = get_random_bytes(AES.block_size)
        
        # Производить ключ
        key = PasswordEncryption.derive_key(master_password, salt)
        
        # Шифровать
        cipher = AES.new(key, AES.MODE_CBC, iv)
        
        # Добавить padding
        plaintext_bytes = plaintext.encode('utf-8')
        padding_length = AES.block_size - (len(plaintext_bytes) % AES.block_size)
        plaintext_bytes += bytes([padding_length]) * padding_length
        
        ciphertext = cipher.encrypt(plaintext_bytes)
        
        # Комбинировать salt + iv + ciphertext и закодировать
        encrypted = salt + iv + ciphertext
        return base64.b64encode(encrypted).decode('utf-8')
    
    @staticmethod
    def decrypt(encrypted_text: str, master_password: str) -> str:
        """
        Расшифровывает текст используя мастер пароль
        
        Args:
            encrypted_text: Base64 закодированный зашифрованный текст
            master_password: Мастер пароль пользователя
        
        Returns:
            Исходный текст
        
        Raises:
            ValueError: Если расшифровка не удалась
        """
        try:
            # Декодировать из base64
            encrypted = base64.b64decode(encrypted_text)
            
            # Извлечь salt, iv и ciphertext
            salt = encrypted[:16]
            iv = encrypted[16:32]
            ciphertext = encrypted[32:]
            
            # Производить ключ
            key = PasswordEncryption.derive_key(master_password, salt)
            
            # Расшифровать
            cipher = AES.new(key, AES.MODE_CBC, iv)
            plaintext_bytes = cipher.decrypt(ciphertext)
            
            # Удалить padding
            padding_length = plaintext_bytes[-1]
            plaintext_bytes = plaintext_bytes[:-padding_length]
            
            return plaintext_bytes.decode('utf-8')
        except Exception as e:
            raise ValueError(f"Ошибка при расшифровке: {e}")


class SecureStorage:
    """Безопасное хранилище для паролей и секретов"""
    
    def __init__(self, master_password: str):
        """
        Инициализирует хранилище с мастер паролем
        
        Args:
            master_password: Мастер пароль для шифрования
        """
        self.master_password = master_password
    
    def encrypt_password(self, password: str) -> str:
        """Шифрует пароль"""
        return PasswordEncryption.encrypt(password, self.master_password)
    
    def decrypt_password(self, encrypted_password: str) -> str:
        """Расшифровывает пароль"""
        return PasswordEncryption.decrypt(encrypted_password, self.master_password)
    
    def encrypt_secret(self, secret: str) -> str:
        """Шифрует secret"""
        return PasswordEncryption.encrypt(secret, self.master_password)
    
    def decrypt_secret(self, encrypted_secret: str) -> str:
        """Расшифровывает secret"""
        return PasswordEncryption.decrypt(encrypted_secret, self.master_password)


# Функции для тестирования
def test_encryption():
    """Тестирует функции шифрования"""
    master_password = "test_master_password"
    
    # Тестировать шифрование
    plaintext = "my_secret_password"
    encrypted = PasswordEncryption.encrypt(plaintext, master_password)
    decrypted = PasswordEncryption.decrypt(encrypted, master_password)
    
    print(f"Original: {plaintext}")
    print(f"Encrypted: {encrypted}")
    print(f"Decrypted: {decrypted}")
    print(f"Match: {plaintext == decrypted}")
    
    # Тестировать SecureStorage
    storage = SecureStorage(master_password)
    stored = storage.encrypt_password("test123")
    retrieved = storage.decrypt_password(stored)
    print(f"Storage test: {retrieved == 'test123'}")


if __name__ == '__main__':
    test_encryption()
