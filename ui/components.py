"""
Reusable UI components for the Task Tracker application.
"""
import tkinter as tk
from tkinter import ttk
import ttkbootstrap as tb
from typing import Optional, Callable, Any
from datetime import datetime
import calendar
from utils import center_window, create_tooltip, format_date, is_overdue
from config import FONTS, STATUS_COLORS
import math

class ModernEntry(ttk.Entry):
    """Modern styled entry widget with placeholder support."""
    
    def __init__(self, parent, placeholder: str = "", **kwargs):
        self.placeholder = placeholder
        
        # Get current theme colors
        try:
            current_theme = "dark" if parent.winfo_toplevel().style.theme_use() == "darkly" else "light"
            from config import THEMES
            theme_colors = THEMES[current_theme]
            self.placeholder_color = theme_colors["text_secondary"]
            self.text_color = theme_colors["text_primary"]
        except:
            # Fallback colors
            self.placeholder_color = "#9ca3af"
            self.text_color = "#1f2937"
        
        super().__init__(parent, **kwargs)
        
        # Always set background and foreground explicitly
        self.configure(foreground=self.placeholder_color, background=theme_colors["background_color"] if 'theme_colors' in locals() else "#fff")
        
        if placeholder:
            self.insert(0, placeholder)
            self.configure(foreground=self.placeholder_color)
        
        self.bind("<FocusIn>", self._on_focus_in)
        self.bind("<FocusOut>", self._on_focus_out)
        self.bind("<KeyRelease>", self._on_key_release)
    
    def _on_focus_in(self, event):
        if self.get() == self.placeholder:
            self.delete(0, tk.END)
            self.configure(foreground=self.text_color)
    
    def _on_focus_out(self, event):
        if not self.get().strip():
            self.insert(0, self.placeholder)
            self.configure(foreground=self.placeholder_color)
    
    def _on_key_release(self, event):
        current_text = self.get()
        if current_text and current_text != self.placeholder:
            self.configure(foreground=self.text_color)
        elif not current_text.strip():
            self.configure(foreground=self.placeholder_color)
    
    def get_value(self) -> str:
        """Get the actual value, excluding placeholder."""
        value = self.get().strip()
        return "" if value == self.placeholder else value
    
    def set_value(self, value: str):
        """Set the value, handling placeholder properly."""
        self.delete(0, tk.END)
        if value:
            self.insert(0, value)
            self.configure(foreground=self.text_color)
        else:
            self.insert(0, self.placeholder)
            self.configure(foreground=self.placeholder_color)
    
    def update_theme_colors(self, theme_colors: dict):
        """Update colors when theme changes."""
        self.placeholder_color = theme_colors["text_secondary"]
        self.text_color = theme_colors["text_primary"]
        self.configure(background=theme_colors["background_color"])
        # Update current text color if it's not placeholder
        current_text = self.get()
        if current_text and current_text != self.placeholder:
            self.configure(foreground=self.text_color)
        else:
            self.configure(foreground=self.placeholder_color)

class ModernButton(ttk.Button):
    """Modern styled button with hover effects and loading states."""
    
    def __init__(self, parent, text: str, primary: bool = False, 
                 command: Optional[Callable] = None, loading_text: str = "Loading...", **kwargs):
        style = "Modern.Primary.TButton" if primary else "Modern.Secondary.TButton"
        super().__init__(parent, text=text, style=style, command=command, **kwargs)
        
        self.original_text = text
        self.loading_text = loading_text
        self.is_loading = False
        
        # Add hover effects
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
    
    def _on_enter(self, event):
        if not self.is_loading:
            self.configure(cursor="hand2")
    
    def _on_leave(self, event):
        self.configure(cursor="")
    
    def set_loading(self, loading: bool = True):
        """Set loading state for the button."""
        self.is_loading = loading
        
        if loading:
            self.configure(text=self.loading_text, state="disabled")
        else:
            self.configure(text=self.original_text, state="normal")
    
    def set_enabled(self, enabled: bool = True):
        """Enable or disable the button."""
        state = "normal" if enabled else "disabled"
        self.configure(state=state)
        if not enabled:
            self.configure(cursor="")
        else:
            self.configure(cursor="hand2")

