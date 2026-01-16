import os
import json
import time
import random
import string
import base64
import struct
import hmac
import hashlib
import requests
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5

MAFILES_DIR = os.path.join(os.path.dirname(__file__), 'mafiles')

def _ensure_mafiles_dir():
    if not os.path.exists(MAFILES_DIR):
        os.makedirs(MAFILES_DIR, exist_ok=True)

class SteamWrapper:
    def __init__(self):
        _ensure_mafiles_dir()
        try:
            import steamguard
            self.sg = steamguard
        except Exception:
            self.sg = None
        self.session = requests.Session()

    def _randstr(self, n=16):
        return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(n))

    def create_mafile(self, account):
        # account: dict with keys id, account_name, password, shared_secret
        name = account.get('account_name')
        shared = account.get('shared_secret') or ''
        data = {
            'account_name': name,
            'shared_secret': shared,
            'identity_secret': account.get('identity_secret', ''),
            'serial_number': self._randstr(12),
            'revocation_code': self._randstr(20),
            'time_created': int(time.time()),
            'uri': '',
            # local simulation of confirmations
            'pending_confirmations': [
                {'id': 1, 'title': 'Trade 1', 'time': int(time.time())},
                {'id': 2, 'title': 'Login 2', 'time': int(time.time())}
            ],
            'confirmed_history': []
        }
        # if steamguard lib provides helpers, try to use them (best-effort)
        if self.sg:
            try:
                # some versions might provide helpers to build mafile bytes
                if hasattr(self.sg, 'generate_mafile_bytes'):
                    content = self.sg.generate_mafile_bytes(shared)
                    path = os.path.join(MAFILES_DIR, f"{name}_{account.get('id')}.maFile")
                    with open(path, 'wb') as f:
                        f.write(content)
                    return path
            except Exception:
                pass

        # fallback: write JSON mafile
        path = os.path.join(MAFILES_DIR, f"{name}_{account.get('id')}.maFile")
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return path

    def import_mafile(self, path):
        # read JSON (best-effort)
        with open(path, 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)
                return data
            except Exception:
                return None

    def _generate_confirmation_key(self, identity_secret, tag, timestamp=None):
        """Generate Steam mobile confirmation key (HMAC-SHA1) as used by SDA.

        Returns url-safe base64 string without padding.
        """
        if not identity_secret:
            raise ValueError('identity_secret required')
        if timestamp is None:
            timestamp = int(time.time())
        try:
            key = base64.b64decode(identity_secret)
        except Exception:
            # if not base64, try raw bytes
            key = identity_secret.encode()
        data = struct.pack('>Q', int(timestamp)) + tag.encode()
        digest = hmac.new(key, data, hashlib.sha1).digest()
        b64 = base64.b64encode(digest).decode()
        # make url-safe and strip padding
        safe = b64.replace('+', '-').replace('/', '_').rstrip('=')
        return safe

    def set_session_cookies(self, account, cookies_dict):
        """Save session cookies (e.g., steamLoginSecure, sessionid) into mafile or provided account dict.

        cookies_dict should be a dict mapping cookie names to values.
        """
        path = account.get('mafile_path') or account.get('path')
        if not path or not os.path.exists(path):
            raise FileNotFoundError('mafile not found')
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        data.setdefault('session_cookies', {}).update(cookies_dict)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True

    def _get_rsa_key(self, username):
        """Request RSA public key from Steam for username."""
        url = 'https://steamcommunity.com/login/getrsakey/'
        headers = {'User-Agent': 'Python/requests'}
        try:
            resp = self.session.post(url, data={'username': username}, headers=headers, timeout=10)
            j = resp.json()
            if j.get('success'):
                return j
        except Exception:
            return None
        return None

    def web_login(self, account, username, password, emailauth=None, twofactor=None, remember_login=True):
        """
        Perform web login to Steam: getrsakey -> encrypt password -> dologin.
        On success, saves session cookies and steamid into mafile and returns response JSON.
        """
        rsa_info = self._get_rsa_key(username)
        if not rsa_info:
            return {'success': False, 'message': 'Failed to get RSA key'}

        mod_hex = rsa_info.get('publickey_mod')
        exp_hex = rsa_info.get('publickey_exp')
        ts = rsa_info.get('timestamp')
        try:
            mod_int = int(mod_hex, 16)
            exp_int = int(exp_hex, 16)
            rsa_key = RSA.construct((mod_int, exp_int))
        except Exception:
            return {'success': False, 'message': 'Invalid RSA key'}

        cipher = PKCS1_v1_5.new(rsa_key)
        encrypted = cipher.encrypt(password.encode('utf-8'))
        encrypted_b64 = base64.b64encode(encrypted).decode()

        url = 'https://steamcommunity.com/login/dologin/'
        data = {
            'username': username,
            'password': encrypted_b64,
            'rsatimestamp': ts,
            'remember_login': 'true' if remember_login else 'false'
        }
        if emailauth:
            data['emailauth'] = emailauth
        if twofactor:
            data['twofactorcode'] = twofactor

        headers = {'User-Agent': 'Mozilla/5.0'}
        try:
            resp = self.session.post(url, data=data, headers=headers, timeout=10)
            j = resp.json()
        except Exception as e:
            return {'success': False, 'message': 'Login request failed', 'error': str(e)}

        # on success, store cookies and steamid if available
        if j.get('success'):
            cookies = {}
            for name in ('steamLoginSecure', 'sessionid', 'steamLogin'):
                v = self.session.cookies.get(name)
                if v:
                    cookies[name] = v
            # try extract steamid
            steamid = None
            tp = j.get('transfer_parameters') or {}
            steamid = tp.get('steamid') or j.get('steamid')

            # update mafile
            path = account.get('mafile_path')
            if path and os.path.exists(path):
                with open(path, 'r', encoding='utf-8') as f:
                    data_ma = json.load(f)
                data_ma['session_cookies'] = data_ma.get('session_cookies', {})
                data_ma['session_cookies'].update(cookies)
                if steamid:
                    data_ma['steamid'] = steamid
                with open(path, 'w', encoding='utf-8') as f:
                    json.dump(data_ma, f, ensure_ascii=False, indent=2)
            return j

        return j

    def fetch_confirmations(self, account):
        # Prefer real Steam mobileconf API when session cookies and identity_secret available.
        path = account.get('mafile_path')
        if path and os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        else:
            data = {}

        identity = data.get('identity_secret') or account.get('identity_secret') or account.get('identity')
        serial = data.get('serial_number') or account.get('serial_number')
        steamid = data.get('steamid') or account.get('steamid')
        cookies = data.get('session_cookies') or {}

        # If we have session cookies and identity_secret, try real API
        if identity and steamid and cookies.get('steamLoginSecure') and cookies.get('sessionid'):
            try:
                t = int(time.time())
                k = self._generate_confirmation_key(identity, 'conf', t)
                params = {
                    'p': serial or '',
                    'a': steamid,
                    'k': k,
                    't': t,
                    'tag': 'conf'
                }
                url = 'https://steamcommunity.com/mobileconf/conf'
                headers = {
                    'Referer': 'https://steamcommunity.com/mobileauth',
                    'User-Agent': 'Mozilla/5.0'
                }
                resp = self.session.get(url, params=params, headers=headers, cookies=cookies, timeout=10)
                # try parse JSON
                try:
                    j = resp.json()
                    if 'conf' in j:
                        return j['conf']
                    # some responses may embed html; fallback below
                except Exception:
                    pass
                # fallback: return mafile pending_confirmations if exists
                return data.get('pending_confirmations', [])
            except Exception:
                return data.get('pending_confirmations', [])

        # fallback: local mafile-based confirmations
        return data.get('pending_confirmations', [])

    def respond_confirmation(self, account, idx, accept=True):
        # Prefer real Steam mobileconf API when session cookies and identity_secret available.
        path = account.get('mafile_path')
        if path and os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        else:
            data = {}

        identity = data.get('identity_secret') or account.get('identity_secret') or account.get('identity')
        serial = data.get('serial_number') or account.get('serial_number')
        steamid = data.get('steamid') or account.get('steamid')
        cookies = data.get('session_cookies') or {}

        if identity and steamid and cookies.get('steamLoginSecure') and cookies.get('sessionid'):
            # attempt real API call
            try:
                t = int(time.time())
                k = self._generate_confirmation_key(identity, 'allow', t) if accept else self._generate_confirmation_key(identity, 'cancel', t)
                url = 'https://steamcommunity.com/mobileconf/ajaxop'
                headers = {
                    'Referer': 'https://steamcommunity.com/mobileauth',
                    'User-Agent': 'Mozilla/5.0'
                }
                data_post = {
                    'op': 'allow' if accept else 'cancel',
                    'cid': idx,
                    'k': k,
                    't': t
                }
                resp = self.session.post(url, data=data_post, headers=headers, cookies=cookies, timeout=10)
                try:
                    j = resp.json()
                    return j.get('success', False)
                except Exception:
                    return False
            except Exception:
                return False

        # fallback: local mafile handling
        try:
            confs = data.get('pending_confirmations', [])
            if idx < 0 or idx >= len(confs):
                return False
            item = confs.pop(idx)
            history = data.get('confirmed_history', [])
            item['accepted'] = bool(accept)
            item['handled_at'] = int(time.time())
            history.append(item)
            data['pending_confirmations'] = confs
            data['confirmed_history'] = history
            if path:
                with open(path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except Exception:
            return False
