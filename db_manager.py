# FINAL PRODUCTION VERSION - ROBUST EXE SUPPORT
import warnings
import logging
import os
import sys

# --- NUCLEAR WARNING SUPPRESSION (Applied before any imports) ---
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", message=".*deprecated since 1.8.0.*")
logging.getLogger('appwrite').setLevel(logging.CRITICAL)
logging.getLogger('appwrite').propagate = False

import requests
import json
import base64
import time
from dotenv import load_dotenv
from appwrite.client import Client
from appwrite.services.account import Account
from appwrite.services.databases import Databases
from appwrite.id import ID
from appwrite.exception import AppwriteException
from appwrite.query import Query
from datetime import datetime, timezone

# Helper to find files in EXE vs Source vs Android
def get_base_dir():
    # If running on Android, use a writable temp/files directory
    import platform
    if "android" in platform.uname().release.lower() or os.environ.get("ANDROID_ROOT"):
        import tempfile
        return tempfile.gettempdir()
    
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

# Load environment variables from the correct location
env_path = os.path.join(get_base_dir(), ".env")
if os.path.exists(env_path):
    load_dotenv(env_path)
else:
    load_dotenv() # Fallback

class DBManager:
    def __init__(self):
        self.client = Client()
        
        # Configuration
        self.endpoint = os.getenv("APPWRITE_ENDPOINT", "https://cloud.appwrite.io/v1")
        self.project_id = os.getenv("APPWRITE_PROJECT_ID")
        self.db_id = os.getenv("APPWRITE_DB_ID", "ThreatViper_1234")
        self.collection_history = os.getenv("APPWRITE_COLLECTION_HISTORY", "table_1")
        
        # Absolute path for session persistence (Always near the app)
        self.session_file = os.path.join(get_base_dir(), ".session.json")
        
        self.client.set_endpoint(self.endpoint)
        self.client.set_project(self.project_id)
        
        self.account = Account(self.client)
        self.databases = Databases(self.client)
        
        self.current_user = None
        # DEFERRED: load_session() will be called by main.py or lazily

    def _save_session_data(self, cookie_header, secret=None):
        try:
            data = {
                "cookie": cookie_header,
                "secret": secret,
                "timestamp": time.time()
            }
            with open(self.session_file, "w") as f:
                json.dump(data, f)
        except: pass

    def load_session(self):
        if not os.path.exists(self.session_file):
            return False
        try:
            with open(self.session_file, "r") as f:
                data = json.load(f)
            
            if time.time() - data.get('timestamp', 0) > (30 * 24 * 3600):
                return False

            if data.get('cookie'):
                self.client.add_header('Cookie', data['cookie'])
            if data.get('secret'):
                self.client.set_session(data['secret'])
            
            try:
                self.current_user = self.account.get()
                return True
            except:
                self.current_user = None
                return False
        except:
            return False

    def login(self, email, password):
        try:
            url = f"{self.endpoint}/account/sessions/email"
            payload = {"email": email, "password": password}
            headers = {"X-Appwrite-Project": self.project_id, "Content-Type": "application/json"}
            
            session_req = requests.post(url, json=payload, headers=headers)
            if session_req.status_code >= 400:
                return False, "Login Failed. Check credentials."
            
            cookie_parts = [f"{c.name}={c.value}" for c in session_req.cookies]
            cookie_header_val = "; ".join(cookie_parts)
            self.client.add_header('Cookie', cookie_header_val)
            
            secret_found = None
            try:
                for cookie in session_req.cookies:
                    if cookie.name.startswith('a_session_') and not cookie.name.endswith('_legacy'):
                        cv = cookie.value + '=' * (-len(cookie.value) % 4)
                        sdata = json.loads(base64.b64decode(cv).decode('utf-8'))
                        if 'secret' in sdata:
                            secret_found = sdata['secret']
                            self.client.set_session(secret_found)
                            break
            except: pass

            self._save_session_data(cookie_header_val, secret_found)
            self.current_user = self.account.get()
            return True, f"Welcome, {self.current_user['name']}"
        except Exception as e:
            return False, f"Auth Error: {str(e)}"

    def register(self, email, password, name):
        try:
            self.account.create(ID.unique(), email, password, name)
            return self.login(email, password)
        except Exception as e:
            return False, f"Registration Failed: {str(e)}"
            
    def logout(self):
        try:
            self.account.delete_session('current')
            self.current_user = None
            if os.path.exists(self.session_file):
                os.remove(self.session_file)
            return True
        except:
            return False

    def get_current_user(self):
        if not self.current_user:
             self.load_session()
        return self.current_user

    def log_scan(self, files_scanned, threats_found, location, details=""):
        """Syncs scan results with exact camelCase mapping and robust user check"""
        user = self.get_current_user()
        if not user: 
            logging.error("Sync failed: No active user session.")
            return False
        try:
            # Mapping based on user screenshot attributes
            data = {
                "userId": str(user['$id']),
                "username": str(user['name']),
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "filesScanned": int(files_scanned),
                "threatsFound": int(threats_found),
                "location": str(location),
                "details": str(details)[:1000]
            }
            
            self.databases.create_document(
                database_id=self.db_id, 
                collection_id=self.collection_history, 
                document_id=ID.unique(), 
                data=data
            )
            return True
        except Exception as e:
            logging.error(f"Sync Issue for user {user.get('$id')}: {e}")
            return False

    def get_history(self):
        if not self.get_current_user(): return []
        try:
            result = self.databases.list_documents(
                database_id=self.db_id, 
                collection_id=self.collection_history,
                queries=[Query.order_desc("$createdAt"), Query.limit(50)]
            )
            return result['documents']
        except Exception as e:
            logging.error(f"History Fetch Error: {e}")
            return []