class SearchEntry(ModernEntry):
    """Search entry with debounced search functionality."""
    
    def __init__(self, parent, on_search: Callable[[str], None], **kwargs):
        super().__init__(parent, placeholder="Search tasks...", **kwargs)
        self.on_search = on_search
        self.search_after_id = None
        
        self.bind("<KeyRelease>", self._on_search_key_release)
    
    def _on_search_key_release(self, event):
        # Cancel previous search
        if self.search_after_id:
            self.after_cancel(self.search_after_id)
        
        # Schedule new search
        self.search_after_id = self.after(300, self._perform_search)
    
    def _perform_search(self):
        search_term = self.get_value()  # Use the new get_value method
        self.on_search(search_term)
    
    def clear_search(self):
        """Clear the search field."""
        self.set_value("")
        self.on_search("")

class StatusPill(ttk.Label):
    """Status pill widget for displaying task status."""
    
    def __init__(self, parent, status: str, **kwargs):
        super().__init__(parent, text=status, **kwargs)
        self.status = status
        self._update_style()
    
    def _update_style(self):
        color = STATUS_COLORS.get(self.status, "#6b7280")
        self.configure(
            background=color,
            foreground="white",
            font=FONTS["secondary"],
            padding=(8, 4),
            relief="flat",
            borderwidth=0
        )

class PriorityBadge(ttk.Label):
    """Priority badge widget."""
    
    def __init__(self, parent, priority: str, **kwargs):
        super().__init__(parent, text=priority, **kwargs)
        self.priority = priority
        self._update_style()
    
    def _update_style(self):
        priority_colors = {
            "Low": "#10b981",
            "Medium": "#f59e0b", 
            "High": "#ef4444",
            "Urgent": "#dc2626"
        }
        color = priority_colors.get(self.priority, "#6b7280")
        self.configure(
            background=color,
            foreground="white",
            font=FONTS["caption"],
            padding=(6, 2),
            relief="flat",
            borderwidth=0
        )

