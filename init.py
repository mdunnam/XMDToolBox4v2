"""
XMD ToolBox 4.0 - Main Entry Point
ZBrush Python Plugin for Asset Management & Workflow Automation

Entry point executed when:
1. Plugin loads via PYTHONPATH or ZBRUSH_PLUGIN_PATH
2. User clicks "Load" in ZScript > Python Scripting palette
3. ZBrush startup if registered in init.py paths
"""
import os
import sys

# Add script directory to sys.path so we can import src modules
_script_dir = os.path.dirname(os.path.abspath(__file__))
if _script_dir not in sys.path:
    sys.path.insert(0, _script_dir)

from zbrush import commands as zbc
from src.core import app
from src.ui import palette


def _setup_libs() -> str | None:
    """
    Add local libs directory to sys.path for bundled dependencies.
    Must be cleaned up in finally block.
    """
    libs_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "libs")
    if os.path.isdir(libs_dir):
        sys.path.insert(0, libs_dir)
        return libs_dir
    return None


def _teardown_libs(libs_dir: str | None) -> None:
    """Remove libs directory from sys.path."""
    if libs_dir and libs_dir in sys.path:
        sys.path.remove(libs_dir)


def main() -> None:
    """
    Main initialization. Idempotent—safe to call multiple times.
    """
    try:
        # Initialize app state/config
        app.initialize()
        
        # Build UI palette
        palette.build()
        
        print("✓ XMD ToolBox 4.0 initialized successfully")
        
    except Exception as e:
        error_msg = f"ToolBox initialization failed:\n{str(e)}"
        print(f"✗ {error_msg}")
        zbc.message_ok(error_msg, "ToolBox Error")
        raise


if __name__ == "__main__":
    libs = _setup_libs()
    try:
        main()
    finally:
        _teardown_libs(libs)
        # Clean up script dir from sys.path
        if _script_dir in sys.path:
            sys.path.remove(_script_dir)
