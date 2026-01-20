# API Copilot Instructions (ZBrush Python SDK 2026.1)

## Purpose
Author safe, repeatable ToolBox scripts/plugins that respect ZBrush's shared Python VM and GUI-centric API.

## Core Guardrails
- Single embedded Python 3.11.9 VM shared by all scripts; state persists until ZBrush exits.
- Working directory is always the ZBrush install folder; never change it. Use absolute or __file__-relative paths.
- sys.executable is ZBrush; do not spawn it. multiprocessing unsupported; subprocess must not target the VM.
- Do not overwrite sys.stdout/sys.stderr/sys.stdin or mutate shared modules (e.g., sys.modules.clear, math.pi, random.seed).
- Init must be idempotent and fast; PYTHONPATH runs init.py; ZBRUSH_PLUGIN_PATH runs all *.py on startup.

## Imports & Dependencies
- Preferred: bundle deps under libs/; insert libs path, import, then remove; guard sys.modules or rename deps to avoid collisions.
- Alternative: unified global/site-packages with matching Python version (3.11.9); avoid mixed versions.
- Script folders are not auto-added to sys.path; add explicitly and clean up.

## UI API (gui)
- Item paths are case-insensitive and ignore spaces; picker items are addressable by name.
- Build UI with add_palette, add_subpalette, add_button, add_slider, add_switch.
- Callback signatures: button fn(sender: str); slider fn(sender: str, value: float); switch fn(sender: str, value: bool).
- Batch UI actions: consider show_actions(0) and freeze(fn); call update(redraw_ui=True) after renames/path changes.
- Notes: add_note_button/switch before show_note; read via get_from_note.

## Modeling API Constraints
- No direct brush/material/texture data access; drive via UI/file ops.
- Mesh access is shallow: query_mesh3d for counts/bounds/UV tiles; no verts/UVs/normals editing.
- Strokes: replay/transform recorded data via canvas_stroke(s); you cannot synthesize arbitrary points beyond provided stroke strings.
- Curves: write-only (new_curves, add_curve_point, curves_to_ui); cannot read existing.
- Transforms: set_transform/get_transform affect tool-in-canvas (camera-like). Per-subtool transforms via UI item paths (e.g., Tool:Geometry:X Position).
- ZSpheres: all edits inside edit_zsphere; root not deletable; delete children before parents.

## Assets, Maps, Subtools
- Displacement/normal maps: require UVs and correct subd level; call create_displacement_map/create_normal_map with explicit sizes.
- Subtool flags via get_subtool_status/set_subtool_status (visibility, volume modes, folder states).

## Files & Paths
- Always use absolute or script-relative paths; never rely on CWD. Prefer your own path handling over legacy increment_filename/make_filename.
- ZBrush console mis-renders backslashes visually; paths remain valid on disk.

## Timeline
- Times are normalized [0,1]; manage with new_keyframe, set_keyframe_time, set_timeline_time, set_active_track_index.

## Performance & UX
- Minimize UI flicker and console spam; batch work inside freeze; re-enable show_actions(1) after.
- Keep startup code fast; avoid heavy operations in init.

## Style
- PEP 8-ish; line length <= 120; type hints encouraged; keep comprehensions simple.
- Do not hijack hotkeys; only set on your own items (set_hotkey).
- Icons: BMP/PSD; subpalette icon 20px grayscale; validate existence before assigning.

## Safety Checklist (never do)
- Spawn ZBrush/VM via subprocess or use multiprocessing.
- chdir, clear sys.modules, overwrite std streams, or mutate shared builtins/globals.
- Assume script directory is on sys.path.
- Delete native UI items (only remove script-created ones with delete_interface_item).

## Quick Init Pattern
```python
import os
import sys
from zbrush import commands as zbc


def _add_libs() -> str | None:
    libs_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "libs")
    if os.path.isdir(libs_dir):
        sys.path.insert(0, libs_dir)
        return libs_dir
    return None


def _remove_libs(libs_dir: str | None) -> None:
    if libs_dir and libs_dir in sys.path:
        sys.path.remove(libs_dir)


def on_button(sender: str) -> None:
    zbc.message_ok(f"Clicked: {sender}")


def init() -> None:
    if zbc.exists("ZScript:ToolBox"):
        zbc.close("ZScript:ToolBox")
    zbc.add_subpalette("ZScript:ToolBox", title_mode=0)
    zbc.add_button("ZScript:ToolBox:Rescan", "Rescan assets", on_button)
    zbc.add_switch("ZScript:ToolBox:Toggle", True, "Toggle demo", lambda s, v: None)
    zbc.update(redraw_ui=True)


if __name__ == "__main__":
    libs = _add_libs()
    try:
        init()
    finally:
        _remove_libs(libs)
```
