#!/usr/bin/env python3
"""
Comprehensive test runner for the SoulPlanner Task Tracker application.
"""
import sys
import os
import time
import threading
from typing import List, Dict, Any

# Add the current directory to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def run_component_tests():
    """Run tests for individual UI components."""
    print("🧪 Running Component Tests...")
    
    try:
        import tkinter as tk
        import ttkbootstrap as tb
        from ui.components import ModernEntry, ModernButton, SearchEntry, StatusPill, PriorityBadge
        from config import THEMES, FONTS
        
        # Create test window
        root = tb.Window(themename=THEMES["light"]["name"])
        root.title("Component Tests")
        root.geometry("800x600")
        
        test_frame = tk.Frame(root, padx=20, pady=20)
        test_frame.pack(fill="both", expand=True)
        
        results = []
        
        def test_component(name: str, test_func):
            """Test a component and record results."""
            try:
                test_func()
                results.append(f"✅ {name}: PASS")
                print(f"✅ {name}: PASS")
            except Exception as e:
                results.append(f"❌ {name}: FAIL - {str(e)}")
                print(f"❌ {name}: FAIL - {str(e)}")
        
        # Test ModernEntry
        def test_modern_entry():
            try:
                entry = ModernEntry(test_frame, placeholder="Test placeholder")
                entry.pack(pady=5)
                
                # Test initial state
                assert entry.get() == "Test placeholder"
                
                # Test focus in
                entry.focus_set()
                entry.event_generate("<FocusIn>")
                assert entry.get() == ""
                
                # Test focus out with empty content
                entry.event_generate("<FocusOut>")
                assert entry.get() == "Test placeholder"
                
                # Test get_value method
                entry.delete(0, tk.END)
                entry.insert(0, "test value")
                assert entry.get_value() == "test value"
                
                # Test set_value method
                entry.set_value("new value")
                assert entry.get() == "new value"
                
            except Exception as e:
                print(f"ModernEntry test error: {e}")
                raise
        
        test_component("ModernEntry", test_modern_entry)
        
        # Test ModernButton
        def test_modern_button():
            try:
                button = ModernButton(test_frame, text="Test Button", primary=True)
                button.pack(pady=5)
                
                # Test initial state
                assert button.cget("text") == "Test Button"
                
                # Test loading state
                button.set_loading(True)
                assert button.cget("state") == "disabled"
                
                button.set_loading(False)
                assert button.cget("state") == "normal"
                
                # Test enable/disable
                button.set_enabled(False)
                assert button.cget("state") == "disabled"
                
                button.set_enabled(True)
                assert button.cget("state") == "normal"
                
            except Exception as e:
                print(f"ModernButton test error: {e}")
                raise
        
        test_component("ModernButton", test_modern_button)
        
        # Test SearchEntry
        def test_search_entry():
            try:
                search_calls = []
                
                def on_search(term):
                    search_calls.append(term)
                
                entry = SearchEntry(test_frame, on_search)
                entry.pack(pady=5)
                
                # Test initial state
                assert entry.get() == "Search tasks..."
                
                # Test search functionality
                entry.delete(0, tk.END)
                entry.insert(0, "test")
                entry.event_generate("<KeyRelease>")
                
                # Wait for debounce
                time.sleep(0.4)
                
                # Should have called search once
                assert len(search_calls) == 1
                assert search_calls[0] == "test"
                
                # Test clear search
                entry.clear_search()
                assert entry.get() == "Search tasks..."
                
            except Exception as e:
                print(f"SearchEntry test error: {e}")
                raise
        
        test_component("SearchEntry", test_search_entry)
        
        # Test StatusPill
        def test_status_pill():
            try:
                pill = StatusPill(test_frame, "Working on it")
                pill.pack(pady=5)
                
                # Test that the widget was created successfully
                assert pill.cget("text") == "Working on it"
                
            except Exception as e:
                print(f"StatusPill test error: {e}")
                raise
        
        test_component("StatusPill", test_status_pill)
        
        # Test PriorityBadge
        def test_priority_badge():
            try:
                badge = PriorityBadge(test_frame, "High")
                badge.pack(pady=5)
                
                # Test that the widget was created successfully
                assert badge.cget("text") == "High"
                
            except Exception as e:
                print(f"PriorityBadge test error: {e}")
                raise
        
        test_component("PriorityBadge", test_priority_badge)
        
        # Display results
        results_text = "\n".join(results)
        results_label = tk.Label(test_frame, text=results_text, font=FONTS["primary"], justify="left")
        results_label.pack(pady=20)
        
        # Close button
        close_btn = ModernButton(test_frame, text="Close Tests", command=root.destroy)
        close_btn.pack(pady=10)
        
        print(f"\n📊 Component Test Results:\n{results_text}")
        print(f"\n✅ {len([r for r in results if 'PASS' in r])} passed, ❌ {len([r for r in results if 'FAIL' in r])} failed")
        
        root.mainloop()
        
    except Exception as e:
        print(f"❌ Component tests failed: {e}")

