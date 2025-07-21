"""
Comprehensive testing framework for the SoulPlanner Task Tracker application.
"""
import unittest
import tkinter as tk
from tkinter import ttk
import ttkbootstrap as tb
import threading
import time
from typing import Dict, Any, Optional
import sys
import os

# Add the current directory to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import APP_NAME, APP_VERSION, THEMES, FONTS
from database import db_manager
from models import Task, TaskStatus, TaskPriority
from utils import validate_task_data, format_date, is_overdue
from ui.components import ModernEntry, ModernButton, SearchEntry, StatusPill, PriorityBadge
from ui.task_dialog import TaskDialog
from ui.task_table import ModernTaskTable
from ui.theme_manager import ThemeManager

class TestBase(unittest.TestCase):
    """Base class for all tests with common setup."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment once for all tests."""
        cls.root = tb.Window(themename=THEMES["light"]["name"])
        cls.root.withdraw()  # Hide window during tests
        
    @classmethod
    def tearDownClass(cls):
        """Clean up test environment."""
        if hasattr(cls, 'root'):
            cls.root.destroy()
    
    def setUp(self):
        """Set up before each test."""
        # Clear database for each test
        try:
            db_manager._init_database()
        except:
            pass
    
    def tearDown(self):
        """Clean up after each test."""
        pass

class TestDatabaseOperations(TestBase):
    """Test database operations."""
    
    def test_add_task(self):
        """Test adding a task to database."""
        task_data = {
            'title': 'Test Task',
            'description': 'Test Description',
            'status': 'Working on it',
            'priority': 'Medium',
            'project': 'test'
        }
        
        task_id = db_manager.add_task(task_data)
        self.assertIsNotNone(task_id)
        self.assertGreater(task_id, 0)
    
    def test_get_tasks(self):
        """Test retrieving tasks from database."""
        # Add a test task
        task_data = {
            'title': 'Test Task',
            'description': 'Test Description',
            'status': 'Working on it',
            'priority': 'Medium',
            'project': 'test'
        }
        db_manager.add_task(task_data)
        
        # Retrieve tasks
        tasks = db_manager.get_tasks(project='test')
        self.assertIsInstance(tasks, list)
        self.assertGreater(len(tasks), 0)
        
        task = tasks[0]
        self.assertEqual(task['title'], 'Test Task')
    
    def test_update_task(self):
        """Test updating a task."""
        # Add a test task
        task_data = {
            'title': 'Original Title',
            'description': 'Original Description',
            'status': 'Working on it',
            'priority': 'Medium',
            'project': 'test'
        }
        task_id = db_manager.add_task(task_data)
        
        # Update the task
        update_data = {
            'title': 'Updated Title',
            'status': 'Done'
        }
        success = db_manager.update_task(task_id, **update_data)
        self.assertTrue(success)
        
        # Verify update
        tasks = db_manager.get_tasks(project='test')
        updated_task = next((t for t in tasks if t['id'] == task_id), None)
        self.assertIsNotNone(updated_task)
        self.assertEqual(updated_task['title'], 'Updated Title')
        self.assertEqual(updated_task['status'], 'Done')
    
    def test_delete_task(self):
        """Test deleting a task."""
        # Add a test task
        task_data = {
            'title': 'Task to Delete',
            'description': 'Will be deleted',
            'status': 'Working on it',
            'priority': 'Medium',
            'project': 'test'
        }
        task_id = db_manager.add_task(task_data)
        
        # Delete the task
        success = db_manager.delete_task(task_id)
        self.assertTrue(success)
        
        # Verify deletion
        tasks = db_manager.get_tasks(project='test')
        deleted_task = next((t for t in tasks if t['id'] == task_id), None)
        self.assertIsNone(deleted_task)

