"""
Database schema and management for the file catalog.
"""
import sqlite3
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class CatalogDatabase:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        # Enable foreign key constraints
        self.conn.execute("PRAGMA foreign_keys = ON")
        self._create_schema()
    
    def _create_schema(self):
        cursor = self.conn.cursor()
        
        # Main files table (already created by scanner)
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
                extra_json TEXT,
                indexed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Tags table (many‑to‑many)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tags (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS file_tags (
                file_id INTEGER NOT NULL,
                tag_id INTEGER NOT NULL,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (file_id, tag_id),
                FOREIGN KEY (file_id) REFERENCES files(id) ON DELETE CASCADE,
                FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
            )
        """)
        
        # Duplicate groups
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS duplicate_groups (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                hash_sha256 TEXT NOT NULL,
                file_count INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS duplicate_files (
                file_id INTEGER NOT NULL,
                group_id INTEGER NOT NULL,
                PRIMARY KEY (file_id),
                FOREIGN KEY (file_id) REFERENCES files(id) ON DELETE CASCADE,
                FOREIGN KEY (group_id) REFERENCES duplicate_groups(id) ON DELETE CASCADE
            )
        """)
        
        # Relationships (file‑to‑file)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS relationships (
                source_id INTEGER NOT NULL,
                target_id INTEGER NOT NULL,
                relation_type TEXT NOT NULL,  -- 'includes', 'references', 'version_of', etc.
                strength REAL DEFAULT 1.0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (source_id, target_id, relation_type),
                FOREIGN KEY (source_id) REFERENCES files(id) ON DELETE CASCADE,
                FOREIGN KEY (target_id) REFERENCES files(id) ON DELETE CASCADE
            )
        """)
        
        # Views (virtual view definitions)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS views (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                description TEXT,
                config_json TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Link transactions (already created by link_creator)
        
        # Create indexes for performance
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_files_path ON files(path)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_files_extension ON files(extension)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_files_category ON files(category)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_files_created ON files(created)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_files_hash ON files(hash_sha256)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_duplicate_hash ON duplicate_groups(hash_sha256)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_tags_name ON tags(name)")
        
        self.conn.commit()
        logger.info("Database schema ensured.")
    
    def add_tag(self, file_id: int, tag_name: str):
        """Add a tag to a file."""
        cursor = self.conn.cursor()
        # Ensure tag exists
        cursor.execute("INSERT OR IGNORE INTO tags (name) VALUES (?)", (tag_name,))
        cursor.execute("SELECT id FROM tags WHERE name = ?", (tag_name,))
        tag_id = cursor.fetchone()[0]
        # Link file to tag
        cursor.execute("INSERT OR IGNORE INTO file_tags (file_id, tag_id) VALUES (?, ?)", (file_id, tag_id))
        self.conn.commit()
    
    def find_duplicates(self, threshold_mb: int = 10):
        """
        Identify duplicate files based on hash.
        Only consider files larger than threshold_mb (optional) to avoid hashing tiny files.
        """
        cursor = self.conn.cursor()
        # Select files with same hash
        cursor.execute("""
            SELECT hash_sha256, GROUP_CONCAT(id) as ids
            FROM files
            WHERE hash_sha256 IS NOT NULL
            GROUP BY hash_sha256
            HAVING COUNT(*) > 1
        """)
        duplicates = []
        for row in cursor.fetchall():
            hash_val, ids_str = row
            file_ids = [int(id) for id in ids_str.split(',')]
            duplicates.append((hash_val, file_ids))
        
        # Store in duplicate_groups
        for hash_val, file_ids in duplicates:
            cursor.execute("INSERT INTO duplicate_groups (hash_sha256, file_count) VALUES (?, ?)",
                           (hash_val, len(file_ids)))
            group_id = cursor.lastrowid
            for fid in file_ids:
                cursor.execute("INSERT OR IGNORE INTO duplicate_files (file_id, group_id) VALUES (?, ?)",
                               (fid, group_id))
        
        self.conn.commit()
        logger.info(f"Found {len(duplicates)} duplicate groups.")
        return duplicates
    
    def close(self):
        self.conn.close()


if __name__ == "__main__":
    # Initialize database
    db = CatalogDatabase("test_catalog.db")
    db.close()
    print("Database schema created.")