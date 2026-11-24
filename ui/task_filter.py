import flet as ft
import os
from openpyxl import Workbook
from datetime import datetime
from components import AppColors, PersianCalendarDialog


class TaskFilterBar(ft.Container):
    def __init__(self, page, storage, on_filter_change, get_active_filters=None):
        super().__init__()
        self.page = page
        self.storage = storage
        self.on_filter_change = on_filter_change  # callback به main_ui
        self.get_active_filters = get_active_filters  # ✅ اضافه شد
        self.search_query = ""
        self.priority_filter = "همه"
        self.date_from = None
        self.date_to = None

        self._build()

    def _build(self):
        self.search_field = ft.TextField(
            hint_text="جستجو در تسک‌ها...",
            prefix_icon=ft.Icons.SEARCH,
            on_change=self._handle_search,
            bgcolor=AppColors.SURFACE_VARIANT,
            border_color=AppColors.PRIMARY,
            text_size=14,
            height=45,
            width=250,
            border_radius=15,
        )

        self.priority_dropdown = ft.Dropdown(
            hint_text="فیلتر اولویت",
            value="همه",
            options=[
                ft.DropdownOption("همه"),
                ft.DropdownOption("بالا"),
                ft.DropdownOption("متوسط"),
                ft.DropdownOption("پایین"),
            ],
            on_change=self._handle_priority_filter,
            bgcolor=AppColors.SURFACE_VARIANT,
            border_color=AppColors.PRIMARY,
            text_size=14,
            width=150,
        )

        self.date_from_field = ft.TextField(
            hint_text="از تاریخ",
            prefix_icon=ft.Icons.CALENDAR_TODAY,
            read_only=True,
            on_click=lambda _: self._show_date_picker("from"),
            bgcolor=AppColors.SURFACE_VARIANT,
            border_color=AppColors.PRIMARY,
            text_size=14,
            width=160,
            border_radius=15,
        )

        self.date_to_field = ft.TextField(
            hint_text="تا تاریخ",
            prefix_icon=ft.Icons.CALENDAR_TODAY,
            read_only=True,
            on_click=lambda _: self._show_date_picker("to"),
            bgcolor=AppColors.SURFACE_VARIANT,
            border_color=AppColors.PRIMARY,
            text_size=14,
            width=160,
            border_radius=15,
        )

        self.content = ft.Row(
            [
                self.search_field,
                self.date_from_field,
                self.date_to_field,
                self.priority_dropdown,
                ft.IconButton(
                    icon=ft.Icons.CLEAR_ALL,
                    icon_color=AppColors.DANGER,
                    tooltip="پاک کردن فیلترها",
                    on_click=self._clear_filters,
                ),
                ft.IconButton(
                    icon=ft.Icons.FILE_DOWNLOAD,
                    icon_color=AppColors.SUCCESS,
                    tooltip="خروجی اکسل",
                    on_click=self._export_to_xlsx,
                ),
            ],
            spacing=8,
            scroll=ft.ScrollMode.AUTO,
        )
        self.padding = ft.Padding(15, 8, 15, 8)
        self.bgcolor = AppColors.CARD_COLOR
        self.border = ft.Border(bottom=ft.BorderSide(1, AppColors.SURFACE_VARIANT))

    def get_filters(self):
        """مقادیر فیلتر فعلی رو برمی‌گردونه"""
        return {
            "search": self.search_field.value or "",
            "priority": self.priority_dropdown.value or "همه",
            "date_from": self.date_from,
            "date_to": self.date_to,
        }

    def _handle_search(self, e):
        self.on_filter_change()

    def _handle_priority_filter(self, e):
        self.on_filter_change()

    def _show_date_picker(self, field_type):
        def on_date_selected(date_str):
            if field_type == "from":
                self.date_from = date_str
                self.date_from_field.value = date_str
                self.date_from_field.update()
            else:
                self.date_to = date_str
                self.date_to_field.value = date_str
                self.date_to_field.update()
            self.on_filter_change()

        calendar = PersianCalendarDialog(
            page=self.page,
            on_date_selected=on_date_selected,
        )
        self.page.open(calendar)

    def _clear_filters(self, e):
        self.date_from = None
        self.date_to = None
        self.search_field.value = ""
        self.priority_dropdown.value = "همه"
        self.date_from_field.value = ""
        self.date_to_field.value = ""
        self.update()
        self.on_filter_change()

    def _export_to_xlsx(self, e):
        tasks = self.storage.get_all_tasks()

        # اعمال فیلترها
        filters = self.get_filters()

        if filters["search"]:
            q = filters["search"].strip().lower()
            tasks = [t for t in tasks if q in t.get('title', '').lower() or q in t.get('description', '').lower()]

        if filters["priority"] != "همه":
            tasks = [t for t in tasks if t.get('priority') == filters["priority"]]

        if filters["date_from"]:
            tasks = [t for t in tasks if t.get('date', '') >= filters["date_from"]]

        if filters["date_to"]:
            tasks = [t for t in tasks if t.get('date', '') <= filters["date_to"]]

        if not tasks:
            self.page.snack_bar = ft.SnackBar(ft.Text("هیچ تسکی برای خروجی وجود ندارد"), open=True)
            self.page.update()
            return
        
        if self.get_active_filters:
            active = self.get_active_filters()
            if active.get("status") == "انجام شده":
                tasks = [t for t in tasks if t.get('completed', False)]
            elif active.get("status") == "در انتظار":
                tasks = [t for t in tasks if not t.get('completed', False)]
            if active.get("category"):
                tasks = [t for t in tasks if t.get('category') == active["category"]]

        filename = f"tasks_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)

        wb = Workbook()
        ws = wb.active
        ws.title = "Tasks"
        ws.append(["عنوان", "توضیحات", "اولویت", "دسته‌بندی", "تاریخ", "وضعیت"])

        for task in tasks:
            ws.append([
                task.get("title", ""),
                task.get("description", ""),
                task.get("priority", ""),
                task.get("category", ""),
                task.get("date", "") or task.get("due_date", ""),
                "انجام شده" if task.get("completed") else "در انتظار",
            ])

        wb.save(filepath)
        self.page.snack_bar = ft.SnackBar(ft.Text(f"فایل ذخیره شد: {filepath}"), open=True)
        self.page.update()
