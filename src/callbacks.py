"""
XMD ToolBox - UI Callbacks
Event handlers for UI buttons, sliders, switches, etc.
Signature patterns:
- Button: fn(sender: str) -> None
- Slider: fn(sender: str, value: float) -> None
- Switch: fn(sender: str, value: bool) -> None
"""
from zbrush import commands as zbc


def on_scan_assets(sender: str) -> None:
    """
    Scan asset library for new models, textures, brushes.
    Triggered by 'Scan Assets' button.
    """
    zbc.message_ok("Asset scanning not yet implemented", "ToolBox")


def on_open_asset_browser(sender: str) -> None:
    """
    Open asset browser dialog.
    Triggered by 'Open Asset Browser' button.
    """
    zbc.message_ok("Asset browser not yet implemented", "ToolBox")


def on_asset_scale_changed(sender: str, value: float) -> None:
    """
    Slider callback: asset scale changed.
    Args:
        sender: Item path (e.g., "ZScript:XMD_ToolBox:Asset Scale")
        value: New scale value (10.0 - 500.0)
    """
    print(f"Asset scale changed to {value:.1f}%")


def on_auto_scan_toggled(sender: str, value: bool) -> None:
    """
    Switch callback: auto-scan toggled.
    Args:
        sender: Item path (e.g., "ZScript:XMD_ToolBox:Auto Scan")
        value: New state (True=on, False=off)
    """
    state = "enabled" if value else "disabled"
    print(f"Auto-scan {state}")


def on_open_settings(sender: str) -> None:
    """
    Open settings/preferences dialog.
    Triggered by 'Settings' button.
    """
    zbc.message_ok("Settings not yet implemented", "ToolBox")


def on_show_about(sender: str) -> None:
    """
    Show about/info dialog.
    Triggered by 'About' button.
    """
    version = "4.0.0"
    msg = f"""XMD ToolBox {version}
Asset Management & Workflow Automation for ZBrush

ZBrush Python SDK 2026.1
© mdunnam"""
    zbc.message_ok(msg, "About XMD ToolBox")
