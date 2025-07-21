"""
Theme management for the Task Tracker application.
"""
import tkinter as tk
from tkinter import ttk
import ttkbootstrap as tb
from typing import Dict, Any, Callable
from config import THEMES, FONTS

class ThemeManager:
    """Manages application themes and provides dynamic theme switching."""
    
    def __init__(self, root: tb.Window):
        self.root = root
        self.current_theme = "light"
        self.theme_callbacks = []
        self._setup_themes()
    
    def _setup_themes(self):
        """Setup custom theme styles."""
        style = ttk.Style()
        
        # Configure base styles for both themes
        for theme_name, theme_config in THEMES.items():
            self._configure_theme_styles(style, theme_name, theme_config)
    
    def _configure_theme_styles(self, style: ttk.Style, theme_name: str, theme_config: Dict[str, Any]):
        """Configure styles for a specific theme."""
        theme_prefix = f"{theme_name}."
        
        # Modern Entry Style
        style.configure(
            f"{theme_prefix}Modern.TEntry",
            font=FONTS["primary"],
            padding=(12, 8),
            borderwidth=1,
            relief="flat",
            foreground=theme_config["text_primary"],
            fieldbackground=theme_config["background_color"],
            background=theme_config["background_color"],
            bordercolor=theme_config["border_color"],
            insertcolor=theme_config["text_primary"],
            insertwidth=2,
            lightcolor=theme_config["background_color"],
            darkcolor=theme_config["background_color"],
            highlightthickness=0,
            focuscolor=theme_config["primary_color"],
        )
        
        # Modern Button Styles
        style.configure(
            f"{theme_prefix}Modern.Primary.TButton",
            font=FONTS["primary_bold"],
            foreground="white",
            background=theme_config["primary_color"],
            borderwidth=0,
            padding=(16, 10),
            relief="flat",
        )
        
        style.configure(
            f"{theme_prefix}Modern.Secondary.TButton",
            font=FONTS["primary_bold"],
            foreground=theme_config["primary_color"],
            background=theme_config["background_color"],
            borderwidth=1,
            bordercolor=theme_config["primary_color"],
            padding=(16, 10),
            relief="flat",
        )
        
        # Card Frame Style
        style.configure(
            f"{theme_prefix}Card.TFrame",
            background=theme_config["background_color"],
            borderwidth=1,
            relief="flat",
            bordercolor=theme_config["border_color"],
        )
        
        # Modern Treeview Style
        style.configure(
            f"{theme_prefix}Modern.Treeview",
            font=FONTS["primary"],
            rowheight=40,
            background=theme_config["background_color"],
            fieldbackground=theme_config["background_color"],
            foreground=theme_config["text_primary"],
            borderwidth=0,
            relief="flat",
        )
        
        style.configure(
            f"{theme_prefix}Modern.Treeview.Heading",
            font=FONTS["primary_bold"],
            background=theme_config["surface_color"],
            foreground=theme_config["text_primary"],
            borderwidth=0,
            relief="flat",
            padding=(8, 12),
        )
        
        # Status Pill Styles
        for status, color in theme_config.get("status_colors", {}).items():
            style.configure(
                f"{theme_prefix}Status.{status}.TLabel",
                font=FONTS["secondary"],
                foreground="white",
                background=color,
                borderwidth=0,
                relief="flat",
                padding=(8, 4),
            )
    
    def switch_theme(self, theme_name: str = None):
        """Switch to a different theme."""
        if theme_name is None:
            # Toggle between light and dark
            theme_name = "dark" if self.current_theme == "light" else "light"
        
        if theme_name not in THEMES:
            return
        
        self.current_theme = theme_name
        theme_config = THEMES[theme_name]
        
        # Update the root window theme
        self.root.style.theme_use(theme_config["name"])
        
        # Update window background
        self.root.configure(bg=theme_config["background_color"])
        
        # Notify all registered callbacks
        for callback in self.theme_callbacks:
            try:
                callback(theme_name, theme_config)
            except Exception as e:
                print(f"Error in theme callback: {e}")
    
    def get_current_theme_config(self) -> Dict[str, Any]:
        """Get the current theme configuration."""
        return THEMES[self.current_theme]
    
    def register_theme_callback(self, callback: Callable[[str, Dict[str, Any]], None]):
        """Register a callback to be called when theme changes."""
        self.theme_callbacks.append(callback)
    
    def unregister_theme_callback(self, callback: Callable[[str, Dict[str, Any]], None]):
        """Unregister a theme callback."""
        if callback in self.theme_callbacks:
            self.theme_callbacks.remove(callback)
    
    def get_color(self, color_name: str) -> str:
        """Get a color from the current theme."""
        theme_config = self.get_current_theme_config()
        return theme_config.get(color_name, "#000000")
    
    def create_theme_button(self, parent: tk.Widget, **kwargs) -> ttk.Button:
        """Create a theme toggle button."""
        button = ttk.Button(
            parent,
            text="🌙" if self.current_theme == "light" else "☀️",
            style=f"{self.current_theme}.Modern.Secondary.TButton",
            command=self.switch_theme,
            **kwargs
        )
        
        # Update button text when theme changes
        def update_button(theme_name: str, theme_config: Dict[str, Any]):
            button.configure(
                text="🌙" if theme_name == "light" else "☀️",
                style=f"{theme_name}.Modern.Secondary.TButton"
            )
        
        self.register_theme_callback(update_button)
        return button 