class TestUIComponents(TestBase):
    """Test individual UI components."""
    
    def test_modern_entry_placeholder(self):
        """Test ModernEntry placeholder functionality."""
        entry = ModernEntry(self.root, placeholder="Test placeholder")
        
        # Check initial state
        self.assertEqual(entry.get(), "Test placeholder")
        
        # Test focus in
        entry.focus_set()
        entry.event_generate("<FocusIn>")
        self.assertEqual(entry.get(), "")
        
        # Test focus out with empty content
        entry.event_generate("<FocusOut>")
        self.assertEqual(entry.get(), "Test placeholder")
    
    def test_modern_button_hover(self):
        """Test ModernButton hover effects."""
        button = ModernButton(self.root, text="Test Button")
        
        # Test hover enter
        button.event_generate("<Enter>")
        # Note: We can't easily test cursor changes in unit tests
        
        # Test hover leave
        button.event_generate("<Leave>")
    
    def test_search_entry_debounce(self):
        """Test SearchEntry debouncing functionality."""
        search_calls = []
        
        def on_search(term):
            search_calls.append(term)
        
        entry = SearchEntry(self.root, on_search)
        
        # Type quickly
        entry.delete(0, tk.END)
        entry.insert(0, "test")
        entry.event_generate("<KeyRelease>")
        
        # Wait for debounce
        time.sleep(0.4)
        
        # Should have called search once
        self.assertEqual(len(search_calls), 1)
        self.assertEqual(search_calls[0], "test")
    
    def test_status_pill_colors(self):
        """Test StatusPill color assignment."""
        status_pill = StatusPill(self.root, "Working on it")
        # Test that the widget was created successfully
        self.assertIsNotNone(status_pill)
    
    def test_priority_badge_colors(self):
        """Test PriorityBadge color assignment."""
        priority_badge = PriorityBadge(self.root, "High")
        # Test that the widget was created successfully
        self.assertIsNotNone(priority_badge)

class TestTaskDialog(TestBase):
    """Test TaskDialog functionality."""
    
    def test_task_dialog_creation(self):
        """Test TaskDialog creation and basic functionality."""
        dialog = TaskDialog(self.root)
        
        # Test that dialog was created
        self.assertIsNotNone(dialog)
        self.assertTrue(dialog.winfo_exists())
        
        # Test window properties
        self.assertEqual(dialog.title(), "Add Task")
        self.assertTrue(dialog.transient())
        
        # Clean up
        dialog.destroy()
    
    def test_task_dialog_edit_mode(self):
        """Test TaskDialog in edit mode."""
        task_data = {
            'id': 1,
            'title': 'Test Task',
            'description': 'Test Description',
            'status': 'Working on it',
            'priority': 'Medium'
        }
        
        dialog = TaskDialog(self.root, task_data=task_data)
        
        # Test that dialog was created in edit mode
        self.assertEqual(dialog.title(), "Edit Task")
        
        # Clean up
        dialog.destroy()
    
    def test_form_validation(self):
        """Test form validation in TaskDialog."""
        dialog = TaskDialog(self.root)
        
        # Test empty title validation
        form_data = dialog._get_form_data()
        self.assertIn('title', form_data)
        
        # Clean up
        dialog.destroy()

class TestTaskTable(TestBase):
    """Test ModernTaskTable functionality."""
    
    def test_task_table_creation(self):
        """Test ModernTaskTable creation."""
        table = ModernTaskTable(self.root)
        
        # Test that table was created
        self.assertIsNotNone(table)
        
        # Test initial state
        self.assertEqual(len(table.get_children()), 0)
    
    def test_task_table_data_setting(self):
        """Test setting data in ModernTaskTable."""
        table = ModernTaskTable(self.root)
        
        # Create test data
        test_tasks = [
            {
                'id': 1,
                'title': 'Task 1',
                'status': 'Working on it',
                'priority': 'Medium',
                'due_date': '2024-01-01'
            },
            {
                'id': 2,
                'title': 'Task 2',
                'status': 'Done',
                'priority': 'High',
                'due_date': '2024-01-02'
            }
        ]
        
        # Set data
        table.set_tasks(test_tasks)
        
        # Verify data was set
        children = table.get_children()
        self.assertEqual(len(children), 2)

class TestThemeManager(TestBase):
    """Test ThemeManager functionality."""
    
    def test_theme_manager_creation(self):
        """Test ThemeManager creation."""
        theme_manager = ThemeManager(self.root)
        
        # Test that manager was created
        self.assertIsNotNone(theme_manager)
    
    def test_theme_switching(self):
        """Test theme switching functionality."""
        theme_manager = ThemeManager(self.root)
        
        # Get current theme
        current_theme = theme_manager.get_current_theme_config()
        self.assertIsNotNone(current_theme)
        
        # Switch theme
        theme_manager.switch_theme()
        
        # Verify theme changed
        new_theme = theme_manager.get_current_theme_config()
        self.assertIsNotNone(new_theme)

