import flet as ft
from components import AppColors, CrazySidebar, PersianCalendarDialog
from ui.task_item import TaskItem
from ui.form_section import TaskFormSection
from category_manager import CategoryManager
from ui.task_filter import TaskFilterBar  # جدید
from settings_dialog import SettingsDialog

class MainUI(ft.Container):
    def __init__(self, page, storage, category_manager, get_active_filters=None):
        self.get_active_filters = get_active_filters  # اضافه کن

        super().__init__()
        self.page = page
        self.storage = storage
        self.category_manager = category_manager

        self.expand = True
        self.bgcolor = AppColors.DARK_BG

        self.current_filter = "همه"
        self.current_category = None
        self.priority_filter = "همه"
        self.search_query = ""
        self.date_from = None
        self.date_to = None
        self.editing_task_id = None

        self._build_ui()

    def _build_ui(self):
        sidebar_items = [
            ("همه تسک‌ها", ft.Icons.HOME),
            ("انجام شده", ft.Icons.CHECK_CIRCLE),
            ("در انتظار", ft.Icons.PENDING),
        ]

        for cat in self.category_manager.get_all_categories():
            sidebar_items.append((cat['name'], ft.Icons.FOLDER))

        self.sidebar = CrazySidebar(
            page=self.page,
            menu_items=sidebar_items,
            on_change=self._handle_sidebar_click,
         #   on_settings=self._open_settings,
        )
