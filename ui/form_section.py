import flet as ft
from components import AppColors, PersianCalendarDialog

class TaskFormSection(ft.Container):
    def __init__(self, page, categories, on_submit, on_cancel, task=None):
        super().__init__()
        self.page = page
        self.categories = categories
        self.on_submit = on_submit
        self.on_cancel = on_cancel
        self.editing_task = task
        
        self.padding = 8
        self.bgcolor = AppColors.CARD_COLOR
        self.border_radius = 12
        self.border = ft.Border(
            top=ft.BorderSide(1, AppColors.PRIMARY),
            bottom=ft.BorderSide(1, AppColors.PRIMARY),
            left=ft.BorderSide(1, AppColors.PRIMARY),
            right=ft.BorderSide(1, AppColors.PRIMARY),
        )
        
        # فیلدهای فرم
        self.title_field = ft.TextField(
            label="عنوان تسک",
            hint_text="عنوان تسک را وارد کنید",
            border_color=AppColors.SURFACE_VARIANT,
            focused_border_color=AppColors.PRIMARY,
            value=task.get('title', '') if task else '',
            autofocus=True,
        )
        
        self.description_field = ft.TextField(
            label="توضیحات",
            hint_text="توضیحات تسک (اختیاری)",
            multiline=True,
            min_lines=3,
            max_lines=5,
            border_color=AppColors.SURFACE_VARIANT,
            focused_border_color=AppColors.PRIMARY,
            value=task.get('description', '') if task else '',
        )
        
        # دسته‌بندی
        category_options = [ft.DropdownOption(cat['name']) for cat in categories]
        self.category_dropdown = ft.Dropdown(
            label="دسته‌بندی",
            options=category_options,
            border_color=AppColors.SURFACE_VARIANT,
            focused_border_color=AppColors.PRIMARY,
            value=task.get('category') if task else (category_options[0].key if category_options else None),
        )
        
        # تاریخ
        self.date_field = ft.TextField(
            label="تاریخ",
            hint_text="انتخاب تاریخ",
            read_only=True,
            border_color=AppColors.SURFACE_VARIANT,
            focused_border_color=AppColors.PRIMARY,
            value=task.get('date', '') if task else '',
            suffix=ft.IconButton(
                icon=ft.Icons.CALENDAR_TODAY,
                icon_color=AppColors.PRIMARY,
                on_click=self._show_calendar,
                tooltip="انتخاب تاریخ",
            ),
        )
        
        # زمان
        self.time_field = ft.TextField(
            label="زمان",
            hint_text="مثال: 14:30",
            border_color=AppColors.SURFACE_VARIANT,
            focused_border_color=AppColors.PRIMARY,
            value=task.get('time', '') if task else '',
            suffix=ft.Icon(ft.Icons.ACCESS_TIME, color=AppColors.PRIMARY),
        )
        
        # اولویت
        self.priority_radio = ft.RadioGroup(
            content=ft.Row([
                ft.Radio(value="بالا", label="بالا", fill_color=AppColors.DANGER),
                ft.Radio(value="متوسط", label="متوسط", fill_color=AppColors.WARNING),
                ft.Radio(value="پایین", label="پایین", fill_color=AppColors.SUCCESS),
            ]),
            value=task.get('priority', 'متوسط') if task else 'متوسط',
        )
        
        # یادآوری
        self.reminder_checkbox = ft.Checkbox(
            label="فعال‌سازی یادآوری",
            value=task.get('reminder', False) if task else False,
            fill_color=AppColors.PRIMARY,
        )
        # بعد از self.reminder_checkbox اضافه کن:
        self.repeat_dropdown = ft.Dropdown(
            label="تکرار",
            options=[
                ft.DropdownOption("بدون تکرار"),
                ft.DropdownOption("روزانه"),
                ft.DropdownOption("هفتگی"),
            ],
            value=task.get("repeat", "بدون تکرار") if task else "بدون تکرار",
            border_color=AppColors.SURFACE_VARIANT,
            focused_border_color=AppColors.PRIMARY,
        )

        # دکمه‌ها
        submit_text = "به‌روزرسانی" if task else "افزودن تسک"
        self.submit_button = ft.ElevatedButton(
            text=submit_text,
            icon=ft.Icons.CHECK,
            bgcolor=AppColors.PRIMARY,
            color=AppColors.ON_PRIMARY,
            on_click=self._handle_submit,
        )
        
        self.cancel_button = ft.OutlinedButton(
            text="انصراف",
            icon=ft.Icons.CLOSE,
            on_click=self._handle_cancel,
        )
        
        # ساختار فرم
        self.content = ft.Column([
            ft.Text(
                "ویرایش تسک" if task else "افزودن تسک جدید",
                size=20,
                weight=ft.FontWeight.BOLD,
                color=AppColors.TEXT_DIM,
            ),
            ft.Divider(color=AppColors.SURFACE_VARIANT),
            self.title_field,
            self.description_field,
            self.category_dropdown,
            ft.Row([
                ft.Container(content=self.date_field, expand=True),
                ft.Container(content=self.time_field, expand=True),
            ], spacing=10),
            ft.Column([
                ft.Text("اولویت:", size=14, color=AppColors.TEXT_BRIGHT),
                self.priority_radio,
            ], spacing=5),
           # self.reminder_checkbox,
            ft.Row(
                [
                    self.reminder_checkbox,
                    ft.Container(self.repeat_dropdown, expand=1),
                ],
                spacing=10,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            ft.Row([
                self.submit_button,
                self.cancel_button,
            ], spacing=10),
        ], spacing=10, scroll=ft.ScrollMode.AUTO)
    
    def _show_calendar(self, e):
        calendar = PersianCalendarDialog(
            page=self.page,
            on_date_selected=self._on_date_selected
        )
        self.page.open(calendar)  # ← روش جدید Flet

    
    def _handle_submit(self, e):
        """ارسال فرم"""
        if not self.title_field.value or not self.title_field.value.strip():
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text("لطفاً عنوان تسک را وارد کنید"),
                bgcolor=AppColors.DANGER,
            )
            self.page.snack_bar.open = True
            self.page.update()
            return
        
        task_data = {
            'title': self.title_field.value.strip(),
            'description': self.description_field.value.strip() if self.description_field.value else '',
            'category': self.category_dropdown.value,
            'date': self.date_field.value,
            'time': self.time_field.value,
            'priority': self.priority_radio.value,
            'reminder': self.reminder_checkbox.value,
            'repeat': self.repeat_dropdown.value or "بدون تکرار",  # ✅ جدید
            'completed': self.editing_task.get('completed', False) if self.editing_task else False,
        }

        
        if self.on_submit:
            self.on_submit(task_data, self.editing_task['id'] if self.editing_task else None)
    
    def _handle_cancel(self, e):
        """انصراف از فرم"""
        if self.on_cancel:
            self.on_cancel()

    def _on_date_selected(self, jalali_date):
        if jalali_date:
            self.date_field.value = jalali_date
            self.date_field.update()
        # دیگه نیازی به بستن دیالوگ اینجا نیست
        # چون PersianCalendarDialog خودش با page_ref.close() می‌بنده
