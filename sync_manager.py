# sync_manager.py
import json
import os
import time
import threading
from pathlib import Path
from filelock import FileLock, Timeout
from datetime import datetime


class SharedStorageManager:
    """مدیریت دسترسی همزمان و هماهنگ‌سازی فایل‌های JSON مشترک"""
    
    def __init__(self, base_path: str = "shared_data", poll_interval: int = 300):
        """
        Args:
            base_path: مسیر پوشه‌ای که فایل‌های JSON در آن قرار می‌گیرند
            poll_interval: فاصله زمانی بررسی تغییرات (ثانیه) - پیش‌فرض 5 دقیقه
        """
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
        
        self.tasks_file = self.base_path / "tasks.json"
        self.categories_file = self.base_path / "categories.json"
        
        self.tasks_lock_file = self.base_path / "tasks.json.lock"
        self.categories_lock_file = self.base_path / "categories.json.lock"
        
        self.poll_interval = poll_interval
        self._running = False
        self._watch_thread = None
        
        # ذخیره زمان آخرین تغییر فایل‌ها
        self._tasks_mtime = 0
        self._categories_mtime = 0
        
        # callbacks برای اطلاع‌رسانی تغییرات
        self._on_tasks_changed = []
        self._on_categories_changed = []
    
    def start_watching(self):
        """شروع نظارت بر تغییرات فایل‌ها"""
        if self._running:
            return
        
        self._running = True
        self._watch_thread = threading.Thread(target=self._watch_files, daemon=True)
        self._watch_thread.start()
    
    def stop_watching(self):
        """توقف نظارت"""
        self._running = False
        if self._watch_thread:
            self._watch_thread.join(timeout=2)
    
    def register_tasks_callback(self, callback):
        """ثبت callback برای زمانی که tasks تغییر می‌کند"""
        self._on_tasks_changed.append(callback)
    
    def register_categories_callback(self, callback):
        """ثبت callback برای زمانی که categories تغییر می‌کند"""
        self._on_categories_changed.append(callback)
    
    def _watch_files(self):
        """حلقه اصلی نظارت بر تغییرات"""
        while self._running:
            try:
                # بررسی tasks.json
                if self.tasks_file.exists():
                    current_mtime = self.tasks_file.stat().st_mtime
                    if current_mtime != self._tasks_mtime:
                        self._tasks_mtime = current_mtime
                        # اطلاع‌رسانی به callbacks
                        for callback in self._on_tasks_changed:
                            try:
                                callback()
                            except Exception:
                                pass
                
                # بررسی categories.json
                if self.categories_file.exists():
                    current_mtime = self.categories_file.stat().st_mtime
                    if current_mtime != self._categories_mtime:
                        self._categories_mtime = current_mtime
                        for callback in self._on_categories_changed:
                            try:
                                callback()
                            except Exception:
                                pass
                
            except Exception:
                pass
            
            time.sleep(self.poll_interval)
    
    def load_tasks(self) -> list[dict]:
        """خواندن tasks با file locking"""
        lock = FileLock(self.tasks_lock_file, timeout=10)
        
        try:
            with lock:
                if not self.tasks_file.exists():
                    return []
                
                with open(self.tasks_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self._tasks_mtime = self.tasks_file.stat().st_mtime
                    return data
        except Timeout:
            # فایل قفل است، داده قبلی را برمی‌گردانیم
            return []
        except Exception:
            return []
    
    def save_tasks(self, tasks: list[dict]) -> bool:
        """ذخیره tasks با file locking"""
        lock = FileLock(self.tasks_lock_file, timeout=10)
        
        try:
            with lock:
                with open(self.tasks_file, "w", encoding="utf-8") as f:
                    json.dump(tasks, f, ensure_ascii=False, indent=2)
                self._tasks_mtime = self.tasks_file.stat().st_mtime
                return True
        except Timeout:
            return False
        except Exception:
            return False
    
    def load_categories(self) -> list[dict]:
        """خواندن categories با file locking"""
        lock = FileLock(self.categories_lock_file, timeout=10)
        
        try:
            with lock:
                if not self.categories_file.exists():
                    return []
                
                with open(self.categories_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self._categories_mtime = self.categories_file.stat().st_mtime
                    return data
        except Timeout:
            return []
        except Exception:
            return []
    
    def save_categories(self, categories: list[dict]) -> bool:
        """ذخیره categories با file locking"""
        lock = FileLock(self.categories_lock_file, timeout=10)
        
        try:
            with lock:
                with open(self.categories_file, "w", encoding="utf-8") as f:
                    json.dump(categories, f, ensure_ascii=False, indent=2)
                self._categories_mtime = self.categories_file.stat().st_mtime
                return True
        except Timeout:
            return False
        except Exception:
            return False