class DatePicker(tk.Toplevel):
    """Modern date picker widget."""
    
    def __init__(self, parent, entry_widget, **kwargs):
        super().__init__(parent, **kwargs)
        self.entry_widget = entry_widget
        self.selected_date = None
        
        self.title("")
        self.geometry("280x320")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        
        # Hide window decorations
        self.overrideredirect(True)
        
        self._create_widgets()
        self._position_window()
        self._load_current_month()
    
    def _create_widgets(self):
        # Header frame
        header_frame = ttk.Frame(self)
        header_frame.pack(fill="x", padx=8, pady=8)
        
        # Navigation buttons
        self.prev_btn = ModernButton(header_frame, text="‹", command=self._prev_month)
        self.prev_btn.pack(side="left")
        
        self.month_label = ttk.Label(header_frame, text="", font=FONTS["primary_bold"])
        self.month_label.pack(side="left", expand=True)
        
        self.next_btn = ModernButton(header_frame, text="›", command=self._next_month)
        self.next_btn.pack(side="right")
        
        # Calendar frame
        self.calendar_frame = ttk.Frame(self)
        self.calendar_frame.pack(fill="both", expand=True, padx=8, pady=8)
        
        # Day headers
        days = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
        for i, day in enumerate(days):
            label = ttk.Label(self.calendar_frame, text=day, font=FONTS["secondary"])
            label.grid(row=0, column=i, sticky="ew", padx=1, pady=1)
        
        # Configure grid weights
        for i in range(7):
            self.calendar_frame.columnconfigure(i, weight=1)
    
    def _position_window(self):
        """Position the date picker near the entry widget."""
        self.update_idletasks()
        
        entry_x = self.entry_widget.winfo_rootx()
        entry_y = self.entry_widget.winfo_rooty()
        entry_height = self.entry_widget.winfo_height()
        
        x = entry_x
        y = entry_y + entry_height + 5
        
        # Ensure it doesn't go off screen
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        
        if x + 280 > screen_width:
            x = screen_width - 280
        
        if y + 320 > screen_height:
            y = entry_y - 320 - 5
        
        self.geometry(f"+{x}+{y}")
    
    def _load_current_month(self):
        """Load and display the current month."""
        now = datetime.now()
        self.current_year = now.year
        self.current_month = now.month
        
        self._update_calendar()
    
    def _update_calendar(self):
        """Update the calendar display."""
        # Clear existing day buttons
        for widget in self.calendar_frame.winfo_children():
            if isinstance(widget, tk.Button):
                widget.destroy()
        
        # Update month label
        month_name = datetime(self.current_year, self.current_month, 1).strftime("%B %Y")
        self.month_label.configure(text=month_name)
        
        # Get calendar data
        cal = calendar.monthcalendar(self.current_year, self.current_month)
        
        # Create day buttons
        for week_num, week in enumerate(cal):
            for day_num, day in enumerate(week):
                if day != 0:
                    btn = tk.Button(
                        self.calendar_frame,
                        text=str(day),
                        font=FONTS["primary"],
                        relief="flat",
                        borderwidth=1,
                        command=lambda d=day: self._select_date(d)
                    )
                    btn.grid(row=week_num + 1, column=day_num, sticky="ew", padx=1, pady=1)
                    
                    # Highlight today
                    if (day == datetime.now().day and 
                        self.current_month == datetime.now().month and 
                        self.current_year == datetime.now().year):
                        btn.configure(background="#3b82f6", foreground="white")
    
    def _prev_month(self):
        """Go to previous month."""
        self.current_month -= 1
        if self.current_month < 1:
            self.current_month = 12
            self.current_year -= 1
        self._update_calendar()
    
    def _next_month(self):
        """Go to next month."""
        self.current_month += 1
        if self.current_month > 12:
            self.current_month = 1
            self.current_year += 1
        self._update_calendar()
    
    def _select_date(self, day):
        """Select a date and close the picker."""
        try:
            date_str = f"{self.current_year:04d}-{self.current_month:02d}-{day:02d}"
            self.entry_widget.delete(0, tk.END)
            self.entry_widget.insert(0, date_str)
            self.entry_widget.configure(foreground="#1f2937")
        except Exception as e:
            print(f"Error setting date: {e}")
        finally:
            self.destroy()

