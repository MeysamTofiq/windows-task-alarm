import os
import time
import datetime
import threading
import winsound

from persiantools.jdatetime import JalaliDateTime, JalaliDate
from storage import load_tasks, update_task

# ── مسیرها
BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
SOUND_FILE = os.path.join(BASE_DIR, "assets", "Song.mp3")
LOG_FILE   = os.path.join(BASE_DIR, "alarm_log.txt")

# ── لاگ
def log(msg):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {msg}\n"
    print(line, end="")
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(line)
    except Exception as e:
        print(f"Log write error: {e}")

# ── winotify
try:
    from winotify import Notification, audio
    WINOTIFY_OK = True
except ImportError:
    WINOTIFY_OK = False
    log("WARNING: winotify not installed → pip install winotify")

# ── pygame
try:
    import pygame
    pygame.mixer.init()
    PYGAME_OK = True
except Exception as e:
    PYGAME_OK = False
    log(f"WARNING: pygame init failed: {e}")

triggered_tasks = set()
stop_event = threading.Event()


# ── نوتیفیکیشن
def show_notification(title, message):
    if WINOTIFY_OK:
        try:
            toast = Notification(
                app_id="مدیریت تسک‌ها",
                title=title,
                msg=message,
                duration="short"
            )
            toast.set_audio(audio.Default, loop=False)
            toast.show()
            log(f"Notification sent: {title}")
        except Exception as e:
            log(f"Notification error: {e}")
    else:
        log("winotify not available, skipping notification.")

# ── صدا
def play_sound():
    if PYGAME_OK and os.path.exists(SOUND_FILE):
        try:
            pygame.mixer.music.load(SOUND_FILE)
            pygame.mixer.music.play()
            timeout = time.time() + 30
            while pygame.mixer.music.get_busy() and time.time() < timeout:
                time.sleep(0.5)
            log("Sound played (pygame)")
            return
        except Exception as e:
            log(f"Sound error (pygame): {e}")

    if not os.path.exists(SOUND_FILE):
        log(f"Sound file not found: {SOUND_FILE}")
    winsound.Beep(1000, 800)
    log("Sound played (winsound fallback)")

# ── تبدیل تاریخ
def convert_jalali_to_gregorian(jdate, jtime):
    if not jdate or not jtime:
        return None
    try:
        jy, jm, jd = map(int, jdate.split("-"))
        hour, minute = map(int, jtime.split(":"))
        return JalaliDateTime(jy, jm, jd, hour, minute).to_gregorian()
    except Exception as e:
        log(f"Date convert error [{jdate} {jtime}]: {e}")
        return None

def gregorian_to_jalali_str(dt):
    try:
        jd = JalaliDate.to_jalali(dt.year, dt.month, dt.day)
        return f"{jd.year}-{jd.month:02d}-{jd.day:02d}", f"{dt.hour:02d}:{dt.minute:02d}"
    except Exception as e:
        log(f"Jalali convert error: {e}")
        return None, None

def get_next_trigger_date(dt, repeat_type):
    if repeat_type == "روزانه":
        return dt + datetime.timedelta(days=1)
    elif repeat_type == "هفتگی":
        return dt + datetime.timedelta(weeks=1)
    return None

def advance_to_today(dt, repeat_type):
    now = datetime.datetime.now()
    if dt >= now:
        return dt
    delta = (datetime.timedelta(days=1) if repeat_type == "روزانه"
             else datetime.timedelta(weeks=1) if repeat_type == "هفتگی"
             else None)
    if not delta:
        return dt
    while dt < now - datetime.timedelta(seconds=60):
        dt += delta
    return dt

# ── حلقه اصلی
def check_tasks():
    log("=== Reminder system started ===")
    log(f"SOUND_FILE: {SOUND_FILE}")

    while not stop_event.is_set():
        try:
            tasks = load_tasks()
            now   = datetime.datetime.now()
            log(f"Checking {len(tasks)} tasks | {now.strftime('%Y-%m-%d %H:%M:%S')}")

            for task in tasks:
                task_id     = task.get("id")
                title       = task.get("title", "بدون عنوان")
                reminder_on = task.get("reminder", False)
                repeat_type = task.get("repeat", "بدون تکرار")

                if not reminder_on:
                    log(f"  SKIP (reminder=off): {title}")
                    continue

                jdate = task.get("date")
                jtime = task.get("time")

                if not jdate or not jtime:
                    log(f"  SKIP (no date/time): {title} | date={jdate} time={jtime}")
                    continue

                # trigger_key شامل تاریخ و زمان — پس از ویرایش دوباره آلارم می‌زند
                trigger_key = f"{task_id}_{jdate}_{jtime}"

                if repeat_type == "بدون تکرار" and trigger_key in triggered_tasks:
                    continue

                dt = convert_jalali_to_gregorian(jdate, jtime)
                if not dt:
                    continue

                diff_debug = (now - dt).total_seconds()
                log(f"  Task: {title} | dt={dt} | diff={diff_debug:.0f}s | repeat={repeat_type}")

                # catch-up برای تکراری‌ها
                if repeat_type in ("روزانه", "هفتگی") and dt < now - datetime.timedelta(seconds=60):
                    dt = advance_to_today(dt, repeat_type)
                    new_date, new_time = gregorian_to_jalali_str(dt)
                    if new_date and (new_date != jdate or new_time != jtime):
                        task["date"] = new_date
                        task["time"] = new_time
                        update_task(task_id, task)
                        log(f"  Catch-up → {new_date} {new_time}")

                diff = (now - dt).total_seconds()
                if 0 <= diff < 60:
                    log(f"*** ALARM: {title} ***")
                    show_notification("یادآوری", title)
                    play_sound()

                    if repeat_type == "بدون تکرار":
                        triggered_tasks.add(trigger_key)
                    else:
                        next_dt = get_next_trigger_date(dt, repeat_type)
                        if next_dt:
                            nd, nt = gregorian_to_jalali_str(next_dt)
                            if nd:
                                task["date"] = nd
                                task["time"] = nt
                                update_task(task_id, task)
                                log(f"  Next alarm → {nd} {nt}")

            # پاکسازی triggered_tasks با trigger_key
            current_keys = {f"{t.get('id')}_{t.get('date')}_{t.get('time')}" for t in tasks}
            triggered_tasks.intersection_update(current_keys)

        except Exception as e:
            import traceback
            log(f"check_tasks error: {e}\n{traceback.format_exc()}")

        stop_event.wait(timeout=20)

# ── شروع
def start_reminder():
    stop_event.clear()
    t = threading.Thread(target=check_tasks, daemon=True)
    t.start()
    log("Reminder thread started.")

# ── توقف
def stop_reminder():
    stop_event.set()
    log("Reminder stopped.")
