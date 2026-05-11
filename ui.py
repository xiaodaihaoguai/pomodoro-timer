import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import threading
import subprocess


COLORS = {
    "bg": "#FFF8E7",
    "tomato": "#FF6B6B",
    "tomato_dark": "#EE5A5A",
    "tomato_light": "#FF8A8A",
    "leaf": "#4CAF50",
    "leaf_dark": "#45A049",
    "text": "#333333",
    "text_light": "#666666",
    "accent": "#FFE66D",
    "white": "#FFFFFF",
    "disabled": "#CCCCCC",
    "secondary": "#9E9E9E",
    "secondary_dark": "#757575",
}


class PomodoroUI:
    def __init__(self, controller):
        self.controller = controller

        self.root = tk.Tk()
        self.root.title("番茄钟")
        self.root.geometry("480x720")
        self.root.resizable(False, False)
        self.root.configure(bg=COLORS["bg"])

        # Enable HiDPI scaling for better display quality
        try:
            self.root.tk.call('tk', 'scaling', 1.5)
        except Exception:
            pass

        self._setup_styles()
        self._create_widgets()
        self._layout_widgets()

        # Bind controller callbacks
        self.controller.on_timer_tick = self._update_timer_display
        self.controller.on_timer_complete = self._on_timer_complete
        self.controller.on_state_change = self._update_button_state
        self.controller.on_stats_update = self._update_stats
        self.controller.on_tasks_update = self._refresh_task_list

    def _setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")

        # Configure ttk styles
        style.configure(".", font=("Microsoft YaHei", 10))
        style.configure("Timer.TLabel",
                        font=("Microsoft YaHei", 56, "bold"),
                        foreground=COLORS["tomato"],
                        background=COLORS["bg"])
        style.configure("Status.TLabel",
                        font=("Microsoft YaHei", 16),
                        foreground=COLORS["text_light"],
                        background=COLORS["bg"])
        style.configure("Title.TLabel",
                        font=("Microsoft YaHei", 12, "bold"),
                        background=COLORS["bg"])
        style.configure("Stats.TLabel",
                        font=("Microsoft YaHei", 12),
                        foreground=COLORS["text"],
                        background=COLORS["bg"])
        style.configure("Header.TLabel",
                        font=("Microsoft YaHei", 18, "bold"),
                        foreground=COLORS["tomato"],
                        background=COLORS["bg"])

        # Button styles
        style.configure("Primary.TButton",
                        font=("Microsoft YaHei", 11, "bold"),
                        background=COLORS["tomato"],
                        foreground=COLORS["white"])
        style.configure("Secondary.TButton",
                        font=("Microsoft YaHei", 10),
                        background=COLORS["leaf"],
                        foreground=COLORS["white"])
        style.configure("Outline.TButton",
                        font=("Microsoft YaHei", 10),
                        background=COLORS["bg"],
                        foreground=COLORS["tomato"],
                        bordercolor=COLORS["tomato"])
        style.map("Primary.TButton",
                  background=[("active", COLORS["tomato_dark"])],
                  relief=[("pressed", "sunken")])
        style.map("Secondary.TButton",
                  background=[("active", COLORS["leaf_dark"])],
                  relief=[("pressed", "sunken")])

    def _create_widgets(self):
        # Header with tomato decoration
        self.header_frame = tk.Frame(self.root, bg=COLORS["bg"], height=80)
        self.header_frame.pack(fill="x", pady=(15, 5))

        # Tomato icon (using canvas)
        self._create_tomato_icon()

        # Header title
        self.header_label = tk.Label(
            self.header_frame,
            text="番茄工作法",
            font=("Microsoft YaHei", 22, "bold"),
            fg=COLORS["tomato"],
            bg=COLORS["bg"]
        )
        self.header_label.pack(pady=(5, 0))

        # Timer display card
        self.timer_card = tk.Frame(
            self.root,
            bg=COLORS["white"],
            highlightthickness=0,
            relief="flat",
            bd=0
        )
        self.timer_card.pack(pady=10)
        self.timer_card.configure(highlightbackground=COLORS["tomato"],
                                   highlightthickness=3)

        # Inner timer frame
        self.timer_inner = tk.Frame(self.timer_card, bg=COLORS["white"], padx=30, pady=20)

        # Status label
        self.status_label = tk.Label(
            self.timer_inner,
            text="准备开始",
            font=("Microsoft YaHei", 16),
            fg=COLORS["text_light"],
            bg=COLORS["white"]
        )

        # Timer display
        self.timer_label = tk.Label(
            self.timer_inner,
            text="25:00",
            font=("Microsoft YaHei", 56, "bold"),
            fg=COLORS["tomato"],
            bg=COLORS["white"]
        )

        # Pomodoro count with leaf
        self.count_label = tk.Label(
            self.timer_inner,
            text="今日番茄: 0",
            font=("Microsoft YaHei", 16),
            fg=COLORS["leaf"],
            bg=COLORS["white"]
        )

        # Buttons frame
        self.button_frame = tk.Frame(self.root, bg=COLORS["bg"], pady=15)

        # Custom styled buttons using tk.Frame
        self.start_button = tk.Button(
            self.button_frame,
            text="开始",
            command=self._on_start_clicked,
            font=("Microsoft YaHei", 12, "bold"),
            bg=COLORS["tomato"],
            fg=COLORS["white"],
            activebackground=COLORS["tomato_dark"],
            activeforeground=COLORS["white"],
            relief="flat",
            padx=25,
            pady=8,
            cursor="hand2"
        )

        self.pause_button = tk.Button(
            self.button_frame,
            text="暂停",
            command=self._on_pause_clicked,
            font=("Microsoft YaHei", 12, "bold"),
            bg=COLORS["accent"],
            fg=COLORS["text"],
            activebackground=COLORS["accent"],
            activeforeground=COLORS["text"],
            relief="flat",
            padx=25,
            pady=8,
            cursor="hand2",
            state="disabled"
        )

        self.reset_button = tk.Button(
            self.button_frame,
            text="重置",
            command=self._on_reset_clicked,
            font=("Microsoft YaHei", 11),
            bg=COLORS["leaf"],
            fg=COLORS["white"],
            activebackground=COLORS["leaf_dark"],
            activeforeground=COLORS["white"],
            relief="flat",
            padx=20,
            pady=8,
            cursor="hand2"
        )

        self.skip_button = tk.Button(
            self.button_frame,
            text="跳过",
            command=self._on_skip_clicked,
            font=("Microsoft YaHei", 11),
            bg=COLORS["text_light"],
            fg=COLORS["white"],
            activebackground=COLORS["text"],
            activeforeground=COLORS["white"],
            relief="flat",
            padx=20,
            pady=8,
            cursor="hand2"
        )

        # Tasks section
        self.tasks_frame = tk.LabelFrame(
            self.root,
            text="  任务清单  ",
            font=("Microsoft YaHei", 12, "bold"),
            bg=COLORS["bg"],
            fg=COLORS["tomato"],
            padx=10,
            pady=5,
            relief="flat",
            bd=2,
            highlightthickness=0
        )

        self.task_listbox = tk.Listbox(
            self.tasks_frame,
            height=5,
            selectmode="single",
            font=("Microsoft YaHei", 10),
            bg=COLORS["white"],
            fg=COLORS["text"],
            selectbackground=COLORS["tomato"],
            selectforeground=COLORS["white"],
            relief="flat",
            bd=0,
            highlightthickness=1,
            highlightbackground=COLORS["tomato"],
            highlightcolor=COLORS["tomato"],
            activestyle="none"
        )
        self.task_scrollbar = ttk.Scrollbar(
            self.tasks_frame,
            orient="vertical",
            command=self.task_listbox.yview
        )
        self.task_listbox.configure(yscrollcommand=self.task_scrollbar.set)

        self.task_button_frame = tk.Frame(self.tasks_frame, bg=COLORS["bg"])

        self.add_task_button = tk.Button(
            self.task_button_frame,
            text="+ 添加",
            command=self._on_add_task,
            font=("Microsoft YaHei", 10),
            bg=COLORS["leaf"],
            fg=COLORS["white"],
            activebackground=COLORS["leaf_dark"],
            relief="flat",
            padx=15,
            pady=5,
            cursor="hand2"
        )
        self.complete_task_button = tk.Button(
            self.task_button_frame,
            text="完成",
            command=self._on_complete_task,
            font=("Microsoft YaHei", 10),
            bg=COLORS["tomato"],
            fg=COLORS["white"],
            activebackground=COLORS["tomato_dark"],
            relief="flat",
            padx=15,
            pady=5,
            cursor="hand2"
        )
        self.delete_task_button = tk.Button(
            self.task_button_frame,
            text="删除",
            command=self._on_delete_task,
            font=("Microsoft YaHei", 10),
            bg=COLORS["secondary"],
            fg=COLORS["white"],
            activebackground=COLORS["secondary_dark"],
            relief="flat",
            padx=15,
            pady=5,
            cursor="hand2"
        )

        # Stats section
        self.stats_frame = tk.LabelFrame(
            self.root,
            text="  统计数据  ",
            font=("Microsoft YaHei", 12, "bold"),
            bg=COLORS["bg"],
            fg=COLORS["leaf"],
            padx=15,
            pady=10,
            relief="flat",
            bd=2,
            highlightthickness=0
        )

        # Stats card style
        self.today_label = tk.Label(
            self.stats_frame,
            text="今日: 0",
            font=("Microsoft YaHei", 12),
            fg=COLORS["text"],
            bg=COLORS["bg"]
        )
        self.week_label = tk.Label(
            self.stats_frame,
            text="本周: 0",
            font=("Microsoft YaHei", 12),
            fg=COLORS["text"],
            bg=COLORS["bg"]
        )

        # Settings button
        self.settings_button = tk.Button(
            self.root,
            text="设置",
            command=self._open_settings,
            font=("Microsoft YaHei", 10),
            bg=COLORS["bg"],
            fg=COLORS["text_light"],
            activebackground=COLORS["bg"],
            relief="flat",
            padx=20,
            pady=5,
            cursor="hand2"
        )

        # Menu
        self._create_menu()

    def _create_tomato_icon(self):
        """Create a cute tomato icon using canvas"""
        canvas = tk.Canvas(
            self.header_frame,
            width=60,
            height=60,
            bg=COLORS["bg"],
            highlightthickness=0
        )
        canvas.pack()

        # Tomato body (ellipse)
        canvas.create_oval(10, 20, 50, 58, fill=COLORS["tomato"], outline=COLORS["tomato_dark"], width=2)

        # Tomato highlight
        canvas.create_oval(18, 28, 32, 40, fill=COLORS["tomato_light"], outline="")

        # Leaf stem
        canvas.create_line(30, 20, 30, 12, fill=COLORS["leaf"], width=3)

        # Leaves
        canvas.create_oval(22, 8, 30, 16, fill=COLORS["leaf"], outline="")
        canvas.create_oval(30, 8, 38, 16, fill=COLORS["leaf"], outline="")
        canvas.create_oval(26, 4, 34, 14, fill=COLORS["leaf"], outline="")

    def _create_menu(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        file_menu = tk.Menu(menubar, tearoff=0, font=("Microsoft YaHei", 10))
        menubar.add_cascade(label="菜单", menu=file_menu, font=("Microsoft YaHei", 10))
        file_menu.add_command(label="退出", command=self.root.quit)

        help_menu = tk.Menu(menubar, tearoff=0, font=("Microsoft YaHei", 10))
        menubar.add_cascade(label="帮助", menu=help_menu)
        help_menu.add_command(label="关于", command=self._show_about)

    def _layout_widgets(self):
        self.header_frame.pack(fill="x")

        # Timer card
        self.timer_card.pack(pady=10, padx=20, fill="x")
        self.timer_inner.pack()

        self.status_label.pack(pady=(5, 0))
        self.timer_label.pack(pady=5)
        self.count_label.pack(pady=(0, 5))

        # Buttons
        self.button_frame.pack(pady=10)
        self.start_button.grid(row=0, column=0, padx=8, pady=5)
        self.pause_button.grid(row=0, column=1, padx=8, pady=5)
        self.reset_button.grid(row=0, column=2, padx=8, pady=5)
        self.skip_button.grid(row=0, column=3, padx=8, pady=5)

        # Tasks
        self.tasks_frame.pack(fill="both", expand=True, padx=20, pady=5)
        self.task_listbox.pack(side="left", fill="both", expand=True, padx=(5, 0), pady=5)
        self.task_scrollbar.pack(side="right", fill="y", pady=5, padx=(0, 5))

        self.task_button_frame.pack(fill="x", pady=5)
        self.add_task_button.pack(side="left", padx=5)
        self.complete_task_button.pack(side="left", padx=5)
        self.delete_task_button.pack(side="left", padx=5)

        # Stats
        self.stats_frame.pack(fill="x", padx=20, pady=5)
        self.today_label.pack(side="left", padx=30)
        self.week_label.pack(side="left", padx=30)

        # Settings
        self.settings_button.pack(pady=10)

    # Button handlers
    def _on_start_clicked(self):
        self.controller.start()

    def _on_pause_clicked(self):
        self.controller.pause()

    def _on_reset_clicked(self):
        self.controller.reset()

    def _on_skip_clicked(self):
        self.controller.skip()

    def _on_add_task(self):
        dialog = AddTaskDialog(self.root)
        if dialog.result:
            name, estimate = dialog.result
            self.controller.add_task(name, estimate)

    def _on_complete_task(self):
        selection = self.task_listbox.curselection()
        if selection:
            task_id = self.controller.get_task_id_at_index(selection[0])
            self.controller.complete_task(task_id)

    def _on_delete_task(self):
        selection = self.task_listbox.curselection()
        if selection:
            task_id = self.controller.get_task_id_at_index(selection[0])
            self.controller.delete_task(task_id)

    def _open_settings(self):
        SettingsDialog(self.root, self.controller.settings)

    def _show_about(self):
        messagebox.showinfo(
            "关于",
            "番茄钟 v1.0\n\n基于番茄工作法的桌面计时器\n\n帮助您专注于工作，提高效率！"
        )

    # Update methods
    def _update_timer_display(self, seconds):
        minutes = seconds // 60
        secs = seconds % 60
        self.timer_label.config(text=f"{minutes:02d}:{secs:02d}")

    def _update_button_state(self, state, timer_type):
        status_map = {
            "pomodoro": "专注时间",
            "short_break": "短休息",
            "long_break": "长休息"
        }

        if state.value == "running":
            self.status_label.config(text=status_map.get(timer_type.value, "运行中"))
            self.start_button.config(state="disabled", bg=COLORS["disabled"], relief="flat")
            self.pause_button.config(state="normal", bg=COLORS["accent"], relief="flat")
        elif state.value == "paused":
            self.status_label.config(text="已暂停")
            self.start_button.config(state="normal", text="继续", bg=COLORS["tomato"], relief="flat")
            self.pause_button.config(state="disabled", bg=COLORS["disabled"], relief="flat")
        else:
            self.status_label.config(text="准备开始")
            self.start_button.config(state="normal", text="开始", bg=COLORS["tomato"], relief="flat")
            self.pause_button.config(state="disabled", bg=COLORS["disabled"], relief="flat")

    def _update_stats(self, today_count, week_count):
        self.today_label.config(text=f"今日: {today_count}")
        self.week_label.config(text=f"本周: {week_count}")
        self.count_label.config(text=f"今日番茄: {self.controller.timer.pomodoro_count}")

    def _refresh_task_list(self, tasks):
        self.task_listbox.delete(0, "end")
        for task in tasks:
            task_id, name, estimate, completed, _, _, _ = task
            display_text = f"{name} ({completed}/{estimate})"
            self.task_listbox.insert("end", display_text)

    def _on_timer_complete(self, timer_type):
        if self.controller.settings.notification_enabled:
            self._show_notification(timer_type)

        if self.controller.settings.sound_enabled:
            self._play_sound()

    def _show_notification(self, timer_type):
        if timer_type.value == "pomodoro":
            title = "番茄钟完成！"
            message = "是时候休息一下了"
        else:
            title = "休息结束"
            message = "准备好继续工作了吗？"

        try:
            subprocess.Popen([
                "notify-send",
                title,
                message,
                "-i", "dialog-information"
            ])
        except Exception:
            pass

    def _play_sound(self):
        try:
            import winsound
            winsound.MessageBeep()
        except ImportError:
            try:
                import subprocess
                subprocess.Popen(["paplay", "/usr/share/sounds/gnome/default/alerts/glass.ogg"])
            except Exception:
                pass

    def run(self):
        self.controller.load_data()
        self.root.mainloop()


class AddTaskDialog(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.result = None

        self.title("添加任务")
        self.geometry("320x180")
        self.resizable(False, False)
        self.configure(bg=COLORS["bg"])

        mainframe = tk.Frame(self, bg=COLORS["bg"], padx=20, pady=15)
        mainframe.pack(fill="both", expand=True)

        tk.Label(mainframe, text="任务名称:", font=("Microsoft YaHei", 11),
                 bg=COLORS["bg"], fg=COLORS["text"]).pack(anchor="w")

        self.name_entry = tk.Entry(mainframe, font=("Microsoft YaHei", 11),
                                    bg=COLORS["white"], relief="flat",
                                    highlightthickness=1,
                                    highlightbackground=COLORS["tomato"])
        self.name_entry.pack(fill="x", pady=(5, 15))

        tk.Label(mainframe, text="预计番茄数:", font=("Microsoft YaHei", 11),
                 bg=COLORS["bg"], fg=COLORS["text"]).pack(anchor="w")

        self.spinbox = ttk.Spinbox(mainframe, from_=1, to=20, width=10, font=("Microsoft YaHei", 11))
        self.spinbox.set(1)
        self.spinbox.pack(anchor="w", pady=(5, 15))

        button_frame = tk.Frame(mainframe, bg=COLORS["bg"])
        button_frame.pack(fill="x")

        tk.Button(button_frame, text="添加", command=self._on_ok,
                  font=("Microsoft YaHei", 11, "bold"),
                  bg=COLORS["tomato"], fg=COLORS["white"],
                  activebackground=COLORS["tomato_dark"],
                  relief="flat", padx=20, pady=5).pack(side="left", padx=5)

        tk.Button(button_frame, text="取消", command=self.destroy,
                  font=("Microsoft YaHei", 11),
                  bg=COLORS["secondary"], fg=COLORS["white"],
                  activebackground=COLORS["secondary_dark"],
                  relief="flat", padx=20, pady=5).pack(side="left", padx=5)

        self.name_entry.focus()
        self.bind("<Return>", lambda e: self._on_ok())

    def _on_ok(self):
        name = self.name_entry.get().strip()
        if not name:
            messagebox.showwarning("警告", "请输入任务名称")
            return

        estimate = int(self.spinbox.get())
        self.result = (name, estimate)
        self.destroy()


class SettingsDialog(tk.Toplevel):
    def __init__(self, parent, settings):
        super().__init__(parent)
        self.settings = settings

        self.title("设置")
        self.geometry("380x420")
        self.resizable(False, False)
        self.configure(bg=COLORS["bg"])

        self._create_widgets()
        self._load_settings()

    def _create_widgets(self):
        mainframe = tk.Frame(self, padding=20, bg=COLORS["bg"])
        mainframe.pack(fill="both", expand=True)

        # Timer settings header
        tk.Label(mainframe, text="计时设置", font=("Microsoft YaHei", 14, "bold"),
                 bg=COLORS["bg"], fg=COLORS["tomato"]).grid(
            row=0, column=0, columnspan=2, pady=(0, 15), sticky="w"
        )

        # Timer settings
        entries = [
            ("番茄时长 (分钟):", "pomodoro_spin", 1, 60),
            ("短休息 (分钟):", "short_break_spin", 1, 30),
            ("长休息 (分钟):", "long_break_spin", 1, 60),
            ("长休息间隔:", "interval_spin", 2, 10),
        ]

        for i, (label, attr, min_val, max_val) in enumerate(entries, 1):
            tk.Label(mainframe, text=label, font=("Microsoft YaHei", 10),
                     bg=COLORS["bg"], fg=COLORS["text"]).grid(
                row=i, column=0, sticky="w", pady=8
            )
            spin = ttk.Spinbox(mainframe, from_=min_val, to=max_val, width=12,
                               font=("Microsoft YaHei", 10))
            spin.grid(row=i, column=1, sticky="w", pady=8, padx=10)
            setattr(self, attr, spin)

        # Notification settings header
        tk.Label(mainframe, text="通知设置", font=("Microsoft YaHei", 14, "bold"),
                 bg=COLORS["bg"], fg=COLORS["tomato"]).grid(
            row=5, column=0, columnspan=2, pady=(15, 15), sticky="w"
        )

        # Checkboxes
        self.sound_var = tk.BooleanVar()
        tk.Checkbutton(mainframe, text="启用声音提示", variable=self.sound_var,
                       font=("Microsoft YaHei", 10), bg=COLORS["bg"],
                       activebackground=COLORS["bg"]).grid(
            row=6, column=0, columnspan=2, sticky="w", pady=5
        )

        self.notification_var = tk.BooleanVar()
        tk.Checkbutton(mainframe, text="启用系统通知", variable=self.notification_var,
                       font=("Microsoft YaHei", 10), bg=COLORS["bg"],
                       activebackground=COLORS["bg"]).grid(
            row=7, column=0, columnspan=2, sticky="w", pady=5
        )

        # Buttons
        button_frame = tk.Frame(mainframe, bg=COLORS["bg"])
        button_frame.grid(row=8, column=0, columnspan=2, pady=20)

        tk.Button(button_frame, text="保存", command=self._save,
                  font=("Microsoft YaHei", 11, "bold"),
                  bg=COLORS["tomato"], fg=COLORS["white"],
                  activebackground=COLORS["tomato_dark"],
                  relief="flat", padx=20, pady=5).pack(side="left", padx=8)

        tk.Button(button_frame, text="重置默认", command=self._reset,
                  font=("Microsoft YaHei", 11),
                  bg=COLORS["leaf"], fg=COLORS["white"],
                  activebackground=COLORS["leaf_dark"],
                  relief="flat", padx=20, pady=5).pack(side="left", padx=8)

        tk.Button(button_frame, text="关闭", command=self.destroy,
                  font=("Microsoft YaHei", 11),
                  bg=COLORS["secondary"], fg=COLORS["white"],
                  activebackground=COLORS["secondary_dark"],
                  relief="flat", padx=20, pady=5).pack(side="left", padx=8)

    def _load_settings(self):
        self.pomodoro_spin.set(self.settings.pomodoro_duration)
        self.short_break_spin.set(self.settings.short_break_duration)
        self.long_break_spin.set(self.settings.long_break_duration)
        self.interval_spin.set(self.settings.long_break_interval)
        self.sound_var.set(self.settings.sound_enabled)
        self.notification_var.set(self.settings.notification_enabled)

    def _save(self):
        self.settings.set("pomodoro_duration", int(self.pomodoro_spin.get()))
        self.settings.set("short_break_duration", int(self.short_break_spin.get()))
        self.settings.set("long_break_duration", int(self.long_break_spin.get()))
        self.settings.set("long_break_interval", int(self.interval_spin.get()))
        self.settings.set("sound_enabled", self.sound_var.get())
        self.settings.set("notification_enabled", self.notification_var.get())

        messagebox.showinfo("成功", "设置已保存")
        self.destroy()

    def _reset(self):
        self.settings.reset()
        self._load_settings()
        messagebox.showinfo("成功", "已恢复到默认设置")