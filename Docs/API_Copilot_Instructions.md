# ZBrush Python SDK 2026.1 - Complete API Reference

## Runtime Environment (Python 3.11.9)

### VM Characteristics
- **Embedded Interpreter**: Python VM runs inside ZBrush.exe/ZBrushMac.app; not a separate process.
- **Persistent State**: Single shared VM for all scripts/plugins; state persists until ZBrush exits.
- **Working Directory**: Always the ZBrush install folder (where executable lives); never `chdir`.
- **sys.executable**: Points to ZBrush binary, not Python; cannot be called with Python CLI args.
- **Module Search Paths**: Script folders NOT auto-added to `sys.path`; must add explicitly and clean up.
- **Stream Handlers**: Custom redirects to ZBrush console; do not overwrite `sys.stdout/stderr/stdin`.

### Unsupported Features
- `multiprocessing` module (spawns new VMs/ZBrush instances).
- `subprocess` targeting `sys.executable` (same reason).
- Third-party libs requiring process spawning.
- Overwriting stream handlers or mutating shared module state (`sys.modules.clear`, `math.pi`, `random.seed`).

### Environment Variables
- **PYTHONPATH**: Adds module search paths; auto-executes any `init.py` found in those dirs at startup.
- **ZBRUSH_PLUGIN_PATH**: Executes all `*.py` files in defined dirs at startup (not just `init.py`).

## Script Execution Methods

### 1. Load Button (Interactive)
- ZScript palette → Python Scripting sub-palette → Load/Reload buttons.
- Script Window Mode must be set to "Python Output" for console visibility.

### 2. Command Line
```bash
ZBrush.exe -script "C:\path\script.py" "arg1" "arg2" "lastArgIsZPROrZTL"
```

### 3. Auto-Run (Plugin)
- Place scripts in `PYTHONPATH` dirs (as `init.py`) or `ZBRUSH_PLUGIN_PATH` dirs (as `*.py`).
- Scripts execute on ZBrush startup.

### 4. Macro Recording
- Python Scripting sub-palette: New Macro / End Macro.
- Records UI actions into Python script; saves as macro button in console.

## Path Handling Rules

### Always Use Absolute Paths
```python
import os

# WRONG: Relative to CWD (ZBrush install dir, not script dir)
with open("my_file.txt", "r") as f:
    data = f.read()

# CORRECT: Script-relative absolute path
script_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(script_dir, "my_file.txt")
with open(file_path, "r") as f:
    data = f.read()
```

### Path Resolution Helpers
- `zbrush.commands.resolve_path(relative_path)` - makes path absolute relative to executing module.
- Prefer Python's `os.path` for clarity; `resolve_path` is ZScript legacy.

### Known Issue: Console Backslash Rendering
- ZBrush console mis-renders backslashes visually (`\` shows as missing).
- Paths remain valid on disk; this is display-only bug.
- Use raw strings: `r"C:\path\to\file.txt"` or forward slashes on Windows.

## Importing Libraries - Three Strategies

### Strategy 1: Local Dependencies (Recommended)
Bundle deps under `libs/`; modify `sys.path` at runtime; guard `sys.modules` to avoid collisions.

#### Complex Approach (Full Isolation)
```python
import os
import sys

# Add libs to search path
libs_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "libs")
if not os.path.isdir(libs_dir):
    raise FileNotFoundError(f"libs directory not found: {libs_dir}")

sys.path.insert(0, libs_dir)

# Store original module states to prevent conflicts
module_states = {}
try:
    # Remove conflicting modules temporarily
    for name in ["requests", "urllib3"]:
        module_states[name] = sys.modules.pop(name, None)
    
    from libs import requests
    from libs import urllib3

finally:
    # Restore original sys.modules state
    if libs_dir in sys.path:
        sys.path.remove(libs_dir)
    for name, module in module_states.items():
        if module is not None:
            sys.modules[name] = module
        else:
            sys.modules.pop(name, None)
```

#### Simple Approach (Renamed Deps)
```python
import os
import sys

libs_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "libs")
sys.path.insert(0, libs_dir)

# Rename deps to avoid collisions: libs/my_plugin_requests/
from libs import my_plugin_requests as requests
from libs import my_plugin_urllib3 as urllib3

# Clean up
if libs_dir in sys.path:
    sys.path.remove(libs_dir)
