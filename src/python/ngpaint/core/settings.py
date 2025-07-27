"""
Settings management for Next-Gen Paint
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional


class Settings:
    """Application settings manager"""
    
    def __init__(self, config_file: Optional[str] = None):
        """Initialize settings with optional config file path"""
        if config_file is None:
            # Default config location
            config_dir = Path.home() / ".ngpaint"
            config_dir.mkdir(exist_ok=True)
            config_file = config_dir / "settings.json"
        
        self.config_file = Path(config_file)
        self._settings = self._load_default_settings()
        self.load()
    
    def _load_default_settings(self) -> Dict[str, Any]:
        """Load default application settings"""
        return {
            "ui": {
                "theme": "dark",
                "window_size": [1200, 800],
                "window_position": [100, 100],
                "toolbar_visible": True,
                "statusbar_visible": True,
                "panels": {
                    "tools": True,
                    "layers": True,
                    "properties": True,
                    "color": True
                }
            },
            "canvas": {
                "default_width": 1920,
                "default_height": 1080,
                "default_dpi": 300,
                "background_color": [255, 255, 255, 255],
                "grid_enabled": False,
                "grid_size": 20,
                "snap_to_grid": False
            },
            "tools": {
                "brush_size": 10,
                "brush_hardness": 0.8,
                "brush_opacity": 1.0,
                "eraser_size": 20,
                "eraser_hardness": 0.5,
                "eyedropper_sample_size": 1
            },
            "performance": {
                "tile_size": 256,
                "max_undo_steps": 50,
                "auto_save_interval": 300,  # seconds
                "memory_limit_mb": 1024
            },
            "file": {
                "default_format": "png",
                "recent_files": [],
                "max_recent_files": 10,
                "auto_save_enabled": True
            }
        }
    
    def load(self) -> None:
        """Load settings from file"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded_settings = json.load(f)
                    self._merge_settings(loaded_settings)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Warning: Could not load settings from {self.config_file}: {e}")
    
    def save(self) -> None:
        """Save settings to file"""
        try:
            # Ensure directory exists
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self._settings, f, indent=2, ensure_ascii=False)
        except IOError as e:
            print(f"Error: Could not save settings to {self.config_file}: {e}")
    
    def _merge_settings(self, loaded_settings: Dict[str, Any]) -> None:
        """Merge loaded settings with defaults, preserving structure"""
        def merge_dict(target: Dict[str, Any], source: Dict[str, Any]) -> None:
            for key, value in source.items():
                if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                    merge_dict(target[key], value)
                else:
                    target[key] = value
        
        merge_dict(self._settings, loaded_settings)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a setting value using dot notation (e.g., 'ui.theme')"""
        keys = key.split('.')
        value = self._settings
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key: str, value: Any) -> None:
        """Set a setting value using dot notation (e.g., 'ui.theme')"""
        keys = key.split('.')
        target = self._settings
        
        # Navigate to the parent of the target key
        for k in keys[:-1]:
            if k not in target:
                target[k] = {}
            target = target[k]
        
        # Set the value
        target[keys[-1]] = value
    
    def reset_to_defaults(self) -> None:
        """Reset all settings to default values"""
        self._settings = self._load_default_settings()
        self.save()
    
    def get_all(self) -> Dict[str, Any]:
        """Get all settings as a dictionary"""
        return self._settings.copy() 