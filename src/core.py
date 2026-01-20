"""
XMD ToolBox - Core Application Module
Manages state, config, and runtime behavior.
"""
import os
import json
from typing import Any


class Config:
    """
    Configuration manager for ToolBox settings.
    Loads/saves from config.json in the script directory.
    """
    
    DEFAULT_CONFIG = {
        "version": "4.0.0",
        "palette_name": "ZScript:XMD_ToolBox",
        "auto_scan": True,
        "asset_paths": [],
        "recent_files": [],
        "max_recent": 10,
    }
    
    def __init__(self, config_path: str | None = None):
        """
        Initialize config from file or defaults.
        
        Args:
            config_path: Optional path to config.json; defaults to script dir.
        """
        if config_path is None:
            config_path = os.path.join(
                os.path.dirname(os.path.abspath(__file__)), "config.json"
            )
        
        self.path = config_path
        self.data = self._load()
    
    def _load(self) -> dict[str, Any]:
        """Load config from file or return defaults."""
        if os.path.isfile(self.path):
            try:
                with open(self.path, "r") as f:
                    return json.load(f)
            except Exception as e:
                print(f"Warning: Failed to load config: {e}. Using defaults.")
                return self.DEFAULT_CONFIG.copy()
        return self.DEFAULT_CONFIG.copy()
    
    def save(self) -> None:
        """Save current config to file."""
        try:
            os.makedirs(os.path.dirname(self.path), exist_ok=True)
            with open(self.path, "w") as f:
                json.dump(self.data, f, indent=2)
        except Exception as e:
            print(f"Warning: Failed to save config: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get config value by key."""
        return self.data.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """Set config value and save."""
        self.data[key] = value
        self.save()


# Global app state
_config: Config | None = None
_initialized: bool = False


def initialize() -> None:
    """Initialize app state. Idempotent."""
    global _config, _initialized
    
    if _initialized:
        return
    
    _config = Config()
    _initialized = True


def get_config() -> Config:
    """Get global config instance."""
    if _config is None:
        initialize()
    return _config


def is_initialized() -> bool:
    """Check if app is initialized."""
    return _initialized
