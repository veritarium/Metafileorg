"""
Create symbolic links (or junctions) for virtual views, with safety and undo.
"""
import os
import shutil
import sqlite3
import json
import logging
import platform
import subprocess
from pathlib import Path, PureWindowsPath
from datetime import datetime
from typing import List, Dict, Optional, Tuple
import sys

logger = logging.getLogger(__name__)


def is_junction(path: Path) -> bool:
    """
    Check if a path is a junction point (Windows) or symlink.
    Compatible with Python 3.11+ (is_junction() added in 3.12).
    """
    if sys.version_info >= (3, 12):
        return path.is_junction()
    elif os.name == 'nt':
        # On Windows with Python < 3.12, check if it's a symlink to a directory
        # Junction points appear as symlinks on Windows
        try:
            return path.is_symlink() and path.is_dir()
        except (OSError, PermissionError):
            return False
    else:
        # On Unix-like systems, junctions don't exist - only symlinks
        return False


class LinkCreator:
    def __init__(self, db_path: str, views_root: str = "./_Views"):
        self.db_path = db_path
        self.views_root = Path(views_root)
        self.conn = sqlite3.connect(db_path)
        self._create_tables()
    
    def _create_tables(self):
        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS link_transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                operation TEXT NOT NULL,  -- 'create', 'delete', 'rollback'
                view_name TEXT NOT NULL,
                source_path TEXT NOT NULL,
                link_path TEXT NOT NULL,
                success INTEGER DEFAULT 0,
                error TEXT
            )
        """)
        self.conn.commit()
    
    def create_links(self, mappings: List[Dict], view_name: str, dry_run: bool = True):
        """
        Create symbolic links for a list of source→target mappings.
        If dry_run is True, only log intended actions without creating anything.
        """
        log_entries = []
        created = 0
        errors = 0
        
        for mapping in mappings:
            src = Path(mapping['source_path'])
            rel_target = mapping['target_path']
            # Determine link path
            link_path = self.views_root / view_name / rel_target
            
            if dry_run:
                logger.info(f"[DRY-RUN] Would link {src} → {link_path}")
                success = True
                error = None
            else:
                success, error = self._create_single_link(src, link_path)
                if success:
                    created += 1
                else:
                    errors += 1
            
            log_entries.append({
                'timestamp': datetime.now().isoformat(),
                'operation': 'create',
                'view_name': view_name,
                'source_path': str(src),
                'link_path': str(link_path),
                'success': success,
                'error': error
            })
        
        # Store log entries in database
        if not dry_run:
            self._store_logs(log_entries)
        
        logger.info(f"Links created: {created}, errors: {errors}")
        return created, errors
    
    def _create_single_link(self, source: Path, link_path: Path) -> Tuple[bool, Optional[str]]:
        """Create a symbolic link (or junction) on Windows, with fallbacks."""
        # Ensure parent directory exists
        link_path.parent.mkdir(parents=True, exist_ok=True)
        
        # If a file or link already exists, remove it (optional)
        if link_path.exists():
            # If it's a symlink/junction, remove it
            if link_path.is_symlink() or is_junction(link_path):
                link_path.unlink()
            else:
                # Regular file/directory – we shouldn't overwrite; skip with error
                return False, f"Target already exists and is not a link: {link_path}"
        
        # Determine OS
        is_windows = platform.system() == 'Windows'

        # Attempt strategies in order
        strategies = []
        if source.is_dir():
            strategies.append(('symlink', self._create_symlink))
            if is_windows:
                strategies.append(('junction', self._create_junction))
        else:
            strategies.append(('symlink', self._create_symlink))
            strategies.append(('hardlink', self._create_hardlink))
        
        last_error = None
        for name, strategy in strategies:
            try:
                strategy(source, link_path)
                logger.info(f"Created {name} link from {source} to {link_path}")
                return True, None
            except (OSError, PermissionError, subprocess.CalledProcessError) as e:
                last_error = e
                logger.warning(f"Failed to create {name} link: {e}")
                # Remove any partially created link
                if link_path.exists():
                    try:
                        link_path.unlink()
                    except OSError:
                        pass
                continue
        
        # All strategies failed
        error_msg = f"All link creation strategies failed. Last error: {last_error}"
        logger.error(error_msg)
        return False, error_msg
    
    def _create_symlink(self, source: Path, link_path: Path):
        """Create a symbolic link."""
        # On Windows, specify target_is_directory for correct symlink type
        if os.name == 'nt':
            target_is_directory = source.is_dir()
            os.symlink(source, link_path, target_is_directory=target_is_directory)
        else:
            os.symlink(source, link_path)
    
    def _create_hardlink(self, source: Path, link_path: Path):
        """Create a hard link (same filesystem only)."""
        os.link(source, link_path)
    
    def _create_junction(self, source: Path, link_path: Path):
        """Create a directory junction (Windows only)."""
        # Use `mklink /J` via subprocess
        cmd = ['cmd', '/c', 'mklink', '/J', str(link_path), str(source)]
        try:
            subprocess.run(cmd, check=True, capture_output=True, text=True)
        except subprocess.CalledProcessError as e:
            # Provide a more helpful error message
            if 'privilege' in e.stderr.lower():
                raise OSError(
                    f"Failed to create junction due to insufficient privileges. "
                    f"On Windows, you may need to run as Administrator or enable Developer Mode. "
                    f"Original error: {e.stderr.strip()}"
                ) from e
            else:
                raise
    
    def _store_logs(self, logs: List[Dict]):
        cursor = self.conn.cursor()
        for log in logs:
            cursor.execute("""
                INSERT INTO link_transactions 
                (timestamp, operation, view_name, source_path, link_path, success, error)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                log['timestamp'], log['operation'], log['view_name'],
                log['source_path'], log['link_path'],
                log['success'], log['error']
            ))
        self.conn.commit()
    
    def rollback_view(self, view_name: str):
        """Delete all links created for a given view (using transaction log)."""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT link_path FROM link_transactions 
            WHERE view_name = ? AND operation = 'create' AND success = 1
        """, (view_name,))
        rows = cursor.fetchall()
        
        deleted = 0
        errors = []
        for (link_path,) in rows:
            path = Path(link_path)
            try:
                if path.exists():
                    if path.is_symlink() or is_junction(path):
                        path.unlink()
                    else:
                        # Not a link – skip
                        errors.append(f"Not a link: {link_path}")
                        continue
                    # Remove empty parent directories
                    self._remove_empty_parents(path.parent)
                deleted += 1
            except OSError as e:
                errors.append(str(e))
        
        # Log rollback operation
        cursor.execute("""
            INSERT INTO link_transactions 
            (timestamp, operation, view_name, source_path, link_path, success, error)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            datetime.now().isoformat(), 'rollback', view_name, '', '', deleted > 0, '; '.join(errors)
        ))
        self.conn.commit()
        
        logger.info(f"Rollback deleted {deleted} links for view '{view_name}'")
        return deleted, errors
    
    def _remove_empty_parents(self, directory: Path):
        """Recursively remove empty directories up to views_root."""
        try:
            while directory != self.views_root and directory.exists():
                if not any(directory.iterdir()):
                    directory.rmdir()
                    directory = directory.parent
                else:
                    break
        except OSError:
            pass
    
    def close(self):
        self.conn.close()


if __name__ == "__main__":
    # Example usage
    if len(sys.argv) < 3:
        print("Usage: python link_creator.py <db> <view_name> [--dry-run]")
        sys.exit(1)
    
    db = sys.argv[1]
    view = sys.argv[2]
    dry_run = '--dry-run' in sys.argv
    
    # In a real scenario, mappings would come from view generator
    # For demo, we'll create dummy mappings
    mappings = [
        {'source_path': 'C:\\test\\file1.txt', 'target_path': 'Category/Docs/file1.txt'},
        {'source_path': 'C:\\test\\file2.jpg', 'target_path': 'Category/Images/file2.jpg'},
    ]
    
    creator = LinkCreator(db, views_root=r"U:\_Views")
    created, errors = creator.create_links(mappings, view, dry_run=dry_run)
    creator.close()
    print(f"Dry-run: {dry_run}, Created: {created}, Errors: {errors}")