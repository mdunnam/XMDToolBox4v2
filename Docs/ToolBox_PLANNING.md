# XMD ToolBox 4.0 - Planning Document

A comprehensive plan to rebuild and modernize the XMD ToolBox plugin for ZBrush, supporting organization of all ZBrush asset types and leveraging insights from xmdsource.com.

---

## 1. Goals & Scope

- Recreate and modernize the XMD ToolBox for ZBrush from scratch.
- Support organization of all ZBrush asset types (brushes, alphas, materials, tools, subtools, projects, lightcaps, stencils, noisemakers, macros, polygroups, color sets, etc.).
- Achieve feature parity with the current version and introduce modern improvements based on xmdsource.com.
- Ensure modularity, extensibility, and a modern, user-friendly interface.
- Follow clean code principles with comprehensive documentation.

### Legacy Feature Parity (v2.x/v3.x) — from User Guide
- Panels: brushes, alphas, textures, materials, fibers, tools, lights, projects, macros, ZBrush UI, library (store), updates, favorites, icon size modes, filter menu per asset, search bar, mini mode, keep-on-top.
- Settings: per-asset locations, categories, tags; import/export database; rescan local files; theme; single-click select; advanced tooltips; XMD category toggle; auto-update toggle; ZBrush path; store download path.
- Favorites & sets: multiple favorite sets, star toggle, collapse favorites.
- Layout: collapse panels (general/properties), keep-on-top, mini strip mode.

---

## 2. Research & Requirements

### ZBrush Asset Types to Support
- **Brushes** (.ZBP)
- **Alphas** (.PSD, .TIF, .BMP)
- **Materials** (.ZMT)
- **Textures** (.PSD, .TIF, .BMP, .JPG)
- **Tools** (.ZTL)
- **Subtools**
- **Projects** (.ZPR)
- **LightCaps** (.ZLC)
- **Stencils**
- **Noisemakers** (.ZNS)
- **Macros/Scripts** (.TXT, .ZSC)
- **Polygroups**
- **Color Sets**

### Current Features (xmdsource.com)
- Asset browsing and tagging
- Search and filtering capabilities
- Favorites and custom collections
- Import/export of assets
- Integration with ZBrush UI
- Asset preview thumbnails
- Batch operations (install, delete, tag, etc.)

### Must-Have Features
- [ ] Fast asset discovery and indexing
- [ ] Tagging and metadata management
- [ ] Advanced search and filtering
- [ ] Asset preview generation
- [ ] Import/export functionality
- [ ] Batch operations
- [ ] Favorites and collections
- [ ] ZBrush integration (loading assets, UI hooks)

### Nice-to-Have Features
- [ ] AI-powered asset suggestions
- [ ] Asset analytics and usage tracking
- [ ] Version control for assets
- [ ] Asset sharing and marketplace integration

### Cloud & Integration Features (Priority)
- [ ] AWS S3 integration for cloud asset storage
- [ ] XMDSource.com license validation and subscription checking
- [ ] Cloud sync and backup of user assets and preferences
- [ ] Direct integration with xmdsource.com for asset downloads
- [ ] Streaming assets from S3 for on-demand loading

### Comprehensive Asset Taxonomy (2026.1-safe)
**Brush/Alpha/Stroke**: brushes (standard, custom, IMM, curve, NanoMesh, multi-alpha, noise-based, layer-aware), alphas (drag, tiled, height, float/displacement), stroke presets (LazyMouse, Roll/DragDot, curve behavior).  
**Mesh Libraries**: IMM assets (single/multi, curve IMM, NanoMesh sources, kitbash sets), insert meshes with embedded ZTL.  
**Models & Scenes**: tools (single/multi-subtool, base, blockout, hero, scans, trim sheets), projects (ZPR).  
**Materials & Render**: materials, MatCaps, render presets (BPR, AO/shadows, NPR, turntable), LightCaps.  
**Textures**: polypaint, color, mask, height/displacement, normal, opacity; EXR external support.  
**Hair/Fiber**: FiberMesh presets (hair/fur/foliage/fuzz).  
**Noise & Surface**: noise presets, procedural noise stacks, tileable noise patterns.  
**Deformation & Operation Presets**: gizmo and deformer presets (bend/taper/array/lattice), modeling operation presets (bevel/crease/rules), reusable procedural operation chains.  
**Presentation**: camera presets/stacks (turntable, orthographic, portfolio), Spotlight assets (images, layouts), array mesh setups, grids/scene helpers, turntable animation snippets, snapshot presets.  
**Character State Assets**: pose libraries (body/hands/face), morph targets, layers (detail passes), polygroups templates.  
**UI & Automation**: UI layouts, shelf/button configs, macros/scripts, workflow presets, naming/export presets, validation rulesets (game-ready, Nanite-safe, portfolio-ready).  
**Reference Assets**: reference images/boards/turnarounds/callouts/scans.

