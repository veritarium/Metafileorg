# Virtual File Organizer

[![Python Version](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey.svg)]()

A powerful, portable tool for creating **multiple virtual views** of your file collection without moving or duplicating any data. Perfect for organizing 60,000+ files across categories, dates, projects, and custom rules using symbolic links.

## 🌟 Key Features

- **Zero-storage virtual organization** - Symbolic links keep original files untouched
- **Multiple simultaneous views** - Browse files organized by different dimensions
- **Advanced metadata extraction** - EXIF, document properties, source code analysis
- **Intelligent categorization** - Rule-based classification (300+ file types supported)
- **Duplicate detection** - Find identical files via SHA-256 hashing
- **Smart tagging engine** - Manual and automatic tagging
- **Custom view definition** - Create arbitrary views with YAML rules
- **Dry-run preview** - Full HTML report before any changes
- **Transaction-safe** - Undo/rollback capability for all operations
- **Web-based search interface** - Flask UI with faceted filtering
- **Cross-platform** - Works on Windows, Linux, and macOS

## 🚀 Quick Start

### Installation

#### Option 1: From Source

```bash
# Clone the repository
git clone https://github.com/veritarium/Metafileorg.git
cd Metafileorg

# Install dependencies
pip install -r file_organizer/requirements.txt

# Run tests
pytest file_organizer/tests/
```

#### Option 2: Pre-built Executable (Coming Soon)

