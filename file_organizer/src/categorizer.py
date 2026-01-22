"""
Categorize files based on extension mapping and heuristic rules.
"""
import yaml
import re
from pathlib import Path
from typing import Dict, Tuple, Optional
import logging

logger = logging.getLogger(__name__)

class Categorizer:
    def __init__(self, config_path: str):
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        self.mapping = config.get('mapping', {})
        self.default = config.get('default', {'category': 'Miscellaneous', 'subcategory': 'Unknown'})
        
        # Pre-compile regex patterns for filename-based categorization
        # Note: Patterns are evaluated in order, so more specific patterns should come first
        # Using word boundaries (\b) to avoid false matches (e.g., "cascade" shouldn't match "cad")
        self.patterns = [
            # More specific patterns first
            (re.compile(r'(?i)\bscreenshot\b'), ('Images', 'Screenshots')),
            (re.compile(r'(?i)\binvoice\b'), ('Documents', 'Invoices')),
            (re.compile(r'(?i)\bresume\b'), ('Documents', 'Resumes')),
            (re.compile(r'(?i)\bdiagram\b'), ('Images', 'Diagrams')),
            (re.compile(r'(?i)\bcad\b'), ('CAD', 'AutoCAD')),
            (re.compile(r'(?i)\bdrawing\b'), ('CAD', 'Drawings')),
            # More general patterns last
            (re.compile(r'(?i)\breport\b'), ('Documents', 'Reports')),
            (re.compile(r'(?i)\bphoto\b'), ('Images', 'Photos')),
            (re.compile(r'(?i)\bproject\b'), ('Projects', 'General')),
        ]
    
    def categorize_by_extension(self, extension: str) -> Tuple[str, str]:
        """Return (category, subcategory) for a given file extension (without dot)."""
        ext = extension.lower() if extension else ''
        if ext in self.mapping:
            cat = self.mapping[ext].get('category', self.default['category'])
            sub = self.mapping[ext].get('subcategory', self.default['subcategory'])
            return cat, sub
        return self.default['category'], self.default['subcategory']
    
    def categorize_by_filename(self, filename: str) -> Optional[Tuple[str, str]]:
        """Attempt to categorize based on filename patterns."""
        for pattern, cats in self.patterns:
            if pattern.match(filename):
                return cats
        return None
    
    def categorize(self, file_path: Path, extension: str = None) -> Tuple[str, str]:
        """
        Determine category and subcategory for a file.
        Priority: extension mapping → filename patterns → default.
        """
        if extension is None:
            extension = file_path.suffix
            if extension.startswith('.'):
                extension = extension[1:]
        
        # Try extension mapping first
        ext_cat = self.categorize_by_extension(extension)
        # If extension maps to default (unknown), try filename patterns
        if ext_cat == (self.default['category'], self.default['subcategory']):
            filename = file_path.name
            fn_cat = self.categorize_by_filename(filename)
            if fn_cat:
                return fn_cat
        
        return ext_cat
    
    def update_database(self, db_connection):
        """
        Update the 'files' table with category and subcategory for all entries.
        """
        cursor = db_connection.cursor()
        cursor.execute("SELECT id, path FROM files WHERE category IS NULL")
        rows = cursor.fetchall()
        
        updated = 0
        for row_id, path_str in rows:
            path = Path(path_str)
            category, subcategory = self.categorize(path)
            cursor.execute(
                "UPDATE files SET category = ?, subcategory = ? WHERE id = ?",
                (category, subcategory, row_id)
            )
            updated += 1
        
        db_connection.commit()
        logger.info(f"Updated categories for {updated} files.")


if __name__ == "__main__":
    # Simple test
    cat = Categorizer("config/categories.yaml")
    test_files = [
        "invoice_2025.pdf",
        "report.xlsx",
        "screenshot.png",
        "project.dwg",
        "unknown.xyz"
    ]
    for f in test_files:
        cat_result = cat.categorize(Path(f))
        print(f"{f} → {cat_result}")