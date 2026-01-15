"""
Steam Authentication Module
Handles Steam login and 2FA process for mafile creation
"""

import json
import base64
import hmac
import hashlib
import requests
import time
from typing import Dict, Optional, Tuple
from enum import Enum


class AuthStatus(Enum):
    """Authentication status enumeration"""
    IDLE = "idle"
    LOGGING_IN = "logging_in"
    EMAIL_CODE_NEEDED = "email_code_needed"
    SMS_CODE_NEEDED = "sms_code_needed"
    AUTHENTICATOR_CODE_NEEDED = "authenticator_code_needed"
    DEVICE_CONFIRMATION_NEEDED = "device_confirmation_needed"
    SUCCESS = "success"
    FAILED = "failed"


class SteamAuthenticator:
    """Steam authenticator for mafile creation (SDA-like flow)"""
    
    STEAM_API_BASE = "https://steamcommunity.com"
    LOGIN_ENDPOINT = "/login"
    
    def __init__(self):
        self.session = requests.Session()
        self.account_name = ""
        self.password = ""
        self.steam_id = 0
        self.shared_secret = ""
        self.identity_secret = ""
        self.revocation_code = ""
        self.refresh_token = ""
        self.access_token = ""
        self.status = AuthStatus.IDLE
        self.confirmation_method = None  # "email" or "sms"
        self.email_domain = ""
    
    def login(self, account_name: str, password: str) -> Tuple[bool, str]:
        """
        Step 1: Initial login attempt
        
        Args:
            account_name: Steam account name
            password: Steam account password
        
        Returns:
            (success, message) - If success=False and message contains "code_needed",
                                need to call send_code()
        """
        self.account_name = account_name
        self.password = password
        self.status = AuthStatus.LOGGING_IN
        
        try:
            # В реальном приложении здесь была бы настоящая авторизация Steam
            # Для демо используем симуляцию
            
            # Проверить валидность логина
            if not account_name or not password:
                return False, "Invalid credentials"
            
            # Симуляция проверки Steam
            if len(account_name) < 3 or len(password) < 5:
                return False, "Invalid account name or password format"
            
            # Симуляция необходимости двухфакторной аутентификации
            # В реальности Steam вернет нужный метод
            self.confirmation_method = "email"
            self.email_domain = "email.steampowered.com"
            self.status = AuthStatus.EMAIL_CODE_NEEDED
            
            return False, "code_needed:email"
            
        except Exception as e:
            self.status = AuthStatus.FAILED
            return False, f"Login failed: {str(e)}"
    
    def send_code(self) -> Tuple[bool, str]:
        """
        Step 2: Request confirmation code
        
        Returns:
            (success, message)
        """
        try:
            if self.status == AuthStatus.IDLE:
                return False, "No login in progress"
            
            # В реальном приложении здесь отправляется код на email/SMS
            # Для демо просто имитируем отправку
            
            if self.confirmation_method == "email":
                return True, f"Code sent to your email ({self.email_domain})"
            elif self.confirmation_method == "sms":
                return True, "Code sent to your phone"
            else:
                return True, "Confirmation code sent"
                
        except Exception as e:
            return False, f"Failed to send code: {str(e)}"
    
    def confirm_code(self, code: str) -> Tuple[bool, str]:
        """
        Step 3: Confirm the code received
        
        Args:
            code: Confirmation code from email/SMS
        
        Returns:
            (success, message)
        """
        try:
            if not code or len(code) < 5:
                return False, "Invalid code format"
            
            # Валидация кода
            if not code.isalnum():
                return False, "Code must contain only letters and numbers"
            
            # В реальном приложении здесь проверяется код на Steam
            # Для демо проверяем длину и тип
            if len(code) >= 5:
                # Симуляция успешного подтверждения
                self.status = AuthStatus.SUCCESS
                
                # Генерировать симуляционные secrets
                # В реальном приложении эти данные придут от Steam
                self._generate_secrets()
                
                return True, "Code confirmed successfully! Mafile created."
            else:
                return False, "Invalid code"
                
        except Exception as e:
            self.status = AuthStatus.FAILED
            return False, f"Code confirmation failed: {str(e)}"
    
    def confirm_device(self) -> Tuple[bool, str]:
        """
        Step 4 (Alternative): Device confirmation for app-based 2FA
        
        Returns:
            (success, message)
        """
        try:
            # В реальном приложении здесь используется Steam мобильное приложение
            # Для демо просто имитируем подтверждение
            
            self.status = AuthStatus.SUCCESS
            self._generate_secrets()
            
            return True, "Device confirmed! Mafile created."
            
        except Exception as e:
            self.status = AuthStatus.FAILED
            return False, f"Device confirmation failed: {str(e)}"
    
    def _generate_secrets(self):
        """
        Generate shared_secret and identity_secret
        In real app, these come from Steam after successful auth
        """
        # Генерировать random secrets (в реальном приложении они от Steam)
        import os
        import base64
        
        # Генерировать 20 байт для shared_secret
        shared_secret_bytes = os.urandom(20)
        self.shared_secret = base64.b64encode(shared_secret_bytes).decode('utf-8')
        
        # Генерировать 20 байт для identity_secret
        identity_secret_bytes = os.urandom(20)
        self.identity_secret = base64.b64encode(identity_secret_bytes).decode('utf-8')
        
        # Генерировать revocation_code
        self.revocation_code = self._generate_revocation_code()
        
        # Генерировать steam_id (обычно из account_name)
        self.steam_id = self._generate_steam_id_from_username()
    
    def _generate_revocation_code(self) -> str:
        """Generate a revocation code"""
        import random
        import string
        
        chars = string.ascii_uppercase + string.digits
        # Формат: XXXXX-XXXXX-XXXXX
        code = '-'.join(
            ''.join(random.choice(chars) for _ in range(5))
            for _ in range(3)
        )
        return code
    
    def _generate_steam_id_from_username(self) -> int:
        """
        Generate a valid Steam ID from username
        Format: 32-bit number
        """
        import hashlib
        
        # Использовать hash username для генерации ID
        hash_obj = hashlib.md5(self.account_name.encode())
        hash_int = int(hash_obj.hexdigest(), 16)
        
        # Сохранить только 32 бита и добавить базовое смещение Steam
        steam_id_32 = hash_int & 0xffffffff
        # Конвертировать в 64-bit Steam ID
        steam_id_64 = (steam_id_32 & 0xffffffff) | 0x0110000100000000
        
        return steam_id_64
    
    def get_mafile_data(self) -> Optional[Dict]:
        """
        Get mafile data if authentication succeeded
        
        Returns:
            Dictionary with mafile data or None if not authenticated
        """
        if self.status != AuthStatus.SUCCESS:
            return None
        
        return {
            'account_name': self.account_name,
            'shared_secret': self.shared_secret,
            'identity_secret': self.identity_secret,
            'revocation_code': self.revocation_code,
            'steam_id': self.steam_id,
            'uri': '',
            'server_time': int(time.time()),
            'account_name_hmac': '',
            'session_id': '',
            'fully_enrolled': True
        }
    
    def reset(self):
        """Reset authentication state"""
        self.account_name = ""
        self.password = ""
        self.steam_id = 0
        self.shared_secret = ""
        self.identity_secret = ""
        self.revocation_code = ""
        self.refresh_token = ""
        self.access_token = ""
        self.status = AuthStatus.IDLE
        self.confirmation_method = None
        self.email_domain = ""


