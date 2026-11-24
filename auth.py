import json
import hashlib
from pathlib import Path
from typing import Optional, Dict

class AuthManager:
    def __init__(self, users_file: str = "users.json"):
        self.users_file = Path(users_file)
        self.current_user: Optional[Dict] = None
        self._ensure_users_file()
    
    def _ensure_users_file(self):
        """ایجاد فایل کاربران با یک ادمین پیش‌فرض"""
        if not self.users_file.exists():
            default_users = {
                "admin": {
                    "id": "admin",
                    "password": self._hash_password("admin"),
                    "name": "مدیر سیستم",
                    "role": "manager",
                    "manager_id": None
                }
            }
            self._save_users(default_users)
    
    def _hash_password(self, password: str) -> str:
        """هش کردن رمز عبور"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def _load_users(self) -> Dict:
        """بارگذاری کاربران از فایل"""
        try:
            with open(self.users_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    
    def _save_users(self, users: Dict):
        """ذخیره کاربران در فایل"""
        with open(self.users_file, 'w', encoding='utf-8') as f:
            json.dump(users, f, ensure_ascii=False, indent=2)
    
    def login(self, username: str, password: str) -> bool:
        """ورود کاربر"""
        users = self._load_users()
        if username in users:
            hashed = self._hash_password(password)
            if users[username]["password"] == hashed:
                self.current_user = users[username].copy()
                self.current_user["username"] = username
                return True
        return False
    
    def logout(self):
        """خروج کاربر"""
        self.current_user = None
    
    def is_logged_in(self) -> bool:
        """بررسی وضعیت لاگین"""
        return self.current_user is not None
    
    def get_current_user(self) -> Optional[Dict]:
        """دریافت اطلاعات کاربر جاری"""
        return self.current_user
    
    def get_user_id(self) -> Optional[str]:
        """دریافت شناسه کاربر جاری"""
        return self.current_user["id"] if self.current_user else None
