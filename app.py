# app.py - بازنویسی شده با flow تنظیمات -> لاگین -> UI اصلی

import flet as ft
import json
from pathlib import Path

# وارد کردن ماژول‌های سفارشی
from storage import TaskStorage, set_global_storage
from category_manager import CategoryManager
from ui.main_ui import MainUI
from shared_storage_manager import SharedStorageManager
import reminder
from settings_dialog import SettingsDialog
from login_dialog import LoginDialog
from auth import AuthManager
from user_manager import UserManager

SETTINGS_FILE = Path("settings.json")

def load_settings() -> dict:
    """بارگذاری تنظیمات برنامه (مسیر اشتراک‌گذاری)"""
    try:
        if SETTINGS_FILE.exists():
            with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        print(f"خطا در بارگذاری تنظیمات: {e}")
    return {"shared_path": None}

def save_settings(settings: dict):
    """ذخیره تنظیمات"""
    try:
        with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
            json.dump(settings, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"خطا در ذخیره تنظیمات: {e}")

def main(page: ft.Page):
    page.title = "مدیریت تسک‌ها"
    page.theme_mode = ft.ThemeMode.DARK
    page.rtl = True
    page.padding = 0
    page.spacing = 0

    try:
        page.window.icon = "Icon.ico"
    except:
        pass

    page.fonts = {"IRANSans": "fonts/IRANSans.ttf"}
    page.theme = ft.Theme(font_family="IRANSans")

    # ── متغیرهای سراسری ────────────────────────────────────────────────────
    storage = None
    category_manager = None
    auth_manager = None
    user_manager = None
    sync_manager = None
    main_ui = None

    # ── تابع راه‌اندازی اصلی برنامه ──────────────────────────────────────────
    def initialize_app():
        """راه‌اندازی storage، category_manager و سایر اجزا"""
        nonlocal storage, category_manager, auth_manager, user_manager, sync_manager
        
        settings = load_settings()
        shared_path = settings.get("shared_path")

        # مدیریت احراز هویت و کاربران
        auth_manager = AuthManager()
        user_manager = UserManager()

        # مدیریت اشتراک‌گذاری فایل (Sync Manager)
        if shared_path and Path(shared_path).is_dir():
            sync_manager = SharedStorageManager(
                shared_path=shared_path,
                on_change=on_external_file_change
            )
            sync_manager.start_watching()
            storage = TaskStorage(shared_manager=sync_manager)
            print(f"✓ حالت اشتراکی فعال: {shared_path}")
        else:
            storage = TaskStorage()
            print("✓ حالت محلی فعال")
        
        # ثبت storage برای دسترسی سراسری (مثلاً در reminder)
        set_global_storage(storage)
        
        # بارگذاری اولیه داده‌ها (دسته‌بندی‌ها)
        category_manager = CategoryManager("categories.json")

    # ── تابع callback برای تغییرات خارجی ──────────────────────────────────
    def on_external_file_change():
        """وقتی فایل از بیرون تغییر کرد"""
        if main_ui:
            try:
                main_ui.refresh_tasks()
                print("↻ تسک‌ها از فایل اشتراکی به‌روز شدند")
            except Exception as e:
                print(f"خطا در به‌روزرسانی تسک‌ها: {e}")

    # ── دیالوگ تنظیمات ───────────────────────────────────────────────────────
    def handle_settings_save(new_settings):
        """بعد از ذخیره تنظیمات"""
        save_settings(new_settings)
        
        page.snack_bar = ft.SnackBar(
            content=ft.Text(
                "تنظیمات ذخیره شد. لطفاً برنامه را مجدداً اجرا کنید.",
                rtl=True
            ),
            bgcolor=ft.colors.BLUE_700
        )
        page.snack_bar.open = True
        page.update()
        
        # بعد از تنظیم مسیر، دیالوگ لاگین رو نشون بده
        if new_settings.get("shared_path"):
            page.close(settings_dialog)
            initialize_app()
            page.dialog = login_dialog
            login_dialog.open = True
            page.update()

    settings_dialog = SettingsDialog(page=page, on_save=handle_settings_save)

    # ── دیالوگ لاگین ─────────────────────────────────────────────────────────
    def on_login_success():
        """بعد از لاگین موفق"""
        nonlocal main_ui
        
        page.close(login_dialog)
        
        # ساخت UI اصلی
        main_ui = MainUI(page, storage, category_manager, auth_manager, user_manager)
        
        page.clean()
        page.add(main_ui)
        
        main_ui.load_initial_tasks()
        
        # راه‌اندازی reminder
        reminder.start_reminder()
        
        # راه‌اندازی alarm polling (اگر در MainUI وجود داره)
        if hasattr(main_ui, '_start_alarm_polling'):
            main_ui._start_alarm_polling()
        
        page.update()
        print("✓ ورود موفقیت‌آمیز")

    login_dialog = LoginDialog(
        page=page,
        auth_manager=None,  # بعداً set می‌شه
        on_login_success=on_login_success
    )

    # ── فلوی شروع برنامه ──────────────────────────────────────────────────────
    settings = load_settings()
    shared_path = settings.get("shared_path")

    # اگر shared path تنظیم نشده، اول تنظیمات رو نشون بده
    if not shared_path or not Path(shared_path).is_dir():
        print("⚠ مسیر اشتراک‌گذاری تنظیم نشده. نمایش دیالوگ تنظیمات...")
        page.dialog = settings_dialog
        settings_dialog.open = True
        page.update()
    else:
        # اگر تنظیمات OK بود، اول initialize کن، بعد لاگین رو نشون بده
        print("✓ مسیر اشتراک‌گذاری تنظیم شده")
        initialize_app()
        
        # حالا auth_manager آماده است
        login_dialog.auth_manager = auth_manager
        
        page.dialog = login_dialog
        login_dialog.open = True
        page.update()

    # ── تابع پاکسازی هنگام بستن برنامه ────────────────────────────────────────
    def on_disconnect(e):
        print("⏹ برنامه در حال بسته شدن...")
        if sync_manager:
            sync_manager.stop_watching()
            print("  ✓ Sync manager متوقف شد")
        reminder.stop_reminder()
        print("  ✓ Reminder متوقف شد")
    
    page.on_disconnect = on_disconnect

if __name__ == "__main__":
    ft.app(target=main)