class ModernNotificationWidget(ttk.Frame):
    """Modern integrated notification widget for displaying messages within the app."""
    
    def __init__(self, parent, message: str, notification_type: str = "info", duration: int = 4000):
        super().__init__(parent)
        self.message = message
        self.notification_type = notification_type
        self.duration = duration
        self.is_visible = False
        
        # Configure vivid, modern colors based on type
        self.colors = {
            "info": {
                "bg": "#3b82f6",
                "fg": "#ffffff",
                "border": "#1d4ed8",
                "icon": "💡",
                "shadow": "#1e40af"
            },
            "success": {
                "bg": "#10b981",
                "fg": "#ffffff",
                "border": "#059669",
                "icon": "✨",
                "shadow": "#047857"
            },
            "warning": {
                "bg": "#f59e0b",
                "fg": "#ffffff",
                "border": "#d97706",
                "icon": "⚡",
                "shadow": "#b45309"
            },
            "error": {
                "bg": "#ef4444",
                "fg": "#ffffff",
                "border": "#dc2626",
                "icon": "🔥",
                "shadow": "#b91c1c"
            }
        }
        
        self.color_config = self.colors.get(self.notification_type, self.colors["info"])
        
        self._create_widgets()
        self._show_notification()
    
    def _create_widgets(self):
        """Create the notification widgets."""
        # Main container with modern styling
        self.configure(
            relief="flat",
            borderwidth=0,
            style="ModernNotification.TFrame"
        )
        
        # Configure custom style with vivid colors
        style = ttk.Style()
        style.configure(
            "ModernNotification.TFrame",
            background=self.color_config["bg"],
            borderwidth=0,
            relief="flat"
        )
        
        # Create main content container with shadow effect
        main_container = tk.Frame(
            self,
            bg=self.color_config["bg"],
            relief="flat",
            borderwidth=0,
            highlightthickness=2,
            highlightbackground=self.color_config["border"],
            highlightcolor=self.color_config["border"]
        )
        main_container.pack(fill="x", padx=2, pady=2)
        
        # Compact content frame
        content_frame = tk.Frame(main_container, bg=self.color_config["bg"])
        content_frame.pack(fill="x", padx=12, pady=8)
        
        # Icon label with larger, more vibrant icon
        self.icon_label = tk.Label(
            content_frame,
            text=self.color_config["icon"],
            font=("Segoe UI", 24),
            bg=self.color_config["bg"],
            fg=self.color_config["fg"]
        )
        self.icon_label.pack(side="left", padx=(0, 10))
        
        # Message frame
        message_frame = tk.Frame(content_frame, bg=self.color_config["bg"])
        message_frame.pack(side="left", fill="x", expand=True)
        
        # Compact title and message in one line
        title_text = {
            "info": "Info",
            "success": "Success",
            "warning": "Warning", 
            "error": "Error"
        }.get(self.notification_type, "Notification")
        
        # Combined title and message label for compact design
        self.message_label = tk.Label(
            message_frame,
            text=f"{title_text}: {self.message}",
            font=("Segoe UI", 10, "bold"),
            bg=self.color_config["bg"],
            fg=self.color_config["fg"],
            wraplength=350,
            justify="left",
            anchor="w"
        )
        self.message_label.pack(fill="x", expand=True)
        
        # Modern minimalist close button
        self.close_btn = ModernCloseButton(
            content_frame,
            bg=self.color_config["bg"],
            fg=self.color_config["fg"],
            hover_bg=self.color_config["border"],
            command=self._hide_notification
        )
        self.close_btn.pack(side="right", padx=(8, 0))
        
        # Compact progress bar
        self.progress_frame = tk.Frame(main_container, bg=self.color_config["bg"])
        self.progress_frame.pack(fill="x", padx=12, pady=(0, 4))
        
        # Modern progress bar
        self.progress_bar = tk.Canvas(
            self.progress_frame,
            height=3,
            bg=self.color_config["bg"],
            highlightthickness=0,
            relief="flat"
        )
        self.progress_bar.pack(fill="x")
        
        # Draw initial progress bar
        self._draw_progress_bar(0)
    
    def _show_notification(self):
        """Show the notification with animation."""
        self.is_visible = True
        
        # Simple progress animation
        self._animate_progress()
        
        # Auto-hide after duration
        self.after(self.duration, self._hide_notification)
    
    def _draw_progress_bar(self, progress_percent):
        """Draw the progress bar on canvas."""
        try:
            self.progress_bar.delete("all")
            width = self.progress_bar.winfo_width()
            if width <= 1:  # Canvas not yet sized
                width = 300
            
            # Draw background
            self.progress_bar.create_rectangle(
                0, 0, width, 3,
                fill=self.color_config["bg"],
                outline=""
            )
            
            # Draw progress
            progress_width = (progress_percent / 100) * width
            if progress_width > 0:
                self.progress_bar.create_rectangle(
                    0, 0, progress_width, 3,
                    fill=self.color_config["fg"],
                    outline=""
                )
        except Exception as e:
            pass  # Ignore drawing errors
    
    def _animate_progress(self):
        """Smooth progress bar animation."""
        if not self.is_visible:
            return
        
        try:
            # Get current progress and increment
            current_progress = getattr(self, '_current_progress', 0)
            new_progress = min(100, current_progress + 1.5)  # Smooth increment
            self._current_progress = new_progress
            
            # Draw progress bar
            self._draw_progress_bar(new_progress)
        except Exception as e:
            # If there's any error, just set progress to 0
            self._current_progress = 0
            self._draw_progress_bar(0)
        
        # Continue animation
        if self.is_visible:
            self.after(60, self._animate_progress)  # Update every 60ms for smoother animation
    
    def _hide_notification(self):
        """Hide the notification."""
        self.is_visible = False
        self.destroy()