def run_functionality_tests():
    """Run tests for application functionality."""
    print("\n🔧 Running Functionality Tests...")
    
    try:
        from database import db_manager
        from utils import validate_task_data, format_date, is_overdue
        from models import TaskStatus, TaskPriority
        
        results = []
        
        def test_function(name: str, test_func):
            """Test a function and record results."""
            try:
                test_func()
                results.append(f"✅ {name}: PASS")
                print(f"✅ {name}: PASS")
            except Exception as e:
                results.append(f"❌ {name}: FAIL - {str(e)}")
                print(f"❌ {name}: FAIL - {str(e)}")
        
        # Test database operations
        def test_database_operations():
            # Test adding task
            task_data = {
                'title': 'Test Task',
                'description': 'Test Description',
                'status': 'Working on it',
                'priority': 'Medium',
                'project': 'test'
            }
            
            task_id = db_manager.add_task(task_data)
            assert task_id is not None
            assert task_id > 0
            
            # Test getting tasks
            tasks = db_manager.get_tasks(project='test')
            assert isinstance(tasks, list)
            assert len(tasks) > 0
            
            # Test updating task
            update_data = {'title': 'Updated Title'}
            success = db_manager.update_task(task_id, **update_data)
            assert success is True
            
            # Test deleting task
            success = db_manager.delete_task(task_id)
            assert success is True
        
        test_function("Database Operations", test_database_operations)
        
        # Test validation
        def test_validation():
            # Test valid data
            valid_data = {
                'title': 'Test Task',
                'status': 'Working on it',
                'priority': 'Medium'
            }
            is_valid, error = validate_task_data(valid_data)
            assert is_valid is True
            assert error == ""
            
            # Test invalid data
            invalid_data = {
                'status': 'Working on it',
                'priority': 'Medium'
            }
            is_valid, error = validate_task_data(invalid_data)
            assert is_valid is False
            assert "title" in error.lower()
        
        test_function("Data Validation", test_validation)
        
        # Test utility functions
        def test_utility_functions():
            # Test date formatting
            formatted = format_date("2024-01-01")
            assert formatted is not None
            
            # Test overdue checking
            overdue = is_overdue("2020-01-01")
            assert overdue is True
            
            future = is_overdue("2030-01-01")
            assert future is False
        
        test_function("Utility Functions", test_utility_functions)
        
        print(f"\n📊 Functionality Test Results:")
        for result in results:
            print(result)
        print(f"\n✅ {len([r for r in results if 'PASS' in r])} passed, ❌ {len([r for r in results if 'FAIL' in r])} failed")
        
    except Exception as e:
        print(f"❌ Functionality tests failed: {e}")

def run_integration_tests():
    """Run integration tests for the complete application."""
    print("\n🔗 Running Integration Tests...")
    
    try:
        import tkinter as tk
        import ttkbootstrap as tb
        from ui.task_dialog import TaskDialog
        from ui.task_table import ModernTaskTable
        from ui.theme_manager import ThemeManager
        from config import THEMES
        
        # Create test window
        root = tb.Window(themename=THEMES["light"]["name"])
        root.title("Integration Tests")
        root.geometry("1000x700")
        
        test_frame = tk.Frame(root, padx=20, pady=20)
        test_frame.pack(fill="both", expand=True)
        
        results = []
        
        def test_integration(name: str, test_func):
            """Test integration functionality."""
            try:
                test_func()
                results.append(f"✅ {name}: PASS")
                print(f"✅ {name}: PASS")
            except Exception as e:
                results.append(f"❌ {name}: FAIL - {str(e)}")
                print(f"❌ {name}: FAIL - {str(e)}")
        
        # Test TaskDialog
        def test_task_dialog():
            try:
                dialog = TaskDialog(root)
                
                # Test that dialog was created
                assert dialog is not None
                assert dialog.winfo_exists()
                
                # Test window properties
                assert dialog.title() == "Add Task"
                assert dialog.transient()
                
                # Test form data
                form_data = dialog._get_form_data()
                assert isinstance(form_data, dict)
                
                # Clean up immediately
                dialog.destroy()
                
            except Exception as e:
                print(f"TaskDialog test error: {e}")
                raise
        
        test_integration("TaskDialog Creation", test_task_dialog)
        
        # Test TaskTable
        def test_task_table():
            try:
                table = ModernTaskTable(root)
                
                # Test that table was created
                assert table is not None
                
                # Test initial state
                assert len(table.tasks) == 0
                
                # Test setting data
                test_tasks = [
                    {
                        'id': 1,
                        'title': 'Task 1',
                        'status': 'Working on it',
                        'priority': 'Medium',
                        'due_date': '2024-01-01'
                    }
                ]
                
                table.set_tasks(test_tasks)
                assert len(table.tasks) == 1
                
            except Exception as e:
                print(f"TaskTable test error: {e}")
                raise
        
        test_integration("TaskTable Functionality", test_task_table)
        
        # Test ThemeManager
        def test_theme_manager():
            try:
                theme_manager = ThemeManager(root)
                
                # Test that manager was created
                assert theme_manager is not None
                
                # Test theme switching
                current_theme = theme_manager.get_current_theme_config()
                assert current_theme is not None
                
                theme_manager.switch_theme()
                new_theme = theme_manager.get_current_theme_config()
                assert new_theme is not None
                
            except Exception as e:
                print(f"ThemeManager test error: {e}")
                raise
        
        test_integration("ThemeManager", test_theme_manager)
        
        # Display results
        results_text = "\n".join(results)
        results_label = tk.Label(test_frame, text=results_text, font=("Segoe UI", 10), justify="left")
        results_label.pack(pady=20)
        
        # Close button
        close_btn = tk.Button(test_frame, text="Close Tests", command=root.destroy)
        close_btn.pack(pady=10)
        
        print(f"\n📊 Integration Test Results:\n{results_text}")
        print(f"\n✅ {len([r for r in results if 'PASS' in r])} passed, ❌ {len([r for r in results if 'FAIL' in r])} failed")
        
        root.mainloop()
        
    except Exception as e:
        print(f"❌ Integration tests failed: {e}")

