import flet as ft
import json
from pathlib import Path
from components import AppColors

class SettingsDialog(ft.AlertDialog):
    def __init__(self, page: ft.Page, on_save=None):
        self.page = page
        self.on_save_callback = on_save
        self.settings_file = Path("settings.json")
        
        # بارگذاری تنظیمات فعلی
        self.current_settings = self._load_settings()
        
        # فیلد مسیر اشتراکی
        self.shared_path_field = ft.TextField(
            label="مسیر پوشه اشتراکی",
            hint_text="مثال: \\\\server\\shared یا خالی برای حالت standalone",
            value=self.current_settings.get("shared_path", ""),
            expand=True,
            rtl=True
        )
        
        super().__init__(
            modal=True,
            title=ft.Text("تنظیمات", size=20, weight=ft.FontWeight.BOLD),
            content=ft.Container(
                content=ft.Column([
                    ft.Text("مسیر پوشه اشتراکی شبکه:", size=14),
                    self.shared_path_field,
                    ft.Text(
                        "نکته: اگر مسیر خالی باشد، برنامه در حالت standalone اجرا می‌شود.",
                        size=12,
                        color=AppColors.TEXT_DIM  # به جای ft.Colors.GREY_500
,
                        italic=True
                    )
                ], spacing=10),
                width=500,
                padding=20
            ),
            actions=[
                ft.TextButton("لغو", on_click=self._on_cancel),
                ft.ElevatedButton("ذخیره", on_click=self._on_save)
            ],
            actions_alignment=ft.MainAxisAlignment.END
        )
    
    def _load_settings(self) -> dict:
        """بارگذاری تنظیمات از فایل"""
        try:
            if self.settings_file.exists():
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except:
            pass
        return {}
    
    def _save_settings(self, settings: dict):
        """ذخیره تنظیمات در فایل"""
        with open(self.settings_file, 'w', encoding='utf-8') as f:
            json.dump(settings, f, ensure_ascii=False, indent=2)
    
    def _on_save(self, e):
        """ذخیره تنظیمات"""
        settings = {
            "shared_path": self.shared_path_field.value.strip()
        }
        self._save_settings(settings)
        
        self.open = False
        self.page.update()
        
        if self.on_save_callback:
            self.on_save_callback(settings)
    
    def _on_cancel(self, e):
        """لغو و بستن دیالوگ"""
        self.open = False
        self.page.update()
