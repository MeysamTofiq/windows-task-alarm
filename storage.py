# storage.py
import json
import os
from datetime import datetime
from typing import Optional

class TaskStorage:
    def __init__(self, filename="tasks.json", shared_manager=None):
        self.filename = filename
        self.shared_manager = shared_manager
        self.tasks = []
        self.load_tasks()

    def load_tasks(self):
        """بارگذاری تسک‌ها از فایل JSON"""
        # اگر shared_manager داریم، از اون استفاده می‌کنیم
        if self.shared_manager and self.shared_manager.is_online():
            try:
                file_path = self.shared_manager.get_shared_file(self.filename)
                if file_path.exists():
                    with open(file_path, 'r', encoding='utf-8') as f:
                        self.tasks = json.load(f)
                    return
            except Exception as e:
                print(f"خطا در بارگذاری از پوشه اشتراکی: {e}")
                # fallback به فایل محلی
        
        # حالت محلی یا fallback
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r', encoding='utf-8') as f:
                    self.tasks = json.load(f)
            except Exception as e:
                print(f"خطا در بارگذاری تسک‌ها: {e}")
                self.tasks = []
        else:
            self.tasks = []

    def save_tasks(self):
        """ذخیره تسک‌ها در فایل JSON"""
        # اگر shared_manager داریم، در پوشه اشتراکی ذخیره می‌کنیم
        if self.shared_manager and self.shared_manager.is_online():
            try:
                file_path = self.shared_manager.get_shared_file(self.filename)
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(self.tasks, f, ensure_ascii=False, indent=2)
                return
            except Exception as e:
                print(f"خطا در ذخیره در پوشه اشتراکی: {e}")
                # fallback به فایل محلی
        
        # حالت محلی یا fallback
        try:
            with open(self.filename, 'w', encoding='utf-8') as f:
                json.dump(self.tasks, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"خطا در ذخیره تسک‌ها: {e}")

    def add_task(self, task):
        task['id'] = self._generate_id()
        task['created_at'] = datetime.now().isoformat()
        self.tasks.append(task)
        self.save_tasks()
        return task

    def update_task(self, task_id, updated_task):
        for i, task in enumerate(self.tasks):
            if task['id'] == task_id:
                updated_task['id'] = task_id
                updated_task['created_at'] = task.get('created_at', datetime.now().isoformat())
                updated_task['updated_at'] = datetime.now().isoformat()
                self.tasks[i] = updated_task
                self.save_tasks()
                return True
        return False

    def delete_task(self, task_id):
        self.tasks = [t for t in self.tasks if t['id'] != task_id]
        self.save_tasks()

    def get_task(self, task_id):
        for task in self.tasks:
            if task['id'] == task_id:
                return task
        return None

    def get_all_tasks(self):
        return self.tasks

    def get_tasks_by_category(self, category):
        return [t for t in self.tasks if t.get('category') == category]

    def get_tasks_by_date(self, date_str):
        return [t for t in self.tasks if t.get('date') == date_str]
    
    def get_tasks_by_assigned_to(self, user_id):
        """دریافت تسک‌های assign شده به یک کاربر"""
        return [t for t in self.tasks if t.get('assigned_to') == user_id]

    def toggle_task_status(self, task_id):
        for task in self.tasks:
            if task['id'] == task_id:
                task['completed'] = not task.get('completed', False)
                task['completed_at'] = datetime.now().isoformat() if task['completed'] else None
                self.save_tasks()
                return task['completed']
        return None

    def _generate_id(self):
        if not self.tasks:
            return 1
        return max(task['id'] for task in self.tasks) + 1


# ─── توابع سطح ماژول برای reminder.py ───────────────────────────────────────

_shared_storage: Optional[TaskStorage] = None

def set_global_storage(storage: TaskStorage):
    """از app.py صدا زده می‌شه تا instance اصلی رو ثبت کنه"""
    global _shared_storage
    _shared_storage = storage

def load_tasks() -> list:
    """برای استفاده در reminder.py - همیشه از فایل رفرش می‌کنه"""
    if _shared_storage:
        _shared_storage.load_tasks()
        return _shared_storage.get_all_tasks()
    # fallback اگر هنوز set نشده
    tmp = TaskStorage()
    return tmp.get_all_tasks()

def update_task(task_id, updated_task) -> bool:
    """برای استفاده در reminder.py - آپدیت یک تسک"""
    if _shared_storage:
        return _shared_storage.update_task(task_id, updated_task)
    # fallback اگر هنوز set نشده
    tmp = TaskStorage()
    result = tmp.update_task(task_id, updated_task)
    return result

