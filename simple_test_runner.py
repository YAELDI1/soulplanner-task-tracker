#!/usr/bin/env python3
"""
Simple and robust test runner for the SoulPlanner Task Tracker application.
This version avoids Tkinter window lifecycle issues by using a single main window.
"""
import sys
import os
import time
import threading
from typing import List, Dict, Any

# Add the current directory to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def run_simple_tests():
    """Run simple tests that don't require complex UI interactions."""
    print("🧪 Running Simple Tests...")
    
    try:
        from database import db_manager
        from utils import validate_task_data, format_date, is_overdue
        from models import TaskStatus, TaskPriority
        from config import APP_NAME, APP_VERSION, THEMES, FONTS
        
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
        
        # Test configuration
        def test_configuration():
            assert APP_NAME is not None
            assert APP_VERSION is not None
            assert THEMES is not None
            assert FONTS is not None
            assert "light" in THEMES
            assert "dark" in THEMES
        
        test_function("Configuration", test_configuration)
        
        print(f"\n📊 Simple Test Results:")
        for result in results:
            print(result)
        print(f"\n✅ {len([r for r in results if 'PASS' in r])} passed, ❌ {len([r for r in results if 'FAIL' in r])} failed")
        
        return results
        
    except Exception as e:
        print(f"❌ Simple tests failed: {e}")
        return []

def run_ui_tests():
    """Run UI tests with a single main window to avoid lifecycle issues."""
    print("\n🎨 Running UI Tests...")
    
    try:
        import tkinter as tk
        from tkinter import ttk
        import ttkbootstrap as tb
        from ui.components import ModernEntry, ModernButton, SearchEntry, StatusPill, PriorityBadge
        from ui.theme_manager import ThemeManager
        from config import THEMES, FONTS
        
        # Create single test window
        root = tb.Window(themename=THEMES["light"]["name"])
        root.title("UI Test Suite")
        root.geometry("900x700")
        
        # Create notebook for different test categories
        notebook = ttk.Notebook(root)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        results = []
        
        def test_ui_component(name: str, test_func):
            """Test a UI component and record results."""
            try:
                test_func()
                results.append(f"✅ {name}: PASS")
                print(f"✅ {name}: PASS")
            except Exception as e:
                results.append(f"❌ {name}: FAIL - {str(e)}")
                print(f"❌ {name}: FAIL - {str(e)}")
        
        # Component Tests Tab
        component_frame = ttk.Frame(notebook)
        notebook.add(component_frame, text="Components")
        
        # Test ModernEntry
        def test_modern_entry():
            entry = ModernEntry(component_frame, placeholder="Test placeholder")
            entry.pack(pady=5, padx=10, fill="x")
            
            # Test initial state
            assert entry.get() == "Test placeholder"
            
            # Test get_value method
            entry.delete(0, tk.END)
            entry.insert(0, "test value")
            assert entry.get_value() == "test value"
        
        test_ui_component("ModernEntry", test_modern_entry)
        
        # Test ModernButton
        def test_modern_button():
            button = ModernButton(component_frame, text="Test Button", primary=True)
            button.pack(pady=5, padx=10)
            
            # Test initial state
            assert button.cget("text") == "Test Button"
            
            # Test loading state
            button.set_loading(True)
            assert button.cget("state") == "disabled"
            
            button.set_loading(False)
            assert button.cget("state") == "normal"
        
        test_ui_component("ModernButton", test_modern_button)
        
        # Test SearchEntry
        def test_search_entry():
            search_calls = []
            
            def on_search(term):
                search_calls.append(term)
            
            entry = SearchEntry(component_frame, on_search)
            entry.pack(pady=5, padx=10, fill="x")
            
            # Test initial state
            assert entry.get() == "Search tasks..."
        
        test_ui_component("SearchEntry", test_search_entry)
        
        # Test StatusPill
        def test_status_pill():
            pill = StatusPill(component_frame, "Working on it")
            pill.pack(pady=5, padx=10)
            
            # Test that the widget was created successfully
            assert pill.cget("text") == "Working on it"
        
        test_ui_component("StatusPill", test_status_pill)
        
        # Test PriorityBadge
        def test_priority_badge():
            badge = PriorityBadge(component_frame, "High")
            badge.pack(pady=5, padx=10)
            
            # Test that the widget was created successfully
            assert badge.cget("text") == "High"
        
        test_ui_component("PriorityBadge", test_priority_badge)
        
        # Theme Tests Tab
        theme_frame = ttk.Frame(notebook)
        notebook.add(theme_frame, text="Theme")
        
        def test_theme_manager():
            theme_manager = ThemeManager(root)
            
            # Test that manager was created
            assert theme_manager is not None
            
            # Test theme switching
            current_theme = theme_manager.get_current_theme_config()
            assert current_theme is not None
            
            # Create theme toggle button
            theme_btn = theme_manager.create_theme_button(theme_frame)
            theme_btn.pack(pady=20)
        
        test_ui_component("ThemeManager", test_theme_manager)
        
        # Results Tab
        results_frame = ttk.Frame(notebook)
        notebook.add(results_frame, text="Results")
        
        # Display results
        results_text = "\n".join(results)
        results_label = tk.Label(results_frame, text=results_text, font=FONTS["primary"], justify="left")
        results_label.pack(pady=20, padx=20)
        
        # Summary
        summary_text = f"✅ {len([r for r in results if 'PASS' in r])} passed, ❌ {len([r for r in results if 'FAIL' in r])} failed"
        summary_label = tk.Label(results_frame, text=summary_text, font=FONTS["primary_bold"])
        summary_label.pack(pady=10)
        
        # Close button
        close_btn = ModernButton(results_frame, text="Close Tests", command=root.destroy)
        close_btn.pack(pady=20)
        
        print(f"\n📊 UI Test Results:\n{results_text}")
        print(f"\n{summary_text}")
        
        root.mainloop()
        
        return results
        
    except Exception as e:
        print(f"❌ UI tests failed: {e}")
        return []

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
        
        print(f"\n📊 Performance Test Results:")
        for result in results:
            print(result)
        
        return results
        
    except Exception as e:
        print(f"❌ Performance tests failed: {e}")
        return []

def main():
    """Main test runner."""
    print("🚀 Starting SoulPlanner Simple Test Suite")
    print("=" * 50)
    
    all_results = []
    
    # Run simple tests (no UI)
    simple_results = run_simple_tests()
    all_results.extend(simple_results)
    
    # Run UI tests
    ui_results = run_ui_tests()
    all_results.extend(ui_results)
    
    # Run performance tests
    perf_results = run_performance_tests()
    all_results.extend(perf_results)
    
    print("\n" + "=" * 50)
    print("🎉 Test Suite Complete!")
    
    # Summary
    passed = len([r for r in all_results if 'PASS' in r])
    failed = len([r for r in all_results if 'FAIL' in r])
    slow = len([r for r in all_results if 'SLOW' in r])
    
    print(f"\n📊 Final Summary:")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"⚠️ Slow: {slow}")
    print(f"📈 Success Rate: {(passed / len(all_results) * 100):.1f}%" if all_results else "N/A")
    
    print("\n💡 Next Steps:")
    if failed > 0:
        print("1. Review failed tests and fix issues")
    print("2. Run tests regularly during development")
    print("3. Use the manual testing checklist for thorough validation")
    print("4. Consider adding more specific tests for your use cases")

if __name__ == "__main__":
    main() 