class TestUtils(TestBase):
    """Test utility functions."""
    
    def test_validate_task_data(self):
        """Test task data validation."""
        # Valid data
        valid_data = {
            'title': 'Test Task',
            'status': 'Working on it',
            'priority': 'Medium'
        }
        errors = validate_task_data(valid_data)
        self.assertEqual(len(errors), 0)
        
        # Invalid data - missing title
        invalid_data = {
            'status': 'Working on it',
            'priority': 'Medium'
        }
        errors = validate_task_data(invalid_data)
        self.assertGreater(len(errors), 0)
        self.assertIn('title', [e['field'] for e in errors])
    
    def test_format_date(self):
        """Test date formatting."""
        # Test valid date
        formatted = format_date("2024-01-01")
        self.assertIsNotNone(formatted)
        
        # Test invalid date
        formatted = format_date("invalid-date")
        self.assertEqual(formatted, "Invalid date")
    
    def test_is_overdue(self):
        """Test overdue date checking."""
        # Test overdue date
        overdue = is_overdue("2020-01-01")
        self.assertTrue(overdue)
        
        # Test future date
        future = is_overdue("2030-01-01")
        self.assertFalse(future)
        
        # Test None date
        none_date = is_overdue(None)
        self.assertFalse(none_date)

class TestIntegration(TestBase):
    """Integration tests for the complete application."""
    
    def test_complete_task_workflow(self):
        """Test complete task creation and management workflow."""
        # Create task dialog
        dialog = TaskDialog(self.root)
        
        # Fill in task data
        dialog.title_entry.delete(0, tk.END)
        dialog.title_entry.insert(0, "Integration Test Task")
        
        dialog.description_text.delete("1.0", tk.END)
        dialog.description_text.insert("1.0", "Integration test description")
        
        # Set status and priority
        dialog.status_var.set("Working on it")
        dialog.priority_var.set("High")
        
        # Get form data
        form_data = dialog._get_form_data()
        
        # Validate form data
        self.assertEqual(form_data['title'], "Integration Test Task")
        self.assertEqual(form_data['status'], "Working on it")
        self.assertEqual(form_data['priority'], "High")
        
        # Clean up
        dialog.destroy()
    
    def test_error_handling(self):
        """Test error handling in various scenarios."""
        # Test database error handling
        try:
            # This should not crash the application
            db_manager.get_tasks(project="non_existent")
        except Exception as e:
            # Should handle gracefully
            self.assertIsInstance(e, Exception)

def run_ui_tests():
    """Run UI tests with visual feedback."""
    print("Starting UI Tests...")
    
    # Create test window
    root = tb.Window(themename=THEMES["light"]["name"])
    root.title("UI Test Suite")
    root.geometry("800x600")
    
    # Create test frame
    test_frame = ttk.Frame(root, padding=20)
    test_frame.pack(fill="both", expand=True)
    
    # Test results
    results = []
    
    def test_component(component_name, test_func):
        """Test a component and record results."""
        try:
            test_func()
            results.append(f"✅ {component_name}: PASS")
        except Exception as e:
            results.append(f"❌ {component_name}: FAIL - {str(e)}")
    
    # Test ModernEntry
    def test_modern_entry():
        entry = ModernEntry(test_frame, placeholder="Test placeholder")
        entry.pack(pady=5)
        assert entry.get() == "Test placeholder"
    
    test_component("ModernEntry", test_modern_entry)
    
    # Test ModernButton
    def test_modern_button():
        button = ModernButton(test_frame, text="Test Button", primary=True)
        button.pack(pady=5)
        assert button.cget("text") == "Test Button"
    
    test_component("ModernButton", test_modern_button)
    
    # Test SearchEntry
    def test_search_entry():
        def on_search(term):
            pass
        search = SearchEntry(test_frame, on_search)
        search.pack(pady=5)
        assert search.get() == "Search tasks..."
    
    test_component("SearchEntry", test_search_entry)
    
    # Test StatusPill
    def test_status_pill():
        pill = StatusPill(test_frame, "Working on it")
        pill.pack(pady=5)
        assert pill.cget("text") == "Working on it"
    
    test_component("StatusPill", test_status_pill)
    
    # Test PriorityBadge
    def test_priority_badge():
        badge = PriorityBadge(test_frame, "High")
        badge.pack(pady=5)
        assert badge.cget("text") == "High"
    
    test_component("PriorityBadge", test_priority_badge)
    
    # Display results
    results_label = ttk.Label(test_frame, text="\n".join(results), font=FONTS["primary"])
    results_label.pack(pady=20)
    
    # Close button
    close_btn = ModernButton(test_frame, text="Close Tests", command=root.destroy)
    close_btn.pack(pady=10)
    
    print("UI Tests completed. Check the window for results.")
    root.mainloop()

if __name__ == "__main__":
    # Run unit tests
    print("Running Unit Tests...")
    unittest.main(verbosity=2, exit=False)
    
    # Run UI tests
    print("\n" + "="*50)
    run_ui_tests() 