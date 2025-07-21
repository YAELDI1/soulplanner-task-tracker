"""
Modern task table component with enhanced functionality.
"""
import tkinter as tk
from tkinter import ttk
import ttkbootstrap as tb
from typing import List, Dict, Any, Optional, Callable
from datetime import datetime
import math
from collections import Counter
from utils import format_date, is_overdue, truncate_text, show_confirm_dialog
from ui.components import SearchEntry, StatusPill, PriorityBadge, NotificationWidget
from config import FONTS, STATUS_COLORS, TASK_STATUSES
from ui.components import ModernEntry

class ModernTaskTable(ttk.Frame):
    """Modern task table with search, filtering, and enhanced functionality."""
    
    def __init__(self, parent, on_task_click: Optional[Callable] = None,
                 on_task_delete: Optional[Callable] = None,
                 on_task_toggle: Optional[Callable] = None):
        super().__init__(parent)
        
        self.on_task_click = on_task_click
        self.on_task_delete = on_task_delete
        self.on_task_toggle = on_task_toggle
        
        self.tasks = []
        self.filtered_tasks = []
        self.search_term = ""
        self.status_filter = None
        self.priority_filter = None
        self.sort_column = "created_date"
        self.sort_reverse = True
        
        self._create_widgets()
        self._setup_bindings()
    
    def _create_widgets(self):
        """Create the table widgets."""
        # Search and filter bar
        self._create_search_bar()
        
        # Table container
        table_container = ttk.Frame(self)
        table_container.pack(fill="both", expand=True, pady=(16, 0))
        
        # Create treeview
        columns = ("checkbox", "title", "owner", "status", "priority", "due_date", "estimated", "actions")
        self.tree = ttk.Treeview(
            table_container,
            columns=columns,
            show="headings",
            height=15,
            style="Modern.Treeview"
        )
        
        # Configure columns
        self._configure_columns(columns)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(table_container, orient="vertical", command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(table_container, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Grid layout
        self.tree.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")
        
        table_container.grid_rowconfigure(0, weight=1)
        table_container.grid_columnconfigure(0, weight=1)
        
        # Statistics bar
        self._create_statistics_bar()
    
    def _create_search_bar(self):
        """Create search and filter controls."""
        search_frame = ttk.Frame(self)
        search_frame.pack(fill="x", pady=(0, 16))
        
        # Search entry
        self.search_entry = SearchEntry(
            search_frame,
            on_search=self._on_search
        )
        self.search_entry.pack(side="left", fill="x", expand=True, padx=(0, 16))
        
        # Date filter
        date_filter_frame = ttk.Frame(search_frame)
        date_filter_frame.pack(side="left", padx=(0, 8))
        ttk.Label(date_filter_frame, text="Date:", font=FONTS["secondary"]).pack(side="left")
        self.date_filter_var = tk.StringVar(value="Today")
        date_filter_combo = ttk.Combobox(
            date_filter_frame,
            textvariable=self.date_filter_var,
            values=["Today", "Range", "Year", "Custom", "All"],
            state="readonly",
            width=8,
            font=FONTS["secondary"]
        )
        date_filter_combo.pack(side="left", padx=(4, 0))
        date_filter_combo.bind("<<ComboboxSelected>>", self._on_filter_change)
        # Date range entries
        self.date_from_entry = ModernEntry(date_filter_frame, placeholder="From (YYYY-MM-DD)", width=14)
        self.date_to_entry = ModernEntry(date_filter_frame, placeholder="To (YYYY-MM-DD)", width=14)
        self.date_custom_entry = ModernEntry(date_filter_frame, placeholder="Date (YYYY-MM-DD)", width=14)
        self.date_from_entry.pack_forget()
        self.date_to_entry.pack_forget()
        self.date_custom_entry.pack_forget()
        # Show/hide date entries based on filter
        def update_date_entries(*args):
            for w in [self.date_from_entry, self.date_to_entry, self.date_custom_entry]:
                w.pack_forget()
            if self.date_filter_var.get() == "Range":
                self.date_from_entry.pack(side="left", padx=(4, 0))
                self.date_to_entry.pack(side="left", padx=(4, 0))
            elif self.date_filter_var.get() == "Custom":
                self.date_custom_entry.pack(side="left", padx=(4, 0))
        self.date_filter_var.trace_add('write', lambda *a: update_date_entries())
        update_date_entries()
        
        # Status filter
        status_frame = ttk.Frame(search_frame)
        status_frame.pack(side="left", padx=(0, 8))
        
        ttk.Label(status_frame, text="Status:", font=FONTS["secondary"]).pack(side="left")
        
        self.status_var = tk.StringVar(value="All")
        status_combo = ttk.Combobox(
            status_frame,
            textvariable=self.status_var,
            values=["All"] + TASK_STATUSES,
            state="readonly",
            width=12,
            font=FONTS["secondary"]
        )
        status_combo.pack(side="left", padx=(4, 0))
        status_combo.bind("<<ComboboxSelected>>", self._on_filter_change)
        
        # Priority filter
        priority_frame = ttk.Frame(search_frame)
        priority_frame.pack(side="left", padx=(0, 8))
        
        ttk.Label(priority_frame, text="Priority:", font=FONTS["secondary"]).pack(side="left")
        
        self.priority_var = tk.StringVar(value="All")
        priority_combo = ttk.Combobox(
            priority_frame,
            textvariable=self.priority_var,
            values=["All", "Low", "Medium", "High", "Urgent"],
            state="readonly",
            width=10,
            font=FONTS["secondary"]
        )
        priority_combo.pack(side="left", padx=(4, 0))
        priority_combo.bind("<<ComboboxSelected>>", self._on_filter_change)
        
        # Clear filters button
        clear_btn = ttk.Button(
            search_frame,
            text="Clear Filters",
            style="Modern.Secondary.TButton",
            command=self._clear_filters
        )
        clear_btn.pack(side="right")
    
    def _configure_columns(self, columns):
        """Configure table columns."""
        headers = {
            "checkbox": "",
            "title": "Task",
            "owner": "Owner",
            "status": "Status",
            "priority": "Priority",
            "due_date": "Due Date",
            "estimated": "Est. Hours",
            "actions": ""
        }
        
        widths = {
            "checkbox": 40,
            "title": 300,
            "owner": 100,
            "status": 120,
            "priority": 80,
            "due_date": 100,
            "estimated": 80,
            "actions": 80
        }
        
        for col in columns:
            self.tree.heading(col, text=headers[col], command=lambda c=col: self._sort_by_column(c))
            self.tree.column(col, width=widths[col], anchor="center")
        
        # Make title column stretchable
        self.tree.column("title", stretch=True)
    
    def _create_statistics_bar(self):
        """Create statistics display bar."""
        self.stats_frame = ttk.Frame(self)
        self.stats_frame.pack(fill="x", pady=(16, 0))
        
        # Statistics labels
        self.total_label = ttk.Label(self.stats_frame, text="Total: 0", font=FONTS["secondary"])
        self.total_label.pack(side="left", padx=(0, 16))
        
        self.completed_label = ttk.Label(self.stats_frame, text="Completed: 0", font=FONTS["secondary"])
        self.completed_label.pack(side="left", padx=(0, 16))
        
        self.overdue_label = ttk.Label(self.stats_frame, text="Overdue: 0", font=FONTS["secondary"])
        self.overdue_label.pack(side="left", padx=(0, 16))
        
        # Progress bar
        self.progress_frame = ttk.Frame(self.stats_frame)
        self.progress_frame.pack(side="right")
        
        self.progress_label = ttk.Label(self.progress_frame, text="0%", font=FONTS["secondary"])
        self.progress_label.pack(side="right")
        
        self.progress_bar = ttk.Progressbar(
            self.progress_frame,
            length=100,
            mode="determinate"
        )
        self.progress_bar.pack(side="right", padx=(0, 8))
    
    def _setup_bindings(self):
        """Setup event bindings."""
        self.tree.bind("<Button-1>", self._on_click)
        self.tree.bind("<Double-Button-1>", self._on_double_click)
        self.tree.bind("<Delete>", self._on_delete_key)
        self.tree.bind("<Return>", self._on_enter_key)
        
        # Keyboard navigation
        self.tree.bind("<Up>", self._on_key_navigation)
        self.tree.bind("<Down>", self._on_key_navigation)
        self.tree.bind("<Left>", self._on_key_navigation)
        self.tree.bind("<Right>", self._on_key_navigation)
    
    def set_tasks(self, tasks: List[Dict[str, Any]]):
        """Set tasks and refresh the table."""
        try:
            # Validate tasks data
            if not isinstance(tasks, list):
                print("Warning: tasks must be a list")
                tasks = []
            
            # Filter out invalid tasks
            valid_tasks = []
            for task in tasks:
                if isinstance(task, dict) and 'id' in task:
                    valid_tasks.append(task)
                else:
                    print(f"Warning: Skipping invalid task: {task}")
            
            self.tasks = valid_tasks
            self._apply_filters()
            self._update_statistics()
        except Exception as e:
            print(f"Error setting tasks: {e}")
            self.tasks = []
            self._update_statistics()
    
    def _apply_filters(self):
        """Apply search and filter criteria."""
        self.filtered_tasks = self.tasks.copy()
        
        # Apply search filter
        if self.search_term:
            search_lower = self.search_term.lower()
            self.filtered_tasks = [
                task for task in self.filtered_tasks
                if (search_lower in (task.get('title') or '').lower() or
                    search_lower in (task.get('description') or '').lower() or
                    search_lower in (task.get('notes') or '').lower() or
                    search_lower in (task.get('owner') or '').lower())
            ]
        
        # Apply status filter
        if self.status_filter and self.status_filter != "All":
            self.filtered_tasks = [
                task for task in self.filtered_tasks
                if task.get('status') == self.status_filter
            ]
        
        # Apply priority filter
        if self.priority_filter and self.priority_filter != "All":
            self.filtered_tasks = [
                task for task in self.filtered_tasks
                if task.get('priority') == self.priority_filter
            ]
        
        # Apply date filter
        date_filter = getattr(self, 'date_filter_var', None)
        if date_filter:
            filter_type = self.date_filter_var.get()
            today_str = datetime.now().strftime("%Y-%m-%d")
            if filter_type == "Today":
                self.filtered_tasks = [task for task in self.filtered_tasks if str(task.get('due_date')) == today_str]
            elif filter_type == "Range":
                from_str = self.date_from_entry.get_value()
                to_str = self.date_to_entry.get_value()
                try:
                    from_date = datetime.strptime(from_str, "%Y-%m-%d") if from_str else None
                    to_date = datetime.strptime(to_str, "%Y-%m-%d") if to_str else None
                except Exception:
                    from_date = to_date = None
                def in_range(d):
                    try:
                        dt = datetime.strptime(str(d), "%Y-%m-%d")
                        if from_date and dt < from_date:
                            return False
                        if to_date and dt > to_date:
                            return False
                        return True
                    except Exception:
                        return False
                self.filtered_tasks = [task for task in self.filtered_tasks if in_range(task.get('due_date'))]
            elif filter_type == "Year":
                year = datetime.now().year
                self.filtered_tasks = [task for task in self.filtered_tasks if str(task.get('due_date', '')).startswith(str(year))]
            elif filter_type == "Custom":
                custom_str = self.date_custom_entry.get_value()
                self.filtered_tasks = [task for task in self.filtered_tasks if str(task.get('due_date')) == custom_str]
            # 'All' shows all tasks (no filter)
        
        # Apply sorting
        self._sort_tasks()
        
        # Refresh display
        self._refresh_display()
    
    def _sort_tasks(self):
        """Sort tasks by current sort column."""
        if not self.filtered_tasks:
            return
        
        reverse = self.sort_reverse
        
        try:
            if self.sort_column == "title":
                self.filtered_tasks.sort(key=lambda x: str(x.get('title', '')).lower(), reverse=reverse)
            elif self.sort_column == "owner":
                self.filtered_tasks.sort(key=lambda x: str(x.get('owner', '')).lower(), reverse=reverse)
            elif self.sort_column == "status":
                self.filtered_tasks.sort(key=lambda x: str(x.get('status', '')), reverse=reverse)
            elif self.sort_column == "priority":
                priority_order = {"Low": 1, "Medium": 2, "High": 3, "Urgent": 4}
                self.filtered_tasks.sort(key=lambda x: priority_order.get(str(x.get('priority', 'Medium')), 2), reverse=reverse)
            elif self.sort_column == "due_date":
                self.filtered_tasks.sort(key=lambda x: str(x.get('due_date', '') or '9999-12-31'), reverse=reverse)
            elif self.sort_column == "estimated":
                def safe_float(value):
                    try:
                        if value is None:
                            return 0.0
                        return float(value)
                    except (ValueError, TypeError):
                        return 0.0
                self.filtered_tasks.sort(key=lambda x: safe_float(x.get('estimated_hours')), reverse=reverse)
            else:  # created_date
                self.filtered_tasks.sort(key=lambda x: str(x.get('created_date', '')), reverse=reverse)
        except Exception as e:
            print(f"Error sorting tasks by {self.sort_column}: {e}")
            # Fallback to sorting by title
            self.filtered_tasks.sort(key=lambda x: str(x.get('title', '')).lower(), reverse=False)
    
    def _refresh_display(self):
        """Refresh the table display."""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Add filtered tasks
        for i, task in enumerate(self.filtered_tasks):
            self._insert_task(task, i)
    
    def _insert_task(self, task: Dict[str, Any], index: int):
        """Insert a task into the table."""
        try:
            # Prepare values with safe defaults
            checkbox = "☑" if task.get('completed') else "☐"
            title = truncate_text(str(task.get('title', '')), 40)
            owner = str(task.get('owner', '')) or "—"
            # Show only the value for status and priority (not the enum tag)
            status = task.get('status')
            if status is not None and hasattr(status, 'value'):
                status = status.value
            else:
                status = str(status) if status is not None else 'Not Started'
            priority = task.get('priority')
            if priority is not None and hasattr(priority, 'value'):
                priority = priority.value
            else:
                priority = str(priority) if priority is not None else 'Medium'
            due_date = self._format_due_date(task.get('due_date'))
            
            # Handle estimated hours safely
            estimated_hours = task.get('estimated_hours')
            if estimated_hours is not None:
                try:
                    estimated = f"{float(estimated_hours):.1f}"
                except (ValueError, TypeError):
                    estimated = "—"
            else:
                estimated = "—"
            
            actions = "✏️ 🗑️"
            
            # Insert into treeview
            item = self.tree.insert("", "end", values=(
                checkbox, title, owner, status, priority, due_date, estimated, actions
            ))
            
            # Apply tags for styling
            tags = []
            if task.get('completed'):
                tags.append("completed")
            # Safely check if overdue
            due_date = task.get('due_date')
            if due_date and isinstance(due_date, str):
                try:
                    if is_overdue(due_date):
                        tags.append("overdue")
                except Exception as e:
                    print(f"Error checking overdue for task {task.get('id')}: {e}")
            tags.append(f"status_{status.lower().replace(' ', '_')}")
            tags.append(f"priority_{priority.lower()}")
            
            self.tree.item(item, tags=tags)
            
        except Exception as e:
            print(f"Error inserting task {task.get('id', 'unknown')}: {e}")
            # Insert a placeholder row to maintain table structure
            item = self.tree.insert("", "end", values=(
                "☐", "Error loading task", "—", "Not Started", "Medium", "—", "—", "✏️ 🗑️"
            ))
            self.tree.item(item, tags=["error"])
    
    def _format_due_date(self, due_date: Optional[str]) -> str:
        """Format due date for display."""
        if not due_date:
            return "—"
        
        try:
            # Handle different date formats
            if isinstance(due_date, str):
                date_obj = datetime.strptime(due_date, "%Y-%m-%d")
            else:
                return "—"
            
            formatted = date_obj.strftime("%b %d")
            
            if is_overdue(due_date):
                return f"⚠️ {formatted}"
            elif date_obj.date() == datetime.now().date():
                return f"📅 {formatted}"
            else:
                return formatted
        except (ValueError, TypeError) as e:
            print(f"Error formatting date '{due_date}': {e}")
            return "Invalid"
    
    def _update_statistics(self):
        """Update statistics display."""
        total = len(self.tasks)
        completed = len([t for t in self.tasks if t.get('completed')])
        
        # Safely count overdue tasks
        overdue = 0
        for t in self.tasks:
            if not t.get('completed'):
                due_date = t.get('due_date')
                if due_date and isinstance(due_date, str):
                    try:
                        if is_overdue(due_date):
                            overdue += 1
                    except Exception as e:
                        print(f"Error checking overdue in stats for task {t.get('id')}: {e}")
        
        completion_rate = (completed / total * 100) if total > 0 else 0
        
        self.total_label.configure(text=f"Total: {total}")
        self.completed_label.configure(text=f"Completed: {completed}")
        self.overdue_label.configure(text=f"Overdue: {overdue}")
        self.progress_label.configure(text=f"{completion_rate:.1f}%")
        self.progress_bar.configure(value=completion_rate)
    
    def _on_search(self, search_term: str):
        """Handle search input."""
        self.search_term = search_term
        self._apply_filters()
    
    def _on_filter_change(self, event=None):
        """Handle filter changes."""
        self.status_filter = self.status_var.get()
        self.priority_filter = self.priority_var.get()
        self._apply_filters()
    
    def _clear_filters(self):
        """Clear all filters."""
        self.search_entry.delete(0, tk.END)
        self.status_var.set("All")
        self.priority_var.set("All")
        self.search_term = ""
        self.status_filter = None
        self.priority_filter = None
        self._apply_filters()
    
    def _sort_by_column(self, column: str):
        """Sort by column."""
        if self.sort_column == column:
            self.sort_reverse = not self.sort_reverse
        else:
            self.sort_column = column
            self.sort_reverse = False
        
        self._apply_filters()
    
    def _on_click(self, event):
        """Handle click events."""
        region = self.tree.identify("region", event.x, event.y)
        if region == "cell":
            column = self.tree.identify_column(event.x)
            item = self.tree.identify_row(event.y)
            if not item:
                return
            # Get task index
            index = self.tree.index(item)
            if index >= len(self.filtered_tasks):
                return
            task = self.filtered_tasks[index]
            # Handle checkbox click
            if column == "#1":  # checkbox column
                if self.on_task_toggle:
                    self.on_task_toggle(task['id'], not task.get('completed', False))
            # Handle actions column (edit/delete icons)
            elif column == "#8":  # actions column
                # Estimate which icon was clicked based on x offset
                bbox = self.tree.bbox(item, column)
                if bbox:
                    x_offset = event.x - bbox[0]
                    # Assume two icons, each about half the cell width
                    if x_offset < bbox[2] // 2:
                        # Edit icon (left)
                        if self.on_task_click:
                            self.on_task_click(task)
                    else:
                        # Delete icon (right)
                        if self.on_task_delete:
                            self._confirm_delete(task)
    
    def _on_double_click(self, event):
        """Handle double-click events."""
        region = self.tree.identify("region", event.x, event.y)
        if region == "cell":
            item = self.tree.identify_row(event.y)
            if item:
                index = self.tree.index(item)
                if index < len(self.filtered_tasks) and self.on_task_click:
                    self.on_task_click(self.filtered_tasks[index])
    
    def _on_delete_key(self, event):
        """Handle delete key press."""
        selection = self.tree.selection()
        if selection:
            item = selection[0]
            index = self.tree.index(item)
            if index < len(self.filtered_tasks) and self.on_task_delete:
                self._confirm_delete(self.filtered_tasks[index])
    
    def _on_enter_key(self, event):
        """Handle enter key press."""
        selection = self.tree.selection()
        if selection:
            item = selection[0]
            index = self.tree.index(item)
            if index < len(self.filtered_tasks) and self.on_task_click:
                self.on_task_click(self.filtered_tasks[index])
    
    def _on_key_navigation(self, event):
        """Handle keyboard navigation."""
        # Let the treeview handle navigation
        pass
    
    def _confirm_delete(self, task: Dict[str, Any]):
        """Show delete confirmation dialog."""
        title = task.get('title', 'Unknown Task')
        if show_confirm_dialog(
            self,
            "Delete Task",
            f"Are you sure you want to delete '{title}'?\n\nThis action cannot be undone."
        ):
            if self.on_task_delete:
                self.on_task_delete(task['id'])
    
    def get_selected_task(self) -> Optional[Dict[str, Any]]:
        """Get the currently selected task."""
        selection = self.tree.selection()
        if selection:
            item = selection[0]
            index = self.tree.index(item)
            if index < len(self.filtered_tasks):
                return self.filtered_tasks[index]
        return None
    
    def select_task(self, task_id: int):
        """Select a task by ID."""
        for i, task in enumerate(self.filtered_tasks):
            if task.get('id') == task_id:
                items = self.tree.get_children()
                if i < len(items):
                    self.tree.selection_set(items[i])
                    self.tree.see(items[i])
                break 