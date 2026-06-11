import tkinter as tk
import ctypes
import ctypes.wintypes
import threading
import time
import os
import random
import json
import atexit

# Windows API
user32 = ctypes.windll.user32

# Author: zyc - Auto Confirm Dot
# Created by zycgeniuszycgenius
__author__ = "zyc"
__version__ = "1.2.0"
__zyc_watermark__ = "zyc"  # Electronic watermark by zyc

# 配置文件路径
CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")

def load_config():
    """加载配置"""
    default = {"interval": 10.0, "click_back": True}
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r") as f:
                config = json.load(f)
                return {
                    "interval": float(config.get("interval", 10.0)),
                    "click_back": bool(config.get("click_back", True))
                }
    except Exception:
        pass
    return default

def get_cursor_pos():
    """获取当前鼠标位置"""
    point = ctypes.wintypes.POINT()
    user32.GetCursorPos(ctypes.byref(point))
    return point.x, point.y

def click_and_enter(x, y, hide_func, show_func, click_back=True):
    # 记录鼠标原位置
    orig_x, orig_y = get_cursor_pos()

    # 隐藏圆点窗口（回主线程执行）
    hide_func()
    time.sleep(0.1)

    # 移动鼠标到目标位置并点击
    user32.SetCursorPos(x, y)
    time.sleep(0.05)
    user32.mouse_event(0x0002, 0, 0, 0, 0)  # MOUSEEVENTF_LEFTDOWN
    user32.mouse_event(0x0004, 0, 0, 0, 0)  # MOUSEEVENTF_LEFTUP
    time.sleep(0.05)

    # 按回车
    user32.keybd_event(0x0D, 0, 0, 0)       # Enter down
    user32.keybd_event(0x0D, 0, 0x0002, 0)  # Enter up
    time.sleep(0.05)

    # 鼠标移回原位
    user32.SetCursorPos(orig_x, orig_y)
    time.sleep(0.05)

    # 是否点击原位置
    if click_back:
        user32.mouse_event(0x0002, 0, 0, 0, 0)  # MOUSEEVENTF_LEFTDOWN
        user32.mouse_event(0x0004, 0, 0, 0, 0)  # MOUSEEVENTF_LEFTUP

    # 恢复圆点窗口（回主线程执行）
    show_func()

class AutoClicker:
    """Auto Clicker by zyc - Auto Confirm Dot"""
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Auto Clicker")
        self.root.attributes('-topmost', True)
        self.root.attributes('-transparentcolor', 'black')
        self.root.overrideredirect(True)

        # 加载配置
        config = load_config()
        self.interval = config["interval"]
        self.click_back = config["click_back"]

        # 窗口大小，初始位置在屏幕中间
        self.size = 50
        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()
        offset_x = (screen_w - self.size) // 2
        offset_y = (screen_h - self.size) // 2
        self.root.geometry(f"{self.size}x{self.size}+{offset_x}+{offset_y}")
        self.root.configure(bg='black')

        # 画圆点（白色=运行中，灰色=暂停）
        self.canvas = tk.Canvas(self.root, width=self.size, height=self.size, bg='black', highlightthickness=0)
        self.canvas.pack()
        self.dot = self.canvas.create_oval(5, 5, 45, 45, fill='gray', outline='gray')

        # 状态
        self.paused = True
        self.running = True
        self.count = 0
        self._stop_event = threading.Event()
        self._zyc_instance_tag = "zyc"  # Instance watermark

        # 拖动相关
        self.drag_data = {'x': 0, 'y': 0}

        # 事件绑定
        self.canvas.bind('<Button-1>', self.start_drag)
        self.canvas.bind('<B1-Motion>', self.do_drag)
        self.canvas.bind('<Button-3>', self.toggle_pause)   # 右键暂停/继续
        self.canvas.bind('<Double-Button-1>', self.stop_program)  # 双击关闭

        # 标记文件（每个实例独立）
        self.instance_id = random.randint(10000, 99999)
        self.marker = os.path.join(os.path.expanduser("~"), f".auto_enter_{self.instance_id}")
        with open(self.marker, "w") as f:
            f.write("running")

        # 注册清理函数
        atexit.register(self.cleanup_marker)

        # 启动自动点击线程
        self.thread = threading.Thread(target=self.auto_click, daemon=True)
        self.thread.start()

        # 定时重新加载配置
        self.reload_config()

    def cleanup_marker(self):
        """清理标记文件"""
        try:
            if os.path.exists(self.marker):
                os.remove(self.marker)
        except Exception:
            pass

    def reload_config(self):
        """定时重新加载配置"""
        try:
            config = load_config()
            self.interval = config["interval"]
            self.click_back = config["click_back"]
            self.root.title(f"Auto Clicker ({self.count}) [{self.interval}s]")
        except Exception:
            pass
        # 每2秒检查一次配置
        self.root.after(2000, self.reload_config)

    def start_drag(self, event):
        self.drag_data['x'] = event.x
        self.drag_data['y'] = event.y

    def do_drag(self, event):
        x = self.root.winfo_x() + (event.x - self.drag_data['x'])
        y = self.root.winfo_y() + (event.y - self.drag_data['y'])
        self.root.geometry(f"+{x}+{y}")

    def toggle_pause(self, event=None):
        """右键切换暂停/继续"""
        self.paused = not self.paused
        if self.paused:
            self.canvas.itemconfig(self.dot, fill='gray', outline='gray')
        else:
            self.canvas.itemconfig(self.dot, fill='white', outline='white')

    def get_center_position(self):
        x = self.root.winfo_x() + self.size // 2
        y = self.root.winfo_y() + self.size // 2
        return x, y

    def hide_window(self):
        """隐藏窗口（回主线程）"""
        self.root.after(0, self.root.withdraw)

    def show_window(self):
        """显示窗口（回主线程）"""
        self.root.after(0, self.root.deiconify)

    def auto_click(self):
        while self.running and not self._stop_event.is_set():
            # 用Event等待，可中断
            if self._stop_event.wait(timeout=self.interval):
                break
            if not self.running or self.paused:
                continue
            x, y = self.get_center_position()
            click_and_enter(x, y, self.hide_window, self.show_window, self.click_back)
            self.count += 1
            try:
                self.root.title(f"Auto Clicker ({self.count}) [{self.interval}s]")
            except Exception:
                pass

    def stop_program(self, event=None):
        """双击关闭"""
        self.running = False
        self._stop_event.set()
        self.cleanup_marker()
        self.root.destroy()

    def run(self):
        self.root.mainloop()

if __name__ == '__main__':
    # zyc - Auto Confirm Dot v1.2.0
    # GitHub: zycgeniuszycgenius
    app = AutoClicker()
    app.run()