```

### Strategy 2: Global Dependencies
Copy deps to ZBrush global module path (visible in startup console or via Python `sys.path`).

**Pros**: Single version for all plugins; simplest to implement.  
**Cons**: Version conflicts if plugins need different versions; manual install required.

```python
# Just import normally; deps already on sys.path
import requests
import urllib3
```

### Strategy 3: External Package Manager (pip)
Use external CPython 3.11.9 to install into custom site-packages; add to `sys.path` at runtime.

```bash
# External command (not in ZBrush)
mkdir -p '/Applications/ZBrush/ZData/Python/site-packages'
pip install --target '/Applications/ZBrush/ZData/Python/site-packages' requests
```

```python
import os
import sys

site_packages = os.path.join(os.path.dirname(sys.executable), "ZData", "Python", "site-packages")
if not os.path.isdir(site_packages):
    raise FileNotFoundError(f"site-packages not found: {site_packages}")

sys.path.insert(0, site_packages)
import requests

# Clean up
if site_packages in sys.path:
    sys.path.remove(site_packages)
```

**Note**: pip cannot run inside ZBrush VM; requires matching external Python 3.11.9.

## GUI API - Complete Reference

### Core Concepts

#### Item Paths
- Colon-delimited labels from UI (e.g., `"Tool:Geometry:Divide"`).
- Case-insensitive; spaces ignored (`"Tool:Geometry:Divide"` == `"tool:geometry:divide"`).
- Picker items (brushes, tools, materials) addressable by name even if not visible.
- Empty path `""` refers to Tutorial View.

#### Palettes & Sub-palettes
- **Palette**: Top-level menu/tearable window (e.g., Tool, Transform, ZScript).
- **Sub-palette**: Nested section within palette (e.g., Tool > Geometry).
- Can contain buttons, sliders, switches; labels/images emulated via disabled buttons.

#### Notes (Modal Dialogs)
- Modal windows requiring user interaction before continuing.
- Build with `add_note_button` / `add_note_switch` before calling `show_note`.
- Read values after close via `get_from_note`.

### Creating UI Elements

#### add_palette
```python
zbrush.commands.add_palette(
    item_path: str,
    docking_bar: int,  # 0=left, 1=right
    shortcut: str = ""
) -> bool
```

#### add_subpalette
```python
zbrush.commands.add_subpalette(
    item_path: str,
    title_mode: int = 0,  # 0=title+minimize, 1=title only, 2=hidden
    icon_path: str = "",  # BMP/PSD, 20px grayscale for sub-palette
    left_inset: float = 0.0,
    right_inset: float = 0.0,
    top_inset: float = 0.0,
    bottom_inset: float = 0.0
) -> bool
```

#### add_button
```python
zbrush.commands.add_button(
    item_path: str,
    info: str = "",  # Bubble help tooltip
    fn: Callable[[str], None] = None,  # Callback: fn(sender: str) -> None
    initially_disabled: bool = False,
    width: float = 0.0,  # 0=auto-width
    hotkey: str = "",
    icon_path: str = "",  # BMP/PSD
    height: float = 0.0  # 0=auto-height
) -> bool
```

#### add_slider
```python
zbrush.commands.add_slider(
    item_path: str,
    cur_value: float,
    resolution: int,  # 0=continuous, >0=snap steps
    min_value: float,
    max_value: float,
    info: str = "",
    fn: Callable[[str, float], None] = None,  # fn(sender: str, value: float) -> None
    initially_disabled: bool = False,
    width: float = 0.0,
    height: float = 0.0
) -> bool
```

#### add_switch
```python
zbrush.commands.add_switch(
    item_path: str,
    initial_state: bool,
    info: str = "",
    fn: Callable[[str, bool], None] = None,  # fn(sender: str, value: bool) -> None
    initially_disabled: bool = False,
    width: float = 0.0,
    height: float = 0.0,
    icon_path: str = ""
) -> bool
```

### Notes (Modal Dialogs)

#### Building Notes
```python
# Add controls before showing note
zbrush.commands.add_note_button(
    name: str,
    icon_path: str = "",
    initially_pressed: bool = False,
    initially_disabled: bool = False,
    h_rel_position: float = 0.0,  # 0=auto, +left, -right
    v_rel_position: float = 0.0,  # 0=auto, +top, -bottom
    width: float = 0.0,
    height: float = 0.0,
    bg_color: int = -1,  # (blue + green*256 + red*65536), -1=default
    text_color: int = -1,
    bg_opacity: float = 1.0,
    text_opacity: float = 1.0,
    img_opacity: float = 1.0
) -> bool

