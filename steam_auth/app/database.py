import sqlite3
import os
import json
from typing import List, Dict, Optional, Any

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'accounts.db')


class Database:
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self.init_db()

    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self):
        """Инициализировать базу данных"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Таблица для аккаунтов
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS accounts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                account_name TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                shared_secret TEXT NOT NULL,
                identity_secret TEXT,
                revocation_code TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()

    def add_account(self, account_name: str, password: str, shared_secret: str,
                   identity_secret: Optional[str] = None,
                   revocation_code: Optional[str] = None) -> int:
        """Добавить новый аккаунт"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO accounts (account_name, password, shared_secret, identity_secret, revocation_code)
                VALUES (?, ?, ?, ?, ?)
            ''', (account_name, password, shared_secret, identity_secret, revocation_code))
            conn.commit()
            account_id = cursor.lastrowid
            return account_id
        finally:
            conn.close()

    def get_account(self, account_id: int) -> Optional[Dict[str, Any]]:
        """Получить аккаунт по ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM accounts WHERE id = ?', (account_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return dict(row)
        return None

    def get_account_by_name(self, account_name: str) -> Optional[Dict[str, Any]]:
        """Получить аккаунт по имени"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM accounts WHERE account_name = ?', (account_name,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return dict(row)
        return None

    def get_all_accounts(self) -> List[Dict[str, Any]]:
        """Получить все аккаунты"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM accounts ORDER BY created_at DESC')
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]

    def update_account(self, account_id: int, account_name: Optional[str] = None,
                      password: Optional[str] = None, shared_secret: Optional[str] = None) -> bool:
        """Обновить данные аккаунта"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            updates = []
            params = []
            
            if account_name is not None:
                updates.append('account_name = ?')
                params.append(account_name)
            if password is not None:
                updates.append('password = ?')
                params.append(password)
            if shared_secret is not None:
                updates.append('shared_secret = ?')
                params.append(shared_secret)
            
            if not updates:
                return False
            
            updates.append('updated_at = CURRENT_TIMESTAMP')
            params.append(account_id)
            
            query = f'UPDATE accounts SET {", ".join(updates)} WHERE id = ?'
            cursor.execute(query, params)
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()

    def delete_account(self, account_id: int) -> bool:
        """Удалить аккаунт"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('DELETE FROM accounts WHERE id = ?', (account_id,))
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()

    def count_accounts(self) -> int:
        """Подсчитать количество аккаунтов"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM accounts')
        count = cursor.fetchone()[0]
        conn.close()
        
        return count