def run_performance_tests():
    """Run performance tests."""
    print("\n⚡ Running Performance Tests...")
    
    try:
        from database import db_manager
        import time
        
        results = []
        
        def test_performance(name: str, test_func):
            """Test performance and record results."""
            try:
                start_time = time.time()
                test_func()
                end_time = time.time()
                duration = end_time - start_time
                
                if duration < 1.0:
                    results.append(f"✅ {name}: PASS ({duration:.3f}s)")
                    print(f"✅ {name}: PASS ({duration:.3f}s)")
                else:
                    results.append(f"⚠️ {name}: SLOW ({duration:.3f}s)")
                    print(f"⚠️ {name}: SLOW ({duration:.3f}s)")
            except Exception as e:
                results.append(f"❌ {name}: FAIL - {str(e)}")
                print(f"❌ {name}: FAIL - {str(e)}")
        
        # Test database performance
        def test_database_performance():
            # Add multiple tasks
            for i in range(10):
                task_data = {
                    'title': f'Performance Test Task {i}',
                    'description': f'Test description {i}',
                    'status': 'Working on it',
                    'priority': 'Medium',
                    'project': 'performance_test'
                }
                db_manager.add_task(task_data)
            
            # Get tasks
            tasks = db_manager.get_tasks(project='performance_test')
            assert len(tasks) == 10
            
            # Clean up
            for task in tasks:
                db_manager.delete_task(task['id'])
        
        test_performance("Database Operations (10 tasks)", test_database_performance)
        
        # Test UI component creation
        def test_ui_performance():
            import tkinter as tk
            import ttkbootstrap as tb
            from ui.components import ModernEntry, ModernButton
            
            root = tb.Window()
            root.withdraw()
            
            # Create multiple components
            for i in range(50):
                entry = ModernEntry(root, placeholder=f"Entry {i}")
                button = ModernButton(root, text=f"Button {i}")
            
            root.destroy()
        
        test_performance("UI Component Creation (50 components)", test_ui_performance)
        
        print(f"\n📊 Performance Test Results:")
        for result in results:
            print(result)
        
    except Exception as e:
        print(f"❌ Performance tests failed: {e}")

def main():
    """Main test runner."""
    print("🚀 Starting SoulPlanner Test Suite")
    print("=" * 50)
    
    # Run all test suites
    run_component_tests()
    run_functionality_tests()
    run_integration_tests()
    run_performance_tests()
    
    print("\n" + "=" * 50)
    print("🎉 Test Suite Complete!")
    print("\n📋 Summary:")
    print("- Component Tests: UI components and their behavior")
    print("- Functionality Tests: Core application logic")
    print("- Integration Tests: Component interactions")
    print("- Performance Tests: Speed and efficiency")
    
    print("\n💡 Next Steps:")
    print("1. Review any failed tests and fix issues")
    print("2. Add more specific tests for your use cases")
    print("3. Run tests regularly during development")
    print("4. Consider adding automated CI/CD testing")

if __name__ == "__main__":
    main() 