---

## 3. Architecture & Design
 (Python)
│   ├── Asset Registry
│   ├── Search Engine
│   ├── Tag Manager
│   └── Plugin Manager
├── Cloud Services Module
│   ├── AWS S3 Client (boto3)
│   ├── XMDSource.com API Client
│   ├── License Validator
│   ├── Cloud Sync Manager
│   └── Asset Downloader
├── Asset Modules
│   ├── BrushModule
│   ├── AlphaModule
│   ├── MaterialModule
│   ├── ToolModule
│   └── [Other Asset Type Modules]
├── UI Layer (ZBrush Python UI)
│   ├── Main Window
│   ├── Asset Grid/List View
│   ├── Search & Filter Panel
│   ├── Tag Editor
│   ├── Cloud Settings
│   └── License Status
├── Integration Layer
│   ├── ZBrush Python API Hooks
│   ├── File System Watcher
│   ├── Asset Loader (Local + Cloud)
│   └── Background Task Manager
└── Persistence Layer
    ├── SQLite Metadata Database
    ├── User Settings & Preferences
    ├── Cache Manager
    └── License & Auth Token Storageatcher
│   └── Asset Loader
└── Persistence Layer
    ├── Metadata Database
    ├── User Settings
    └── Cache Manager
```

### Design Principles
- **Modularity**: Each asset type has its own module implementing a common interface.
- **Decoupling**: UI layer is separated from business logic.
- **Extensibility**: Plugin system for new asset types and features.
- **Performance**: Fast indexing, caching, and lazy loading.
- **Clean Code**: JSDoc comments, descriptive naming, and modular functions.

### Technology Stack

#### Primary Language: **Python 3.x**
- **ZBrush Integration**: Official ZBrush Python SDK (2026.1+)
- **Cloud Storage**: AWS S3 integration using `boto3` library
- **Web API**: XMDSource.com license validation using `requests` library
- **Database**: SQLite for local metadata storage
- **Image Processing**: Pillow (PIL) for thumbnail generation
- **Async Operations**: `asyncio` for background tasks

#### Key Libraries
- `boto3` - AWS S3 integration for cloud asset storage
- `requests` - HTTP client for XMDSource.com API
- `sqlite3` - Local metadata and cache database
- `Pillow` - Image processing and thumbnail generation
- `pydantic` - Data validation and settings management
- `pytest` - Testing framework

#### Why Python?
- Native ZBrush support (2026+) with official SDK
- Perfect for AWS S3 and web API integration
- Rich ecosystem for networking, file handling, and databases
- Better performance and maintainability than ZScript
- Easier debugging and testing
- Large developer community and extensive documentation

---

## 4. UI/UX Planning

### Main Interface Components
1. **Asset Browser**
   - Grid and list view modes
   - Thumbnail previews with customizable sizes
   - Quick actions on hover (load, favorite, tag)
   
2. **Search & Filter Panel**
   - Real-time search with autocomplete
   - Filter by asset type, tags, date, favorites
   - Advanced filter combinations
   
3. **Tag Management**
   - Visual tag editor
   - Bulk tagging operations
   - Tag hierarchies and categories
   
4. **Collections & Favorites**
   - User-defined collections
   - Quick access to favorites
   - Smart collections based on rules
   
5. **Batch Operations**
   - Multi-select assets
   - Batch import/export
   - Batch tagging and organizing

### UX Improvements
- Drag-and-drop asset organization
- Context menus for quick actions
- Keyboard shortcuts for power users
- Dark mode and theme support
- High-DPI display support
- Responsive layout
- Accessibility features

---

## 5. Implementation Roadmap

### Phase 1: Foundation (Weeks 1-4)
1. Set up project repository and development environment
2. Define core interfaces and data models
3. Implement basic asset discovery and indexing
4. Create minimal viable UI prototype
5. Establish coding standards and documentation templates

### Phase 2: Core Features & Cloud Integration (Weeks 5-12)
1. Implement AWS S3 client and bucket integration
2. Build XMDSource.com API client for license validation
3. Implement asset modules for primary types (brushes, alphas, materials)
4. Build search and filter functionality (local + cloud)
5. Develop tagging and metadata system
6. Create asset preview generation
7. Integrate with ZBrush Python API for asset loading
8. Implement cloud sync and download manager

### Phase 3: Advanced Features (Weeks 11-16)
1. Implement remaining asset modules
2. Add batch operations
3. Build collections and favorites system
4. Develop import/export functionality
5. Create settings and configuration UI

### Phase 4: Polish & Testing (Weeks 17-20)
1. Comprehensive testing and bug fixes
2. Performance optimization
3. User documentation and tutorials
4. Beta testing with user feedback
5. Final release preparation

### Phase 5: Post-Launch
1. Monitor user feedback and bug reports
2. Iterative improvements and feature additions
3. Maintain compatibility with new ZBrush versions
4. Explore advanced features (cloud sync, marketplace integration)

---

## 6. Clean Code & Documentation Standards

### Code Standards (Python PEP 8)
- **Naming Conventions**: 
  - PascalCase for classes and types (`AssetManager`, `CloudService`)
  - snake_case for functions and variables (`index_assets`, `user_settings`)
  - UPPER_CASE for constants (`MAX_CACHE_SIZE`, `API_BASE_URL`)
  - Descriptive, self-documenting names
  - Type hints for all function parameters and returns

- **Function Design**:
  - Single Responsibility Principle
  - Functions should be short and focused
  - Minimize side effects
  - Use pure functions where possible
 & Documentation**:
  - Python docstrings (Google or NumPy style) for all public functions and classes
  - Type hints using `typing` module
  - Inline comments for complex logic
  - Keep comments up-to-date with code changes
  - Use `# TODO:` and `# FIXME:` for tracking work item
  - Keep comments up-to-date with code changes

