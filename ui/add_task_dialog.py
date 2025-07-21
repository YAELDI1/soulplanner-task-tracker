import tkinter as tk
from tkinter import ttk
import ttkbootstrap as tb
from ttkbootstrap.constants import *
import time
import calendar
from datetime import datetime

# Standard font stack: Segoe UI, Arial, sans-serif
MODERN_FONT = ("Segoe UI", 11)
MODERN_FONT_BOLD = ("Segoe UI", 11, "bold")
LABEL_FONT = ("Segoe UI", 11, "bold")
LABEL_COLOR = "#222"
ENTRY_BG = "#fff"
ENTRY_BORDER = "#e0e0e0"
PLACEHOLDER_COLOR = "#b0b8c9"

BG_GRADIENT = "#f7fafd"
CARD_BG = "#ffffff"
SHADOW = "#e0e4ea"
VIBRANT_BLUE = "#2563eb"

class ModernEntry(tb.Entry):
    def __init__(self, parent, textvariable=None, placeholder="", **kwargs):
        entry_kwargs = kwargs.copy()
        if textvariable is not None:
            entry_kwargs['textvariable'] = textvariable
        super().__init__(parent, style="Modern.TEntry", **entry_kwargs)
        self.placeholder = placeholder
        self.textvariable = textvariable
        self.configure(font=MODERN_FONT, background=ENTRY_BG)
        if placeholder and (not textvariable or not textvariable.get()):
            self.insert(0, placeholder)
            self['foreground'] = PLACEHOLDER_COLOR
        self.bind('<FocusIn>', self._clear_placeholder)
        self.bind('<FocusOut>', self._add_placeholder)
    def _clear_placeholder(self, event):
        if self.get() == self.placeholder:
            self.delete(0, tk.END)
            self['foreground'] = LABEL_COLOR
    def _add_placeholder(self, event):
        if not self.get():
            self.insert(0, self.placeholder)
            self['foreground'] = PLACEHOLDER_COLOR

class ModernButton(tb.Button):
    def __init__(self, parent, text, primary=False, command=None, **kwargs):
        style = "Modern.Primary.TButton" if primary else "Modern.Outline.TButton"
        button_kwargs = kwargs.copy()
        if command is not None:
            button_kwargs['command'] = command
        super().__init__(parent, text=text, style=style, **button_kwargs)
        self.primary = primary

