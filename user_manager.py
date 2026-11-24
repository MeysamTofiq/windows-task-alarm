import json
import hashlib
from pathlib import Path
from typing import List, Dict, Optional

class UserManager:
    def __init__(self, users_file: str = "users.json"):
        self.users_file = Path(users_file)
    
    def _hash_password(self, password: str) -> str:
        return hashlib.sha256(password.encode()).hexdigest()
    
    def _load_users(self) -> Dict:
        try:
            with open(self.users_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    
    def _save_users(self, users: Dict):
        with open(self.users_file, 'w', encoding='utf-8') as f:
            json.dump(users, f, ensure_ascii=False, indent=2)
    
    def add_user(self, user_id: str, password: str, name: str, role: str, manager_id: Optional[str] = None) -> bool:
        """افزودن کاربر جدید"""
        users = self._load_users()
        if user_id in users:
            return False
        
        users[user_id] = {
            "id": user_id,
            "password": self._hash_password(password),
            "name": name,
            "role": role,
            "manager_id": manager_id
        }
        self._save_users(users)
        return True
    
    def get_all_users(self) -> List[Dict]:
        """دریافت لیست تمام کاربران"""
        users = self._load_users()
        return [
            {
                "id": uid,
                "name": data["name"],
                "role": data["role"],
                "manager_id": data.get("manager_id")
            }
            for uid, data in users.items()
        ]
    
    def get_user_by_id(self, user_id: str) -> Optional[Dict]:
        """دریافت اطلاعات یک کاربر"""
        users = self._load_users()
        if user_id in users:
            data = users[user_id].copy()
            data.pop("password", None)
            return data
        return None
    
    def get_subordinates(self, manager_id: str) -> List[Dict]:
        """دریافت زیردستان یک مدیر"""
        users = self._load_users()
        return [
            {
                "id": uid,
                "name": data["name"],
                "role": data["role"]
            }
            for uid, data in users.items()
            if data.get("manager_id") == manager_id
        ]
    
    def get_peers(self, user_id: str) -> List[Dict]:
        """دریافت همکاران هم‌سطح"""
        users = self._load_users()
        if user_id not in users:
            return []
        
        manager_id = users[user_id].get("manager_id")
        return [
            {
                "id": uid,
                "name": data["name"],
                "role": data["role"]
            }
            for uid, data in users.items()
            if data.get("manager_id") == manager_id and uid != user_id
        ]
    
    def get_assignable_users(self, current_user_id: str) -> List[Dict]:
        """دریافت کاربرانی که می‌توان به آنها تسک assign کرد"""
        users = self._load_users()
        if current_user_id not in users:
            return []
        
        current_user = users[current_user_id]
        
        if current_user["role"] == "manager":
            # مدیر می‌تواند به زیردستان و خودش assign کند
            subordinates = self.get_subordinates(current_user_id)
            subordinates.append({
                "id": current_user_id,
                "name": current_user["name"],
                "role": current_user["role"]
            })
            return subordinates
        else:
            # کارمند فقط می‌تواند به خودش assign کند
            return [{
                "id": current_user_id,
                "name": current_user["name"],
                "role": current_user["role"]
            }]
    
    def delete_user(self, user_id: str) -> bool:
        """حذف کاربر"""
        users = self._load_users()
        if user_id in users and user_id != "admin":
            del users[user_id]
            self._save_users(users)
            return True
        return False