### Documentation Requirements
- **Developer Documentation**:
  - Architecture overview
  - API reference
  - Module iPython Documentation Format
```python
async def index_assets(directory_path: str, asset_type: AssetType, recursive: bool = True) -> list[Asset]:
    """
    Indexes all assets in the specified directory.
    
    Args:
        directory_path: Absolute path to the directory to scan
        asset_type: Type of assets to index
        recursive: Whether to scan subdirectories (default: True)
    
    Returns:
        List of indexed Asset objects
    
    Raises:
        DirectoryNotFoundError: If the directory doesn't exist
        PermissionError: If directory is not readable
    
    Example:
        >>> assets = await index_assets("/path/to/brushes", AssetType.BRUSH)
        >>> print(f"Found {len(assets)} brushes")
    """
    # Implementation* 
 * @param {string} directoryPath - Absolute path to the directory to scan
 * @param {AssetType} assetType - Type of assets to index
 * @param {boolean} recursive - Whether to scan subdirectories
 * @returns {Promise<Asset[]>} Array of indexed assets
 * @throws {DirectoryNotFoundError} If the directory doesn't exist
 */
async function indexAssets(directoryPath, assetType, recursive = true) {
  // Implementation
}
```

---
Python Integration
- ZBrush Python SDK 2026.1+ compatibility
- File locations for different asset types
- Plugin loading and initialization
- UI integration using ZBrush Python UI API
- Performance considerations for large asset libraries
- ZBrush version detection and compatibility

### Cloud Integration (AWS S3)
- AWS credentials management (IAM roles, access keys)
- S3 bucket structure and organization
- Multipart upload for large assets
- Download resume capability
- Bandwidth optimization and caching
- CDN integration for faster downloads
- Presigned URLs for secure access

