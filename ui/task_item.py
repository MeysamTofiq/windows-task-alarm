import flet as ft
from components import AppColors

class TaskItem(ft.Container):
    def __init__(self, task, on_toggle, on_edit, on_delete):
        super().__init__()
        self.task = task
        self.on_toggle = on_toggle
        self.on_edit = on_edit
        self.on_delete = on_delete
        
        self.padding = 12
        self.margin = ft.Margin(0, 0, 0, 8)
        self.border_radius = 12
        self.bgcolor = AppColors.CARD_COLOR
        self.border = ft.Border(
            top=ft.BorderSide(1, AppColors.SURFACE_VARIANT),
            bottom=ft.BorderSide(1, AppColors.SURFACE_VARIANT),
            left=ft.BorderSide(1, AppColors.SURFACE_VARIANT),
            right=ft.BorderSide(1, AppColors.SURFACE_VARIANT),
        )
        
        # چک‌باکس
        self.checkbox = ft.Checkbox(
            value=task.get('completed', False),
            on_change=self._handle_toggle,
            fill_color=AppColors.PRIMARY,
        )
        
        # عنوان تسک
        self.title_text = ft.Text(
            task.get('title', ''),
            size=16,
            weight=ft.FontWeight.W_500,
            color=AppColors.TEXT_DIM if task.get('completed') else AppColors.TEXT_BRIGHT,
            style=ft.TextStyle(
                decoration=ft.TextDecoration.LINE_THROUGH if task.get('completed') else None
            ),
        )
        
        # توضیحات
        description = task.get('description', '')
        self.description_text = ft.Text(
            description,
            size=13,
            color=AppColors.TEXT_DIM,
            max_lines=2,
            overflow=ft.TextOverflow.ELLIPSIS,
            tooltip=description if description else None,
        ) if description else None
        
        # اطلاعات اضافی
        info_chips = []
        
        # دسته‌بندی
        if task.get('category'):
            info_chips.append(
                ft.Container(
                    content=ft.Text(task['category'], size=11, color=AppColors.PRIMARY),
                    bgcolor=AppColors.TEXT_DIM,
                    padding=ft.Padding(left=8, right=8, top=4, bottom=4),  # تغییر
                    border_radius=6,
                )
            )
        
        # تاریخ
        if task.get('date'):
            info_chips.append(
                ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.Icons.CALENDAR_TODAY, size=12, color=AppColors.TEXT_DIM),
                        ft.Text(task['date'], size=11, color=AppColors.TEXT_DIM),
                    ], spacing=4),
                    padding=ft.Padding(left=8, right=8, top=4, bottom=4),
                )
            )
        
        # زمان
        if task.get('time'):
            info_chips.append(
                ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.Icons.ACCESS_TIME, size=12, color=AppColors.TEXT_DIM),
                        ft.Text(task['time'], size=11, color=AppColors.TEXT_DIM),
                    ], spacing=4),
                    padding=ft.Padding(left=8, right=8, top=4, bottom=4),
                )
            )
        
        
        # اولویت
        priority = task.get('priority', 'متوسط')
        priority_colors = {
            'بالا': AppColors.DANGER,
            'متوسط': AppColors.WARNING,
            'پایین': AppColors.SUCCESS,
        }
        info_chips.append(
            ft.Container(
                content=ft.Text(priority, size=11, color=priority_colors.get(priority, AppColors.TEXT_DIM)),
                border=ft.Border(
                    top=ft.BorderSide(1, priority_colors.get(priority, AppColors.TEXT_DIM)),
                    bottom=ft.BorderSide(1, priority_colors.get(priority, AppColors.TEXT_DIM)),
                    left=ft.BorderSide(1, priority_colors.get(priority, AppColors.TEXT_DIM)),
                    right=ft.BorderSide(1, priority_colors.get(priority, AppColors.TEXT_DIM)),
                ),
                padding=ft.Padding(left=8, right=8, top=4, bottom=4),
                border_radius=6,
            )
        )

        # دکمه‌های عملیات
                # دکمه‌های عملیات  ← این باید خط ۱۰۸ باشه (دست نزن)
        action_buttons = ft.Row([
            ft.IconButton(
                icon=ft.Icons.EDIT_OUTLINED,
                icon_size=18,
                icon_color=AppColors.PRIMARY,
                on_click=self._handle_edit,
                tooltip="ویرایش",
            ),
            ft.IconButton(
                icon=ft.Icons.DELETE_OUTLINE,
                icon_size=18,
                icon_color=AppColors.DANGER,
                on_click=self._handle_delete,
                tooltip="حذف",
            ),
        ], spacing=4)

        # یادآوری  ← از اینجا به بعد کد جدید
        if task.get('reminder'):
            info_chips.append(
                ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.Icons.NOTIFICATIONS_ACTIVE, size=12, color=AppColors.WARNING),
                        ft.Text("یادآوری", size=11, color=AppColors.WARNING),
                    ], spacing=4),
                    padding=ft.Padding(left=8, right=8, top=4, bottom=4),
                )
            )

        # تکرار
        if task.get('repeat') and task['repeat'] != "بدون تکرار":
            repeat_icons = {
                "روزانه": ft.Icons.TODAY,
                "هفتگی": ft.Icons.DATE_RANGE,
                "ماهانه": ft.Icons.CALENDAR_MONTH,
            }
            info_chips.append(
                ft.Container(
                    content=ft.Row([
                        ft.Icon(repeat_icons.get(task['repeat'], ft.Icons.REPEAT), size=12, color=AppColors.SUCCESS),
                        ft.Text(task['repeat'], size=11, color=AppColors.SUCCESS),
                    ], spacing=4),
                    padding=ft.Padding(left=8, right=8, top=4, bottom=4),
                )
            )

        # ردیف اول: عنوان + chips
        chips_row = ft.Row(
            info_chips,
            spacing=4,
            wrap=True,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )

        first_row = ft.Row(
            [self.title_text, chips_row],
            spacing=8,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )

        main_column_controls = [first_row]
        if self.description_text:
            main_column_controls.append(self.description_text)

        main_content = ft.Row(
            [
                self.checkbox,
                ft.Column(
                    main_column_controls,
                    spacing=4,
                    expand=True,
                ),
                action_buttons,
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )

        self.content = main_content

    def _handle_toggle(self, e):
        # فقط task_id رو پاس بده
        if self.on_toggle:
            self.on_toggle(self.task['id'])
    
    def _handle_edit(self, e):
        # فقط task_id رو پاس بده
        if self.on_edit:
            self.on_edit(self.task['id'])
    
    def _handle_delete(self, e):
        # فقط task_id رو پاس بده
        if self.on_delete:
            self.on_delete(self.task['id'])