class NotificationWidget(tk.Toplevel):
    """Legacy notification widget for backward compatibility."""
    
    def __init__(self, parent, message: str, notification_type: str = "info", duration: int = 3000):
        super().__init__(parent)
        self.message = message
        self.notification_type = notification_type
        self.duration = duration
        
        self.title("")
        self.geometry("300x60")
        self.resizable(False, False)
        self.overrideredirect(True)
        
        # Make it stay on top
        self.attributes("-topmost", True)
        
        self._create_widgets()
        self._position_window()
        self._start_timer()
    
    def _create_widgets(self):
        # Configure colors based on type
        colors = {
            "info": {"bg": "#3b82f6", "fg": "white"},
            "success": {"bg": "#10b981", "fg": "white"},
            "warning": {"bg": "#f59e0b", "fg": "white"},
            "error": {"bg": "#ef4444", "fg": "white"}
        }
        
        color_config = colors.get(self.notification_type, colors["info"])
        
        # Main frame
        main_frame = tk.Frame(self, bg=color_config["bg"], relief="flat", borderwidth=1)
        main_frame.pack(fill="both", expand=True, padx=2, pady=2)
        
        # Message label
        message_label = tk.Label(
            main_frame,
            text=self.message,
            font=FONTS["primary"],
            bg=color_config["bg"],
            fg=color_config["fg"],
            wraplength=280
        )
        message_label.pack(expand=True, fill="both", padx=12, pady=8)
        
        # Modern close button
        close_btn = ModernCloseButton(
            main_frame,
            bg=color_config["bg"],
            fg=color_config["fg"],
            hover_bg=color_config["border"],
            hover_fg=color_config["fg"],
            command=self.destroy
        )
        close_btn.pack(side="right", padx=8)
    
    def _position_window(self):
        """Position the notification in the top-right corner."""
        self.update_idletasks()
        
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        
        x = screen_width - 320
        y = 20
        
        self.geometry(f"+{x}+{y}")
    
    def _start_timer(self):
        """Start the auto-close timer."""
        self.after(self.duration, self.destroy)