class GlassModal(tb.Toplevel):
    def __init__(self, parent, task_data=None):
        super().__init__(parent)
        self.title("")
        self.geometry("600x520")
        self.minsize(480, 480)
        self.resizable(True, True)
        self.configure(bg=BG_GRADIENT)
        self.result = None
        if task_data is None:
            task_data = {}
        # Set today's date as default if not provided
        if not task_data.get('due'):
            task_data['due'] = datetime.now().strftime("%Y-%m-%d")
        self.task_data = task_data or {
            'task': '',
            'owner': '',
            'status': 'Working on it',
            'due': '',
            'notes': '',
        }
        self.attributes("-alpha", 0.0)
        self.create_styles()
        self.create_widgets()
        self.center_modal()
        self.after(0, self.fade_in)
        self.grab_set()
        self.wait_window(self)

    def create_styles(self):
        style = ttk.Style()
        style.theme_use("flatly")
        style.configure(
            "Modern.TEntry",
            font=MODERN_FONT,
            padding=2,
            borderwidth=1,
            relief="flat",
            foreground=LABEL_COLOR,
            fieldbackground=ENTRY_BG,
            background=ENTRY_BG,
            bordercolor=ENTRY_BORDER,
            border_radius=5,
            insertcolor=LABEL_COLOR,
            insertwidth=2,
            lightcolor=ENTRY_BG,
            darkcolor=ENTRY_BG,
            highlightthickness=0,
            focuscolor=VIBRANT_BLUE,
            rowheight=36,
        )
        style.configure(
            "Modern.TCombobox",
            font=MODERN_FONT,
            padding=2,
            borderwidth=1,
            relief="flat",
            foreground=LABEL_COLOR,
            fieldbackground=ENTRY_BG,
            background=ENTRY_BG,
            bordercolor=ENTRY_BORDER,
            border_radius=5,
            arrowcolor="#888",
            lightcolor=ENTRY_BG,
            darkcolor=ENTRY_BG,
            highlightthickness=0,
            focuscolor=VIBRANT_BLUE,
        )
        style.map(
            "Modern.TCombobox",
            bordercolor=[('focus', VIBRANT_BLUE)],
            foreground=[('readonly', LABEL_COLOR)],
            fieldbackground=[('readonly', ENTRY_BG)],
        )
        style.configure(
            "Modern.TEntry.Focus",
            font=MODERN_FONT,
            padding=2,
            borderwidth=2,
            relief="flat",
            foreground=LABEL_COLOR,
            fieldbackground=ENTRY_BG,
            background=ENTRY_BG,
            bordercolor=VIBRANT_BLUE,
            border_radius=5,
            insertcolor=LABEL_COLOR,
            insertwidth=2,
            lightcolor=ENTRY_BG,
            darkcolor=ENTRY_BG,
            highlightthickness=0,
            focuscolor=VIBRANT_BLUE,
            rowheight=36,
        )
        # Primary Button
        style.configure(
            "Modern.Primary.TButton",
            font=MODERN_FONT_BOLD,
            foreground="#fff",
            background=VIBRANT_BLUE,
            borderwidth=0,
            padding=(0, 10),
            border_radius=8,
            relief="flat",
        )
        style.map(
            "Modern.Primary.TButton",
            background=[('active', '#1749b1'), ('pressed', '#1749b1')],
            relief=[('pressed', 'sunken'), ('!pressed', 'flat')],
        )
        # Outline Button
        style.configure(
            "Modern.Outline.TButton",
            font=MODERN_FONT_BOLD,
            foreground="#2563eb",
            background="#fff",
            borderwidth=1,
            bordercolor="#2563eb",
            padding=(0, 10),
            border_radius=8,
            relief="flat",
        )
        style.map(
            "Modern.Outline.TButton",
            background=[('active', '#f7fafd'), ('pressed', '#f7fafd')],
            relief=[('pressed', 'sunken'), ('!pressed', 'flat')],
        )

    def fade_in(self):
        for i in range(0, 21):
            self.attributes("-alpha", i / 20)
            self.update()
            time.sleep(0.01)

    def center_modal(self):
        self.update_idletasks()
        w = self.winfo_width()
        h = self.winfo_height()
        ws = self.winfo_screenwidth()
        hs = self.winfo_screenheight()
        x = (ws // 2) - (w // 2)
        y = (hs // 2) - (h // 2)
        self.geometry(f"{w}x{h}+{x}+{y}")

    def _show_date_picker(self, entry):
        # Only open if not already open
        if hasattr(self, '_date_picker') and self._date_picker and self._date_picker.winfo_exists():
            return
        self._date_picker = DatePicker(self, entry, font=MODERN_FONT)

    def create_widgets(self):
        card = tk.Frame(self, bg=CARD_BG, bd=0, highlightthickness=0)
        card.pack(fill="both", expand=True, padx=16, pady=16)
        card.grid_propagate(True)
        card.pack_propagate(True)
        card.update_idletasks()
        shadow = tk.Frame(self, bg=SHADOW, bd=0, highlightthickness=0)
        shadow.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.94, relheight=0.94)
        shadow.lower(card)
        for i in range(1):
            card.columnconfigure(i, weight=1)
        row = 0
        # Task
        ttk.Label(card, text="Task", font=LABEL_FONT, foreground=LABEL_COLOR, background=CARD_BG).grid(row=row, column=0, sticky="w", padx=(24, 8), pady=(18, 0))
        row += 1
        self.task_var = tk.StringVar(value=self.task_data['task'])
        task_entry = ModernEntry(card, textvariable=self.task_var, placeholder="Task name", width=15)
        task_entry.grid(row=row, column=0, sticky="ew", padx=(20, 20), pady=(8, 10))
        card.grid_columnconfigure(0, weight=1)
        row += 1
        # Owner
        ttk.Label(card, text="Owner", font=LABEL_FONT, foreground=LABEL_COLOR, background=CARD_BG).grid(row=row, column=0, sticky="w", padx=(24, 8), pady=(0, 0))
        row += 1
        self.owner_var = tk.StringVar(value=self.task_data['owner'])
        owner_entry = ModernEntry(card, textvariable=self.owner_var, placeholder="Owner", width=15)
        owner_entry.grid(row=row, column=0, sticky="ew", padx=(24, 24), pady=(2, 10))
        card.grid_columnconfigure(0, weight=1)
        row += 1
        # Status
        ttk.Label(card, text="Status", font=LABEL_FONT, foreground=LABEL_COLOR, background=CARD_BG).grid(row=row, column=0, sticky="w", padx=(24, 8), pady=(0, 0))
        row += 1
        self.status_var = tk.StringVar(value=self.task_data['status'])
        status_combo = tb.Combobox(
            card,
            textvariable=self.status_var,
            values=["Working on it", "Done", "Stuck", "Not Started"],
            font=MODERN_FONT,
            style="Modern.TCombobox"
        )
        status_combo.grid(row=row, column=0, sticky="ew", padx=(24, 24), pady=(2, 10))
        card.grid_columnconfigure(0, weight=1)
        self._add_combo_effects(status_combo)
        row += 1
        # Due date
        ttk.Label(card, text="Due date", font=LABEL_FONT, foreground=LABEL_COLOR, background=CARD_BG).grid(row=row, column=0, sticky="w", padx=(24, 8), pady=(0, 0))
        row += 1
        self.due_var = tk.StringVar(value=self.task_data['due'])
        due_entry = ModernEntry(card, textvariable=self.due_var, placeholder="YYYY-MM-DD", width=15)
        due_entry.grid(row=row, column=0, sticky="ew", padx=(24, 24), pady=(2, 10))
        card.grid_columnconfigure(0, weight=1)
        due_entry.bind("<FocusIn>", lambda e: self._show_date_picker(due_entry))
        due_entry.bind("<Button-1>", lambda e: self._show_date_picker(due_entry))
        row += 1
        # Notes
        ttk.Label(card, text="Notes", font=LABEL_FONT, foreground=LABEL_COLOR, background=CARD_BG).grid(row=row, column=0, sticky="w", padx=(24, 8), pady=(0, 0))
        row += 1
        self.notes_var = tk.StringVar(value=self.task_data['notes'])
        notes_entry = ModernEntry(card, textvariable=self.notes_var, placeholder="Notes", width=15)
        notes_entry.grid(row=row, column=0, sticky="ew", padx=(24, 24), pady=(2, 10))
        card.grid_columnconfigure(0, weight=1)
        row += 1
        btn_frame = tk.Frame(card, bg=CARD_BG)
        btn_frame.grid(row=row, column=0, sticky="ew", pady=(24, 10), padx=24)
        btn_frame.columnconfigure(0, weight=1)
        btn_frame.columnconfigure(1, weight=1)
        btn_frame.grid_propagate(True)
        btn_frame.pack_propagate(True)
        cancel_btn = ModernButton(btn_frame, text="Cancel", primary=False, command=self.destroy, width=12)
        cancel_btn.grid(row=0, column=0, sticky="w", padx=(0, 8))
        save_btn = ModernButton(btn_frame, text="Save", primary=True, command=self._save, width=12)
        save_btn.grid(row=0, column=1, sticky="e", padx=(8, 0))

    def _add_combo_effects(self, combo):
        def on_focus_in(e):
            combo.configure(style="info.TCombobox")
        def on_focus_out(e):
            combo.configure(style="TCombobox")
        combo.bind("<FocusIn>", on_focus_in)
        combo.bind("<FocusOut>", on_focus_out)

    def _save(self):
        self.result = {
            'task': self.task_var.get().strip(),
            'owner': self.owner_var.get().strip(),
            'status': self.status_var.get(),
            'due': self.due_var.get().strip(),
            'notes': self.notes_var.get().strip()
        }
        self.destroy()

class DatePicker(tk.Toplevel):
    def __init__(self, parent, entry, font=MODERN_FONT):
        super().__init__(parent)
        self.withdraw()
        self.overrideredirect(True)
        self.configure(bg="#fff")
        self.entry = entry
        self.font = font
        self.selected_date = None
        self._build_ui()
        self._position_picker()
        self.deiconify()
        self.focus_force()
        self.bind("<FocusOut>", lambda e: self._close())
        self.bind("<Escape>", lambda e: self._close())

    def _build_ui(self):
        now = datetime.now()
        self.year = now.year
        self.month = now.month
        self.day = now.day
        self.frame = tk.Frame(self, bg="#fff", bd=0, highlightthickness=0)
        self.frame.pack(padx=8, pady=8)
        nav = tk.Frame(self.frame, bg="#fff")
        nav.pack(fill="x")
        prev_btn = tk.Button(nav, text="<", font=self.font, bg="#f7fafd", fg="#222", bd=0, relief="flat", command=self._prev_month, width=2)
        prev_btn.pack(side="left")
        self.month_label = tk.Label(nav, text=f"{calendar.month_name[self.month]} {self.year}", font=self.font, bg="#fff", fg="#222")
        self.month_label.pack(side="left", expand=True)
        next_btn = tk.Button(nav, text=">", font=self.font, bg="#f7fafd", fg="#222", bd=0, relief="flat", command=self._next_month, width=2)
        next_btn.pack(side="right")
        self.days_frame = tk.Frame(self.frame, bg="#fff")
        self.days_frame.pack()
        self._draw_days()

    def _draw_days(self):
        for widget in self.days_frame.winfo_children():
            widget.destroy()
        days = ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"]
        for i, d in enumerate(days):
            tk.Label(self.days_frame, text=d, font=self.font, bg="#fff", fg="#888", width=3).grid(row=0, column=i)
        cal = calendar.monthcalendar(self.year, self.month)
        for r, week in enumerate(cal, 1):
            for c, day in enumerate(week):
                if day == 0:
                    tk.Label(self.days_frame, text="", bg="#fff", width=3).grid(row=r, column=c)
                else:
                    btn = tk.Button(
                        self.days_frame, text=str(day), font=self.font, bg="#f7fafd" if day != self.day else "#2563eb", fg="#222" if day != self.day else "#fff",
                        bd=0, relief="flat", width=3, command=lambda d=day: self._select_date(d)
                    )
                    btn.grid(row=r, column=c, padx=1, pady=1)

    def _prev_month(self):
        if self.month == 1:
            self.month = 12
            self.year -= 1
        else:
            self.month -= 1
        self.month_label.config(text=f"{calendar.month_name[self.month]} {self.year}")
        self._draw_days()

    def _next_month(self):
        if self.month == 12:
            self.month = 1
            self.year += 1
        else:
            self.month += 1
        self.month_label.config(text=f"{calendar.month_name[self.month]} {self.year}")
        self._draw_days()

    def _select_date(self, day):
        self.selected_date = datetime(self.year, self.month, day)
        self.entry.delete(0, tk.END)
        self.entry.insert(0, self.selected_date.strftime("%Y-%m-%d"))
        self._close()
        # Move focus to parent modal to prevent re-triggering
        self.master.focus_set()

    def _position_picker(self):
        self.update_idletasks()
        x = self.entry.winfo_rootx()
        y = self.entry.winfo_rooty() + self.entry.winfo_height()
        self.geometry(f"+{x}+{y}")

    def _close(self):
        self.destroy()

if __name__ == "__main__":
    app = tb.Window(themename="flatly")
    app.title("Editable Task Modal Example")
    app.geometry("900x700")
    def open_modal():
        dlg = GlassModal(app, task_data={
            'task': 'Design UI',
            'owner': 'Yassine',
            'status': 'Working on it',
            'due': '2024-07-18',
            'notes': 'Pixel-perfect, modern modal.'
        })
        if dlg.result:
            print(dlg.result)
    btn = ttk.Button(app, text="Open Editable Task Modal", command=open_modal)
    btn.pack(pady=80)
    app.mainloop() 