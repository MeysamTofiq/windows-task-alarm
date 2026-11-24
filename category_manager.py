# categories.py
import json
import os


class CategoryManager:
    def __init__(self, filename="categories.json", shared_manager=None):
        self.filename = filename
        self.shared_manager = shared_manager
        self.categories = []
        self.load_categories()

        if self.shared_manager:
            self.shared_manager.register_categories_callback(self._on_external_change)

    def _on_external_change(self):
        """وقتی فایل از بیرون تغییر کرد، reload می‌کنیم"""
        self.load_categories()

    def load_categories(self):
        """بارگذاری دسته‌بندی‌ها"""
        if self.shared_manager:
            self.categories = self.shared_manager.load_categories()
            return

        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r', encoding='utf-8') as f:
                    self.categories = json.load(f)
            except Exception as e:
                print(f"خطا در بارگذاری دسته‌بندی‌ها: {e}")
                self.categories = []
        else:
            self.categories = []

    def save_categories(self):
        """ذخیره دسته‌بندی‌ها"""
        if self.shared_manager:
            self.shared_manager.save_categories(self.categories)
            return

        try:
            with open(self.filename, 'w', encoding='utf-8') as f:
                json.dump(self.categories, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"خطا در ذخیره دسته‌بندی‌ها: {e}")

    def get_all_categories(self):
        return self.categories

    def add_category(self, name: str, color: str = "#607D8B") -> dict:
        cat = {"id": self._generate_id(), "name": name, "color": color}
        self.categories.append(cat)
        self.save_categories()
        return cat

    def update_category(self, cat_id: int, name: str, color: str) -> bool:
        for cat in self.categories:
            if cat['id'] == cat_id:
                cat['name'] = name
                cat['color'] = color
                self.save_categories()
                return True
        return False

    def delete_category(self, cat_id: int) -> bool:
        before = len(self.categories)
        self.categories = [c for c in self.categories if c['id'] != cat_id]
        if len(self.categories) < before:
            self.save_categories()
            return True
        return False

    def get_category_by_name(self, name: str) -> dict | None:
        for cat in self.categories:
            if cat['name'] == name:
                return cat
        return None

    def _generate_id(self) -> int:
        if not self.categories:
            return 1
        return max(c['id'] for c in self.categories) + 1
