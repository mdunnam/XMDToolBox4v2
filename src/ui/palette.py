"""
XMD ToolBox - UI Palette Builder
Constructs and manages the main ZBrush palette interface.
"""
from zbrush import commands as zbc

from src import callbacks
from src.core import get_config


PALETTE_PATH = "ZScript:XMD_ToolBox"


def _ensure_clean_palette() -> None:
    """
    Close existing palette if present.
    Idempotent—safe to call multiple times.
    """
    if zbc.exists(PALETTE_PATH):
        zbc.close(PALETTE_PATH)


def _create_palette() -> None:
    """Create main palette container."""
    zbc.add_subpalette(PALETTE_PATH, title_mode=0)


def _add_buttons() -> None:
    """Add main action buttons."""
    # Scan / Load buttons
    zbc.add_button(
        f"{PALETTE_PATH}:Scan Assets",
        "Scan and load asset library",
        callbacks.on_scan_assets
    )
    
    zbc.add_button(
        f"{PALETTE_PATH}:Open Asset Browser",
        "Open asset browser dialog",
        callbacks.on_open_asset_browser
    )


def _add_sliders() -> None:
    """Add control sliders."""
    zbc.add_slider(
        f"{PALETTE_PATH}:Asset Scale",
        cur_value=100.0,
        resolution=5,
        min_value=10.0,
        max_value=500.0,
        info="Scale imported assets",
        fn=callbacks.on_asset_scale_changed,
        width=1.0
    )


def _add_switches() -> None:
    """Add toggle switches."""
    config = get_config()
    
    zbc.add_switch(
        f"{PALETTE_PATH}:Auto Scan",
        initial_state=config.get("auto_scan", True),
        info="Automatically scan for new assets on startup",
        fn=callbacks.on_auto_scan_toggled,
        width=1.0
    )


def _add_separator_label() -> None:
    """Add visual separator as disabled button."""
    zbc.add_button(
        f"{PALETTE_PATH}:_separator",
        "",
        initially_disabled=True
    )


def _add_settings_button() -> None:
    """Add settings/config button."""
    zbc.add_button(
        f"{PALETTE_PATH}:Settings",
        "Open settings and preferences",
        callbacks.on_open_settings,
        width=0.5
    )
    
    zbc.add_button(
        f"{PALETTE_PATH}:About",
        "About XMD ToolBox",
        callbacks.on_show_about,
        width=0.5
    )


def build() -> None:
    """
    Build complete UI palette.
    Idempotent—safe to call multiple times.
    """
    _ensure_clean_palette()
    _create_palette()
    
    # Main action area
    _add_buttons()
    
    # Controls
    _add_sliders()
    _add_switches()
    
    # Separator
    _add_separator_label()
    
    # Footer
    _add_settings_button()
    
    # Refresh UI
    zbc.update(redraw_ui=True)
