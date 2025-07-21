"""
Main entry point for the SoulPlanner Task Tracker application.
"""
import sys
import os
import traceback
import tkinter as tk
from tkinter import messagebox
import ttkbootstrap as tb

# Add the current directory to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import APP_NAME, APP_VERSION, THEMES
from ui.main_window import MainWindow
from utils import show_error_dialog

def setup_exception_handling():
    """Setup global exception handling."""
    def handle_exception(exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            # Handle Ctrl+C gracefully
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        
        # Log the error
        error_msg = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
        print(f"Unhandled exception: {error_msg}", file=sys.stderr)
        
        # Show error dialog if we have a root window
        try:
            if hasattr(app_instance, 'root') and app_instance.root.winfo_exists():
                show_error_dialog(
                    app_instance.root,
                    "Application Error",
                    f"An unexpected error occurred:\n\n{exc_value}\n\nPlease restart the application."
                )
        except:
            pass
    
    sys.excepthook = handle_exception

def check_dependencies():
    """Check if all required dependencies are available."""
    required_packages = ['ttkbootstrap', 'sqlmodel']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        error_msg = f"Missing required packages: {', '.join(missing_packages)}\n\n"
        error_msg += "Please install them using:\n"
        error_msg += f"pip install {' '.join(missing_packages)}"
        
        # Show error dialog
        root = tk.Tk()
        root.withdraw()  # Hide the main window
        messagebox.showerror("Missing Dependencies", error_msg)
        root.destroy()
        return False
    
    return True

def main():
    """Main application entry point."""
    print(f"Starting {APP_NAME} v{APP_VERSION}...")
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    try:
        # Create the main application window
        app = tb.Window(
            themename=THEMES["light"]["name"],
            title=f"{APP_NAME} v{APP_VERSION}",
            iconphoto=None  # Add icon here if available
        )
        
        # Setup exception handling
        setup_exception_handling()
        
        # Create and initialize the main window
        main_window = MainWindow(app)
        
        # Store reference for exception handling
        global app_instance
        app_instance = main_window
        
        print(f"{APP_NAME} started successfully!")
        
        # Start the main event loop
        app.mainloop()
        
    except Exception as e:
        print(f"Failed to start {APP_NAME}: {e}")
        traceback.print_exc()
        
        # Show error dialog
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror(
            "Startup Error",
            f"Failed to start {APP_NAME}:\n\n{e}\n\nPlease check the console for more details."
        )
        root.destroy()
        sys.exit(1)

if __name__ == "__main__":
    main() 