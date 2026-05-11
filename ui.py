import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import threading
import subprocess


COLORS = {
    "bg": "#FFF8E7",
    "bg_dark": "#F5EDD8",
    "tomato": "#E74C3C",
    "tomato_dark": "#C0392B",
    "tomato_light": "#FF6B6B",
    "leaf": "#27AE60",
    "leaf_dark": "#1E8449",
    "text": "#2C3E50",
    "text_light": "#7F8C8D",
    "accent": "#F39C12",
    "white": "#FFFFFF",
    "disabled": "#BDC3C7",
    "secondary": "#95A5A6",
    "card_shadow": "#E8E0D0",
}


def create_rounded_rectangle(canvas, x1, y1, x2, y2, radius=10, **kwargs):
    """Create a rounded rectangle on canvas"""
    points = [
        x1 + radius, y1,
        x2 - radius, y1,
        x2, y1,
        x2, y1 + radius,
        x2, y2 - radius,
        x2, y2,
        x2 - radius, y2,
        x1 + radius, y2,
        x1, y2,
        x1, y2 - radius,
        x1, y1 + radius,
        x1, y1
    ]
    return canvas.create_polygon(points, smooth=True, **kwargs)


class PomodoroUI:
    def __init__(self, controller):
        self.controller = controller

        self.root = tk.Tk()
        self.root.title("番茄钟")
        self.root.geometry("400x650")
        self.root.resizable(False, False)
        self.root.configure(bg=COLORS["bg"])

        try:
            self.root.tk.call('tk', 'scaling', 1.5)
        except Exception:
            pass

        self._setup_styles()
        self._create_widgets()
        self._layout_widgets()

        self.controller.on_timer_tick = self._update_timer_display
        self.controller.on_timer_complete = self._on_timer_complete
        self.controller.on_state_change = self._update_button_state
        self.controller.on_stats_update = self._update_stats
        self.controller.on_tasks_update = self._refresh_task_list

    def _setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")

        style.configure(".", font=("Microsoft YaHei", 10))
        style.configure("Stats.TLabel",
                        font=("Microsoft YaHei", 11),
                        foreground=COLORS["text"],
                        background=COLORS["bg"])
        style.configure("Header.TLabel",
                        font=("Microsoft YaHei", 14, "bold"),
                        foreground=COLORS["tomato"],
                        background=COLORS["bg"])

        style.configure("Primary.TButton",
                        font=("Microsoft YaHei", 10, "bold"),
                        background=COLORS["tomato"],
                        foreground=COLORS["white"])
        style.map("Primary.TButton",
                  background=[("active", COLORS["tomato_dark"])])

    def _create_widgets(self):
        # Main container
        self.main_container = tk.Frame(self.root, bg=COLORS["bg"])
        self.main_container.pack(fill="both", expand=True, padx=20, pady=15)

        # Header section with animated tomato
        self.header_frame = tk.Frame(self.main_container, bg=COLORS["bg"])
        self._create_animated_tomato()
        self.header_label = tk.Label(
            self.header_frame,
            text="番茄工作法",
            font=("Microsoft YaHei", 20, "bold"),
            fg=COLORS["tomato"],
            bg=COLORS["bg"]
        )

        # Timer card with modern design
        self.timer_card = self._create_modern_card(self.main_container)
        self._build_timer_content(self.timer_card)

        # Control buttons
        self.button_frame = tk.Frame(self.main_container, bg=COLORS["bg"])
        self._create_control_buttons()

        # Tasks section
        self.task_card = self._create_modern_card(self.main_container)
        self._build_task_content(self.task_card)

        # Stats section
        self.stats_frame = tk.Frame(self.main_container, bg=COLORS["bg"])
        self._build_stats_content()

        # Settings button
        self.settings_button = tk.Button(
            self.main_container,
            text="⚙  设置",
            command=self._open_settings,
            font=("Microsoft YaHei", 9),
            bg=COLORS["bg"],
            fg=COLORS["text_light"],
            activebackground=COLORS["bg_dark"],
            relief="flat",
            cursor="hand2"
        )

        self._create_menu()

    def _create_modern_card(self, parent):
        card = tk.Frame(
            parent,
            bg=COLORS["white"],
            relief="flat",
            bd=0
        )
        # Add shadow effect using multiple frames
        shadow = tk.Frame(card, bg=COLORS["card_shadow"], bd=0)
        shadow.place(x=2, y=2, relwidth=1, relheight=1)
        inner = tk.Frame(card, bg=COLORS["white"], bd=0, padx=15, pady=12)
        inner.pack(fill="both", expand=True)
        card.inner = inner
        return card

    def _create_animated_tomato(self):
        """Create a stylish animated tomato icon"""
        canvas = tk.Canvas(
            self.header_frame,
            width=70,
            height=70,
            bg=COLORS["bg"],
            highlightthickness=0
        )

        # Tomato body - gradient effect using multiple ovals
        canvas.create_oval(12, 22, 58, 65, fill=COLORS["tomato"], outline="")
        canvas.create_oval(18, 28, 48, 56, fill=COLORS["tomato_light"], outline="")
        canvas.create_oval(25, 32, 40, 46, fill="#FFB8B8", outline="")

        # Stem
        canvas.create_line(35, 22, 35, 14, fill=COLORS["leaf"], width=3, capstyle="round")

        # Leaves - more organic shape
        canvas.create_oval(26, 6, 38, 18, fill=COLORS["leaf"], outline="")
        canvas.create_oval(36, 4, 50, 16, fill=COLORS["leaf"], outline="")
        canvas.create_oval(30, 2, 42, 14, fill="#2ECC71", outline="")

        self.tomato_canvas = canvas

    def _build_timer_content(self, card):
        inner = card.inner

        # Status with icon
        self.status_frame = tk.Frame(inner, bg=COLORS["white"])
        self.status_frame.pack(pady=(5, 0))

        self.status_indicator = tk.Canvas(self.status_frame, width=10, height=10, bg=COLORS["white"], highlightthickness=0)
        self.status_indicator.create_oval(0, 0, 10, 10, fill=COLORS["leaf"])
        self.status_indicator.pack(side="left", padx=(0, 6))

        self.status_label = tk.Label(
            self.status_frame,
            text="准备开始",
            font=("Microsoft YaHei", 13),
            fg=COLORS["text_light"],
            bg=COLORS["white"]
        )
        self.status_label.pack(side="left")

        # Large timer display
        self.timer_label = tk.Label(
            inner,
            text="25:00",
            font=("Microsoft YaHei", 64, "bold"),
            fg=COLORS["tomato"],
            bg=COLORS["white"]
        )
        self.timer_label.pack(pady=5)

        # Progress bar
        self.progress_canvas = tk.Canvas(inner, width=280, height=6, bg=COLORS["bg_dark"], highlightthickness=0)
        self.progress_canvas.pack(pady=(0, 8))
        create_rounded_rectangle(self.progress_canvas, 0, 0, 280, 6, radius=3, fill=COLORS["bg_dark"], outline="")
        self.progress_bar = create_rounded_rectangle(self.progress_canvas, 0, 0, 0, 6, radius=3, fill=COLORS["tomato"], outline="")

        # Pomodoro count
        self.count_label = tk.Label(
            inner,
            text="今日完成 0 个番茄",
            font=("Microsoft YaHei", 11),
            fg=COLORS["leaf"],
            bg=COLORS["white"]
        )
        self.count_label.pack(pady=(0, 5))

    def _create_control_buttons(self):
        # Styled button factory
        def create_button(text, cmd, bg, fg, **kwargs):
            btn = tk.Button(
                self.button_frame,
                text=text,
                command=cmd,
                font=("Microsoft YaHei", 11, "bold"),
                bg=bg,
                fg=fg,
                activebackground=self._darken_color(bg),
                activeforeground=fg,
                relief="flat",
                padx=20,
                pady=8,
                cursor="hand2",
                **kwargs
            )
            return btn

        self.start_button = create_button(
            "▶ 开始", self._on_start_clicked,
            COLORS["tomato"], COLORS["white"]
        )

        self.pause_button = create_button(
            "⏸ 暂停", self._on_pause_clicked,
            COLORS["accent"], COLORS["white"],
            state="disabled"
        )

        buttons_row = tk.Frame(self.button_frame, bg=COLORS["bg"])
        buttons_row.pack()

        self.start_button.pack(in_=buttons_row, side="left", padx=6)
        self.pause_button.pack(in_=buttons_row, side="left", padx=6)

        secondary_frame = tk.Frame(self.button_frame, bg=COLORS["bg"])
        secondary_frame.pack(pady=8)

        self.reset_button = create_button(
            "↺ 重置", self._on_reset_clicked,
            COLORS["leaf"], COLORS["white"]
        )
        self.skip_button = create_button(
            "⏭ 跳过", self._on_skip_clicked,
            COLORS["secondary"], COLORS["white"]
        )

        self.reset_button.pack(in_=secondary_frame, side="left", padx=6)
        self.skip_button.pack(in_=secondary_frame, side="left", padx=6)

    def _build_task_content(self, card):
        inner = card.inner

        # Section header
        header = tk.Frame(inner, bg=COLORS["white"])
        header.pack(fill="x", pady=(0, 8))

        tk.Label(
            header,
            text="📋 任务清单",
            font=("Microsoft YaHei", 13, "bold"),
            fg=COLORS["tomato"],
            bg=COLORS["white"]
        ).pack(side="left")

        # Task list with modern styling
        list_frame = tk.Frame(inner, bg=COLORS["white"], bd=0)
        list_frame.pack(fill="both", expand=True)

        self.task_listbox = tk.Listbox(
            list_frame,
            height=4,
            selectmode="single",
            font=("Microsoft YaHei", 10),
            bg=COLORS["bg_dark"],
            fg=COLORS["text"],
            selectbackground=COLORS["tomato"],
            selectforeground=COLORS["white"],
            relief="flat",
            bd=0,
            highlightthickness=0,
            activestyle="none"
        )
        self.task_listbox.pack(side="left", fill="both", expand=True)

        self.task_scrollbar = ttk.Scrollbar(
            list_frame,
            orient="vertical",
            command=self.task_listbox.yview
        )
        self.task_listbox.configure(yscrollcommand=self.task_scrollbar.set)
        self.task_scrollbar.pack(side="right", fill="y", padx=(5, 0))

        # Task buttons
        btn_frame = tk.Frame(inner, bg=COLORS["white"])
        btn_frame.pack(fill="x", pady=(8, 0))

        for text, cmd, bg in [
            ("+ 添加", self._on_add_task, COLORS["leaf"]),
            ("✓ 完成", self._on_complete_task, COLORS["tomato"]),
            ("🗑 删除", self._on_delete_task, COLORS["secondary"])
        ]:
            tk.Button(
                btn_frame,
                text=text,
                command=cmd,
                font=("Microsoft YaHei", 9),
                bg=bg,
                fg=COLORS["white"],
                activebackground=self._darken_color(bg),
                relief="flat",
                padx=12,
                pady=4,
                cursor="hand2"
            ).pack(side="left", padx=4)

    def _build_stats_content(self):
        # Stats in a single row with icons
        for text, key in [("今日", "today"), ("本周", "week")]:
            frame = tk.Frame(self.stats_frame, bg=COLORS["white"], padx=15, pady=8)
            frame.pack(side="left", padx=8)

            icon_map = {"today": "📅", "week": "📆"}
            label = tk.Label(
                frame,
                text=f"{icon_map[key]} {text}: 0",
                font=("Microsoft YaHei", 11),
                fg=COLORS["text"],
                bg=COLORS["white"]
            )
            label.pack()
            setattr(self, f"{key}_label", label)

    def _darken_color(self, color):
        """Darken a hex color slightly"""
        if color.startswith("#") and len(color) == 7:
            r = int(color[1:3], 16)
            g = int(color[3:5], 16)
            b = int(color[5:7], 16)
            factor = 0.85
            return f"#{int(r*factor):02x}{int(g*factor):02x}{int(b*factor):02x}"
        return color

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
        # Header
        self.header_frame.pack(pady=(0, 10))
        self.tomato_canvas.pack(in_=self.header_frame)
        self.header_label.pack(in_=self.header_frame)

        # Timer card
        self.timer_card.pack(fill="x", pady=(0, 12))

        # Buttons
        self.button_frame.pack(pady=(0, 12))

        # Tasks card
        self.task_card.pack(fill="both", expand=True, pady=(0, 12))

        # Stats
        self.stats_frame.pack(fill="x", pady=(0, 10))

        # Settings
        self.settings_button.pack()

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

        # Update progress bar
        total = self.controller.timer.get_total_seconds()
        if total > 0:
            ratio = 1 - (seconds / total)
            # Temporarily delete and recreate the progress bar for polygon update
            self.progress_canvas.delete(self.progress_bar)
            if ratio > 0:
                width = int(280 * ratio)
                self.progress_bar = create_rounded_rectangle(
                    self.progress_canvas, 0, 0, width, 6, radius=3,
                    fill=COLORS["tomato"], outline=""
                )

    def _update_button_state(self, state, timer_type):
        status_map = {
            "pomodoro": "🍅 专注时间",
            "short_break": "☕ 短休息",
            "long_break": "🌴 长休息"
        }

        # Update status indicator color
        if state.value == "running":
            color = COLORS["tomato"]
        elif state.value == "paused":
            color = COLORS["accent"]
        else:
            color = COLORS["leaf"]
        self.status_indicator.delete("all")
        self.status_indicator.create_oval(0, 0, 10, 10, fill=color)

        if state.value == "running":
            self.status_label.config(text=status_map.get(timer_type.value, "运行中"))
            self.start_button.config(state="disabled", bg=COLORS["disabled"])
            self.pause_button.config(state="normal", bg=COLORS["accent"])
        elif state.value == "paused":
            self.status_label.config(text="⏸ 已暂停")
            self.start_button.config(state="normal", text="▶ 继续", bg=COLORS["tomato"])
            self.pause_button.config(state="disabled", bg=COLORS["disabled"])
        else:
            self.status_label.config(text="✓ 准备开始")
            self.start_button.config(state="normal", text="▶ 开始", bg=COLORS["tomato"])
            self.pause_button.config(state="disabled", bg=COLORS["disabled"])

    def _update_stats(self, today_count, week_count):
        self.today_label.config(text=f"📅 今日: {today_count}")
        self.week_label.config(text=f"📆 本周: {week_count}")
        self.count_label.config(text=f"今日完成 {self.controller.timer.pomodoro_count} 个番茄")

    def _refresh_task_list(self, tasks):
        self.task_listbox.delete(0, "end")
        for task in tasks:
            task_id, name, estimate, completed, _, _, _ = task
            prefix = "✓" if completed >= estimate else "○"
            display_text = f"{prefix} {name} ({completed}/{estimate})"
            self.task_listbox.insert("end", display_text)
            if completed >= estimate:
                self.task_listbox.itemconfigure("end", fg=COLORS["secondary"])

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

        tk.Label(mainframe, text="计时设置", font=("Microsoft YaHei", 14, "bold"),
                 bg=COLORS["bg"], fg=COLORS["tomato"]).grid(
            row=0, column=0, columnspan=2, pady=(0, 15), sticky="w"
        )

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

        tk.Label(mainframe, text="通知设置", font=("Microsoft YaHei", 14, "bold"),
                 bg=COLORS["bg"], fg=COLORS["tomato"]).grid(
            row=5, column=0, columnspan=2, pady=(15, 15), sticky="w"
        )

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