"""
Modern main window for the Task Tracker application.
"""
import tkinter as tk
from tkinter import ttk
from tkinter import simpledialog
from tkinter import messagebox
import ttkbootstrap as tb
from typing import Optional, Dict, Any
from datetime import datetime
import threading
import time

from database import db_manager
from utils import show_error_dialog, show_info_dialog
from ui.components import ModernNotificationWidget, NotificationWidget
from ui.components import ModernButton, ModernEntry, LoadingSpinner
from ui.task_dialog import TaskDialog
from ui.task_table import ModernTaskTable
from ui.theme_manager import ThemeManager
from config import APP_NAME, APP_VERSION, DEFAULT_WINDOW_SIZE, MIN_WINDOW_SIZE, FONTS

class MainWindow:
    """Modern main application window."""
    
    def __init__(self, root: tb.Window):
        self.root = root
        self.current_project = ""
        self.tasks = []
        self.is_loading = False
        
        # Setup window
        self._setup_window()
        
        # Initialize theme manager
        self.theme_manager = ThemeManager(root)
        
        # Initialize database
        self._init_database()
        
        # Create UI
        self._create_widgets()
        
        # Select project with the last created task if any, and refresh UI
        last_project = self._get_last_task_project()
        if last_project:
            self.current_project = last_project
        self._refresh_project_dropdown(self.project_combo.master)
        self._load_tasks()
        
        # Start background tasks
        self._start_background_tasks()
    
    def _setup_window(self):
        """Setup the main window."""
        self.root.title(f"{APP_NAME} v{APP_VERSION}")
        self.root.geometry(DEFAULT_WINDOW_SIZE)
        self.root.minsize(800, 600)
        
        # Configure window icon and properties
        self.root.attributes("-alpha", 0.0)  # Start transparent for fade-in effect
        
        # Bind window events
        self.root.bind("<Control-n>", lambda e: self._add_task())
        self.root.bind("<Control-f>", lambda e: self._focus_search())
        self.root.bind("<Control-t>", lambda e: self.theme_manager.switch_theme())
        self.root.bind("<F5>", lambda e: self._refresh_data())
        
        # Fade in effect
        self._fade_in()
    
    def _fade_in(self):
        """Fade in the window."""
        def fade_step(step=0):
            if step <= 20:
                alpha = step / 20
                self.root.attributes("-alpha", alpha)
                self.root.after(20, lambda: fade_step(step + 1))
        
        fade_step()
    
    def _init_database(self):
        """Initialize database connection."""
        try:
            # Database is already initialized in database.py
            pass
        except Exception as e:
            show_error_dialog(self.root, "Database Error", f"Failed to initialize database: {e}")
    
    def _create_widgets(self):
        """Create the main window widgets."""
        # Main container
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill="both", expand=True)
        
        # Header
        self._create_header()
        
        # Content area
        self._create_content()
        
        # Status bar
        self._create_status_bar()
    
    def _create_header(self):
        """Create the application header."""
        header_frame = ttk.Frame(self.main_frame, style="Card.TFrame")
        header_frame.pack(fill="x", padx=16, pady=16)
        
        # Left side - Title and project selector
        left_frame = ttk.Frame(header_frame)
        left_frame.pack(side="left", fill="y", padx=16, pady=12)
        
        # App title
        title_label = ttk.Label(
            left_frame,
            text=APP_NAME,
            font=FONTS["title"],
            foreground="#1f2937"
        )
        title_label.pack(anchor="w")
        
        # Project selector
        project_frame = ttk.Frame(left_frame)
        project_frame.pack(fill="x", pady=(8, 0))
        
        ttk.Label(project_frame, text="Project:", font=FONTS["secondary"]).pack(side="left")
        
        self.project_var = tk.StringVar(value=self.current_project)
        self._refresh_project_dropdown(project_frame)
        
        # Add delete button for project
        delete_btn = ModernButton(
            project_frame,
            text="🗑️",
            command=self._delete_project,
            primary=False
        )
        delete_btn.pack(side="left", padx=(8, 0))
        self.delete_project_btn = delete_btn
        
        # Right side - Actions
        right_frame = ttk.Frame(header_frame)
        right_frame.pack(side="right", fill="y", padx=16, pady=12)
        
        # Theme toggle button
        self.theme_btn = self.theme_manager.create_theme_button(right_frame)
        self.theme_btn.pack(side="right", padx=(8, 0))
        
        # Add task button
        add_btn = ModernButton(
            right_frame,
            text="+ Add Task",
            primary=True,
            command=self._add_task
        )
        add_btn.pack(side="right")
        
        # Refresh button
        refresh_btn = ModernButton(
            right_frame,
            text="🔄",
            command=self._refresh_data
        )
        refresh_btn.pack(side="right", padx=(8, 0))
    
    def _create_content(self):
        """Create the main content area."""
        content_frame = ttk.Frame(self.main_frame)
        content_frame.pack(fill="both", expand=True, padx=16, pady=(0, 16))
        
        # Notification area (top of content)
        self.notification_area = ttk.Frame(content_frame)
        self.notification_area.pack(fill="x", pady=(0, 16))
        
        # Loading indicator
        self.loading_frame = ttk.Frame(content_frame)
        self.loading_frame.pack(fill="both", expand=True)
        
        self.loading_spinner = LoadingSpinner(self.loading_frame, size=60)
        self.loading_spinner.pack(expand=True)
        
        loading_label = ttk.Label(
            self.loading_frame,
            text="Loading tasks...",
            font=FONTS["primary"]
        )
        loading_label.pack(pady=(16, 0))
        
        # Task table (initially hidden)
        self.task_table = ModernTaskTable(
            content_frame,
            on_task_click=self._edit_task,
            on_task_delete=self._delete_task,
            on_task_toggle=self._toggle_task
        )
    
    def _create_status_bar(self):
        """Create the status bar."""
        self.status_frame = ttk.Frame(self.main_frame)
        self.status_frame.pack(fill="x", side="bottom", padx=16, pady=(0, 8))
        
        # Status label
        self.status_label = ttk.Label(
            self.status_frame,
            text="Ready",
            font=FONTS["secondary"],
            foreground="#6b7280"
        )
        self.status_label.pack(side="left")
        
        # Last updated
        self.last_updated_label = ttk.Label(
            self.status_frame,
            text="",
            font=FONTS["secondary"],
            foreground="#6b7280"
        )
        self.last_updated_label.pack(side="right")
    
    def _load_tasks(self):
        """Load tasks from database."""
        self._show_loading(True)
        
        def load_tasks_async():
            try:
                tasks = db_manager.get_tasks(project=self.current_project)
                # Use after_idle for safer thread communication
                self.root.after_idle(lambda: self._on_tasks_loaded(tasks))
            except Exception as e:
                self.root.after_idle(lambda: self._on_load_error(str(e)))
        
        threading.Thread(target=load_tasks_async, daemon=True).start()
    
    def _on_tasks_loaded(self, tasks):
        """Handle tasks loaded successfully."""
        self.tasks = tasks
        self._show_loading(False)
        self.task_table.set_tasks(tasks)
        self._update_status(f"Loaded {len(tasks)} tasks")
        self._update_last_updated()
    
    def _on_load_error(self, error_message):
        """Handle task loading error."""
        self._show_loading(False)
        show_error_dialog(self.root, "Load Error", f"Failed to load tasks: {error_message}")
        self._update_status("Error loading tasks")
    
    def _show_loading(self, show: bool):
        """Show or hide loading indicator."""
        self.is_loading = show
        
        if show:
            self.loading_frame.pack(fill="both", expand=True)
            self.task_table.pack_forget()
            self.loading_spinner.start()
        else:
            self.loading_frame.pack_forget()
            self.task_table.pack(fill="both", expand=True)
            self.loading_spinner.stop()
    
    def _add_task(self):
        """Add a new task."""
        dialog = TaskDialog(
            self.root,
            on_save=self._save_task
        )
        
        if dialog.result:
            self._refresh_data()
            self._show_notification("Task created successfully!", "success")
    
    def _edit_task(self, task: Dict[str, Any]):
        """Edit an existing task."""
        dialog = TaskDialog(
            self.root,
            task_data=task,
            on_save=self._update_task
        )
        
        if dialog.result:
            self._refresh_data()
            self._show_notification("Task updated successfully!", "success")
    
    def _save_task(self, task_data: Dict[str, Any]):
        """Save a new task."""
        try:
            task_data['project'] = self.current_project
            task_id = db_manager.add_task(task_data)
            
            if task_id:
                self._refresh_data()
            else:
                show_error_dialog(self.root, "Save Error", "Failed to save task")
        except Exception as e:
            show_error_dialog(self.root, "Save Error", f"Failed to save task: {e}")
    
    def _update_task(self, task_data: Dict[str, Any]):
        """Update an existing task."""
        try:
            task_id = task_data.get('id')
            if not task_id:
                show_error_dialog(self.root, "Update Error", "Task ID not found")
                return
            
            # Remove id from data to avoid updating it
            update_data = {k: v for k, v in task_data.items() if k != 'id'}
            
            success = db_manager.update_task(task_id, **update_data)
            
            if success:
                self._refresh_data()
            else:
                show_error_dialog(self.root, "Update Error", "Failed to update task")
        except Exception as e:
            show_error_dialog(self.root, "Update Error", f"Failed to update task: {e}")
    
    def _delete_task(self, task_id: int):
        """Delete a task."""
        try:
            success = db_manager.delete_task(task_id)
            
            if success:
                self._refresh_data()
                self._show_notification("Task deleted successfully!", "info")
            else:
                show_error_dialog(self.root, "Delete Error", "Failed to delete task")
        except Exception as e:
            show_error_dialog(self.root, "Delete Error", f"Failed to delete task: {e}")
    
    def _toggle_task(self, task_id: int, completed: bool):
        """Toggle task completion status."""
        try:
            update_data = {
                'completed': completed,
                'status': 'Done' if completed else 'Working on it'
            }
            
            if completed:
                update_data['completed_date'] = datetime.now().strftime("%Y-%m-%d")
            else:
                update_data['completed_date'] = None
            
            success = db_manager.update_task(task_id, **update_data)
            
            if success:
                self._refresh_data()
                status = "completed" if completed else "uncompleted"
                status_text = "completed" if completed else "in progress"
                self._show_notification(f"Task marked as {status_text}!", "info")
            else:
                show_error_dialog(self.root, "Update Error", "Failed to update task")
        except Exception as e:
            show_error_dialog(self.root, "Update Error", f"Failed to update task: {e}")
    
    def _refresh_project_dropdown(self, project_frame):
        # Remove old combobox if it exists
        if hasattr(self, 'project_combo'):
            current_value = self.project_var.get()
            self.project_combo.destroy()
        else:
            current_value = self.current_project
        projects = [p["name"] for p in db_manager.get_projects()]
        # Do not append current_value if not in projects; only show real projects
        projects = sorted(set(projects))
        projects.append("+ Add Project...")
        self.project_combo = ttk.Combobox(
            project_frame,
            textvariable=self.project_var,
            values=projects,
            state="readonly" if projects else "disabled",
            width=15,
            font=FONTS["secondary"]
        )
        self.project_combo.pack(side="left", padx=(8, 0))
        self.project_combo.bind("<<ComboboxSelected>>", self._on_project_change)
        # Restore selection (case-insensitive match)
        if self.current_project:
            for proj in projects:
                if proj.lower() == self.current_project.lower():
                    self.project_var.set(proj)
                    self.current_project = proj
                    break
            else:
                if projects:
                    self.project_var.set(projects[0])
                    self.current_project = projects[0]
                else:
                    self.project_var.set("")
                    self.current_project = ""
        elif projects:
            self.project_var.set(projects[0])
            self.current_project = projects[0]
        else:
            self.project_var.set("")
            self.current_project = ""
        # Disable delete button if no projects
        if hasattr(self, 'delete_project_btn'):
            if not projects:
                self.delete_project_btn.config(state="disabled")
            else:
                self.delete_project_btn.config(state="normal")

    def _on_project_change(self, event=None):
        """Handle project change."""
        new_project = self.project_var.get()
        if new_project == "+ Add Project...":
            # Prompt for new project name
            new_name = simpledialog.askstring("New Project", "Enter new project name:")
            if new_name:
                # Add to database
                db_manager.add_project({"name": new_name})
                self.current_project = new_name
                self.project_var.set(new_name)
                self._refresh_project_dropdown(self.project_combo.master)
                self._load_tasks()
            else:
                # Reset to previous project
                self.project_var.set(self.current_project)
        elif new_project != self.current_project:
            self.current_project = new_project
            self._load_tasks()
    
    def _delete_project(self):
        project = self.project_var.get()
        if project == "+ Add Project...":
            return
        if not project:
            return
        confirm = messagebox.askyesnocancel("Delete Project", f"Do you want to permanently delete the project '{project}' and all its tasks? (Yes = permanent, No = hide, Cancel = abort)")
        if confirm is None:
            return  # Cancelled
        if confirm:
            # Permanent delete
            success = db_manager.delete_project_permanently(project)
            if success:
                projects = [p["name"] for p in db_manager.get_projects()]
                if projects:
                    self.current_project = projects[0]
                else:
                    self.current_project = "learning"
                self.project_var.set(self.current_project)
                self._refresh_project_dropdown(self.delete_project_btn.master)
                self._load_tasks()
                self._show_notification(f"Project '{project}' and all its data permanently deleted.", "info")
            else:
                self._show_notification(f"Failed to permanently delete project '{project}'.", "error")
        else:
            # Soft delete (hide)
            success = db_manager.delete_project(project)
            if success:
                projects = [p["name"] for p in db_manager.get_projects()]
                if projects:
                    self.current_project = projects[0]
                else:
                    self.current_project = "learning"
                self.project_var.set(self.current_project)
                self._refresh_project_dropdown(self.delete_project_btn.master)
                self._load_tasks()
                self._show_notification(f"Project '{project}' hidden.", "info")
            else:
                self._show_notification(f"Failed to delete project '{project}'.", "error")
    
    def _refresh_data(self):
        """Refresh all data."""
        self._load_tasks()
        self._update_status("Data refreshed")
    
    def _focus_search(self):
        """Focus on the search entry."""
        if hasattr(self.task_table, 'search_entry'):
            self.task_table.search_entry.focus_set()
    
    def _update_status(self, message: str):
        """Update status bar message."""
        self.status_label.configure(text=message)
    
    def _update_last_updated(self):
        """Update last updated timestamp."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.last_updated_label.configure(text=f"Last updated: {timestamp}")
    
    def _show_notification(self, message: str, notification_type: str = "info"):
        """Show a modern integrated notification."""
        # Clear any existing notifications
        for widget in self.notification_area.winfo_children():
            widget.destroy()
        
        # Create and show new notification
        notification = ModernNotificationWidget(
            self.notification_area,
            message,
            notification_type,
            duration=4000
        )
        notification.pack(fill="x", pady=(0, 8))
        
        # Auto-remove notification area if empty
        def check_empty():
            if not self.notification_area.winfo_children():
                self.notification_area.pack_forget()
        
        notification.after(4500, check_empty)
    
    def _start_background_tasks(self):
        """Start background tasks like checking for overdue tasks."""
        def check_overdue_tasks():
            try:
                overdue_tasks = db_manager.get_overdue_tasks()
                if overdue_tasks:
                    count = len(overdue_tasks)
                    self._show_notification(
                        f"You have {count} overdue task{'s' if count > 1 else ''}!",
                        "warning"
                    )
            except Exception:
                pass
            
            # Check again in 1 hour
            self.root.after(3600000, check_overdue_tasks)
        
        # Start checking after 5 minutes
        self.root.after(300000, check_overdue_tasks)
    
    def get_current_project(self) -> str:
        """Get the current project name."""
        return self.current_project
    
    def set_current_project(self, project: str):
        """Set the current project."""
        self.current_project = project
        self.project_var.set(project)
        self._load_tasks() 

    def _get_last_task_project(self):
        """Return the project name of the task with the highest id, or None if no tasks exist."""
        try:
            tasks = db_manager.get_tasks()
            if not tasks:
                return None
            # Get the task with the highest id
            last_task = max(tasks, key=lambda t: t.get('id', 0))
            return last_task.get('project')
        except Exception:
            return None 