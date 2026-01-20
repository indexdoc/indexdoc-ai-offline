import threading
import time
import subprocess
import tkinter
import tkinter as tk
from functools import partial
from tkinter import ttk, filedialog, messagebox
import os
import json
from datetime import datetime
import webbrowser
import sys

import pythoncom
import requests
import winshell as winshell

from install_util import DirUtil


# ========================
# 主应用程序类
# ========================
class ProductInstallerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("IndexDoc - 个人 AI 工作台 安装程序")
        self.root.geometry("1000x610")
        self.root.resizable(False, False)

        # Clam 风格配色方案
        self.colors = {
            'primary_bg': '#f0f0f0',  # 主背景色 - Clam浅灰色
            'header_bg': '#4a86e8',  # 标题栏背景 - 柔和蓝色
            'header_fg': 'white',  # 标题栏文字色
            'card_bg': 'white',  # 卡片背景
            'card_border': '#d0d0d0',  # 卡片边框色 - 浅灰边框
            'text_primary': '#2d3748',  # 主要文字色 - 深灰黑
            'text_secondary': '#718096',  # 次要文字色 - 中灰色
            'accent': '#3182ce',  # 强调色 - 标准蓝色
            'accent_hover': '#2b6cb0',  # 强调色悬停
            'success': '#38a169',  # 成功色 - 柔和绿色
            'warning': '#ed8936',  # 警告色 - 暖橙色
            'disabled': '#a0a0a0',  # 禁用色
            'log_bg': '#2d3748',  # 日志背景 - 深灰
            'log_fg': '#f7fafc',  # 日志文字 - 浅灰
            'progress_bg': '#4299e1',  # 进度条颜色 - 明亮蓝色
            'copyright': '#718096'  # 版权文字色 - 中灰色g
        }

        self.root.configure(bg=self.colors['primary_bg'])
        self.root.withdraw()

        self.selected_product_id = tk.IntVar(value=0)
        self.selected_product_path = "IndexDoc"
        self.selected_product = None
        self.version_info = None
        self.install_path = tk.StringVar()
        self.product_data = {}
        self.app_path = ''

        self.config_file = "product_series.json"
        self.selected_install_path = os.path.expanduser("~")

        self.setup_styles()
        self.show_security_notice()
        self.setup_ui()
        self.load_product_series()

    def show_security_notice(self):
        """显示美化版安全声明窗口，用户确认后才继续"""
        # 创建自定义弹窗（Toplevel窗口）
        notice_window = tk.Toplevel(self.root)
        notice_window.withdraw()
        notice_window.title("安全声明 - IndexDoc")
        # notice_window.geometry("800x600")
        notice_window.overrideredirect(True)  # 去掉窗口边框
        notice_window.resizable(False, False)
        notice_window.grab_set()  # 模态窗口，阻止操作主窗口

        # 设置窗口图标
        try:
            icon_path = self.resource_path('html/favicon-indexdoc.ico')
            notice_window.iconbitmap(icon_path)
        except:
            pass

        # 定义弹窗配色（与主程序一致）
        colors = self.colors
        bg_color = colors['accent']
        # 顶部标题栏
        header_frame = tk.Frame(notice_window, bg=bg_color, height=60)
        header_frame.pack(fill="x", side="top")
        header_frame.pack_propagate(False)
        border_frame = tk.Frame(
            header_frame,
            bg="#90caf9",  # 浅绿色边框（与深绿#2e7d32搭配）
            height=2  # 边框高度（细边框更精致）
        )
        border_frame.pack(fill="x", side="bottom")
        title_label = tk.Label(
            header_frame,
            text="🛡️  IndexDoc 安全声明",
            font=("Microsoft YaHei", 16, "bold"),
            fg=colors['header_fg'],
            bg=bg_color
        )
        title_label.pack(side="left", padx=15, pady=10)

        # 内容容器（带滚动条）
        content_frame = tk.Frame(notice_window, bg=colors['primary_bg'])
        content_frame.pack(fill="both", expand=True, padx=20, pady=15)

        # 文本显示区域（带滚动条）
        text_frame = tk.Frame(content_frame, bg=colors['card_bg'], relief="ridge", bd=1)
        text_frame.pack(fill="both", expand=True)

        # 文本框
        notice_text = tk.Text(
            text_frame,
            font=("Microsoft YaHei", 10),
            bg=colors['card_bg'],
            fg=colors['text_primary'],
            relief="flat",
            bd=0,
            wrap="word"
        )
        notice_text.pack(side="left", fill="both", expand=True, padx=15, pady=15)

        # 安全声明内容（带格式优化）
        content = f"""【软件信息】
    • 软件名称：IndexDoc - 个人 AI 工作台
    • 软件类型：纯绿色桌面应用程序
    • 开发公司：杭州智予数信息技术有限公司
    • 官方网址：https://www.indexdoc.com
    
    【安全承诺】
    • 本软件无恶意代码、无捆绑安装、无后台偷跑行为
    • 所有文件经过多重安全检测，符合国家网络安全相关标准
    • 严格保护用户隐私，不收集任何个人敏感信息
    
    【安全软件兼容说明】
    ✅ 腾讯电脑管家：完全兼容，无拦截提示
    ✅ 火绒安全软件：完全兼容，无拦截提示
    ⚠️  360安全软件：可能出现误报拦截，解决方案如下：
       1. 当弹出拦截提示时，选择"信任此程序"
       2. 手动添加安装目录至360安全中心的"信任区"
       3. 若仍有问题，暂时关闭360实时防护后重试安装
    
    【官方联系方式】
    • 官方网站：https://www.indexdoc.com
    • 联系我们：https://www.indexdoc.com/contact.html
    • 客服邮箱：indexdoc@qq.com
    
    【重要提示】
    ⚠️  请务必从官方渠道下载本软件，非官方渠道下载可能存在安全风险！
    ⚠️  点击"我已阅读并同意"即表示您接受以上声明内容。
    """
        notice_text.insert("1.0", content)
        notice_text.config(state="disabled")  # 禁止编辑

        # 底部按钮区域
        btn_frame = tk.Frame(notice_window, bg=colors['primary_bg'])
        btn_frame.pack(fill="x", padx=20, pady=10)

        # 同意按钮（强调色）
        agree_btn = ttk.Button(
            btn_frame,
            text="我已阅读并同意",
            style="Install.TButton",
            command=notice_window.destroy  # 关闭弹窗，继续执行主程序
        )
        agree_btn.pack(side="right", padx=(5, 0))

        # 取消按钮（灰色）
        cancel_btn = ttk.Button(
            btn_frame,
            text="取消安装",
            style="Quit.TButton",
            command=lambda: (notice_window.destroy(), self.root.quit(), sys.exit(0))  # 关闭弹窗并退出程序
        )
        cancel_btn.pack(side="right", padx=(0, 10))

        # 窗口居中
        notice_window.update_idletasks()
        x = (notice_window.winfo_screenwidth() // 2) - (700 // 2)
        y = (notice_window.winfo_screenheight() // 2) - (700 // 2)
        notice_window.geometry(f"700x700+{x}+{y}")
        self.center_window()
        notice_window.deiconify()

    def setup_styles(self):
        """设置Clam主题和自定义配色"""
        style = ttk.Style()
        style.theme_use('clam')

        # 为进度条设置Clam风格配色
        style.configure("Custom.Horizontal.TProgressbar",
                        background=self.colors['progress_bg'],
                        troughcolor='#e2e8f0')  # Clam风格浅灰槽色

        # 安装按钮样式
        style.configure("Install.TButton", background="#2d7ff9", foreground="white")
        style.map("Install.TButton",
                  background=[('active', '#1a68e0'), ('disabled', '#c9d1d9')],
                  foreground=[('disabled', '#86909c')])
        # 退出按钮样式
        style.configure("Quit.TButton", background="#6b7280", foreground="white")
        style.map("Quit.TButton",
                  background=[('active', '#4b5563')])

        style.configure("IconBrowse.TButton",
                        font=("Microsoft YaHei", 10),  # 字体大小与其他按钮一致
                        padding=(3, 1, 3, 1),  # 内边距匹配按钮高度，确保尺寸协调
                        background=self.colors['primary_bg'],  # 主界面背景色，完全融合
                        borderwidth=0, relief="flat"
                        )  # 关键：移除边框，消除线条干扰

    def resource_path(self, relative_path):
        """ 获取资源的正确路径，兼容 PyInstaller 打包 """
        try:
            # PyInstaller 会创建一个临时文件夹 _MEIPASS
            base_path = sys._MEIPASS
        except Exception:
            # 普通运行时，base_path 是项目根目录的上一级（根据你的结构调整）
            base_path = os.path.abspath("..")  # 或 os.path.dirname(__file__)
        return os.path.join(base_path, relative_path)

    def setup_ui(self):
        """设置界面 - 应用Clam风格配色"""
        icon_path = self.resource_path('html/favicon-indexdoc.ico')
        self.root.iconbitmap(icon_path)
        # Banner区域 - Clam蓝色标题栏
        header_frame = tk.Frame(self.root, bg=self.colors['header_bg'], height=120)
        header_frame.pack(fill="x", side="top")
        header_frame.pack_propagate(False)

        content_frame = tk.Frame(header_frame, bg=self.colors['header_bg'])
        content_frame.pack(expand=True, fill="both", padx=25, pady=15)

        title_frame = tk.Frame(content_frame, bg=self.colors['header_bg'])
        title_frame.pack(expand=True, fill="both")

        title_label = tk.Label(title_frame, text="IndexDoc - 个人 AI 工作台 安装程序",
                               font=("Microsoft YaHei", 18, "bold"),
                               fg=self.colors['header_fg'],
                               bg=self.colors['header_bg'])
        title_label.pack(anchor="center", pady=(5, 0))

        # 副标题与网址整合控件
        subtitle_website_label = tk.Label(title_frame,
                                          text="简单，智能，高效 | www.IndexDoc.com",
                                          font=("Microsoft YaHei", 11),
                                          fg='#e6f2ff',  # 浅蓝色，在深蓝背景上更可见
                                          bg=self.colors['header_bg'],
                                          cursor="hand2")
        subtitle_website_label.pack(anchor="center", pady=(8, 0))
        subtitle_website_label.bind("<Button-1>", lambda e: webbrowser.open("https://www.indexdoc.com"))

        # 主内容区域
        main_container = tk.Frame(self.root, bg=self.colors['primary_bg'])
        main_container.pack(fill="both", expand=True, padx=25, pady=15)

        self.create_product_selection(main_container)
        self.create_install_section(main_container)
        self.create_button_section(main_container)
        self.create_log_section(main_container)

        self.create_bottom_section()
        # 关键：启用print重定向（传入日志文本框和主窗口）
        self.redirect_print_to_log(self.info_text, self)
        # 初始日志
        self.log("=" * 60)
        self.log("🚀 欢迎使用 IndexDoc - 个人 AI 工作台 安装程序")
        self.log("=" * 60)
        self.log(f"📁 默认安装路径: {self.selected_product_path}")
        self.log("⏳ 正在加载产品信息...")

    def create_button_section(self, parent):
        button_frame = tk.Frame(parent, bg=self.colors['primary_bg'])
        button_frame.pack(fill="x", pady=(30, 15))

        button_container = tk.Frame(button_frame, bg=self.colors['primary_bg'])
        button_container.pack(anchor="center")

        # 安装按钮 - 使用Clam蓝色
        self.install_btn = ttk.Button(button_container, text="安装", style="Install.TButton",
                                      command=self.start_installation,
                                      state="disabled")
        self.install_btn.pack(side="left", padx=(0, 10))
        # 退出按钮 - 灰色
        self.cancel_btn = ttk.Button(button_container, text="退出", style="Quit.TButton", command=self.root.quit)
        self.cancel_btn.pack(side="left")

    def create_log_section(self, parent):
        self.log_frame = tk.Frame(parent, bg=self.colors['primary_bg'])
        self.log_frame.pack(fill="both", expand=True, pady=(0, 0))
        self.log_frame.pack_forget()

        self.info_text = tk.Text(self.log_frame, height=8, wrap="word",
                                 font=("Consolas", 9),
                                 bg=self.colors['log_bg'],
                                 fg=self.colors['log_fg'],
                                 insertbackground='white',
                                 relief="sunken",
                                 bd=1)
        scrollbar_log = ttk.Scrollbar(self.log_frame, orient="vertical",
                                      command=self.info_text.yview)
        self.info_text.configure(yscrollcommand=scrollbar_log.set)

        self.info_text.pack(side="left", fill="both", expand=True)
        scrollbar_log.pack(side="right", fill="y")

        self.progress_frame = tk.Frame(parent, bg=self.colors['primary_bg'])
        self.progress_frame.pack(fill="x", pady=(5, 0))
        self.progress_frame.pack_forget()

        # 使用自定义样式的进度条
        self.progress = ttk.Progressbar(self.progress_frame, mode='determinate',
                                        style="Custom.Horizontal.TProgressbar")
        self.progress.pack(fill="x")

    def create_shortcut(self, name, target, icon=None, args='', work_dir=None):
        """在桌面创建一个快捷方式 (.lnk)

        :param name: 快捷方式名称（不带后缀）
        :param target: 目标程序路径（.exe 或 .py 等）
        :param icon: 图标路径（可选）
        :param args: 启动参数（可选）
        :param work_dir: 工作目录（可选）
        """

        # 尝试初始化 COM
        try:
            pythoncom.CoInitialize()
        except pythoncom.com_error:
            pass  # 已经初始化则忽略

        # 获取桌面路径
        desktop = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
        shortcut_path = os.path.join(desktop, f"{name}.lnk")

        # 创建快捷方式对象
        import win32com.client
        shell = win32com.client.Dispatch('WScript.Shell')
        shortcut = shell.CreateShortcut(shortcut_path)

        # 设置属性
        shortcut.TargetPath = target
        shortcut.Arguments = args
        shortcut.WorkingDirectory = work_dir if work_dir else os.path.dirname(target)
        if icon and os.path.exists(icon):
            shortcut.IconLocation = icon
        else:
            shortcut.IconLocation = target  # 默认用程序图标

        # 保存
        shortcut.save()
        print(f"✅ 快捷方式已创建")

    def show_installation_ui(self):
        self.root.geometry("1000x800")
        self.center_window()
        self.log_frame.pack(fill="both", expand=True, pady=(0, 0))
        self.progress_frame.pack(fill="x", pady=(5, 0))

    def create_bottom_section(self):
        bottom_frame = tk.Frame(self.root, bg=self.colors['primary_bg'])
        bottom_frame.pack(fill="x", side="bottom", padx=25, pady=(5, 15))

        bottom_content_frame = tk.Frame(bottom_frame, bg=self.colors['primary_bg'])
        bottom_content_frame.pack(fill="x")

        center_frame = tk.Frame(bottom_content_frame, bg=self.colors['primary_bg'])
        center_frame.pack(anchor="center")

        copyright_label = tk.Label(center_frame,
                                   text=f"Copyright © {datetime.now().year} 杭州智予数信息技术有限公司",
                                   font=("Microsoft YaHei", 8),
                                   fg=self.colors['copyright'],
                                   bg=self.colors['primary_bg'])
        copyright_label.pack(side="left")

        contact_btn = tk.Label(center_frame, text=" 🔗 联系我们",
                               font=("Microsoft YaHei", 8),
                               fg=self.colors['accent'],
                               bg=self.colors['primary_bg'],
                               cursor="hand2")
        contact_btn.pack(side="left", padx=(5, 0))
        contact_btn.bind("<Button-1>", lambda e: self.open_contact_support())

    def create_product_selection(self, parent):
        self.card_container = tk.Frame(parent, bg=self.colors['primary_bg'])
        self.card_container.pack(fill="x", pady=(0, 15))

    def create_install_section(self, parent):
        """安装目录区域 - Clam风格"""
        dir_frame = tk.Frame(parent, bg=self.colors['primary_bg'])
        dir_frame.pack(fill="x", pady=(0, 12))

        dir_selection_frame = tk.Frame(dir_frame, bg=self.colors['primary_bg'])
        dir_selection_frame.pack(fill="x")

        dir_label = tk.Label(dir_selection_frame, text="安装目录：",
                             font=("Microsoft YaHei", 10, "bold"),
                             bg=self.colors['primary_bg'],
                             fg=self.colors['text_primary'])
        dir_label.pack(side="left")

        # 创建容器框架来包裹输入框和按钮，让它们紧密连接
        entry_button_frame = tk.Frame(dir_selection_frame, bg=self.colors['primary_bg'])
        entry_button_frame.pack(side="left", fill="x", expand=True, padx=(10, 0))

        # 安装目录输入栏
        self.dir_entry = tk.Entry(entry_button_frame,
                                  textvariable=self.install_path,
                                  font=("Microsoft YaHei", 10),
                                  relief="sunken",
                                  bd=1,
                                  bg='white',
                                  fg=self.colors['text_primary'])
        self.dir_entry.pack(side="left", fill="x", expand=True)

        # 选择目录按钮 - 设置最小宽度
        browse_btn = ttk.Button(
            entry_button_frame,
            text="📂",
            style="IconBrowse.TButton",
            command=self.browse_directory,
            width=3  # 设置最小宽度
        )
        browse_btn.pack(side="right")

        self.install_path.set(self.selected_install_path)

    def create_product_card(self, product, row, col):
        """产品卡片 - Clam风格"""
        card_frame = tk.Frame(self.card_container,
                              bg=self.colors['card_bg'],
                              relief="ridge",
                              bd=1,
                              padx=12,
                              pady=10,
                              width=200,
                              height=130)
        card_frame.pack_propagate(False)
        card_frame.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")

        self.card_container.grid_rowconfigure(row, weight=1)
        self.card_container.grid_columnconfigure(col, weight=1)

        content_frame = tk.Frame(card_frame, bg=self.colors['card_bg'])
        content_frame.pack(fill="both", expand=True)

        header_frame = tk.Frame(content_frame, bg=self.colors['card_bg'])
        header_frame.pack(fill="x", pady=(0, 8))

        radio = tk.Radiobutton(header_frame,
                               variable=self.selected_product_id,
                               value=product['id'],
                               command=lambda p=product: self.on_product_selected(p),
                               bg=self.colors['card_bg'],
                               fg=self.colors['text_primary'],
                               activebackground=self.colors['card_bg'],
                               font=("Microsoft YaHei", 10))
        radio.pack(side="left")

        name_status_frame = tk.Frame(header_frame, bg=self.colors['card_bg'])
        name_status_frame.pack(side="left", fill="x", expand=True, padx=(5, 0))

        name_label = tk.Label(name_status_frame, text=product['name'],
                              font=("Microsoft YaHei", 10, "bold"),
                              bg=self.colors['card_bg'],
                              fg=self.colors['text_primary'],
                              wraplength=100, justify="left")
        name_label.pack(side="left")

        # 状态标签
        if product.get('downloadable', False):
            status_text = "🟢 可安装"
            status_label = tk.Label(name_status_frame, text=status_text,
                                    font=("Microsoft YaHei", 8),
                                    bg=self.colors['card_bg'],
                                    fg=self.colors['success'])
        else:
            radio.config(state="disabled")
            status_text = "🟡 联系客服"
            status_label = tk.Label(name_status_frame, text=status_text,
                                    font=("Microsoft YaHei", 8),
                                    bg=self.colors['card_bg'],
                                    fg=self.colors['warning'],
                                    cursor="hand2")
            status_label.bind("<Button-1>", lambda e: self.open_contact_support())
        status_label.pack(side="left", padx=(5, 0))

        desc_frame = tk.Frame(content_frame, bg=self.colors['card_bg'])
        desc_frame.pack(fill="both", expand=True)

        desc_text = tk.Text(desc_frame,
                            wrap="word",
                            font=("Microsoft YaHei", 8),
                            bg=self.colors['card_bg'],
                            fg=self.colors['text_secondary'],
                            relief="flat",
                            bd=0,
                            padx=0,
                            pady=0,
                            width=22,
                            height=3)
        desc_text.insert("1.0", product.get('description', '暂无描述'))
        desc_text.config(state="disabled")
        desc_text.pack(fill="both", expand=True)

        if product['id'] == 1:
            radio.invoke()

        return card_frame

    def browse_directory(self):
        directory = filedialog.askdirectory(title="选择安装目录")
        self.selected_install_path = directory
        if directory:
            self.install_path.set(os.path.normpath(self.selected_install_path + '/' + self.selected_product_path))
            self.log(f"📁 已选择安装目录: {directory}")

    def log(self, message: str):
        if len(message) == 0:
            self.info_text.insert(tk.END, "\n")
            return
        timestamp = time.strftime("%H:%M:%S")
        self.info_text.insert(tk.END, f"[{timestamp}] {message}\n")
        # if message.endswith('\n'):
        #     self.info_text.insert(tk.END, f"[{timestamp}] {message}")
        # else:
        #     self.info_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.info_text.see(tk.END)
        self.root.update()

    def log_progress(self, message):
        # 删除最后一行（如果有内容）
        line_count = int(self.info_text.index('end-1c').split('.')[0])
        if line_count > 1:
            # 删除最后一行（不包括末尾的空行）
            self.info_text.delete(f"{line_count - 1}.0", "end-1c")
        # 添加新消息（不换行）
        self.info_text.insert(tk.END, message)
        self.root.update()

    def update_progress(self, value):
        self.progress['value'] = value
        self.root.update()

    def open_contact_support(self):
        webbrowser.open("https://www.indexdoc.com/contact.html")

    def load_product_series(self):
        url = "https://app.indexdoc.com/pack/product_series.json"
        try:
            # 下载文件
            resp = requests.get(url, timeout=30)
            resp.raise_for_status()
            content = resp.text

            # 解析 JSON
            self.product_data = json.loads(content)
            self.on_products_loaded()
        except Exception as e:
            self.on_config_load_error(str(e))

    def on_products_loaded(self):
        self.log("✅ 产品信息加载成功")
        self.log(f"📅 数据更新日期: {self.product_data.get('updated_date', '未知')}")
        self.create_product_cards()
        self.log(f"📦 找到 {len(self.product_data.get('product_series', []))} 个产品版本")
        self.center_window()
        self.root.deiconify()

    def center_window(self):
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2) - 50
        y = max(y, 0)
        self.root.geometry(f'{width}x{height}+{x}+{y}')

    def create_product_cards(self):
        products = self.product_data.get('product_series', [])
        for i, product in enumerate(products):
            row = i // 4
            col = i % 4
            self.create_product_card(product, row, col)

    def on_product_selected(self, product):
        if product.get('downloadable', False):
            self.install_btn.config(state="normal")
            self.selected_product_path = product.get("path_name")
            self.selected_product = product
            self.install_path.set(os.path.normpath(self.selected_install_path + '/' + self.selected_product_path))
            self.log(f"✅ 已选择产品: {product['name']}")
            # 获取版本信息
            resp = requests.get('https://app.indexdoc.com/api/getCurrentVersion?productName=' + product['path_name'])
            resp.raise_for_status()
            self.version_info = json.loads(resp.text)['data']

        else:
            self.install_btn.config(state="disabled")
            self.log(f"⚠️  {product['name']} 暂不支持安装，请联系客服")

    def start_installation(self):
        if self.selected_product_id.get() == 0:
            messagebox.showerror("错误", "请选择要安装的产品版本")
            return
        if not self.install_path.get():
            messagebox.showerror("错误", "请选择安装目录")
            return

        selected_product = None
        for product in self.product_data.get('product_series', []):
            if product['id'] == self.selected_product_id.get():
                selected_product = product
                self.selected_product_path = product.get("path_name")
                break
        if not selected_product:
            messagebox.showerror("错误", "未找到选中的产品信息")
            return
        if not selected_product.get('downloadable', False):
            messagebox.showerror("错误", "选中的产品暂不支持安装，请联系客服")
            return

        result = messagebox.askyesno(
            "确认安装",
            f"确定要安装 {selected_product['name']} 吗？\n\n"
            f"安装目录: {self.install_path.get()}\n"
            f"所需空间: 约 2-5GB (根据版本不同)"
        )
        if not result:
            return

        self.show_installation_ui()
        # 启动安装线程
        installation_thread = threading.Thread(
            target=self.do_installation,
            args=(selected_product,),
            daemon=True
        )
        installation_thread.start()

    def do_installation(self, product):
        self.install_btn.config(state="disabled")
        self.cancel_btn.config(state="disabled")

        self.log("=" * 50)
        self.log(f"🚀 开始安装: {product['name']}")
        self.log(f"📁 安装目录: {self.install_path.get()}")
        self.log("=" * 50)

        # 1、检查环境
        self.log(f"检查环境是否满足安装要求：")
        from install_util import installer_util
        install_path = self.install_path.get()
        _is_success, _message = installer_util.check_environment(
            install_path,
            required_space_gb=5
        )
        if not _is_success:
            self.log(f"❌ 环境检查失败: {_message}")
            messagebox.showerror("环境检查失败", _message)
            return
        self.update_progress(10)
        self.log(f"环境检查通过")
        # 2、检查安装目录是否已存在，如已存在则提示是否覆盖安装
        if os.path.exists(install_path) and os.listdir(install_path):
            # 目录存在且非空
            user_choice = messagebox.askyesno(
                "目录已存在",
                f"安装目录 '{install_path}' 已存在且包含文件。\n"
                "是否继续并覆盖现有内容？\n\n"
                "⚠️ 注意：继续将删除该目录下的已安装的程序！"
            )
            if not user_choice:
                self.log("❌ 用户取消安装：不删除现有目录内容")
                self.install_btn.config(state="normal")
                self.cancel_btn.config(state="normal")
                return
            else:
                self.log("⚠️  用户选择覆盖现有安装目录")
                # 检查是否有程序正在运行
                if not self.check_and_close_running_programs(['indexdoc_win.exe', '_indexdoc_main.bin']):
                    self.log("安装中止：用户取消。")
                    self.install_btn.config(state="normal")
                    return  # 返回安装界面
                time.sleep(1)  # 等待文件句柄释放（1 秒或更久）
                self._delete_install_path_content(install_path)
        # 3、创建目录
        if not os.path.exists(install_path):
            DirUtil.create_directory(install_path, overwrite=False)
            self.log(f"创建安装目录：{install_path}")
        # 4、下载文件到安装目录，同时输出下载进度 在_download中更新下载进度
        self.log("下载安装包：")
        import asyncio
        success = asyncio.run(self._download(install_path))
        if not success:
            self.install_btn.config(state="normal", text="重新下载")
            self.cancel_btn.config(state="normal")
            messagebox.showinfo("提示", "下载失败，请重新下载。")
            return
        # 5、解压
        download_file_path = install_path + '/downloads' + self.selected_product['download_url']
        file_size_mb = os.path.getsize(download_file_path) / 1024 / 1024
        self.log(f"安装包下载成功：{download_file_path}({file_size_mb:.2f}MB)")
        self.update_progress(80)  # 下载成功
        import ZipUtil
        try:
            self.log(f"✅ 解压安装包{download_file_path}({file_size_mb:.2f}MB)")
            last_time = time.time()
            def decompress_progress(processed_size, filename, progress):
                nonlocal last_time
                if time.time() - last_time > 1:
                    print(f"\r进度: {progress:.1f}% | 已处理: {processed_size / 1024 / 1024:.2f} MB | 当前文件: {filename}",end="",flush=True)
                    last_time = time.time()
            ZipUtil.zip_decompress(download_file_path, install_path, progress_callback=decompress_progress)
            self.app_path = install_path + '/indexdoc_win.exe'
            self.update_progress(95)  # 解压完成
        except Exception as e:
            # 弹出错误提示框
            messagebox.showerror(
                "安装失败",
                f"解压过程中发生错误\n\n"
                f"请退出安装程序后重新下载安装。"
            )
            self.cancel_btn.config(state="normal")
            return
        # 创建快捷方式到桌面
        try:
            desktop = winshell.desktop()  # 获取桌面路径
            shortcut_path = os.path.join(desktop, "IndexDoc.lnk")
            if os.path.exists(shortcut_path):
                self.log("⚠️ 桌面已存在快捷方式“IndexDoc”，跳过创建。")
            else:
                self.create_shortcut('IndexDoc', install_path + '/indexdoc_win.exe')
                self.log("✅ 已在桌面创建快捷方式。")

            self.update_progress(100)
        except Exception as e:
            # 弹出错误提示框
            messagebox.showerror(
                "安装警告",
                f"创建桌面快捷方式失败\n\n"
                f"请至安装目录手工创建快捷方式。"
            )
            self.cancel_btn.config(state="normal")
            return
        self.log("🎉 安装完成，已在桌面创建快捷方式\"IndexDoc\"，请点击快捷方式启动应用。")
        self.log("本软件为纯绿色软件，请放心使用，请忽略杀毒软件的误报。")
        # messagebox.showinfo(
        #     "安装完成",
        #     f"{product['name']} 安装成功，已在桌面创建快捷方式\"IndexDoc\"！\n\n"
        #     f"安装目录: {self.install_path.get()}\n\n"
        #     f"感谢您选择 IndexDoc - 个人 AI 工作台！\n\n"
        #     f"本软件为纯绿色软件，请放心使用，忽略杀毒软件的误报！\n\n"
        # )

        # 删除安装包文件
        download_file = os.path.join(self.install_path.get(), "downloads", "indexdoc_win.zst")
        if os.path.exists(download_file):
            try:
                os.remove(download_file)
                self.log(f"🧹 已删除安装包文件: {download_file}")
            except Exception as e:
                self.log(f"⚠️ 删除安装包文件失败: {e}")

        res = messagebox.askyesno(
            "安装完成",
            f"{product['name']} 安装成功，已在桌面创建快捷方式 \"IndexDoc\"！\n\n"
            f"安装目录: {self.install_path.get()}\n\n"
            f"感谢您选择 IndexDoc - 个人 AI 工作台！\n\n"
            f"本软件为纯绿色软件，请放心使用，忽略杀毒软件的误报！\n\n"
            f"是否立即启动应用？"
        )

        if res:
            subprocess.Popen([self.app_path], cwd=os.path.dirname(self.app_path))
        else:
            os.startfile(self.install_path.get())
            self.log("📂 已打开安装目录。")
        self.root.quit()
        self.cancel_btn.config(state="normal")

    async def _download(self, install_path):
        name, ext = os.path.splitext(self.selected_product['download_url'])
        version = 'v' + self.version_info['version']
        download_servers = [_path + '/' + version + name + '_' + version + ext for _path in
                            self.product_data["download_servers"]]
        save_path = f"{install_path}/downloads"
        if not os.path.exists(save_path):
            DirUtil.create_directory(save_path, overwrite=False)
        from urllib.parse import urlparse
        filename = os.path.basename(urlparse(self.selected_product["download_url"]).path)
        save_path = f"{save_path}/{filename}"

        # 进度回调函数
        from install_util import DownloadUtil
        # 实时速度计算变量
        last_time = 0
        last_downloaded = 0
        print_interval = 1  # 每1秒打印一次

        def progress_callback(self_ref, progress: DownloadUtil.DownloadProgress):
            nonlocal last_time, last_downloaded
            current_time = time.time()
            # 频率控制：只有超过时间间隔才处理
            if current_time - last_time < print_interval:
                return
            # 计算实时速度
            last_time = current_time
            if progress.stage == "testing":
                message = f"🔄 测试下载速度 - 进度: {progress.progress * 100:.1f}% | " + \
                          " | ".join([f"源{i}: {speed:.1f}KB/s" for i, speed in progress.source_speeds.items()])
                print(f"\r{message}", end="", flush=True)
            elif progress.stage == "downloading":
                overall_progress = 10 + progress.progress * 80
                self_ref.update_progress(overall_progress)
                total_size_str = DownloadUtil.format_file_size(progress.total)
                downloaded_str = DownloadUtil.format_file_size(progress.downloaded)
                remaining_time_str = DownloadUtil.format_time(progress.remaining_time)
                message = f"📥 下载阶段 - 进度: {progress.progress * 100:.1f}% | " + \
                          f"大小: {downloaded_str}/{total_size_str} | " + \
                          f"速度: {progress.speed:.1f}KB/s | " + \
                          f"剩余: {remaining_time_str}"
                print(f"\r{message}", end="", flush=True)
            elif progress.stage == "completed":
                print(f"✅ 下载完成! 总大小: {progress.downloaded / 1024 / 1024:.1f}MB")

        bound_callback = partial(progress_callback, self)
        print(f"下载地址：{download_servers}")
        success, message = await DownloadUtil.multi_source_download(
            sources=download_servers,
            save_path=save_path,
            test_duration=5,
            progress_callback=bound_callback
        )
        if success:
            print(f"✅ 下载成功：{message}")
        else:
            print(f"❌ 下载失败：{message}")
        return success

    def _delete_install_path_content(self, target_path):
        # 删除现有安装目录中的特定文件
        files_to_delete = [
            f"{target_path}/_internal",  # 删除 _internal 目录及其全部内容
        ]
        import glob
        bin_files = glob.glob(os.path.join(target_path, "_indexdoc_main.bin*"))
        files_to_delete.extend(bin_files)
        bin_files = glob.glob(os.path.join(target_path, "indexdoc*"))
        files_to_delete.extend(bin_files)

        for item in files_to_delete:
            item_path = os.path.join(target_path, item)
            try:
                if os.path.exists(item_path):
                    if os.path.isdir(item_path):
                        import shutil
                        shutil.rmtree(item_path)
                        self.log(f"🗑️  已删除目录: {item}")
                    else:
                        os.remove(item_path)
                        self.log(f"🗑️  已删除文件: {os.path.basename(item)}")
            except Exception as e:
                self.log(f"❌ 删除失败 {item}: {e}")
                return False
        return True

    def check_and_close_running_programs(self, process_names):
        """
        检查指定程序是否在运行中（可多个）。
        若运行中，则提示用户是否关闭。
        :param process_names: 程序名列表（如 ['indexdoc_win.exe', '_indexdoc_main.bin']）
        :return: True 表示可以继续安装，False 表示用户取消
        """
        import os
        import signal
        import psutil
        import tkinter
        from tkinter import messagebox
        import time

        running_procs = []

        # 遍历当前进程，查找匹配的程序
        for p in psutil.process_iter(['pid', 'name']):
            try:
                if p.info['name'] and any(p.info['name'].lower() == name.lower() for name in process_names):
                    running_procs.append(p)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        if not running_procs:
            return True  # 没有运行的程序，可继续安装

        # 组合提示信息

        root = tkinter.Tk()
        root.withdraw()  # 隐藏主窗口

        msg = f"检测到IndexDoc正在运行。\n是否关闭后继续安装？"
        result = messagebox.askyesno("程序正在运行", msg)

        root.destroy()

        if result:
            # 用户选择“确定” → 关闭程序
            for p in running_procs:
                try:
                    os.kill(p.info['pid'], signal.SIGTERM)
                    self.log(f"✅ 已结束程序: {p.info['name']} (PID={p.info['pid']})")
                except Exception as e:
                    self.log(f"⚠️ 无法结束进程 {p.info['name']} (PID={p.info['pid']}): {e}", "ERROR")

            # 等待释放文件句柄
            time.sleep(1.5)
            return True
        else:
            # 用户选择“取消”
            self.log("❌ 用户取消安装（检测到程序正在运行）")
            return False

    def on_config_load_error(self, error):
        self.log(f"❌ 加载产品信息失败: {error}")
        self.log("💡 重启安装程序重试")
        messagebox.showerror("错误", f"无法加载产品信息:\n{error}")
        self.center_window()
        self.root.deiconify()

    def redirect_print_to_log(self, log_widget, app):
        # 保存原始的stdout和stderr
        original_stdout = sys.stdout
        original_stderr = sys.stderr

        class StreamToLogger:
            def __init__(self, text_widget, app, original_stream):
                self.text_space = text_widget
                self.root = app.root
                self.original_stream = original_stream
                self.app = app

            def write(self, string):
                # 写入控制台
                if self.original_stream:
                    try:
                        self.original_stream.write(string)
                    except Exception:
                        pass
                # 直接安排UI更新
                self.root.after(0, lambda: self._update_log(string))

            def flush(self):
                if self.original_stream:
                    try:
                        self.original_stream.flush()
                    except Exception:
                        pass

            def _update_log(self, message: str):
                if message == "\n":
                    return
                if message.startswith('\r'):
                    self.app.log_progress(message)
                else:
                    self.app.log(message)

        # 重定向stdout和stderr
        sys.stdout = StreamToLogger(log_widget, app, original_stdout)
        sys.stderr = StreamToLogger(log_widget, app, original_stderr)


def check_single_instance():
    """
    检查是否已有本安装程序在运行。
    若存在，则弹出提示并退出。
    """
    import psutil
    import os

    current_pid = os.getpid()
    current_name = 'indexdoc_install.exe'  # 当前程序名，如 installer.exe

    for p in psutil.process_iter(['pid', 'name']):
        try:
            if p.info['pid'] == current_pid:
                continue
            if p.info['name'] and p.info['name'].lower() == current_name:
                # 找到另一个相同的安装程序
                root = tkinter.Tk()
                root.withdraw()
                messagebox.showwarning("安装程序已在运行", "检测到 IndexDoc 安装程序已在运行，不能同时打开多个安装程序。")
                root.destroy()
                return False
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    return True


# 主函数
# ========================
def main():
    # 启动前检测是否已有运行实例
    # if not check_single_instance():
    #     return  # 检测到已有运行的安装程序，直接退出

    root = tk.Tk()
    app = ProductInstallerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
