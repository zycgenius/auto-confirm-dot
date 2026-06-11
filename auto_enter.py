import tkinter as tk
import ctypes
import ctypes.wintypes
import threading
import time
import os
import random
import atexit

# Windows API
user32 = ctypes.windll.user32

# Author: zyc - Auto Confirm Dot
# Created by zycgeniuszycgenius
__author__ = "zyc"
__version__ = "1.1.0"
__zyc_watermark__ = "zyc"  # Electronic watermark by zyc

def get_cursor_pos():
    """获取当前鼠标位置"""
    point = ctypes.wintypes.POINT()
    user32.GetCursorPos(ctypes.byref(point))
    return point.x, point.y

def click_and_enter(x, y, hide_func, show_func):
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

    # 鼠标移回原位并点击（选中原来的窗口）
    user32.SetCursorPos(orig_x, orig_y)
    time.sleep(0.05)
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

        # 窗口大小，位置随机偏移避免重叠
        self.size = 50
        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()
        offset_x = random.randint(50, max(100, screen_w - 100))
        offset_y = random.randint(50, max(100, screen_h - 100))
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
        self.interval = 10.0  # 默认间隔10秒
        self._stop_event = threading.Event()
        self._zyc_instance_tag = "zyc"  # Instance watermark

        # 拖动相关
        self.drag_data = {'x': 0, 'y': 0, 'moved': False}

        # 事件绑定
        self.canvas.bind('<Button-1>', self.on_left_click)
        self.canvas.bind('<B1-Motion>', self.on_drag)
        self.canvas.bind('<ButtonRelease-1>', self.on_left_release)
        self.canvas.bind('<Button-3>', self.show_interval_dialog)   # 右键设置间隔
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

    def cleanup_marker(self):
        """清理标记文件"""
        try:
            if os.path.exists(self.marker):
                os.remove(self.marker)
        except Exception:
            pass

    def on_left_click(self, event):
        """左键按下"""
        self.drag_data['x'] = event.x
        self.drag_data['y'] = event.y
        self.drag_data['moved'] = False

    def on_drag(self, event):
        """拖动"""
        dx = event.x - self.drag_data['x']
        dy = event.y - self.drag_data['y']
        if abs(dx) > 3 or abs(dy) > 3:
            self.drag_data['moved'] = True
        x = self.root.winfo_x() + dx
        y = self.root.winfo_y() + dy
        self.root.geometry(f"+{x}+{y}")

    def on_left_release(self, event):
        """左键释放，如果没移动则暂停/继续"""
        if not self.drag_data['moved']:
            self.toggle_pause()

    def show_interval_dialog(self):
        """显示间隔设置对话框"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Set Interval")
        dialog.attributes('-topmost', True)
        dialog.geometry("250x120")
        dialog.resizable(False, False)
        dialog.configure(bg='white')

        # 居中显示
        x = self.root.winfo_x()
        y = self.root.winfo_y()
        dialog.geometry(f"+{x}+{y-130}")

        # 标签
        tk.Label(dialog, text="Interval (seconds):", bg='white', font=('Arial', 11)).pack(pady=(15, 5))

        # 输入框
        entry = tk.Entry(dialog, font=('Arial', 12), justify='center', width=10)
        entry.pack(pady=5)
        entry.insert(0, str(self.interval))
        entry.select_range(0, tk.END)
        entry.focus()

        def confirm():
            try:
                val = float(entry.get())
                if val > 0:
                    self.interval = val
                    self.root.title(f"Auto Clicker ({self.count}) [{self.interval}s]")
                    dialog.destroy()
            except ValueError:
                pass

        # 回车确认
        entry.bind('<Return>', lambda e: confirm())

        # 确认按钮
        tk.Button(dialog, text="OK", command=confirm, font=('Arial', 10), width=8).pack(pady=10)

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
            click_and_enter(x, y, self.hide_window, self.show_window)
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
    # zyc - Auto Confirm Dot v1.1.0
    # GitHub: zycgeniuszycgenius
    app = AutoClicker()
    app.run()
