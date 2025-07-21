"""
Modern task creation and editing dialog.
"""
import tkinter as tk
from tkinter import ttk, messagebox
import ttkbootstrap as tb
from typing import Optional, Dict, Any, Callable
from datetime import datetime
from utils import validate_task_data, format_date, show_error_dialog
from ui.components import ModernEntry, ModernButton, StatusPill, PriorityBadge, ModernCloseButton
from config import FONTS, TASK_STATUSES, STATUS_COLORS, THEMES
from models import TaskPriority

class TaskDialog(tb.Toplevel):
    """Modern task creation and editing dialog."""
    
    def __init__(self, parent, task_data: Optional[Dict[str, Any]] = None, 
                 on_save: Optional[Callable[[Dict[str, Any]], None]] = None):
        super().__init__(parent)
        
        self.task_data = task_data or {}
        # Set today's date as default if not provided
        if not self.task_data.get('due_date'):
            self.task_data['due_date'] = datetime.now().strftime("%Y-%m-%d")
        self.on_save = on_save
        self.result = None
        
        # Window setup
        self.title("Add Task" if not task_data else "Edit Task")
        
        # Get screen dimensions
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        
        # Calculate responsive size (adaptive to screen size)
        if screen_width >= 1920:  # Large screens (4K, Full HD)
            dialog_width = 900
            dialog_height = 900
        elif screen_width >= 1366:  # Medium screens (laptops)
            dialog_width = 700
            dialog_height = 800
        elif screen_width >= 1024:  # Small screens (tablets)
            dialog_width = 600
            dialog_height = 750
        else:  # Very small screens
            dialog_width = min(500, screen_width - 50)
            dialog_height = min(650, screen_height - 50)
        # Set minimum size (responsive to screen size)
        min_width = 500
        min_height = max(500, screen_height // 4)
        self.geometry(f"{dialog_width}x{dialog_height}")
        self.minsize(min_width, min_height)
        self.maxsize(screen_width - 50, screen_height - 50)  # Prevent larger than screen
        self.resizable(True, True)
        self.transient(parent)
        self.grab_set()
        
        # Center the window
        self.update_idletasks()
        x = (screen_width // 2) - (dialog_width // 2)
        y = (screen_height // 2) - (dialog_height // 2)
        self.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")
        
        # Bind resize events for responsive behavior
        self.bind("<Configure>", self._on_resize)
        
        # Bind window state changes
        self.bind("<Map>", self._on_window_map)
        self.bind("<Unmap>", self._on_window_unmap)
        
        self._create_widgets()
        self._load_task_data()
        
        # Register theme callback
        self._register_theme_callback()
        
        # Bind events
        self.bind("<Escape>", lambda e: self.destroy())
        self.bind("<Return>", lambda e: self._save())
        
        # Focus on title entry
        self.title_entry.focus_set()
    
    def _on_resize(self, event):
        """Handle window resize events for responsive behavior."""
        if event.widget == self:
            # Update form layout when window is resized
            self._update_form_layout()
    
    def _update_form_layout(self):
        """Update form layout based on current window size."""
        try:
            current_width = self.winfo_width()
            
            # Adjust padding based on window size
            if current_width < 500:
                padding = 8
            elif current_width < 700:
                padding = 16
            else:
                padding = 24
            
            # Update main frame padding
            if hasattr(self, 'main_frame'):
                self.main_frame.configure(padding=padding)
            
            # Update form field padding
            if hasattr(self, 'form_frame'):
                for child in self.form_frame.winfo_children():
                    if isinstance(child, ttk.Frame):
                        child.configure(padding=(0, 0, 0, padding // 2))
        except Exception as e:
            # Silently handle any layout errors
            pass
    
    def _on_window_map(self, event):
        """Handle window map event (when window becomes visible)."""
        # Refresh layout when window becomes visible
        self.update_idletasks()
        self._update_form_layout()
    
    def _on_window_unmap(self, event):
        """Handle window unmap event (when window is hidden)."""
        # Clean up any resources when window is hidden
        pass
    
    def _register_theme_callback(self):
        """Register theme change callback."""
        try:
            # Get the main window's theme manager
            main_window = self.master
            if hasattr(main_window, 'theme_manager'):
                main_window.theme_manager.register_theme_callback(self._on_theme_change)
        except Exception as e:
            print(f"Could not register theme callback: {e}")
    
    def _on_theme_change(self, theme_name: str, theme_config: dict):
        """Handle theme changes."""
        try:
            # Update header label color
            if hasattr(self, 'header_label'):
                self.header_label.configure(
                    foreground=theme_config["text_primary"]
                )
            
            # Update close button colors
            if hasattr(self, 'close_btn'):
                self.close_btn.configure(
                    bg=theme_config["surface_color"],
                    fg=theme_config["text_secondary"]
                )
            
            # Update entry widget colors
            if hasattr(self, 'entry_widgets'):
                for entry in self.entry_widgets:
                    if hasattr(entry, 'update_theme_colors'):
                        entry.update_theme_colors(theme_config)
            
            # Update text widget colors
            if hasattr(self, 'description_text'):
                current_text = self.description_text.get("1.0", "end-1c")
                placeholder = "Enter task description..."
                
                if current_text == placeholder:
                    self.description_text.configure(
                        bg=theme_config["background_color"],
                        fg=theme_config["text_secondary"],
                        insertbackground=theme_config["text_primary"],
                        selectbackground=theme_config["primary_color"]
                    )
                else:
                    self.description_text.configure(
                        bg=theme_config["background_color"],
                        fg=theme_config["text_primary"],
                        insertbackground=theme_config["text_primary"],
                        selectbackground=theme_config["primary_color"]
                    )
            
            if hasattr(self, 'notes_text'):
                current_text = self.notes_text.get("1.0", "end-1c")
                placeholder = "Enter additional notes..."
                
                if current_text == placeholder:
                    self.notes_text.configure(
                        bg=theme_config["background_color"],
                        fg=theme_config["text_secondary"],
                        insertbackground=theme_config["text_primary"],
                        selectbackground=theme_config["primary_color"]
                    )
                else:
                    self.notes_text.configure(
                        bg=theme_config["background_color"],
                        fg=theme_config["text_primary"],
                        insertbackground=theme_config["text_primary"],
                        selectbackground=theme_config["primary_color"]
                    )
        except Exception as e:
            print(f"Error updating theme colors: {e}")
    
    def _create_widgets(self):
        """Create the dialog widgets."""
        # Main container with responsive padding
        self.main_frame = ttk.Frame(self, padding=24)
        self.main_frame.pack(fill="both", expand=True)
        self.main_frame.columnconfigure(0, weight=1)
        
        # Header
        header_frame = ttk.Frame(self.main_frame)
        header_frame.pack(fill="x", pady=(0, 16))
        
        # Show 'Add Task' if no id in task_data, else 'Edit Task'
        is_edit = self.task_data and self.task_data.get('id')
        title_text = "Edit Task" if is_edit else "Add Task"
        
        # Get current theme colors for header
        current_theme = "dark" if self.winfo_toplevel().style.theme_use() == "darkly" else "light"
        theme_colors = THEMES[current_theme]
        
        header_label = ttk.Label(
            header_frame, 
            text=title_text,
            font=FONTS["heading"],
            foreground=theme_colors["text_primary"]
        )
        header_label.pack(side="left")
        
        # Store reference for theme updates
        self.header_label = header_label
        
        # Get current theme colors for close button
        current_theme = "dark" if self.winfo_toplevel().style.theme_use() == "darkly" else "light"
        theme_colors = THEMES[current_theme]
        
        # Modern close button with theme-aware colors
        
        # Form container with scrollbar
        form_container = ttk.Frame(self.main_frame)
        form_container.pack(fill="both", expand=True)
        form_container.columnconfigure(0, weight=1)
        
        # Create canvas for scrolling
        canvas = tk.Canvas(form_container, bg="white", highlightthickness=0)
        scrollbar = ttk.Scrollbar(form_container, orient="vertical", command=canvas.yview)
        self.form_frame = ttk.Frame(canvas)
        self.form_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        self.form_frame.columnconfigure(0, weight=1)
        
        canvas.create_window((0, 0), window=self.form_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Bind mouse wheel to canvas for scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        canvas.bind("<MouseWheel>", _on_mousewheel)
        self.form_frame.bind("<MouseWheel>", _on_mousewheel)
        
        # Title field
        self._create_field(self.form_frame, "Title *", "title_entry", "Enter task title...")
        
        # Description field
        self._create_text_field(self.form_frame, "Description", "description_text", "Enter task description...")
        
        # Owner field
        self._create_field(self.form_frame, "Owner", "owner_entry", "Enter owner name...")
        
        # Status field
        self._create_status_field(self.form_frame)
        
        # Priority field
        self._create_priority_field(self.form_frame)
        
        # Due date field
        self._create_date_field(self.form_frame, "Due Date", "due_date_entry")
        
        # Estimated hours field
        self._create_field(self.form_frame, "Estimated Hours", "estimated_hours_entry", "e.g., 2.5")
        
        # Tags field
        self._create_field(self.form_frame, "Tags", "tags_entry", "Enter tags separated by commas...")
        
        # Notes field
        self._create_text_field(self.form_frame, "Notes", "notes_text", "Enter additional notes...")
        
        # Add some spacing before buttons
        spacer = ttk.Frame(self.form_frame, height=20)
        spacer.pack(fill="x")
        
        # Buttons
        self._create_buttons(self.main_frame)
    
    def _create_field(self, parent, label_text: str, attr_name: str, placeholder: str):
        """Create a text field with label."""
        # Container frame for responsive layout
        field_frame = ttk.Frame(parent)
        field_frame.pack(fill="x", pady=(8, 12))
        field_frame.columnconfigure(0, weight=1)
        
        # Get current theme colors for label
        current_theme = "dark" if self.winfo_toplevel().style.theme_use() == "darkly" else "light"
        theme_colors = THEMES[current_theme]
        
        # Label
        label = ttk.Label(
            field_frame, 
            text=label_text, 
            font=FONTS["primary_bold"],
            foreground=theme_colors["text_primary"]
        )
        label.pack(anchor="w", pady=(0, 4))
        
        # Entry
        entry = ModernEntry(field_frame, placeholder=placeholder)
        entry.pack(fill="x", expand=True)
        
        setattr(self, attr_name, entry)
        
        # Store reference for theme updates
        if not hasattr(self, 'entry_widgets'):
            self.entry_widgets = []
        self.entry_widgets.append(entry)
    
    def _create_text_field(self, parent, label_text: str, attr_name: str, placeholder: str):
        """Create a text area with label."""
        # Container frame for responsive layout
        field_frame = ttk.Frame(parent)
        field_frame.pack(fill="both", expand=True, pady=(8, 12))
        field_frame.columnconfigure(0, weight=1)
        
        # Get current theme colors for label
        current_theme = "dark" if self.winfo_toplevel().style.theme_use() == "darkly" else "light"
        theme_colors = THEMES[current_theme]
        
        # Label
        label = ttk.Label(
            field_frame, 
            text=label_text, 
            font=FONTS["primary_bold"],
            foreground=theme_colors["text_primary"]
        )
        label.pack(anchor="w", pady=(0, 4))
        
        # Text widget
        text_frame = ttk.Frame(field_frame)
        text_frame.pack(fill="both", expand=True)
        text_frame.columnconfigure(0, weight=1)
        
        # Calculate responsive height based on screen size
        screen_height = self.winfo_screenheight()
        if screen_height >= 1080:  # Large screens
            text_height = 5
        elif screen_height >= 768:  # Medium screens
            text_height = 4
        else:  # Small screens
            text_height = 3
        
        # Get current theme colors
        current_theme = "dark" if self.winfo_toplevel().style.theme_use() == "darkly" else "light"
        theme_colors = THEMES[current_theme]
        
        text_widget = tk.Text(
            text_frame,
            height=text_height,
            font=FONTS["primary"],
            wrap="word",
            relief="flat",
            borderwidth=1,
            padx=8,
            pady=8,
            bg=theme_colors["background_color"],
            fg=theme_colors["text_secondary"],
            insertbackground=theme_colors["text_primary"],
            selectbackground=theme_colors["primary_color"],
            selectforeground="white"
        )
        text_widget.pack(fill="both", expand=True)
        
        # Add placeholder
        text_widget.insert("1.0", placeholder)
        text_widget.configure(foreground=theme_colors["text_secondary"])
        
        def on_focus_in(event):
            if text_widget.get("1.0", "end-1c") == placeholder:
                text_widget.delete("1.0", "end")
                text_widget.configure(foreground=theme_colors["text_primary"])
        
        def on_focus_out(event):
            if not text_widget.get("1.0", "end-1c").strip():
                text_widget.insert("1.0", placeholder)
                text_widget.configure(foreground=theme_colors["text_secondary"])
        
        text_widget.bind("<FocusIn>", on_focus_in)
        text_widget.bind("<FocusOut>", on_focus_out)
        
        setattr(self, attr_name, text_widget)
    
    def _create_status_field(self, parent):
        """Create status selection field."""
        # Container frame for responsive layout
        field_frame = ttk.Frame(parent)
        field_frame.pack(fill="x", pady=(8, 12))
        field_frame.columnconfigure(0, weight=1)
        
        # Get current theme colors for label
        current_theme = "dark" if self.winfo_toplevel().style.theme_use() == "darkly" else "light"
        theme_colors = THEMES[current_theme]
        
        # Label
        label = ttk.Label(
            field_frame, 
            text="Status", 
            font=FONTS["primary_bold"],
            foreground=theme_colors["text_primary"]
        )
        label.pack(anchor="w", pady=(0, 4))
        
        # Status frame
        status_frame = ttk.Frame(field_frame)
        status_frame.pack(fill="x", expand=True)
        status_frame.columnconfigure(0, weight=1)
        status_frame.columnconfigure(1, weight=1)
        
        # Status buttons with responsive layout
        self.status_var = tk.StringVar(value="Working on it")
        status_buttons = []
        
        # Create a responsive grid for radio buttons
        for i, status in enumerate(TASK_STATUSES):
            btn = ttk.Radiobutton(
                status_frame,
                text=status,
                variable=self.status_var,
                value=status,
                style="TRadiobutton"
            )
            # Use grid for better responsive layout
            row = i // 2
            col = i % 2
            btn.grid(row=row, column=col, sticky="ew", padx=(0, 16), pady=2)
            status_buttons.append(btn)
    
    def _create_priority_field(self, parent):
        """Create priority selection field."""
        # Container frame for responsive layout
        field_frame = ttk.Frame(parent)
        field_frame.pack(fill="x", pady=(8, 12))
        field_frame.columnconfigure(0, weight=1)
        
        # Get current theme colors for label
        current_theme = "dark" if self.winfo_toplevel().style.theme_use() == "darkly" else "light"
        theme_colors = THEMES[current_theme]
        
        # Label
        label = ttk.Label(
            field_frame, 
            text="Priority", 
            font=FONTS["primary_bold"],
            foreground=theme_colors["text_primary"]
        )
        label.pack(anchor="w", pady=(0, 4))
        
        # Priority frame
        priority_frame = ttk.Frame(field_frame)
        priority_frame.pack(fill="x", expand=True)
        priority_frame.columnconfigure(0, weight=1)
        priority_frame.columnconfigure(1, weight=1)
        
        # Priority buttons with responsive layout
        self.priority_var = tk.StringVar(value="Medium")
        priority_buttons = []
        
        # Create a responsive grid for radio buttons
        for i, priority in enumerate(TaskPriority):
            btn = ttk.Radiobutton(
                priority_frame,
                text=priority.value,
                variable=self.priority_var,
                value=priority.value,
                style="TRadiobutton"
            )
            # Use grid for better responsive layout
            row = i // 2
            col = i % 2
            btn.grid(row=row, column=col, sticky="ew", padx=(0, 16), pady=2)
            priority_buttons.append(btn)
    
    def _create_date_field(self, parent, label_text: str, attr_name: str):
        """Create a date field with picker."""
        # Container frame for responsive layout
        field_frame = ttk.Frame(parent)
        field_frame.pack(fill="x", pady=(8, 12))
        field_frame.columnconfigure(0, weight=1)
        
        # Get current theme colors for label
        current_theme = "dark" if self.winfo_toplevel().style.theme_use() == "darkly" else "light"
        theme_colors = THEMES[current_theme]
        
        # Label
        label = ttk.Label(
            field_frame, 
            text=label_text, 
            font=FONTS["primary_bold"],
            foreground=theme_colors["text_primary"]
        )
        label.pack(anchor="w", pady=(0, 4))
        
        # Date frame
        date_frame = ttk.Frame(field_frame)
        date_frame.pack(fill="x", expand=True)
        date_frame.columnconfigure(0, weight=1)
        
        # Date entry
        entry = ModernEntry(date_frame, placeholder="YYYY-MM-DD")
        entry.pack(side="left", fill="x", expand=True)
        
        # Date picker button
        picker_btn = ttk.Button(
            date_frame,
            text="📅 Select Date",
            command=lambda: self._show_date_picker(entry),
            style="TButton",
            width=12
        )
        picker_btn.pack(side="right", padx=(8, 0))
        
        setattr(self, attr_name, entry)
        
        # Store reference to automatically open date picker
        setattr(self, f"{attr_name}_picker_btn", picker_btn)
    
    def _create_buttons(self, parent):
        """Create action buttons."""
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill="x", pady=(16, 8))
        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)
        
        # Responsive button layout
        # Cancel button
        cancel_btn = ModernButton(
            button_frame,
            text="Cancel",
            command=self.destroy
        )
        cancel_btn.pack(side="right", padx=(8, 0), fill="x", expand=True)
        
        # Save button
        self.save_btn = ModernButton(
            button_frame,
            text="Save Task",
            primary=True,
            command=self._save
        )
        self.save_btn.pack(side="right", fill="x", expand=True)
    
    def _show_date_picker(self, entry):
        """Show a simple date picker dialog."""
        try:
            # Create a simple date picker dialog
            picker = tk.Toplevel(self)
            picker.title("Select Date")
            picker.geometry("300x250")
            picker.resizable(False, False)
            picker.transient(self)
            picker.grab_set()
            
            # Center the picker
            picker.update_idletasks()
            x = (self.winfo_screenwidth() // 2) - (300 // 2)
            y = (self.winfo_screenheight() // 2) - (250 // 2)
            picker.geometry(f"300x250+{x}+{y}")
            
            # Create the date picker content
            self._create_simple_date_picker(picker, entry)
            
        except Exception as e:
            print(f"Date picker error: {e}")
            # Fallback: just focus the entry
            entry.focus_set()
    
    def _create_simple_date_picker(self, picker, entry):
        """Create a simple date picker interface."""
        import calendar
        from datetime import datetime, date
        
        # Get current date
        now = datetime.now()
        current_year = now.year
        current_month = now.month
        current_day = now.day
        
        # Variables
        year_var = tk.StringVar(value=str(current_year))
        month_var = tk.StringVar(value=str(current_month))
        day_var = tk.StringVar(value=str(current_day))
        
        # Main frame
        main_frame = ttk.Frame(picker, padding=20)
        main_frame.pack(fill="both", expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="Select Date", font=FONTS["heading"])
        title_label.pack(pady=(0, 20))
        
        # Year selection
        year_frame = ttk.Frame(main_frame)
        year_frame.pack(fill="x", pady=5)
        ttk.Label(year_frame, text="Year:").pack(side="left")
        year_spinbox = ttk.Spinbox(
            year_frame, 
            from_=1900, 
            to=2100, 
            textvariable=year_var,
            width=10
        )
        year_spinbox.pack(side="right")
        
        # Month selection
        month_frame = ttk.Frame(main_frame)
        month_frame.pack(fill="x", pady=5)
        ttk.Label(month_frame, text="Month:").pack(side="left")
        month_spinbox = ttk.Spinbox(
            month_frame, 
            from_=1, 
            to=12, 
            textvariable=month_var,
            width=10
        )
        month_spinbox.pack(side="right")
        
        # Day selection
        day_frame = ttk.Frame(main_frame)
        day_frame.pack(fill="x", pady=5)
        ttk.Label(day_frame, text="Day:").pack(side="left")
        day_spinbox = ttk.Spinbox(
            day_frame, 
            from_=1, 
            to=31, 
            textvariable=day_var,
            width=10
        )
        day_spinbox.pack(side="right")
        
        def update_day_range(*args):
            """Update the day range based on selected month and year."""
            try:
                year = int(year_var.get())
                month = int(month_var.get())
                current_day = int(day_var.get())
                
                # Get the number of days in the selected month
                _, last_day = calendar.monthrange(year, month)
                
                # Update day spinbox range
                day_spinbox.configure(to=last_day)
                
                # If current day is greater than last day of month, reset to 1
                if current_day > last_day:
                    day_var.set("1")
                    
            except ValueError:
                pass
        
        # Bind month and year changes to update day range
        month_var.trace("w", update_day_range)
        year_var.trace("w", update_day_range)
        
        # Buttons frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill="x", pady=(20, 0))
        
        def set_date():
            """Set the selected date in the entry field."""
            try:
                year = int(year_var.get())
                month = int(month_var.get())
                day = int(day_var.get())
                
                # Validate date
                selected_date = date(year, month, day)
                date_str = selected_date.strftime("%Y-%m-%d")
                
                # Clear entry and set new date
                entry.set_value(date_str)
                
                # Close picker
                picker.destroy()
                
            except ValueError as e:
                # Show error for invalid date
                error_label = ttk.Label(main_frame, text="Invalid date!", foreground="red")
                error_label.pack(pady=5)
                picker.after(2000, error_label.destroy)
        
        def cancel():
            """Cancel date selection."""
            picker.destroy()
        
        def set_today():
            """Set today's date."""
            today = datetime.now()
            year_var.set(str(today.year))
            month_var.set(str(today.month))
            day_var.set(str(today.day))
        
        # Buttons
        today_btn = ttk.Button(button_frame, text="Today", command=set_today)
        today_btn.pack(side="left")
        
        cancel_btn = ttk.Button(button_frame, text="Cancel", command=cancel)
        cancel_btn.pack(side="right", padx=(5, 0))
        
        ok_btn = ttk.Button(button_frame, text="OK", command=set_date)
        ok_btn.pack(side="right")
        
        # Bind Enter key to OK button
        picker.bind("<Return>", lambda e: set_date())
        picker.bind("<Escape>", lambda e: cancel())
        
        # Focus on year spinbox
        year_spinbox.focus_set()
    
    def _load_task_data(self):
        """Load existing task data into the form."""
        if not self.task_data:
            return
        
        # Title
        if hasattr(self, 'title_entry'):
            self.title_entry.set_value(self.task_data.get('title', ''))
        
        # Description
        if hasattr(self, 'description_text'):
            self.description_text.delete("1.0", "end")
            description = self.task_data.get('description', '')
            if description:
                self.description_text.insert("1.0", description)
                self.description_text.configure(foreground="#1f2937")
        
        # Owner
        if hasattr(self, 'owner_entry'):
            self.owner_entry.set_value(self.task_data.get('owner', ''))
        
        # Status
        if hasattr(self, 'status_var'):
            status = self.task_data.get('status', 'Working on it')
            self.status_var.set(status)
        
        # Priority
        if hasattr(self, 'priority_var'):
            priority = self.task_data.get('priority', 'Medium')
            self.priority_var.set(priority)
        
        # Due date
        if hasattr(self, 'due_date_entry'):
            due_date = self.task_data.get('due_date', '')
            if due_date:
                self.due_date_entry.set_value(due_date)
        
        # Estimated hours
        if hasattr(self, 'estimated_hours_entry'):
            estimated_hours = self.task_data.get('estimated_hours', '')
            if estimated_hours:
                self.estimated_hours_entry.set_value(str(estimated_hours))
        
        # Tags
        if hasattr(self, 'tags_entry'):
            self.tags_entry.set_value(self.task_data.get('tags', ''))
        
        # Notes
        if hasattr(self, 'notes_text'):
            self.notes_text.delete("1.0", "end")
            notes = self.task_data.get('notes', '')
            if notes:
                self.notes_text.insert("1.0", notes)
                self.notes_text.configure(foreground="#1f2937")
        
        # Automatically open date picker after dialog is fully loaded
        self.after(100, self._auto_open_date_picker)
    
    def _auto_open_date_picker(self):
        """Automatically open the date picker when dialog loads."""
        try:
            # Check if due date entry exists and is empty
            if hasattr(self, 'due_date_entry'):
                current_value = self.due_date_entry.get_value().strip()
                if not current_value or current_value == "YYYY-MM-DD":
                    # Automatically open date picker
                    self._show_date_picker(self.due_date_entry)
        except Exception as e:
            # Silently handle any errors
            pass
    
    def _get_form_data(self) -> Dict[str, Any]:
        """Get data from the form."""
        data = {}
        
        # Title
        if hasattr(self, 'title_entry'):
            data['title'] = self.title_entry.get_value().strip()
        
        # Description
        if hasattr(self, 'description_text'):
            description = self.description_text.get("1.0", "end-1c").strip()
            if description and description != "Enter task description...":
                data['description'] = description
        
        # Owner
        if hasattr(self, 'owner_entry'):
            owner = self.owner_entry.get_value().strip()
            if owner and owner != "Enter owner name...":
                data['owner'] = owner
        
        # Status
        if hasattr(self, 'status_var'):
            data['status'] = self.status_var.get()
        
        # Priority
        if hasattr(self, 'priority_var'):
            data['priority'] = self.priority_var.get()
        
        # Due date
        if hasattr(self, 'due_date_entry'):
            due_date = self.due_date_entry.get_value().strip()
            if due_date and due_date != "YYYY-MM-DD":
                data['due_date'] = due_date
        
        # Estimated hours
        if hasattr(self, 'estimated_hours_entry'):
            estimated_hours = self.estimated_hours_entry.get_value().strip()
            if estimated_hours:
                try:
                    data['estimated_hours'] = float(estimated_hours)
                except ValueError:
                    pass
        
        # Tags
        if hasattr(self, 'tags_entry'):
            tags = self.tags_entry.get_value().strip()
            if tags and tags != "Enter tags separated by commas...":
                data['tags'] = tags
        
        # Notes
        if hasattr(self, 'notes_text'):
            notes = self.notes_text.get("1.0", "end-1c").strip()
            if notes and notes != "Enter additional notes...":
                data['notes'] = notes
        
        return data
    
    def _save(self):
        """Save the task data."""
        try:
            # Disable save button to prevent double-clicks
            if hasattr(self, 'save_btn'):
                self.save_btn.configure(state="disabled")
            
            data = self._get_form_data()
            
            # Validate data
            is_valid, error_message = validate_task_data(data)
            if not is_valid:
                show_error_dialog(self, "Validation Error", error_message)
                # Re-enable save button
                if hasattr(self, 'save_btn'):
                    self.save_btn.configure(state="normal")
                return
            
            # Preserve the task ID if editing an existing task
            if self.task_data and 'id' in self.task_data:
                data['id'] = self.task_data['id']
            
            # Preserve other important fields from original task data
            if self.task_data:
                # Preserve created_date if it exists
                if 'created_date' in self.task_data:
                    data['created_date'] = self.task_data['created_date']
                
                # Preserve project if it exists
                if 'project' in self.task_data:
                    data['project'] = self.task_data['project']
                else:
                    data['project'] = 'learning'
            else:
                # For new tasks, set default project
                data['project'] = 'learning'
            
            # Set completion status based on status
            if data.get('status') == 'Done':
                data['completed'] = True
                data['completed_date'] = datetime.now().strftime("%Y-%m-%d")
            else:
                data['completed'] = False
                data['completed_date'] = None
            
            self.result = data
            
            # Call save callback if provided
            if self.on_save:
                self.on_save(data)
            
            self.destroy()
            
        except Exception as e:
            show_error_dialog(self, "Save Error", f"Failed to save task: {e}")
            # Re-enable save button on error
            if hasattr(self, 'save_btn'):
                self.save_btn.configure(state="normal") 