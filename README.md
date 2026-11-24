# مدیر کارها و آلارم ویندوز (Windows Task Manager & Alarm)

## معرفی (فارسی)

برنامه دسکتاپ ویندوزی برای **مدیریت کارها** با **تقویم شمسی** و **سیستم آلارم** — وظایف را دسته‌بندی می‌کنید، یادآورها را تنظیم می‌کنید و برنامه سر وقت خودش **آلارم** می‌دهد. چند کاربره است و می‌تواند داده‌ها را در یک مسیر اشتراکی شبکه هم‌گام کند.

### ویژگی‌ها

- ✅ مدیریت وظایف با دسته‌بندی (`categories.json`) و وضعیت‌ها
- 🔔 سیستم یادآور و آلارم (`reminder.py`) در پس‌زمینه
- 🗓 تقویم شمسی برای تاریخ وظایف
- 👥 چند کاربر: ورود با کلمه عبور (`auth.py`, `user_manager.py`) و صفحه تنظیمات
- 🔄 هم‌گام‌سازی داده بین سیستم‌ها (`sync_manager.py`, `shared_storage_manager.py`) — مسیر اشتراکی شبکه
- 📌 اجرای دائمی در System Tray (`tray.py`)
- 🖥 رابط گرافیکی Flet + پنل مدیریت دسته‌ها

### فناوری

Python · Flet · JSON · Windows Tray

### اجرا

```bash
pip install flet
python app.py
```

> جریان اجرا: تنظیمات ← لاگین ← رابط اصلی

---

# Windows Task Manager & Alarm

## Overview (English)

A Windows desktop app for **task management** with a **Jalali (Persian) calendar** and an **alarm system** — organize tasks into categories, set reminders, and the app raises an **alarm** at the right time. Multi-user, and it can sync data across a shared network path.

### Features

- ✅ Task management with categories & statuses
- 🔔 Background reminder/alarm engine
- 🗓 Jalali calendar for task dates
- 👥 Multi-user: password login + settings screen
- 🔄 Data sync between machines (shared network path)
- 📌 System Tray for persistent background running
- 🖥 Flet GUI + category manager panel

### Tech Stack

Python · Flet · JSON · Windows Tray

### Run

```bash
pip install flet
python app.py
```

> Startup flow: Settings → Login → Main UI
