"""
Configuration and constants for the Task Tracker application.
"""
import os
from typing import Dict, Any

# Database Configuration
DATABASE_NAME = 'tasks.db'

# Store the database in the user's AppData\Local\MyTaskApp directory for persistence
APP_NAME = 'SoulPlanner'
appdata_dir = os.path.join(os.environ.get('LOCALAPPDATA', os.path.expanduser('~')), APP_NAME)
os.makedirs(appdata_dir, exist_ok=True)
DATABASE_PATH = os.path.join(appdata_dir, DATABASE_NAME)

# Application Settings
APP_VERSION = "2.0.0"
DEFAULT_WINDOW_SIZE = "1200x800"
MIN_WINDOW_SIZE = "800x600"

# Theme Configuration
THEMES = {
    "light": {
        "name": "flatly",
        "primary_color": "#2563eb",
        "secondary_color": "#64748b",
        "success_color": "#22c55e",
        "warning_color": "#f59e0b",
        "danger_color": "#ef4444",
        "background_color": "#ffffff",
        "surface_color": "#f8fafc",
        "text_primary": "#1e293b",
        "text_secondary": "#64748b",
        "border_color": "#e2e8f0",
        "shadow_color": "#e0e4ea"
    },
    "dark": {
        "name": "darkly",
        "primary_color": "#3b82f6",
        "secondary_color": "#94a3b8",
        "success_color": "#10b981",
        "warning_color": "#f59e0b",
        "danger_color": "#ef4444",
        "background_color": "#0f172a",
        "surface_color": "#1e293b",
        "text_primary": "#f1f5f9",
        "text_secondary": "#94a3b8",
        "border_color": "#334155",
        "shadow_color": "#1e293b"
    }
}

# Task Status Configuration
TASK_STATUSES = [
    "Not Started",
    "Working on it", 
    "Stuck",
    "Done"
]

STATUS_COLORS = {
    "Not Started": "#94a3b8",
    "Working on it": "#f59e0b",
    "Stuck": "#ef4444",
    "Done": "#10b981"
}

# UI Configuration
FONTS = {
    "primary": ("Segoe UI", 11),
    "primary_bold": ("Segoe UI", 11, "bold"),
    "secondary": ("Segoe UI", 10),
    "heading": ("Segoe UI", 16, "bold"),
    "title": ("Segoe UI", 20, "bold"),
    "caption": ("Segoe UI", 9)
}

# Animation Configuration
ANIMATION_DURATION = 200  # milliseconds
FADE_DURATION = 15  # steps for fade animation

# Search Configuration
SEARCH_DELAY = 300  # milliseconds before triggering search

# Notification Configuration
NOTIFICATION_DURATION = 3000  # milliseconds

# File Paths
ASSETS_DIR = os.path.join(os.path.dirname(__file__), "assets")
ICONS_DIR = os.path.join(ASSETS_DIR, "icons") if os.path.exists(ASSETS_DIR) else None

# Default Project
DEFAULT_PROJECT = "learning"

# Validation Rules
MAX_TITLE_LENGTH = 100
MAX_NOTES_LENGTH = 500
MAX_OWNER_LENGTH = 50

# Performance Settings
BATCH_SIZE = 50  # Number of tasks to load at once
CACHE_DURATION = 300  # seconds 