###
        
        
        ###
        # دکمه مدیریت دسته‌بندی‌ها در سایدبار
        manage_btn = ft.Container(
            content=ft.Row(
                [
                    ft.Icon(ft.Icons.CATEGORY, color=AppColors.TEXT_DIM, size=24),
                    ft.Text("مدیریت دسته‌بندی‌ها", color=AppColors.TEXT_DIM, size=13),
                ],
                spacing=10,
            ),
            padding=ft.Padding(10, 0, 10, 0),
            height=60,
            width=190,
            border_radius=15,
            bgcolor=ft.Colors.TRANSPARENT,
            on_click=lambda e: self._show_category_manager(),
        )
        sidebar_col = self.sidebar.content.controls[1]
        sidebar_col.controls.append(ft.Divider(color=ft.Colors.WHITE10, height=1))
        sidebar_col.controls.append(manage_btn)

        
        self.header = ft.Container(
            content=ft.Row([
                ft.Text("مديريت وظايف", size=28, weight=ft.FontWeight.BOLD, color=AppColors.PRIMARY),
                ft.Container(expand=True),
                ft.IconButton(
                    icon=ft.Icons.ADD_CIRCLE,
                    icon_size=32,
                    icon_color=AppColors.PRIMARY,
                    on_click=self._show_add_form,
                    tooltip="افزودن",
                ),
            ]),
            padding=20,
            bgcolor=AppColors.CARD_COLOR,
            border=ft.Border(bottom=ft.BorderSide(1, AppColors.SURFACE_VARIANT)),
        )

        self.tasks_list = ft.Column(scroll=ft.ScrollMode.AUTO, spacing=0)
        self.tasks_container = ft.Container(content=self.tasks_list, padding=20, expand=True)
        self.form_container = ft.Container(visible=False, padding=20)
        
        self.filter_bar = TaskFilterBar(
            page=self.page,
            storage=self.storage,
            on_filter_change=self._load_tasks,
            get_active_filters=lambda: {   # جدید
                "status": self.current_filter,
                "category": self.current_category,
            }
        )


        main_content = ft.Column([
            self.header,
            self.filter_bar,   # جایگزین filter_bar قبلی
            ft.Container(
                content=ft.Row([
                    ft.Container(content=self.tasks_container, expand=True),
                    self.form_container,
                ]),
                expand=True,
            ),
        ], spacing=0, expand=True)

        self.content = ft.Row([
            self.sidebar,
            ft.Container(content=main_content, expand=True),
        ], spacing=0, expand=True)

    def load_initial_tasks(self):
        self._load_tasks()


    def _load_tasks(self):
        tasks = self.storage.get_all_tasks()
        filters = self.filter_bar.get_filters()

        if self.current_filter == "انجام شده":
            tasks = [t for t in tasks if t.get('completed', False)]
        elif self.current_filter == "در انتظار":
            tasks = [t for t in tasks if not t.get('completed', False)]

        if self.current_category:
            tasks = [t for t in tasks if t.get('category') == self.current_category]

        if filters["search"]:
            q = filters["search"].strip().lower()
            tasks = [t for t in tasks if q in t.get('title','').lower() or q in t.get('description','').lower()]

        if filters["priority"] != "همه":
            tasks = [t for t in tasks if t.get('priority') == filters["priority"]]

        if filters["date_from"]:
            tasks = [t for t in tasks if t.get('date','') >= filters["date_from"]]

        if filters["date_to"]:
            tasks = [t for t in tasks if t.get('date','') <= filters["date_to"]]

        # ... بقیه کد نمایش تسک‌ها بدون تغییر

        self.tasks_list.controls.clear()

        if not tasks:
            self.tasks_list.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.Icons.INBOX, size=64, color=AppColors.TEXT_DIM),
                        ft.Text("هیچ تسکی پیدا نشد", size=18, color=AppColors.TEXT_DIM),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
                    padding=50,
                    alignment=ft.Alignment(0, 0),
                )
            )
        else:
            for task in tasks:
                self.tasks_list.controls.append(
                    TaskItem(
                        task=task,
                        on_toggle=self._handle_toggle_task,
                        on_edit=self._handle_edit_task,
                        on_delete=self._handle_delete_task,
                    )
                )

        self.update()
    def _handle_search(self, e):
        self.search_query = e.control.value
        self._load_tasks()

    def _handle_priority_filter(self, e):
        self.priority_filter = e.control.value
        self._load_tasks()

    def _show_date_picker(self, field_type):
        def on_date_selected(date_str):
            if field_type == "from":
                self.date_from = date_str          # ✅ متغیر فیلتر ست میشه
                self.date_from_field.value = date_str
                self.date_from_field.update()
            else:
                self.date_to = date_str            # ✅ متغیر فیلتر ست میشه
                self.date_to_field.value = date_str
                self.date_to_field.update()
            self._load_tasks()  # بعد از انتخاب تاریخ، لیست فیلتر بشه

        calendar = PersianCalendarDialog(
            page=self.page,
            on_date_selected=on_date_selected,
        )
        self.page.open(calendar)


  
    def _show_category_manager(self):
        categories = self.category_manager.get_all_categories()

        name_field = ft.TextField(
            label="نام دسته‌بندی جدید",
            text_align=ft.TextAlign.RIGHT,
            bgcolor=AppColors.DARK_BG,
            border_color="#3d3d5c",# رنگ مديريت دسته بندي  xxx
            color="white",
        )

        def add_category(e):
            if name_field.value.strip():
                self.category_manager.add_category(name_field.value.strip())
                name_field.value = ""
                refresh_list()
                self.page.update()

        def delete_category(cat_id):
            self.category_manager.delete_category(cat_id)
            refresh_list()
            self.page.update()

        list_col = ft.Column(scroll=ft.ScrollMode.AUTO, height=250)

        def refresh_list():
            list_col.controls.clear()
            for cat in self.category_manager.get_all_categories():
                list_col.controls.append(
                    ft.Row(
                        [
                            ft.Text(cat["name"], color="white", expand=True, text_align=ft.TextAlign.RIGHT),
                            ft.IconButton(
                                icon=ft.Icons.DELETE,
                                icon_color="#FF5252",
                                # ✅ جدید - ایمن
                                on_click=lambda e, cid=cat.get("id", ""): delete_category(cid),
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    )
                )

        refresh_list()

        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text("مدیریت دسته‌بندی‌ها", text_align=ft.TextAlign.RIGHT, color="white"),
            bgcolor=AppColors.DARK_BG,
            content=ft.Column(
                [
                    list_col,
                    ft.Divider(color="#3d3d5c"),
                    name_field,
                    ft.ElevatedButton(
                        "افزودن دسته‌بندی",
                        on_click=add_category,
                        bgcolor=AppColors.CARD_COLOR,   # XXX
                        color="white",
                    ),
                ],
                tight=True,
                width=350,
            ),
            actions=[
                ft.TextButton(
                    "بستن",
                    on_click=lambda e: close_dlg(),
                    style=ft.ButtonStyle(color="#6c63ff"),
                )
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        def close_dlg():
            dlg.open = False
            self.page.update()
            self._rebuild_sidebar()

        self.page.overlay.append(dlg)
        dlg.open = True
        self.page.update()


    def _rebuild_sidebar(self):
        sidebar_items = [
            ("همه تسک‌ها", ft.Icons.HOME),
            ("انجام شده", ft.Icons.CHECK_CIRCLE),
            ("در انتظار", ft.Icons.PENDING),
        ]
        for cat in self.category_manager.get_all_categories():
            sidebar_items.append((cat["name"], ft.Icons.FOLDER))

        self.sidebar.menu_items_data = sidebar_items
        self.sidebar.menu_col.controls.clear()
        self.sidebar.build_menu()
        self.sidebar.update()
    #اينجا****

    def _handle_sidebar_click(self, index):
        
            
        if index < 3:
            filters = ["همه", "انجام شده", "در انتظار"]
            self.current_filter = filters[index]
            self.current_category = None
        else:
            cats = self.category_manager.get_all_categories()
            cat_index = index - 4
            if 0 <= cat_index < len(cats):
                self.current_category = cats[cat_index]['name']
                self.current_filter = "همه"

        self._load_tasks()
##00
    def _open_settings(self):
        """وقتی روی دکمه تنظیمات کلیک می‌شه، دیالوگ باز می‌شه"""
        dlg = SettingsDialog(
            page=self.page,
            on_settings_changed=self._on_settings_changed,
        )
        self.page.overlay.append(dlg)
        dlg.open = True
        self.page.update()

    def _on_settings_changed(self, new_path):
        """بعد از ذخیره تنظیمات، یه پیام نشون می‌ده"""
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text("تنظیمات ذخیره شد. برای اعمال تغییرات برنامه را ریستارت کنید."),
            bgcolor=ft.Colors.BLUE_700,
        )
        self.page.snack_bar.open = True
        self.page.update()
##00
    def _show_add_form(self, e=None):
        self.editing_task_id = None
        categories = self.category_manager.get_all_categories()
        form = TaskFormSection(
            page=self.page,
            categories=categories,
            on_submit=self._handle_add_task,
            on_cancel=self._hide_form,
        )

        self.form_container.content = form
        self.form_container.visible = True
        self.update()

    def _hide_form(self):
        self.editing_task_id = None
        self.form_container.visible = False
        self.form_container.content = None
        self.update()

    def _handle_add_task(self, task_data,task_id=None,*args):
        
        if self.editing_task_id:
            self.storage.update_task(self.editing_task_id, task_data)
            msg = "تسک با موفقیت ویرایش شد"
        else:
            self.storage.add_task(task_data)
            msg = "تسک با موفقیت اضافه شد"

        self.page.snack_bar = ft.SnackBar(
            content=ft.Text(msg),
            bgcolor=AppColors.SUCCESS,
        )
        self.page.snack_bar.open = True
        self.page.update()

        self._hide_form()
        self._load_tasks()

    def _handle_toggle_task(self, task_id):
        task = self.storage.get_task(task_id)
        if task:
            task['completed'] = not task.get('completed', False)
            self.storage.update_task(task_id, task)
            self._load_tasks()

    def _handle_edit_task(self, task_id):
        task = self.storage.get_task(task_id)
        if not task:
            return

        self.editing_task_id = task_id
        categories = self.category_manager.get_all_categories()
        form = TaskFormSection(
            page=self.page,
            categories=categories,
            on_submit=self._handle_add_task,
            on_cancel=self._hide_form,
            task=task,
        )

        self.form_container.content = form
        self.form_container.visible = True
        self.update()

    def _handle_delete_task(self, task_id):
        self.storage.delete_task(task_id)

        self.page.snack_bar = ft.SnackBar(
            content=ft.Text("تسک حذف شد"),
            bgcolor=AppColors.DANGER,
        )
        self.page.snack_bar.open = True
        self.page.update()
        self._load_tasks()


   