zbrush.commands.add_note_switch(
    name: str,
    icon_path: str = "",
    initially_pressed: bool = False,
    initially_disabled: bool = False,
    # ... same optional params as add_note_button
) -> bool

# Show note; returns button ID clicked (1-indexed)
zbrush.commands.show_note(
    text: str,  # Title
    item_path: str = "",  # No effect
    display_duration: float = 0.0,  # 0=wait, -1=combine with next, >0=auto-close secs
    bg_color: int = -1,
    distance_to_ui_item: int = 48,  # No effect
    preferred_width: int = 400,  # No effect
    fill_color: int = -1,  # No effect
    frame_h_size: float = 1.0,  # No effect
    frame_v_size: float = 1.0,  # No effect
    frame_left_side: float = 0.0,  # No effect
    frame_top_side: float = 0.0,  # No effect
    icon_path: str = ""
) -> int  # Button ID (1-indexed) or <=0 for ESC/Enter

# Read note values after close
zbrush.commands.get_from_note(index: int | str) -> Any
```

#### Note Example
```python
from zbrush import commands as zbc

# Button IDs are 1-indexed in order added
ID_COLOR = 2
ID_CLOSE = 3

states = ["Red", "Green", "Blue"]
current = states[0]

while True:
    zbc.add_note_button("Color:", initially_disabled=True, bg_opacity=0)  # ID 1
    zbc.add_note_button(current)  # ID 2
    zbc.add_note_button("Close")  # ID 3
    
    result = zbc.show_note("Select Color")
    
    if result == ID_COLOR:
        current = states[(states.index(current) + 1) % len(states)]
    elif result == ID_CLOSE or result <= 0:
        break
```

### System Dialogs
```python
# File dialogs
zbrush.commands.ask_filename(
    extensions: str,  # "Label A (*.ext1)|*.ext1|Label B (*.ext2)|*.ext2"
    default_file_name: str = "",  # Empty=open, non-empty=save
    title: str = ""
) -> str  # Full path or empty if canceled

# Text input
zbrush.commands.ask_string(
    initial_string: str = "",
    title: str = ""
) -> str

# Messages
zbrush.commands.message_ok(message: str = "", title: str = "") -> None
zbrush.commands.message_ok_cancel(message: str = "", title: str = "") -> bool  # True=OK
zbrush.commands.message_yes_no(message: str = "", title: str = "") -> bool  # True=YES
zbrush.commands.message_yes_no_cancel(message: str = "", title: str = "") -> int  # 1=YES, 0=NO, -1=CANCEL
```

### Getters
```python
exists(item_path: str) -> bool
get(item_path: str) -> float  # Primary value (0.0 for non-value items)
get_secondary(item_path: str) -> float  # E.g., y-component of 2D control
get_status(item_path: str) -> bool  # Enabled/disabled
get_title(item_path: str, full_path: bool = False) -> str
get_info(item_path: str) -> str  # Bubble help
get_hotkey(item_path: str) -> str
get_id(item_path: str) -> int
get_min(item_path: str) -> float
get_max(item_path: str) -> float
get_mod(item_path: str) -> int  # Modifier flags (e.g., XYZ on deformation sliders)
get_width(item_path: str) -> float
get_height(item_path: str) -> int
get_pos(item_path: str, global_coordinates: bool = False) -> float  # Horizontal position
get_flags(item_path: str) -> int  # [Private] Status bitfield

# Canvas/Mouse
get_canvas_pan() -> tuple[float, float]  # (h_offset, v_offset)
get_canvas_zoom() -> float
get_mouse_pos(global_coordinates: bool = False) -> tuple[float, float]
get_left_mouse_button_state() -> bool
```

### Setters
```python
set(item_path: str, h_value: float | None = None, v_value: float | None = None) -> None
set_status(item_name: str, value: bool) -> None  # Script-created items only
set_min(item_path: str, value: float) -> None  # Script-created items only
set_max(item_path: str, value: float) -> None  # Script-created items only
set_mod(item_path: str, value: float) -> None  # Script-created items only
set_hotkey(item_path: str, hotkey: str) -> None
set_canvas_pan(h: float, v: float) -> None
set_canvas_zoom(zoom_factor: float) -> None
set_color(r: int, g: int, b: int) -> None  # Primary color picker [0, 255]
set_notebar_text(text: str, progress: float = 0.0) -> None  # Top progress bar
```

### Interaction
```python
press(item_path: str) -> None
un_press(item_path: str) -> None
toggle(item_path: str) -> None
click(item_path: str, X1=None, Y1=None, X2=None, Y2=None, ...) -> None  # Click with optional drag
canvas_click(X1: float, Y1: float, X2=None, Y2=None, ...) -> None

