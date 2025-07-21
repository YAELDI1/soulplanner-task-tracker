"""
Development auto-reloader for SoulPlanner.
Monitors file changes and automatically restarts the application.
"""
import os
import sys
import time
import subprocess
import signal
from pathlib import Path

class AutoReloader:
    """Auto-reloader for development."""
    
    def __init__(self):
        self.process = None
        self.watched_extensions = {'.py', '.txt', '.md'}
        self.ignored_dirs = {'.git', '__pycache__', '.pytest_cache', 'venv', 'env'}
        self.last_restart = 0
        self.restart_cooldown = 2  # seconds
        
    def start(self):
        """Start the auto-reloader."""
        print("🚀 SoulPlanner Auto-Reloader Started")
        print("📁 Watching for changes in Python files...")
        print("⏹️  Press Ctrl+C to stop")
        print("-" * 50)
        
        try:
            while True:
                if self.should_restart():
                    self.restart_app()
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop()
    
    def should_restart(self):
        """Check if the application should be restarted."""
        current_time = time.time()
        
        # Check cooldown
        if current_time - self.last_restart < self.restart_cooldown:
            return False
        
        # Check for file changes
        for file_path in self.get_python_files():
            if self.has_file_changed(file_path):
                return True
        
        return False
    
    def get_python_files(self):
        """Get all Python files in the project."""
        python_files = []
        project_dir = Path(__file__).parent
        
        for root, dirs, files in os.walk(project_dir):
            # Skip ignored directories
            dirs[:] = [d for d in dirs if d not in self.ignored_dirs]
            
            for file in files:
                if file.endswith('.py'):
                    python_files.append(Path(root) / file)
        
        return python_files
    
    def has_file_changed(self, file_path):
        """Check if a file has been modified recently."""
        try:
            stat = file_path.stat()
            # Check if file was modified in the last 2 seconds
            return time.time() - stat.st_mtime < 2
        except (OSError, FileNotFoundError):
            return False
    
    def restart_app(self):
        """Restart the application."""
        print(f"\n🔄 Restarting SoulPlanner... ({time.strftime('%H:%M:%S')})")
        
        # Stop current process
        if self.process:
            try:
                self.process.terminate()
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
            except Exception as e:
                print(f"⚠️  Error stopping process: {e}")
        
        # Start new process
        try:
            self.process = subprocess.Popen([sys.executable, 'main.py'])
            self.last_restart = time.time()
            print("✅ Application restarted successfully")
        except Exception as e:
            print(f"❌ Error starting application: {e}")
    
    def stop(self):
        """Stop the auto-reloader and application."""
        print("\n⏹️  Stopping auto-reloader...")
        
        if self.process:
            try:
                self.process.terminate()
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
            except Exception as e:
                print(f"⚠️  Error stopping process: {e}")
        
        print("👋 Goodbye!")

def main():
    """Main entry point for auto-reloader."""
    reloader = AutoReloader()
    reloader.start()

if __name__ == "__main__":
    main() 