Download the latest release from the [Releases page](https://github.com/veritarium/Metafileorg/releases).

### Basic Usage

```bash
# Navigate to the file_organizer directory
cd file_organizer

# 1. Scan your drive
python src/main.py scan /path/to/your/files --db catalog.db --hash

# 2. Generate a dry-run report
python src/main.py dryrun --db catalog.db --output report.html

# 3. Review the HTML report in your browser
# Open report.html to preview the virtual organization

# 4. Create virtual links for a specific view
python src/main.py generate ByCategory --db catalog.db --output mappings.json
python src/main.py link ByCategory --mappings mappings.json --dry-run  # Test first
python src/main.py link ByCategory --mappings mappings.json             # Create links

# 5. Browse your virtual views
# Files are now organized in ./_Views/ByCategory/

# 6. Start the web search interface (optional)
python src/main.py web --port 5000
# Visit http://localhost:5000 in your browser
```

## 📋 Available Views

The system includes several pre-configured views:

| View | Description | Example Path |
|------|-------------|--------------|
| **ByCategory** | Organizes by document type | `_Views/ByCategory/Documents/PDF/invoice.pdf` |
| **ByDate** | Groups by creation year/month | `_Views/ByDate/2025/January/photo.jpg` |
| **ByProject** | Heuristic project detection | `_Views/ByProject/ProjectAlpha/CAD/drawing.dwg` |
| **BySoftware** | Associated application | `_Views/BySoftware/AutoCAD/*.dwg` |
| **BySize** | File size ranges | `_Views/BySize/Large (10-100MB)/video.mp4` |
| **ByUsage** | Last-access time | `_Views/ByUsage/Recent (last 30 days)/report.docx` |
| **Custom** | User-defined queries | `_Views/Custom/Large PDFs/2025/manual.pdf` |

## ⚙️ Configuration

### Categories (file_organizer/config/categories.yaml)

Maps 300+ file extensions to categories and subcategories:

```yaml
mapping:
  pdf:
    category: Documents
    subcategory: PDF
  dwg:
    category: CAD
    subcategory: AutoCAD
  # ... 300+ mappings
```

### Views (file_organizer/config/views.yaml)

Define custom organization rules:

```yaml
views:
  MyCustomView:
    description: "Large PDFs from 2025"
    rules:
      - condition:
          extension: "pdf"
          size: "> 5242880"
        target: "LargePDFs/{year}/{name}"
```

## 🏗️ Architecture

```
┌─────────────┐    ┌──────────────┐    ┌─────────────┐
│   Scanner   │───▶│  Categorizer │───▶│  Database   │
└─────────────┘    └──────────────┘    └─────────────┘
                                              │
                   ┌──────────────┐           │
                   │ Rule Engine  │◀──────────┘
                   └──────────────┘
                          │
       ┌──────────────────┼──────────────────┐
       ▼                  ▼                  ▼
┌─────────────┐    ┌──────────────┐   ┌─────────────┐
│   View      │    │    Link      │   │  Web UI     │
│ Generator   │───▶│   Creator    │   │  (Flask)    │
└─────────────┘    └──────────────┘   └─────────────┘
```

### Components

- **Scanner** - Walks filesystem, extracts metadata, stores in SQLite
- **Categorizer** - Applies extension-based and heuristic rules
- **Rule Engine** - Evaluates YAML rules to compute virtual paths
- **View Generator** - Produces mapping plans and dry-run reports
- **Link Creator** - Creates symbolic links/junctions with transaction logging
- **Database** - SQLite store of metadata, tags, duplicates, relationships
- **Web Interface** - Flask-based search UI with faceted filtering

## 🔒 Safety Features

- **No modifications to original files** - All operations are read-only (except optional hard-link deduplication)
- **Dry-run always available** - Preview every change before executing
- **Transaction log** - Every link creation is recorded; rollback removes all links
- **Conflict resolution** - Duplicate filenames are automatically suffixed
- **Comprehensive error handling** - Operations fail gracefully with clear messages

## 🖥️ Platform Support

### Windows

- Requires administrator privileges for symbolic links (or Developer Mode enabled)
- Automatically falls back to directory junctions when needed
- Full support for Windows file attributes

### Linux / macOS

- Works with standard symbolic links (no special permissions required)
- Portable across Unix-like systems

## 📊 Performance

- Handles **60,000+ files** efficiently
- Parallel I/O for hash computation (planned)
- Indexed SQLite database for fast queries
- Pagination support in web UI
- Low memory footprint

## 🛠️ Development

### Building from Source

```bash
# Install development dependencies
pip install -r file_organizer/requirements.txt

# Run tests
pytest file_organizer/tests/

# Build standalone executable
cd file_organizer
python build.py
# Executable will be in dist/
```

### Project Structure

```
Metafileorg/
├── file_organizer/
│   ├── src/
│   │   ├── main.py              # CLI entry point
│   │   ├── scanner.py           # File scanning
│   │   ├── categorizer.py       # File categorization
│   │   ├── rule_engine.py       # Rule evaluation
│   │   ├── view_generator.py    # View generation
│   │   ├── link_creator.py      # Link creation
│   │   └── database.py          # Database management
│   ├── config/
│   │   ├── categories.yaml      # File type mappings
│   │   └── views.yaml           # View definitions
│   ├── webui/
│   │   └── app.py               # Flask web interface
│   ├── tests/
│   │   └── test_integration.py  # Integration tests
│   ├── build.py                 # Build script
│   └── requirements.txt         # Python dependencies
├── master_claude_review.md      # Comprehensive code review
├── IMPLEMENTATION_SUMMARY.md    # Recent fixes and changes
└── README.md                    # This file
```

## 🚧 Known Limitations

- Symbolic links require **administrator privileges** on Windows (or Developer Mode enabled)
  - The tool attempts symbolic links first; if that fails, it falls back to directory junctions for folders
- Scanning 60,000 files may take several minutes
- Hash computation for duplicate detection is I/O intensive
- Web interface is designed for **local use only** (no authentication by default)
  - **WARNING:** Do not expose the web UI to a network without adding authentication

## 🔧 Recent Improvements

**v1.0 (Latest)**

The following critical fixes have been applied:

✅ Fixed Python 3.11 compatibility (is_junction() bug)
✅ Fixed build process (PyInstaller configuration)
✅ Fixed package installation (requirements.txt)
✅ Enhanced web UI error handling and security
✅ Fixed file categorization patterns (word boundaries)
✅ Added comprehensive input validation

See [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) for detailed changelog.

## 📝 To-Do / Roadmap

- [ ] Add authentication to web UI
- [ ] Implement real-time file monitoring (watchdog integration)
- [ ] Add relationship graph visualization
- [ ] Parallel hash computation for faster scanning
- [ ] Windows Search integration
- [ ] Content-aware categorization (text extraction)
- [ ] Advanced project detection (git, package.json markers)
- [ ] Export/import catalog functionality

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Development Guidelines

- Write tests for new features
- Follow PEP 8 style guidelines
- Add docstrings to public methods
- Update documentation as needed

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with Python 3.11+
- Uses PyInstaller for standalone executables
- Flask for web interface
- SQLite for catalog storage
- PyYAML for configuration

## 📞 Support

- **Issues:** [GitHub Issues](https://github.com/veritarium/Metafileorg/issues)
- **Documentation:** See files in the repository
- **Email:** Create an issue for support requests

## ⚠️ Disclaimer

This tool creates symbolic links to organize your files virtually. While it does not modify original files, ensure you:

- Have **backups** of important data
- Test with a **small dataset** first using `--dry-run`
- Understand that deleting a symbolic link does **not** delete the original file
- Review the dry-run HTML report before creating links

**The authors are not responsible for any data loss. Use at your own risk.**

---

**Made with ❤️ for file organization enthusiasts**

*Star this repo if you find it useful!* ⭐