enable(item_path: str) -> None  # Script-created items only
disable(item_path: str) -> None  # Script-created items only
lock(item_path: str) -> None  # All items
unlock(item_path: str) -> None  # All items

show(item_path: str, show_zoom_rects: bool = False, parent_window: bool = False) -> None
hide(item_path: str, show_zoom_rects: bool = False, parent_window: bool = False) -> None
maximize(item_path: str, maximize_all: bool = False) -> None
minimize(item_path: str, minimize_all: bool = False) -> None
close(item_path: str, show_zoom_rects: bool = False, parent_window: bool = False) -> None
delete_interface_item(item_path: str) -> bool  # Script-created gadgets only; not palettes

# Performance
show_actions(value: int) -> None  # 0=hide script UI actions, 1=show
freeze(fn: Callable, fade_time: float = 0.0) -> None  # Disable UI updates during fn
update(repeat_count: int = 1, redraw_ui: bool = False) -> None
reset(item: int = 0, version: float = 1.5) -> int  # 0=all, 1=UI, 2=doc, 3=tools, 4=lights, 5=materials, 6=stencils
```

### State Testing
```python
is_enabled(item_path: str) -> bool
is_disabled(item_path: str) -> bool
is_locked(item_path: str) -> bool
is_unlocked(item_path: str) -> bool
```

### Color Helpers
```python
zbrush.commands.rgb(r: int, g: int, b: int) -> int  # (blue + green*256 + red*65536)
```

## Modeling API - Data Access & Manipulation

### Constraints
- **No direct mesh editing**: Cannot manipulate verts/edges/faces/UVs programmatically.
- **Metadata only**: `query_mesh3d` provides counts, bounds, UV tile info—not geometry data.
- **Strokes are replay-only**: Transform/replay recorded strokes; cannot synthesize arbitrary point data.
- **Curves are write-only**: Can create/commit curves; cannot read existing curve data.
- **File I/O required**: For deep mesh edits, export to OBJ/FBX, edit externally, re-import.

### Strokes

#### Stroke Class
```python
class zbrush.commands.Stroke:
    def __init__(string: str) -> None  # From recorded stroke string
    def __repr__() -> str  # Returns stroke string

class zbrush.commands.Strokes:
    def __init__(string: str) -> None  # Multiple strokes
    def __repr__() -> str
```

#### Applying Strokes
```python
canvas_stroke(
    stroke: Stroke,
    delayed: bool | None = None,
    rotation: float | None = None,  # Degrees
    h_scale: float | None = None,   # 1.0 = 100%
    v_scale: float | None = None,
    h_offset: float | None = None,  # Canvas pixels
    v_offset: float | None = None,
    h_rot_center: float | None = None,
    v_rot_center: float | None = None
) -> bool

canvas_strokes(strokes: Strokes, ...) -> bool  # Same params
```

#### Stroke Info
```python
get_last_stroke() -> Stroke

get_stroke_info(stroke: Stroke, info: int, index: int = 0) -> float
# info: 0=point_count, 1=h_pos[index], 2=v_pos[index], 3=pressure[index],
#       4=min_x, 5=min_y, 6=max_x, 7=max_y, 8=max_radius, 9=farthest_point_idx,
#       10=max_h_delta, 11=max_v_delta, 12=total_length, 13=twirl_count,
#       14=delta_z, 15=modifier_key[index]

load_stroke(path: str) -> Stroke
load_strokes(path: str) -> Strokes
```

### Curves (Write-Only)
```python
new_curves() -> None  # Creates new list; deletes previous
add_new_curve() -> int  # Returns 0-indexed curve ID or -1
add_curve_point(curve_index: int, x: float, y: float, z: float) -> int  # Returns point index or -1
curves_to_ui() -> int  # Commits to active brush; 0=success, -1=fail
delete_curves() -> None
```

### Tools & Subtools

#### Tool Selection & Info
```python
get_tool_count() -> int
get_active_tool_index() -> int  # 0-indexed; -1=error
get_active_tool_path() -> str  # Name or full path
get_tool_path(index: int = -1) -> str  # -1=active tool
set_tool_path(index: int, path: str) -> int  # 0=success; path/name (no ext)
select_tool(index: int) -> int  # 0=success

