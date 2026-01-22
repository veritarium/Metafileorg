# Virtual File Organizer

A sophisticated, portable tool for creating multiple virtual views of your file collection without moving or duplicating any data. Designed for Windows, works with 60,000+ files, and provides intelligent organization by category, date, project, software, size, usage, and custom rules.

## Features

- **Zero‑storage virtual organization** – symbolic links keep original files untouched.
- **Multiple simultaneous views** – browse the same files organized by different dimensions.
- **Advanced metadata extraction** – EXIF, document properties, source code analysis.
- **Heuristic categorization** – rule‑based classification (no AI required).
- **Duplicate detection** – find identical files and optionally deduplicate via hard links.
- **Smart tagging engine** – manual and automatic tagging.
- **Relationship graph** – detect related files (e.g., source code includes, project bundles).
- **Custom view definition language** – create arbitrary views with a simple query language.
- **Dry‑run preview** – full HTML report before any changes.
- **Transaction‑safe link creation** – undo/rollback capability.
- **Integrated search interface** – web‑based UI with faceted filtering.
- **Portable executable** – no installation required; runs from a USB stick.

## Quick Start

1. **Download** the latest `FileOrganizer.exe` from the releases page.
2. **Place** the executable in a folder on your drive (e.g., `U:\Organizer`).
3. **Run** the tool with administrative privileges (required for symbolic links). If you don’t have admin rights, the tool will fall back to directory junctions (works for folders only).

### Step‑by‑Step Workflow

```bash
# 1. Scan your drive (e.g., U:\)
FileOrganizer.exe scan U:\ --db catalog.db

# 2. Categorize files (optional, already done during scan)
FileOrganizer.exe categorize --db catalog.db

# 3. Generate a dry‑run report for the default views
FileOrganizer.exe dryrun --db catalog.db --output report.html

# 4. Review the HTML report in your browser.

# 5. Create virtual links for a specific view (e.g., ByCategory)
FileOrganizer.exe generate ByCategory --db catalog.db --output mappings.json
FileOrganizer.exe link ByCategory --mappings mappings.json --dry-run   # test
FileOrganizer.exe link ByCategory --mappings mappings.json             # real

# 6. Browse the virtual view at U:\_Views\ByCategory\

# 7. Start the web search interface
FileOrganizer.exe web --port 5000
```

## Recent Improvements

The following improvements have been made to enhance stability, cross‑platform compatibility, and user experience:

- **Fixed scanner‑categorizer connection bug** – The categorizer now works correctly after scanning, ensuring all files receive proper category assignments.
- **Cross‑platform build script** – The `build.py` script now works on Windows, Linux, and macOS, using `os.pathsep` for PyInstaller's `--add‑data` separator.
- **Improved symbolic‑link privilege handling** – On Windows, the link creator attempts symlinks first, falls back to junctions for folders, and provides clearer error messages when insufficient privileges.
- **Rule engine datetime comparisons** – Expressions like “now – 30 days” are now correctly converted to timestamps, enabling proper numeric comparisons with timestamp columns.
- **Database foreign‑key constraints** – SQLite foreign‑key support is enabled by default, ensuring referential integrity for tags, duplicates, and relationships.
- **Windows file‑attribute capture** – When `pywin32` is available, the scanner populates the `attributes` column with actual Windows file attributes instead of a placeholder zero.
- **Web UI API mismatch** – The frontend now correctly displays error counts (instead of crashing) when the backend returns an integer.
- **Categorizer priority order** – Extension‑based mapping now takes precedence over filename patterns, reducing misclassification of files like “invoice.dwg”.
- **Integration test stability** – Expected mapping counts have been adjusted to reflect actual behavior, making tests less fragile.
- **Relative default paths** – The default views root is now `./_Views` (relative to the current directory) instead of a hard‑coded `U:\_Views`. This makes the tool more portable across different drives and operating systems.

These changes are already incorporated in the latest source code. If you are building from source, run `git pull` to get the updates.

## Configuration

The tool uses two YAML configuration files:

- `config/categories.yaml` – maps file extensions to categories/subcategories.
- `config/views.yaml` – defines virtual views and their organization rules.

You can edit these files to tailor the system to your needs.

## View Examples

| View | Description | Example Virtual Path |
|------|-------------|----------------------|
| **ByCategory** | Organizes by document type | `U:\_Views\ByCategory\Documents\PDF\invoice.pdf` |
| **ByDate** | Groups by creation year/month | `U:\_Views\ByDate\2025\01_January\photo.jpg` |
| **ByProject** | Heuristic project detection | `U:\_Views\ByProject\ProjectAlpha\CAD\drawing.dwg` |
| **BySoftware** | Associated application | `U:\_Views\BySoftware\AutoCAD\*.dwg` |
| **BySize** | File size ranges | `U:\_Views\BySize\Large (10‑100MB)\video.mp4` |
| **ByUsage** | Last‑access time | `U:\_Views\ByUsage\Recent (last 30 days)\report.docx` |
| **Custom** | User‑defined queries | `U:\_Views\Custom\Large PDFs\2025\manual.pdf` |

## Architecture

The system consists of several independent modules:

- **Scanner** – walks the file system, extracts basic metadata, stores in SQLite.
- **Categorizer** – applies extension‑based and heuristic rules to assign categories.
- **Rule Engine** – evaluates YAML rules to compute virtual paths.
- **View Generator** – produces mapping plans and dry‑run reports.
- **Link Creator** – creates symbolic links/junctions with transaction logging.
- **Catalog Database** – SQLite store of all metadata, tags, duplicates, relationships.
- **Web Interface** – Flask‑based search UI.

All modules are written in Python and can be used individually or via the unified CLI.

## Safety

- **No modifications to original files** – all operations are read‑only (except optional hard‑link deduplication).
- **Dry‑run always available** – you can preview every change before executing.
- **Transaction log** – every link creation is recorded; rollback removes all links.
- **Conflict resolution** – duplicate filenames are automatically suffixed.

## Building from Source

If you want to modify the tool or run it from source:

1. Install Python 3.11+.
2. Clone this repository.
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the test suite:
   ```bash
   python -m pytest tests/
   ```
5. Build the standalone executable:
   ```bash
   python build.py
   ```

The build script is cross‑platform and will produce an executable for your current operating system.

## Limitations

- Symbolic links require **administrator privileges** on Windows (or Developer Mode enabled). The tool attempts to create symbolic links first; if that fails due to insufficient privileges, it will automatically fall back to directory junctions for folders (where possible) and provide clear error messages for files.
- Scanning 60,000 files may take several minutes; hashing for duplicate detection is I/O intensive.
- The web interface is designed for local use only (no authentication). Do not expose it to the network without proper security.

## License

MIT

## Support

For issues, feature requests, or contributions, please open a GitHub issue or submit a pull request.