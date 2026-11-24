import os
import time
from pathlib import Path
from threading import Thread, Event
from typing import Optional, Callable

class SharedStorageManager:
    def __init__(self, shared_path: str, on_change: Optional[Callable] = None):
        self.shared_path = Path(shared_path)
        self.on_change = on_change
        self.watching = False
        self.watch_thread: Optional[Thread] = None
        self.stop_event = Event()
        self.last_modified = 0
    
    def get_shared_file(self, filename: str) -> Path:
        """دریافت مسیر فایل در پوشه اشتراکی"""
        return self.shared_path / filename
    
    def is_online(self) -> bool:
        """بررسی دسترسی به پوشه اشتراکی"""
        try:
            return self.shared_path.exists() and os.access(self.shared_path, os.W_OK)
        except:
            return False
    
    def start_watching(self, filename: str = "tasks.json"):
        """شروع نظارت بر تغییرات فایل"""
        if self.watching:
            return
        
        self.watching = True
        self.stop_event.clear()
        self.watch_thread = Thread(target=self._watch_file, args=(filename,), daemon=True)
        self.watch_thread.start()
    
    def stop_watching(self):
        """توقف نظارت"""
        self.watching = False
        self.stop_event.set()
        if self.watch_thread:
            self.watch_thread.join(timeout=2)
    
    def _watch_file(self, filename: str):
        """نظارت بر تغییرات فایل (در thread جداگانه)"""
        file_path = self.get_shared_file(filename)
        
        try:
            if file_path.exists():
                self.last_modified = file_path.stat().st_mtime
        except:
            pass
        
        while self.watching and not self.stop_event.is_set():
            try:
                if self.is_online() and file_path.exists():
                    current_mtime = file_path.stat().st_mtime
                    if current_mtime > self.last_modified:
                        self.last_modified = current_mtime
                        if self.on_change:
                            self.on_change()
            except:
                pass
            
            self.stop_event.wait(2)  # بررسی هر 2 ثانیه
