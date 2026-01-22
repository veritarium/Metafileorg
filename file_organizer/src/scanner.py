"""
File system scanner for metadata extraction.
"""
import os
import sqlite3
import hashlib
from pathlib import Path, PureWindowsPath
import time
import logging
from datetime import datetime
from typing import Optional, Dict, Any, List
from tqdm import tqdm
import sys

# Windows‑specific file attributes
try:
    import win32file
    HAS_WIN32FILE = True
except ImportError:
    HAS_WIN32FILE = False

def _to_long_path(path: Path) -> Path:
    """
    Convert a Windows path to a long‑path form (\\?\ prefix) if it exceeds 260 characters.
    """
    if os.name != 'nt':
        return path
    # Convert to absolute path
    try:
        abs_path = path.resolve()
    except OSError:
        abs_path = path.absolute()
    # Check length
    str_path = str(abs_path)
    if len(str_path) >= 260:
        # Already in long‑path form?
        if not str_path.startswith('\\\\?\\'):
            # Add prefix
            if str_path.startswith('\\\\'):
                # UNC path -> convert to \\?\UNC\server\share
                str_path = '\\\\?\\UNC\\' + str_path[2:]
            else:
                str_path = '\\\\?\\' + str_path
        return Path(str_path)
    return abs_path

logger = logging.getLogger(__name__)

class FileScanner:
    """Recursively scans a drive/directory and collects file metadata."""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self._create_tables()
    
    def _create_tables(self):
        """Create the necessary tables if they don't exist."""
        cursor = self.conn.cursor()
        # Main files table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                path TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                extension TEXT,
                size INTEGER,
                created REAL,
                modified REAL,
                accessed REAL,
                attributes INTEGER,
                hash_sha256 TEXT,
                category TEXT,
                subcategory TEXT,
                tags TEXT,
                project TEXT,
                software TEXT,
                version TEXT,
                extra_json TEXT
            )
        """)
        # Indexes for performance
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_files_path ON files(path)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_files_extension ON files(extension)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_files_category ON files(category)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_files_created ON files(created)")
        self.conn.commit()
    
    def scan(self, root: str, follow_symlinks: bool = False,
             compute_hash: bool = False, extensions_ignore: list = None):
        """
        Scan a directory recursively and insert/update metadata.
        
        Args:
            root: Root directory to scan.
            follow_symlinks: Whether to follow symbolic links.
            compute_hash: Whether to compute SHA‑256 hash (slow for large files).
            extensions_ignore: List of extensions to skip (e.g., ['.tmp', '.log']).
        Returns:
            dict with keys 'scanned' (int), 'errors' (int)
        """
        if extensions_ignore is None:
            extensions_ignore = []
        
        root_path = _to_long_path(Path(root).resolve())
        logger.info(f"Starting scan of {root_path}")
        
        # Collect all files recursively
        file_paths = []
        for dirpath, dirnames, filenames in os.walk(root_path, followlinks=follow_symlinks):
            # Skip certain directories? (optional)
            for fname in filenames:
                full_path = Path(dirpath) / fname
                file_paths.append(_to_long_path(full_path))
        
        logger.info(f"Found {len(file_paths)} files")
        
        # Prepare insert/update statement
        cursor = self.conn.cursor()
        insert_sql = """
            INSERT OR REPLACE INTO files
            (path, name, extension, size, created, modified, accessed, attributes, hash_sha256)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        scanned = 0
        errors = 0
        # Process files with progress bar
        for full_path in tqdm(file_paths, desc="Scanning files"):
            try:
                # Skip ignored extensions
                ext = full_path.suffix.lower()
                if ext in extensions_ignore:
                    continue
                
                # Get file stats
                stat = os.stat(full_path)
                size = stat.st_size
                created = stat.st_ctime
                modified = stat.st_mtime
                accessed = stat.st_atime
                # Get file attributes (Windows only)
                if os.name == 'nt' and HAS_WIN32FILE:
                    try:
                        attributes = win32file.GetFileAttributes(str(full_path))
                    except Exception:
                        attributes = 0
                else:
                    attributes = 0
                
                # Compute hash if requested
                hash_val = None
                if compute_hash:
                    hash_val = self._compute_hash(full_path)
                
                # Convert path to string (use Windows path style if on Windows)
                path_str = str(PureWindowsPath(full_path)) if os.name == 'nt' else str(full_path)
                name = full_path.name
                
                cursor.execute(insert_sql, (
                    path_str, name, ext if ext else None, size,
                    created, modified, accessed, attributes, hash_val
                ))
                scanned += 1
                
            except (OSError, PermissionError) as e:
                logger.warning(f"Cannot read {full_path}: {e}")
                errors += 1
                continue
        
        self.conn.commit()
        logger.info(f"Scan completed. Scanned: {scanned}, Errors: {errors}")
        return {'scanned': scanned, 'errors': errors}
    
    def _compute_hash(self, filepath: Path, block_size: int = 65536) -> str:
        """Compute SHA‑256 hash of file content."""
        sha256 = hashlib.sha256()
        try:
            with open(filepath, 'rb') as f:
                for block in iter(lambda: f.read(block_size), b''):
                    sha256.update(block)
            return sha256.hexdigest()
        except (OSError, PermissionError):
            return None
    
    def close(self):
        self.conn.close()


if __name__ == "__main__":
    # Example usage
    import sys
    if len(sys.argv) < 2:
        print("Usage: python scanner.py <directory>")
        sys.exit(1)
    
    logging.basicConfig(level=logging.INFO)
    scanner = FileScanner("catalog.db")
    try:
        scanner.scan(sys.argv[1], compute_hash=False)
    finally:
        scanner.close()