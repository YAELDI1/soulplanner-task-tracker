"""
Utility functions for the Task Tracker application.
"""
import re
import time
import threading
from typing import Optional, Callable, Any
from datetime import datetime, timedelta
from tkinter import messagebox
import tkinter as tk

def validate_date(date_string: str) -> bool:
    """Validate date string in YYYY-MM-DD format."""
    if not date_string:
        return True  # Empty dates are allowed
    
    try:
        datetime.strptime(date_string, "%Y-%m-%d")
        return True
    except ValueError:
        return False

def validate_email(email: str) -> bool:
    """Validate email address format."""
    if not email:
        return True  # Empty emails are allowed
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def format_date(date_string: str, format_type: str = "short") -> str:
    """Format date string for display."""
    if not date_string:
        return ""
    
    try:
        date_obj = datetime.strptime(date_string, "%Y-%m-%d")
        
        if format_type == "short":
            return date_obj.strftime("%b %d")
        elif format_type == "long":
            return date_obj.strftime("%B %d, %Y")
        elif format_type == "relative":
            today = datetime.now().date()
            date_only = date_obj.date()
            
            if date_only == today:
                return "Today"
            elif date_only == today + timedelta(days=1):
                return "Tomorrow"
            elif date_only == today - timedelta(days=1):
                return "Yesterday"
            elif date_only < today:
                days_ago = (today - date_only).days
                return f"{days_ago} days ago"
            else:
                days_until = (date_only - today).days
                return f"In {days_until} days"
        else:
            return date_string
    except ValueError:
        return date_string

def is_overdue(date_string) -> bool:
    """Check if a date is overdue."""
    if not date_string:
        return False
    
    try:
        due_date = datetime.strptime(date_string, "%Y-%m-%d").date()
        return due_date < datetime.now().date()
    except ValueError:
        return False

def truncate_text(text: str, max_length: int = 50) -> str:
    """Truncate text to specified length with ellipsis."""
    if not text:
        return ""
    
    if len(text) <= max_length:
        return text
    
    return text[:max_length-3] + "..."

def sanitize_filename(filename: str) -> str:
    """Sanitize filename by removing invalid characters."""
    # Remove or replace invalid characters
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    
    # Remove leading/trailing spaces and dots
    filename = filename.strip(' .')
    
    return filename

def show_error_dialog(parent, title: str, message: str):
    """Show error dialog."""
    messagebox.showerror(title, message, parent=parent)

def show_info_dialog(parent, title: str, message: str):
    """Show info dialog."""
    messagebox.showinfo(title, message, parent=parent)

def show_confirm_dialog(parent, title: str, message: str) -> bool:
    """Show confirmation dialog and return user choice."""
    return messagebox.askyesno(title, message, parent=parent)