### XMDSource.com API Integration
- RESTful API endpoints for license validation
- OAuth2 or JWT token authentication
- Subscription tier checking
- User account synchronization
- Asset entitlement verification
- API rate limiting and retry logic
- Offline mode with cached credentials

### File System Management
- Watching for file changes (local assets)
- Handling asset file formats
- Thumbnail generation and caching
- Backup and recovery
- Local + cloud asset synchronization
- Conflict resolution for sync

### Performance Optimization
- Lazy loading of assets
- Efficient indexing algorithms
- Multi-level caching (memory, disk, cloud)
- Background processing using asyncio
- Parallel downloads from S3
- Database query optimization
- Asset preview streaming

### Security Considerations
- Secure storage of AWS credentials
- Encrypted storage of auth tokens
- HTTPS for all API communications
- Input validation and sanitization
- Rate limiting for API calls
- Secure handling of user data

### Cross-Platform Considerations
- File path handling (Windows/Mac)
- ZBrush version compatibility (2026+)
- Python version compatibility (3.10+)
- Platform-specific file permissions
- Network connectivity detection
- File path handling (Windows/Mac)
- ZBrush version compatibility
- Platform-specific UI considerations

---

## 8. Testing Strategy

### Unit Tests
- Ax] **Language Choice**: Python 3.10+ with ZBrush Python SDK 2026.1+
- [x] **Cloud Storage**: AWS S3 integration confirmed
- [x] **License Validation**: XMDSource.com API integration confirmed
- [ ] What are the XMDSource.com API endpoints and authentication method?
- [ ] AWS S3 bucket structure and naming conventions?
- [ ] How to handle offline mode when cloud services are unavailable?
- [ ] What are the highest-priority workflows for the first release?
- [ ] What level of backward compatibility with previous versions is required?
- [ ] Should we implement a plugin marketplace or extension system?
- [ ] How will we handle asset versioning and updates?
- [ ] What subscription tiers exist and what features do they unlock?
- [ ] Should assets be encrypted in S3 or use presigned URL
- File system operations
- UI interactions

### User Acceptance Testing
- Beta testing with real users
- Performance testing with large asset libraries
- Usability testing
- Bug reporting and tracking

---

## 9. Risk Management

### Potential Risks
- **ZBrush API Limitations**: Mitigation through early prototyping and research
- **Performance Issues**: Implement optimization strategies and profiling
- **User Adoption**: Ensure backward compatibility and easy migration
- **Maintenance Burden**: Modular design and comprehensive documentation

---

## 10. Success Metrics

- **User Adoption**: Number of active users and downloads
- **Performance**: Asset indexing speed, search response time
- **User Satisfaction**: Feedback scores, feature requests
- **Code Quality**: Test coverage, code review scores
- **Documentation**: Completeness and clarity of documentation

---

## 11. Open Questions & Decisions

- [ ] Should we support direct integration or syncing with xmdsource.com?
- [ ] What are the highest-priority workflows for the first release?
- [ ] Are there licensing or API considerations for using website data?
- [ ] Should we develop a separate UI framework or use native ZScript UI?
- [ ] What level of backward compatibility with previous versions is required?
- [ ] Should we implement a plugin marketplace or extension system?
- [ ] How will we handle asset versioning and updates?

---

## 12. Next Steps

1. **Immediate Actions**:
   - [ ] Review and validate this planning document
   - [ ] Prioritize features for MVP (Minimum Viable Product)
   - [ ] Research xmdsource.com in detail for feature parity
   - [ ] Set up project repository and folder structure
   - [ ] Create initial architecture diagrams
   
2. **Short-Term Goals**:
   - [ ] Complete detailed requirements gathering
   - [ ] Design asset module interfaces
   - [ ] Prototype asset discovery mechanism
   - [ ] Create UI mockups
   
3. **Long-Term Goals**:
   - [ ] Complete Phase 1 implementation
   - [ ] Establish beta testing program
   - [ ] Prepare for public release

---

**Document Version**: 1.0  
**Last Updated**: January 20, 2026  
**Status**: Draft - Awaiting Review
