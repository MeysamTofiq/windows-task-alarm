import flet as ft
from components import AppColors

class LoginDialog(ft.AlertDialog):
    def __init__(self, page: ft.Page, auth_manager, on_login_success=None):
        self.page = page
        self.auth_manager = auth_manager
        self.on_login_success_callback = on_login_success
        
        # فیلدهای ورودی
        self.username_field = ft.TextField(
            label="نام کاربری",
            autofocus=True,
            rtl=True
        )
        
        self.password_field = ft.TextField(
            label="رمز عبور",
            password=True,
            can_reveal_password=True,
            rtl=True,
            on_submit=self._on_login
        )
        
        self.error_text = ft.Text(
            "",
            color=AppColors.DANGER,
            size=12,
            visible=False
        )
        
        super().__init__(
            modal=True,
            title=ft.Text("ورود به سیستم", size=20, weight=ft.FontWeight.BOLD),
            content=ft.Container(
                content=ft.Column([
                    self.username_field,
                    self.password_field,
                    self.error_text,
                    ft.Text(
                        "کاربر پیش‌فرض: admin / admin",
                        size=11,
                        color=AppColors.TEXT_DIM,
                        italic=True
                    )
                ], spacing=15, tight=True),
                width=400,
                padding=20
            ),
            actions=[
                ft.ElevatedButton(
                    "ورود",
                    on_click=self._on_login,
                    style=ft.ButtonStyle(
                        bgcolor=AppColors.PRIMARY,
                        color=AppColors.ON_PRIMARY
                    )
                )
            ],
            actions_alignment=ft.MainAxisAlignment.CENTER
        )
    
    def _on_login(self, e):
        """تلاش برای ورود"""
        username = self.username_field.value.strip()
        password = self.password_field.value
        
        if not username or not password:
            self._show_error("لطفاً نام کاربری و رمز عبور را وارد کنید")
            return
        
        if self.auth_manager.login(username, password):
            self.open = False
            self.page.update()
            
            if self.on_login_success_callback:
                self.on_login_success_callback()
        else:
            self._show_error("نام کاربری یا رمز عبور اشتباه است")
    
    def _show_error(self, message: str):
        """نمایش پیام خطا"""
        self.error_text.value = message
        self.error_text.visible = True
        self.page.update()