def animate_widget(widget: tk.Widget, animation_type: str = "fade_in", duration: int = 200):
    """Animate a widget with various effects."""
    if animation_type == "fade_in":
        widget.attributes("-alpha", 0.0)
        
        def fade_in_step(step=0, total_steps=20):
            if step <= total_steps:
                alpha = step / total_steps
                widget.attributes("-alpha", alpha)
                widget.after(duration // total_steps, lambda: fade_in_step(step + 1, total_steps))
        
        fade_in_step()
    
    elif animation_type == "fade_out":
        def fade_out_step(step=0, total_steps=20):
            if step <= total_steps:
                alpha = 1.0 - (step / total_steps)
                widget.attributes("-alpha", alpha)
                if step == total_steps:
                    widget.destroy()
                else:
                    widget.after(duration // total_steps, lambda: fade_out_step(step + 1, total_steps))
        
        fade_out_step()

def debounce(func: Callable, delay: int = 300):
    """Debounce function calls to prevent excessive execution."""
    timer = None
    
    def debounced(*args, **kwargs):
        nonlocal timer
        if timer:
            timer.cancel()
        timer = threading.Timer(delay / 1000.0, lambda: func(*args, **kwargs))
        timer.start()
    
    return debounced

def throttle(func: Callable, delay: int = 100):
    """Throttle function calls to limit execution frequency."""
    last_called = 0
    
    def throttled(*args, **kwargs):
        nonlocal last_called
        current_time = time.time() * 1000
        if current_time - last_called >= delay:
            last_called = current_time
            return func(*args, **kwargs)
    
    return throttled

def center_window(window: tk.Toplevel):
    """Center a window on the screen."""
    window.update_idletasks()
    width = window.winfo_width()
    height = window.winfo_height()
    x = (window.winfo_screenwidth() // 2) - (width // 2)
    y = (window.winfo_screenheight() // 2) - (height // 2)
    window.geometry(f"{width}x{height}+{x}+{y}")

def create_tooltip(widget: tk.Widget, text: str, delay: int = 500):
    """Create a tooltip for a widget."""
    tooltip = None
    
    def show_tooltip(event):
        nonlocal tooltip
        if tooltip:
            tooltip.destroy()
        
        tooltip = tk.Toplevel()
        tooltip.wm_overrideredirect(True)
        tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
        
        label = tk.Label(tooltip, text=text, 
                        background="#2d3748", foreground="white",
                        relief="solid", borderwidth=1,
                        font=("Segoe UI", 9))
        label.pack(padx=4, pady=2)
    
    def hide_tooltip(event):
        nonlocal tooltip
        if tooltip:
            tooltip.destroy()
            tooltip = None
    
    widget.bind("<Enter>", lambda e: widget.after(delay, lambda: show_tooltip(e)))
    widget.bind("<Leave>", hide_tooltip)
    widget.bind("<Button-1>", hide_tooltip)

def format_duration(minutes: int) -> str:
    """Format duration in minutes to human-readable string."""
    if minutes < 60:
        return f"{minutes}m"
    elif minutes < 1440:  # Less than 24 hours
        hours = minutes // 60
        remaining_minutes = minutes % 60
        if remaining_minutes == 0:
            return f"{hours}h"
        else:
            return f"{hours}h {remaining_minutes}m"
    else:
        days = minutes // 1440
        remaining_hours = (minutes % 1440) // 60
        if remaining_hours == 0:
            return f"{days}d"
        else:
            return f"{days}d {remaining_hours}h"

def parse_duration(duration_str: str) -> Optional[int]:
    """Parse human-readable duration string to minutes."""
    if not duration_str:
        return None
    
    duration_str = duration_str.lower().strip()
    total_minutes = 0
    
    # Match patterns like "2h 30m", "1d 5h", "45m", etc.
    patterns = [
        (r'(\d+)\s*d', lambda x: int(x) * 1440),  # days
        (r'(\d+)\s*h', lambda x: int(x) * 60),    # hours
        (r'(\d+)\s*m', lambda x: int(x))          # minutes
    ]
    
    for pattern, converter in patterns:
        match = re.search(pattern, duration_str)
        if match:
            total_minutes += converter(match.group(1))
    
    return total_minutes if total_minutes > 0 else None

def get_priority_color(priority: str) -> str:
    """Get color for priority level."""
    priority_colors = {
        "Low": "#10b981",      # Green
        "Medium": "#f59e0b",   # Yellow
        "High": "#ef4444",     # Red
        "Urgent": "#dc2626"    # Dark red
    }
    return priority_colors.get(priority, "#6b7280")

def validate_task_data(data: dict) -> tuple[bool, str]:
    """Validate task data and return (is_valid, error_message)."""
    errors = []
    
    # Title validation
    title = data.get('title', '').strip()
    if not title:
        errors.append("Task title is required")
    elif len(title) > 100:
        errors.append("Task title must be 100 characters or less")
    
    # Due date validation
    due_date = data.get('due_date', '').strip()
    if due_date and not validate_date(due_date):
        errors.append("Invalid due date format. Use YYYY-MM-DD (e.g., 2024-12-31)")
    
    # Owner validation
    owner = data.get('owner', '').strip()
    if owner and len(owner) > 50:
        errors.append("Owner name must be 50 characters or less")
    
    # Estimated hours validation
    estimated_hours = data.get('estimated_hours')
    if estimated_hours is not None:
        try:
            hours = float(estimated_hours)
            if hours < 0:
                errors.append("Estimated hours must be a positive number")
            elif hours > 1000:
                errors.append("Estimated hours must be 1000 or less")
        except (ValueError, TypeError):
            errors.append("Estimated hours must be a valid number")
    
    # Notes validation
    notes = data.get('notes', '').strip()
    if notes and len(notes) > 1000:
        errors.append("Notes must be 1000 characters or less")
    
    # Tags validation
    tags = data.get('tags', '').strip()
    if tags and len(tags) > 200:
        errors.append("Tags must be 200 characters or less")
    
    if errors:
        return False, "\n".join(f"• {error}" for error in errors)
    
    return True, "" 