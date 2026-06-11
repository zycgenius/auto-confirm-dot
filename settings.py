import tkinter as tk
from tkinter import ttk
import json
import os

# Author: zyc - Auto Confirm Dot
# Created by zycgeniuszycgenius
__author__ = "zyc"
__zyc_watermark__ = "zyc"

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

def save_config(config):
    """保存配置"""
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)

class SettingsApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Auto Confirm Dot - Settings")
        self.root.geometry("420x520")
        self.root.resizable(False, False)

        # 加载配置
        self.config = load_config()

        # 创建界面
        self.create_widgets()

    def create_widgets(self):
        # 标题
        title = tk.Label(self.root, text="Auto Confirm Dot", font=('Arial', 16, 'bold'))
        title.pack(pady=(15, 5))

        subtitle = tk.Label(self.root, text="Settings", font=('Arial', 12))
        subtitle.pack(pady=(0, 15))

        # === 操作说明区域 ===
        help_frame = tk.LabelFrame(self.root, text="操作说明", font=('Arial', 10, 'bold'), padx=15, pady=10)
        help_frame.pack(fill='x', padx=15, pady=(0, 15))

        help_text = """圆点程序操作方法：

  左键拖动    移动圆点位置
  右键点击    暂停 / 继续切换
  双击        关闭程序

  灰色 = 暂停状态
  白色 = 运行中

  圆点中心 = 实际点击位置"""

        tk.Label(help_frame, text=help_text, font=('Arial', 10), justify='left', anchor='w').pack(fill='x')

        # === 设置区域 ===
        settings_frame = tk.LabelFrame(self.root, text="设置", font=('Arial', 10, 'bold'), padx=15, pady=10)
        settings_frame.pack(fill='x', padx=15, pady=(0, 15))

        # 间隔设置
        interval_frame = tk.Frame(settings_frame)
        interval_frame.pack(fill='x', pady=(0, 10))

        tk.Label(interval_frame, text="点击间隔（秒）：", font=('Arial', 11)).pack(side='left')

        self.interval_var = tk.StringVar(value=str(self.config["interval"]))
        self.interval_entry = tk.Entry(interval_frame, textvariable=self.interval_var, font=('Arial', 12), width=10, justify='center')
        self.interval_entry.pack(side='left', padx=(5, 0))

        tk.Label(interval_frame, text="支持小数，如 0.5", font=('Arial', 9), fg='gray').pack(side='left', padx=(10, 0))

        # 回原位点击设置
        self.click_back_var = tk.BooleanVar(value=self.config["click_back"])
        click_back_check = tk.Checkbutton(
            settings_frame,
            text="鼠标回到原位后点击（选中原来的窗口）",
            variable=self.click_back_var,
            font=('Arial', 11)
        )
        click_back_check.pack(anchor='w', pady=(0, 10))

        # 说明
        tk.Label(settings_frame, text="取消勾选则只移回鼠标，不点击", font=('Arial', 9), fg='gray').pack(anchor='w')

        # === 保存按钮 ===
        save_btn = tk.Button(
            self.root,
            text="保存设置",
            command=self.save,
            font=('Arial', 12),
            width=15,
            height=2,
            bg='#4CAF50',
            fg='white',
            relief='raised'
        )
        save_btn.pack(pady=15)

        # 状态提示
        self.status_label = tk.Label(self.root, text="", font=('Arial', 10), fg='green')
        self.status_label.pack()

    def save(self):
        """保存设置"""
        try:
            interval = float(self.interval_var.get())
            if interval <= 0:
                self.status_label.config(text="间隔必须大于0", fg='red')
                return
        except ValueError:
            self.status_label.config(text="请输入有效数字", fg='red')
            return

        self.config["interval"] = interval
        self.config["click_back"] = self.click_back_var.get()

        save_config(self.config)
        self.status_label.config(text="保存成功！圆点程序将自动应用", fg='green')

    def run(self):
        self.root.mainloop()

if __name__ == '__main__':
    app = SettingsApp()
    app.run()