class LoadingSpinner(tk.Canvas):
    """Loading spinner widget."""
    
    def __init__(self, parent, size: int = 40, **kwargs):
        super().__init__(parent, width=size, height=size, **kwargs)
        self.size = size
        self.angle = 0
        self.is_spinning = False
        
        self.configure(bg="white", highlightthickness=0)
        self._draw_spinner()
    
    def _draw_spinner(self):
        """Draw the spinner."""
        center = self.size // 2
        radius = (self.size // 2) - 4
        
        # Clear canvas
        self.delete("all")
        
        # Draw spinner segments
        for i in range(8):
            angle = self.angle + (i * 45)
            start_angle = angle
            end_angle = angle + 30
            
            # Calculate opacity based on position
            opacity = 1.0 - (i * 0.1)
            if opacity < 0.1:
                opacity = 0.1
            
            # Convert angle to radians
            start_rad = math.radians(start_angle)
            end_rad = math.radians(end_angle)
            
            # Calculate coordinates
            x1 = center + radius * math.cos(start_rad)
            y1 = center + radius * math.sin(start_rad)
            x2 = center + radius * math.cos(end_rad)
            y2 = center + radius * math.sin(end_rad)
            
            # Draw arc
            self.create_arc(
                center - radius, center - radius,
                center + radius, center + radius,
                start=start_angle, extent=30,
                fill=f"#{int(59 * opacity):02x}{int(130 * opacity):02x}{int(246 * opacity):02x}",
                outline=""
            )
    
    def start(self):
        """Start the spinner animation."""
        self.is_spinning = True
        self._animate()
    
    def stop(self):
        """Stop the spinner animation."""
        self.is_spinning = False
    
    def _animate(self):
        """Animate the spinner."""
        if self.is_spinning:
            self.angle = (self.angle + 10) % 360
            self._draw_spinner()
            self.after(50, self._animate)

class ModernCloseButton(tk.Canvas):
    """Modern minimalist close button with hover effects."""
    
    def __init__(self, parent, bg="#ffffff", fg="#666666", hover_bg="#ff4757", 
                 hover_fg="#ffffff", size=24, command=None, **kwargs):
        super().__init__(parent, width=size, height=size, **kwargs)
        
        self.bg = bg
        self.fg = fg
        self.hover_bg = hover_bg
        self.hover_fg = hover_fg
        self.size = size
        self.command = command
        self.is_hovered = False
        
        # Configure canvas
        self.configure(
            bg=bg,
            highlightthickness=0,
            relief="flat",
            cursor="hand2"
        )
        
        # Bind events
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<Button-1>", self._on_click)
        self.bind("<ButtonRelease-1>", self._on_release)
        
        # Draw initial state
        self._draw_button()
    
    def _draw_button(self):
        """Draw the close button."""
        self.delete("all")
        
        # Determine colors based on hover state
        bg_color = self.hover_bg if self.is_hovered else self.bg
        fg_color = self.hover_fg if self.is_hovered else self.fg
        
        # Handle transparent background
        if bg_color == "transparent":
            # Get parent background color
            try:
                parent_bg = self.master.cget("bg")
                bg_color = parent_bg if parent_bg else "#ffffff"
            except:
                bg_color = "#ffffff"
        
        # Draw background circle
        padding = 2
        self.create_oval(
            padding, padding,
            self.size - padding, self.size - padding,
            fill=bg_color,
            outline="",
            tags="background"
        )
        
        # Draw X icon
        icon_padding = 6
        # First diagonal line
        self.create_line(
            icon_padding, icon_padding,
            self.size - icon_padding, self.size - icon_padding,
            fill=fg_color,
            width=2,
            capstyle="round",
            tags="icon"
        )
        # Second diagonal line
        self.create_line(
            self.size - icon_padding, icon_padding,
            icon_padding, self.size - icon_padding,
            fill=fg_color,
            width=2,
            capstyle="round",
            tags="icon"
        )
    
    def _on_enter(self, event):
        """Handle mouse enter event."""
        self.is_hovered = True
        self._draw_button()
        
        # Add subtle scale animation
        self.scale("all", self.size/2, self.size/2, 1.1, 1.1)
    
    def _on_leave(self, event):
        """Handle mouse leave event."""
        self.is_hovered = False
        self._draw_button()
        
        # Reset scale
        self.scale("all", self.size/2, self.size/2, 1.0, 1.0)
    
    def _on_click(self, event):
        """Handle click event."""
        # Add click animation
        self.scale("all", self.size/2, self.size/2, 0.95, 0.95)
    
    def _on_release(self, event):
        """Handle button release event."""
        # Reset scale
        self.scale("all", self.size/2, self.size/2, 1.0, 1.0)
        
        # Execute command
        if self.command:
            self.command()
    
    def configure(self, **kwargs):
        """Configure button properties."""
        if "bg" in kwargs:
            self.bg = kwargs["bg"]
        if "fg" in kwargs:
            self.fg = kwargs["fg"]
        if "hover_bg" in kwargs:
            self.hover_bg = kwargs["hover_bg"]
        if "hover_fg" in kwargs:
            self.hover_fg = kwargs["hover_fg"]
        if "command" in kwargs:
            self.command = kwargs["command"]
        
        # Redraw with new colors
        self._draw_button()
        
        # Call parent configure
        super().configure(**kwargs) 