# Shortcut: press tool by name
# zbc.press("Tool:Sphere3D")
```

#### Subtool Management
```python
get_subtool_count(index: int = -1) -> int  # -1=active tool
get_active_subtool_index() -> int  # 0-indexed in Tool:Subtool list
select_subtool(index: int = -1) -> int  # 0=success

get_subtool_id(index: int = -1, subToolIndex: int = -1) -> int  # Unique ID
locate_subtool(id: int) -> int  # Find by ID; -1=not found
locate_subtool_by_name(name: str) -> int  # Find by name; -1=not found

get_subtool_folder_index(index: int = -1) -> int
get_subtool_folder_name(index: int = -1) -> str

# Status flags (bitmask)
get_subtool_status(index: int = -1) -> int
set_subtool_status(index: int = -1, value: int = 0) -> None
# Masks: 0x0001=eye, 0x0002=folder_eye, 0x0010=volume_add, 0x0020=volume_sub,
#        0x0040=volume_clip, 0x0080=volume_start, 0x0400=folder_closed, 0x0800=folder_open
```

### Mesh Queries (Metadata Only)
```python
query_mesh3d(property: int, index: int | None = None) -> list[float]
# property: 0=point_count, 1=face_count,
#           2=bbox(index: 0=visible_current, 1=full_current, 2=visible_all, 3=full_all),
#           3=uv_bbox, 4=first_uv_tile_id, 5=next_uv_tile_id(index),
#           6=uv_tile_polygon_count(index), 7=uv_tile_area(index), 8=full_mesh_area

get_polymesh3d_area() -> float
get_polymesh3d_volume() -> float
is_polymesh3d_solid() -> bool  # Watertight check

pixol_pick(component: int, h_position: float, v_position: float) -> float
# component: 0=hex_color, 1=z_depth(broken), 2=red[0-255], 3=green, 4=blue,
#            5=material_idx, 6=normal_x[-1,1], 7=normal_y, 8=normal_z
```

### Transforms

#### Tool Transform (Camera-Like)
```python
get_transform() -> list[float]
# [x_pos, y_pos, z_pos, x_scale, y_scale, z_scale, x_rot_deg, y_rot_deg, z_rot_deg]

set_transform(
    x_position: float | None = None,
    y_position: float | None = None,
    z_position: float | None = None,
    x_scale: float | None = None,
    y_scale: float | None = None,
    z_scale: float | None = None,
    x_rotate: float | None = None,  # Degrees
    y_rotate: float | None = None,
    z_rotate: float | None = None
) -> None

# Note: Affects tool-in-canvas (viewport), not geometry.
# For per-subtool geometry transforms, use UI item paths:
# zbc.set("Tool:Geometry:X Position", value)
```

#### Transpose Tools
```python
is_transpose_shown() -> bool

get_transpose() -> list[float]
# [origin_x, origin_y, origin_z, normal_x, normal_y, normal_z, length,
#  red_axis_x, red_axis_y, red_axis_z, green_axis_x, green_axis_y, green_axis_z,
#  blue_axis_x, blue_axis_y, blue_axis_z]

set_transpose(
    x_start=None, y_start=None, z_start=None,  # Origin
    x_end=None, y_end=None, z_end=None,        # Normal (not endpoint)
    length=None,
    x_red=None, y_red=None, z_red=None,
    x_green=None, y_green=None, z_green=None,
    x_blue=None, y_blue=None, z_blue=None
) -> None
```

### ZSpheres (Must Edit Inside Context)
```python
edit_zsphere(commands: Callable, store_undo: bool = False) -> None

# Inside edit_zsphere context:
add_zsphere(
    x: float, y: float, z: float, radius: float,
    parent_index: int,
    color: int = -1,  # (blue + green*256 + red*65536)
    mask: int = 0,    # [0, 255]; 0=unmasked
    time_stamp: int = 0,
    flags: int = 0    # 0=default, 1=invisible_link
) -> int  # Index or -1

delete_zsphere(index: int) -> int  # 0=success; root (0) not deletable; delete children first

get_zsphere(property: int, index: int, sub_index: int) -> float
# property: 0=total_count, 1=x, 2=y, 3=z, 4=radius, 5=color, 6=mask, 7=parent_idx,
#           8=last_click_idx, 9=timestamp, 10=child_count, 11=sub_idx, 12=timestamp_count,
#           13=timestamp_idx, 14=flags, 15=twist_angle, 16=membrane, 17=x_res, 18=y_res,
#           19=z_res, 20=xyz_res, 21=user_value

