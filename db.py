import sqlite3
import os
import time

DB_PATH = os.path.join(os.path.dirname(__file__), 'accounts.db')

class Database:
    def __init__(self, path=DB_PATH):
        self.path = path
        self._ensure()

    def _conn(self):
        return sqlite3.connect(self.path)

    def _ensure(self):
        with self._conn() as c:
            cur = c.cursor()
            cur.execute('''
            CREATE TABLE IF NOT EXISTS accounts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                account_name TEXT NOT NULL,
                password TEXT,
                shared_secret TEXT,
                identity_secret TEXT,
                session_data TEXT,
                created_at INTEGER,
                mafile_path TEXT
            )
            ''')
            c.commit()
            # migrate: add columns if missing (for older DBs)
            cur.execute("PRAGMA table_info(accounts)")
            cols = [r[1] for r in cur.fetchall()]
            if 'identity_secret' not in cols:
                cur.execute('ALTER TABLE accounts ADD COLUMN identity_secret TEXT')
            if 'session_data' not in cols:
                cur.execute('ALTER TABLE accounts ADD COLUMN session_data TEXT')
            c.commit()

    def add_account(self, account_name, password, shared_secret, identity_secret=None):
        ts = int(time.time())
        with self._conn() as c:
            cur = c.cursor()
            cur.execute('INSERT INTO accounts (account_name, password, shared_secret, identity_secret, created_at) VALUES (?,?,?,?,?)',
                        (account_name, password, shared_secret, identity_secret, ts))
            c.commit()
            return cur.lastrowid

    def set_mafile_path(self, acc_id, path):
        with self._conn() as c:
            cur = c.cursor()
            cur.execute('UPDATE accounts SET mafile_path=? WHERE id=?', (path, acc_id))
            c.commit()

    def set_session_data(self, acc_id, session_dict):
        import json
        with self._conn() as c:
            cur = c.cursor()
            cur.execute('UPDATE accounts SET session_data=? WHERE id=?', (json.dumps(session_dict), acc_id))
            c.commit()

    def update_account(self, acc_id, account_name, password, shared_secret):
        with self._conn() as c:
            cur = c.cursor()
            cur.execute('UPDATE accounts SET account_name=?, password=?, shared_secret=? WHERE id=?',
                        (account_name, password, shared_secret, acc_id))
            c.commit()

    def update_account(self, acc_id, account_name, password, shared_secret, identity_secret=None):
        with self._conn() as c:
            cur = c.cursor()
            cur.execute('UPDATE accounts SET account_name=?, password=?, shared_secret=?, identity_secret=? WHERE id=?',
                        (account_name, password, shared_secret, identity_secret, acc_id))
            c.commit()

    def delete_account(self, acc_id):
        with self._conn() as c:
            cur = c.cursor()
            cur.execute('DELETE FROM accounts WHERE id=?', (acc_id,))
            c.commit()

    def get_accounts_paginated(self, start, count):
        with self._conn() as c:
            cur = c.cursor()
            cur.execute('SELECT id, account_name, password, shared_secret, created_at, mafile_path FROM accounts ORDER BY id LIMIT ? OFFSET ?', (count, start))
            rows = cur.fetchall()
            keys = ['id','account_name','password','shared_secret','created_at','mafile_path']
            return [dict(zip(keys, r)) for r in rows]

    def count_accounts(self):
        with self._conn() as c:
            cur = c.cursor()
            cur.execute('SELECT COUNT(*) FROM accounts')
            return cur.fetchone()[0]

    def get_account_by_id(self, acc_id):
        with self._conn() as c:
            cur = c.cursor()
            cur.execute('SELECT id, account_name, password, shared_secret, created_at, mafile_path FROM accounts WHERE id=?', (acc_id,))
            r = cur.fetchone()
            if not r:
                return None
            keys = ['id','account_name','password','shared_secret','created_at','mafile_path']
            return dict(zip(keys, r))