class SteamLoginValidator:
    """Validator for Steam login credentials"""
    
    @staticmethod
    def validate_account_name(account_name: str) -> Tuple[bool, str]:
        """
        Validate Steam account name
        
        Args:
            account_name: Steam account name
        
        Returns:
            (is_valid, error_message)
        """
        if not account_name:
            return False, "Account name is required"
        
        if len(account_name) < 3:
            return False, "Account name must be at least 3 characters"
        
        if len(account_name) > 32:
            return False, "Account name must be at most 32 characters"
        
        # Allow alphanumeric, underscore, and hyphen
        allowed_chars = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-")
        if not all(c in allowed_chars for c in account_name):
            return False, "Account name contains invalid characters"
        
        return True, ""
    
    @staticmethod
    def validate_password(password: str) -> Tuple[bool, str]:
        """
        Validate Steam password
        
        Args:
            password: Steam account password
        
        Returns:
            (is_valid, error_message)
        """
        if not password:
            return False, "Password is required"
        
        if len(password) < 5:
            return False, "Password must be at least 5 characters"
        
        if len(password) > 120:
            return False, "Password must be at most 120 characters"
        
        return True, ""
    
    @staticmethod
    def validate_confirmation_code(code: str) -> Tuple[bool, str]:
        """
        Validate confirmation code
        
        Args:
            code: Code from email/SMS
        
        Returns:
            (is_valid, error_message)
        """
        if not code:
            return False, "Code is required"
        
        if len(code) < 5:
            return False, "Code must be at least 5 characters"
        
        if len(code) > 10:
            return False, "Code must be at most 10 characters"
        
        if not code.isalnum():
            return False, "Code must contain only letters and numbers"
        
        return True, ""


# Global authenticator instance
_auth_instance = None


def get_authenticator() -> SteamAuthenticator:
    """Get global authenticator instance"""
    global _auth_instance
    if _auth_instance is None:
        _auth_instance = SteamAuthenticator()
    return _auth_instance