set_zsphere(property: int, index: int, value: float) -> int  # 0=success
# Settable: 1-7, 9, 14-21; Read-only: 0, 8, 10-13
```

### Maps
```python
create_displacement_map(
    width: int, height: int,
    smooth: bool = True,
    sub_poly: int = 0,
    border: int = 8,
    uv_tile: int = 1000000,  # 1000000=ignore tiles
    use_hd: bool = True
) -> None  # Requires UVs and correct subd level

create_normal_map(
    width: int, height: int,
    smooth: bool = True,
    sub_poly: int = 0,
    border: int = 8,
    uv_tile: int = 1000000,
    local_coordinates: bool = False  # False=world, True=tangent
) -> None
```

## System API - Files, Config, Timeline

### File Handling
```python
# Last used/typed paths (full paths, not just names)
get_last_typed_filename() -> str  # User entered via dialog/typing
get_last_used_filename() -> str   # Any file operation

# Preset for next dialog
set_next_filename(path: str = "", template_path: str = "") -> None
get_next_filename() -> str
has_next_filename() -> bool

# Path resolution
resolve_path(path: str) -> str  # Relative to executing module dir

# Filename helpers (prefer Python's os.path)
increment_filename(base: str, digits: int = 3, add_copy: bool = False) -> str
make_filename(base: str, index: int, digits: int = 0) -> str
```

### Configuration
```python
config(version: float) -> None  # Set ZBrush to version config (e.g., 2026.0)
reset(item: int = 0, version: float = 1.5) -> int
# item: 0=all, 1=UI, 2=doc, 3=tools, 4=lights, 5=materials, 6=stencils
```

### System Info
```python
system_info() -> str  # CPU/RAM info (may truncate)

zbrush_info(info: int) -> float
# 0=version, 1=type(0=demo,1=beta,2=full), 2=runtime_secs, 3=phys_mem_mb, 4=virt_mem_mb,
# 5=free_mem_mb, 6=os(0=PC,1=Mac,2=MacOSX), 7=session_id, 8=total_ram_bytes(broken),
# 9-15=year/month/day/hour/min/sec/day_of_week, 16=cpu_bit_depth
```

### Random
```python
randomize(seed: int) -> None  # [0, 32767]; affects all plugins!
zbrush.zscript_compatibility.rand(value: float) -> float  # [0, value); prefer random.uniform
zbrush.zscript_compatibility.rand_int(value: float) -> int  # [0, value]; prefer random.randint
```

### Interpolation
```python
interpolate(
    time: float,  # [0, 1]
    v1: float | list[float],
    v2: float | list[float],
    v3: float | list[float] | None = None,
    v4: float | list[float] | None = None,
    as_angle: bool = False
) -> float | list[float]
# 2 args: linear (v1, v2)
# 3 args: quadratic (v1, bias=v3, v2)
# 4 args: cubic (left_tangent=v1, v2, v3, right_tangent=v4)
```

### Python Execution
```python
zbrush.utils.run_path(script_path: str, shared_environment: bool = True) -> bool
zbrush.utils.run_script(script: str, shared_environment: bool = True) -> bool
zbrush.utils.clear_output() -> None  # Clears console; affects all users
```

### Timeline (Normalized Times [0,1])
```python
# Keyframes
new_keyframe(time: float | None) -> int  # Index or -1
delete_keyframe(frame_index: int) -> int  # Remaining count or -1
get_keyframes_count() -> int
get_keyframe_time(frame_index: int) -> float  # [0,1] or -1
set_keyframe_time(frame_index: int, time: float) -> int  # Index or -1
set_timeline_to_keyframe_time(frame_index: int) -> float  # New time or -1

# Playhead
get_timeline_time() -> float  # [0,1]
set_timeline_time(time: float) -> int  # 0=success

# Tracks
get_active_track_index() -> int
set_active_track_index(track_index: int) -> int  # 0=success; 0=main track
```

## Coding Style & Best Practices

### PEP 8 Deviations
- **Line length**: 100 chars (SDK), 120 recommended (users).
- **Type hints**: Encouraged; use PEP 585/604 syntax (`list[str]`, `str | int`).
- **Comprehensions**: Allowed when simple; avoid deep nesting.
- **Walrus operator**: Allowed for reducing duplication.

### Type Hinting Quick Reference
```python
# Basic types
name: str = "Alice"
age: int = 30
ratio: float = 0.5
flag: bool = True

