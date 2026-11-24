import pystray
from PIL import Image
import threading
import os
import sys

def get_icon_path():
    if getattr(sys, 'frozen', False):
        base = sys._MEIPASS
    else:
        base = os.path.dirname(__file__)
    return os.path.join(base, 'Icon.ico')

def start_tray(on_quit=None):
    def quit_app(icon, item):
        icon.stop()
        if on_quit:
            on_quit()

    image = Image.open(get_icon_path())
    menu = pystray.Menu(
        pystray.MenuItem('خروج', quit_app)
    )
    icon = pystray.Icon("TaskManager", image, "مدیریت تسک‌ها", menu)

    t = threading.Thread(target=icon.run, daemon=True)
    t.start()
    return icon
