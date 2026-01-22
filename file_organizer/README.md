# Virtual File Organizer

**For complete documentation, please see the main README:**

👉 **[Main README.md](../README.md)**

👉 **[German Guide (ANLEITUNG_DE.md)](../ANLEITUNG_DE.md)**

## Quick Start

```bash
# From this directory (file_organizer/):

# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the tool
python src/main.py --help

# 3. Example: Scan a directory
python src/main.py scan /path/to/files --db catalog.db

# 4. Generate a view
python src/main.py generate ByCategory --db catalog.db --output mappings.json
python src/main.py link ByCategory --mappings mappings.json
```

## Documentation

- **Main Documentation:** [../README.md](../README.md)
- **German Guide:** [../ANLEITUNG_DE.md](../ANLEITUNG_DE.md)
- **Implementation Summary:** [../IMPLEMENTATION_SUMMARY.md](../IMPLEMENTATION_SUMMARY.md)
- **Code Review:** [../master_claude_review.md](../master_claude_review.md)

## Project Structure

```
file_organizer/
├── src/              # Source code
├── config/           # Configuration files (categories.yaml, views.yaml)
├── webui/            # Flask web interface
├── tests/            # Integration tests
├── requirements.txt  # Python dependencies
└── build.py         # Build script for standalone executable
```

## Running from Source

This is the recommended way to use the tool:

```bash
# Make sure you're in the file_organizer directory
cd file_organizer

# Install dependencies
pip install -r requirements.txt

# Run commands
python src/main.py scan /your/path --db catalog.db
python src/main.py dryrun --db catalog.db --output report.html
python src/main.py generate ByCategory --db catalog.db --output mappings.json
python src/main.py link ByCategory --mappings mappings.json
```

## Building Executable (Optional)

If you want to create a standalone executable:

```bash
python build.py
# Executable will be in dist/
```

Note: The build process is experimental and may require adjustments based on your platform.

---

**For full documentation, examples, and troubleshooting, see:**
- [Main README.md](../README.md)
- [German Guide (ANLEITUNG_DE.md)](../ANLEITUNG_DE.md)