# Collections
names: list[str] = ["Alice", "Bob"]
ages: dict[str, int] = {"Alice": 30, "Bob": 25}
point: tuple[float, float] = (1.0, 2.0)

# Unions
data: str | list[str] = "single"
data: str | list[str] = ["multi"]

# Callbacks
def greet(fn: typing.Callable[[str], None]) -> None:
    fn("Alice")

# Iterators
def count_up(n: int) -> typing.Iterator[int]:
    for i in range(n):
        yield i

# Any (use sparingly)
value: typing.Any = "anything"
```

### Shared VM Best Practices

#### Never Mutate Shared State
```python
# FORBIDDEN
sys.modules.clear()
math.pi = 3.0
random.seed(42)  # Affects all plugins
os.chdir("/some/path")  # Changes for everyone
sys.stdout = open("file.txt", "w")  # Breaks console
```

#### Always Use Absolute Paths
```python
# WRONG
with open("data.json", "r") as f:
    data = json.load(f)

# CORRECT
import os
script_dir = os.path.dirname(os.path.abspath(__file__))
data_path = os.path.join(script_dir, "data.json")
with open(data_path, "r") as f:
    data = json.load(f)
```

#### Clean Up sys.path Modifications
```python
libs_dir = os.path.join(os.path.dirname(__file__), "libs")
sys.path.insert(0, libs_dir)
try:
    import my_lib
finally:
    if libs_dir in sys.path:
        sys.path.remove(libs_dir)
```

#### Make Init Idempotent
```python
# Safe to run multiple times
if zbc.exists("ZScript:ToolBox"):
    zbc.close("ZScript:ToolBox")

zbc.add_subpalette("ZScript:ToolBox")
zbc.add_button("ZScript:ToolBox:Scan", "Scan assets", on_scan)
```

### UI Performance
```python
# For batch UI actions
zbc.show_actions(0)  # Disable visual feedback
try:
    for i in range(100):
        zbc.press("Tool:Geometry:Divide")
finally:
    zbc.show_actions(1)

# Or use freeze for heavy operations
def heavy_work():
    for i in range(1000):
        zbc.set("Draw:Draw Size", i)

zbc.freeze(heavy_work)
zbc.update(redraw_ui=True)
```

### Progress Feedback
```python
import time

total = 1000
for i in range(total):
    progress = i / total
    zbc.set_notebar_text(f"Processing: {round(100*progress, 2)}%", progress)
    time.sleep(0.001)

zbc.set_notebar_text("", 0)  # Clear when done
```

## ZScript Migration Reference

### Key Differences
- **No control flow commands**: Use Python's `if`, `for`, `while`, etc.
- **No variable commands**: Use Python variables directly.
- **No file I/O commands**: Use `os`, `open`, `json`, `pathlib`, etc.
- **No window commands**: Font/paint/layout commands removed; use native UI.
- **Function names**: Snake_case; `IButton` → `add_button`, `IGet` → `get`, etc.
- **Callbacks**: ZScript command groups → Python functions with specific signatures.

### Common Conversions
| ZScript | Python | Notes |
|---------|--------|-------|
| `[IButton, "path", code]` | `add_button("path", "", fn)` | `fn(sender: str) -> None` |
| `[ISlider, "path", val, ...]` | `add_slider("path", val, ...)` | `fn(sender: str, value: float) -> None` |
| `[ISwitch, "path", state, code]` | `add_switch("path", state, "", fn)` | `fn(sender: str, value: bool) -> None` |
| `[ISet, "path", val]` | `set("path", val)` | Direct call |
| `[IGet, "path"]` | `get("path")` | Returns `float` |
| `[IPress, "path"]` | `press("path")` | Direct call |
| `[VarDef, name, val]` | `name = val` | Python variable |
| `[If, condition, ...]` | `if condition:` | Python syntax |
| `[Loop, n, ...]` | `for i in range(n):` | Python syntax |
| `[FileNameResolvePath, "file"]` | `resolve_path("file")` | Or use `os.path` |
| `[Note, "msg", dur, ...]` | `show_note("msg", ...)` | Add controls first |
| `[StrAsk, "title"]` | `ask_string("", "title")` | Returns `str` |
| `[MessageOK, "msg"]` | `message_ok("msg")` | Direct call |
| `[Delay, secs]` | `time.sleep(secs)` | Import `time` |
| `[CanvasClick, x, y]` | `canvas_click(x, y)` | Direct call |
| `[RAND, max]` | `random.uniform(0, max)` | Prefer `random` |

## VS Code Setup

### Required Extensions
- **Python** (ms-python.python)
- **Pylance** (ms-python.vscode-pylance) - optional but recommended

### Settings (JSON)
```json
{
    "python.analysis.extraPaths": [
        "C:\\Users\\YourName\\Documents\\ZBrush SDK 2026.1.0\\api"
    ],
    "python.formatting.provider": "autopep8",
    "python.formatting.autopep8Args": ["--max-line-length", "120"],
    "editor.rulers": [120],
    "[python]": {
        "editor.tabSize": 4,
        "editor.insertSpaces": true
    }
}
```

## Complete Init Template

```python
"""
ToolBox Plugin for ZBrush 2026.1
Demonstrates safe init pattern with local dependencies.
"""
import os
import sys
from zbrush import commands as zbc


