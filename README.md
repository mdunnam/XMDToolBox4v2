# XMD ToolBox 4.0

Asset Management & Workflow Automation for ZBrush 2026.1

## Features (Planned)

- **Asset Scanning**: Auto-discover and organize brushes, tools, materials
- **Asset Browser**: Browse and import assets with preview
- **Quick Import**: Drag-and-drop asset management
- **Batch Operations**: Apply operations to multiple assets
- **Custom Workflows**: Save and load workflow presets
- **Integration**: Seamless ZBrush UI integration

## Installation

1. Download/clone to your ZBrush plugins directory
2. Add to PYTHONPATH or ZBRUSH_PLUGIN_PATH environment variable
3. Restart ZBrush or load via Python Scripting palette

## Usage

Load via ZScript > Python Scripting > Load button, or auto-load on startup if registered.

Main palette: `ZScript:XMD_ToolBox`

## Directory Structure

```
XMD_ToolBox4.0/
├── init.py                  # Entry point
├── Docs/
│   ├── API_Copilot_Instructions.md  # Complete API reference
│   └── ToolBox_PLANNING.md           # Feature planning
├── src/
│   ├── __init__.py
│   ├── core.py              # App state & config
│   ├── callbacks.py         # UI event handlers
│   └── ui/
│       ├── __init__.py
│       └── palette.py       # Main palette UI
├── libs/                    # Local dependencies (bundled)
├── config.json              # User settings (generated)
└── README.md                # This file
```

## Development

### Adding New Features

1. Create module in `src/` (e.g., `src/assets.py`)
2. Add callbacks to `src/callbacks.py`
3. Add UI controls in `src/ui/palette.py`
4. Update `src/core.py` if new config needed

### Testing

Load via ZScript > Python Scripting > Load, or:

```python
import sys
sys.path.insert(0, r"E:\XMD_ToolBox4.0")
from init import main
main()
```

## Requirements

- ZBrush 2026.1+
- Python 3.11.9 (embedded in ZBrush)

## API Reference

See [API_Copilot_Instructions.md](Docs/API_Copilot_Instructions.md) for complete ZBrush Python SDK reference.

## Best Practices Enforced

- Idempotent init (safe to load multiple times)
- Absolute paths only
- Clean sys.path modifications
- No shared state mutation
- Type hints throughout
- Callback signature compliance

## Roadmap

- [ ] Asset scanning and organization
- [ ] Asset browser UI
- [ ] Drag-and-drop import
- [ ] Batch operations
- [ ] Workflow presets
- [ ] Settings/preferences
- [ ] Documentation

## License

© 2026 mdunnam. All rights reserved.