def _add_libs() -> str | None:
    """Add libs directory to sys.path if it exists."""
    libs_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "libs")
    if os.path.isdir(libs_dir):
        sys.path.insert(0, libs_dir)
        return libs_dir
    return None


def _remove_libs(libs_dir: str | None) -> None:
    """Remove libs directory from sys.path."""
    if libs_dir and libs_dir in sys.path:
        sys.path.remove(libs_dir)


def on_rescan(sender: str) -> None:
    """Button callback: rescan asset library."""
    zbc.message_ok("Rescanning assets...", "ToolBox")


def on_toggle(sender: str, value: bool) -> None:
    """Switch callback: toggle feature."""
    state = "ON" if value else "OFF"
    print(f"Feature is now {state}")


def init_ui() -> None:
    """Initialize ToolBox UI palette."""
    palette_path = "ZScript:ToolBox"
    
    # Idempotent: safe to run multiple times
    if zbc.exists(palette_path):
        zbc.close(palette_path)
    
    zbc.add_subpalette(palette_path, title_mode=0)
    zbc.add_button(f"{palette_path}:Rescan", "Rescan asset library", on_rescan)
    zbc.add_switch(f"{palette_path}:Toggle", True, "Toggle feature", on_toggle)
    zbc.add_slider(f"{palette_path}:Size", 50, 1, 0, 100, "Adjust size", 
                   lambda s, v: print(f"Size: {v}"))
    
    zbc.update(redraw_ui=True)


def main() -> None:
    """Main entry point."""
    libs = _add_libs()
    try:
        # Import any local dependencies here
        # from libs import my_module
        
        init_ui()
        print("ToolBox initialized successfully")
        
    except Exception as e:
        zbc.message_ok(f"ToolBox initialization failed:\n{e}", "Error")
        raise
    finally:
        _remove_libs(libs)


if __name__ == "__main__":
    main()
```

## Critical Reminders

### What You CANNOT Do
- Edit mesh geometry (verts/UVs/normals) programmatically.
- Read existing curve data.
- Synthesize arbitrary stroke point data.
- Access brush/material/texture data directly.
- Spawn Python processes or call `sys.executable`.
- Use `multiprocessing`.
- Rely on CWD being script directory.
- Mutate shared modules (`sys.modules`, `math.pi`, `random.seed`, etc.).
- Overwrite `sys.stdout/stderr/stdin`.
- Delete native UI items (only script-created via `delete_interface_item`).

### What You CAN Do
- Drive UI via item paths (`press`, `set`, `toggle`).
- Query mesh metadata (counts, bounds, UV tiles).
- Replay/transform recorded strokes.
- Create/commit new curves.
- Edit ZSpheres within `edit_zsphere` context.
- Generate displacement/normal maps (requires UVs).
- Manage tools/subtools (select, status flags).
- Build custom UI (palettes, buttons, sliders, switches, notes).
- Handle files with Python stdlib (`os`, `json`, `pathlib`, etc.).
- Import external libraries (with proper `sys.path` handling).

### Mandatory Patterns
1. **Always** use absolute or `__file__`-relative paths.
2. **Always** clean up `sys.path` modifications.
3. **Always** make init idempotent (`exists` + `close` before `add_*`).
4. **Always** match callback signatures exactly.
5. **Never** mutate shared state (modules, streams, CWD, random seed).
6. **Never** assume script folder is on `sys.path`.
7. Use `freeze` or `show_actions(0)` for batch UI operations.
8. Call `update(redraw_ui=True)` after renaming/path changes.
9. Use `set_notebar_text` for progress; clear when done.
10. Guard expensive operations; ZBrush is single-threaded.

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
