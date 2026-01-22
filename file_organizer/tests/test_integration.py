"""
Integration test for the file organizer pipeline.
"""
import tempfile
import shutil
import os
import sqlite3
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from scanner import FileScanner
from categorizer import Categorizer
from rule_engine import RuleEngine
from view_generator import ViewGenerator

def create_test_files(root: Path):
    """Create a small set of dummy files."""
    (root / "document.pdf").write_bytes(b"dummy pdf")
    (root / "image.jpg").write_bytes(b"dummy jpg")
    (root / "code.py").write_text("print('hello')")
    (root / "data.csv").write_text("a,b,c")
    (root / "subdir").mkdir()
    (root / "subdir" / "notes.txt").write_text("some notes")
    (root / "subdir" / "photo.png").write_bytes(b"dummy png")

def test_scan():
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        create_test_files(tmp_path)
        
        db_path = tmp_path / "test.db"
        scanner = FileScanner(str(db_path))
        scanner.scan(str(tmp_path), compute_hash=False)
        scanner.close()
        
        # Verify that files are in database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM files")
        count = cursor.fetchone()[0]
        assert count == 7, f"Expected 7 files, got {count}"
        conn.close()
        print("✓ Scan test passed")

def test_categorize():
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        create_test_files(tmp_path)
        
        db_path = tmp_path / "test.db"
        scanner = FileScanner(str(db_path))
        scanner.scan(str(tmp_path), compute_hash=False)
        scanner.close()
        
        # Categorize
        cat = Categorizer(str(Path(__file__).parent.parent / 'config' / 'categories.yaml'))
        conn = sqlite3.connect(db_path)
        cat.update_database(conn)
        
        cursor = conn.cursor()
        cursor.execute("SELECT category, subcategory FROM files WHERE name = 'document.pdf'")
        row = cursor.fetchone()
        assert row[0] == 'Documents' and row[1] == 'PDF', f"Unexpected categorization: {row}"
        conn.close()
        print("✓ Categorization test passed")

def test_rule_engine():
    # Create a simple rule file
    import yaml
    rules = {
        'views': {
            'ByCategory': {
                'rules': [
                    {'condition': {'category': 'Documents'}, 'target': 'Docs/{name}'},
                    {'condition': {}, 'target': 'Other/{name}'}
                ]
            }
        }
    }
    
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        rules_file = tmp_path / 'rules.yaml'
        with open(rules_file, 'w') as f:
            yaml.dump(rules, f)
        
        # Need a database with categorized files
        db_path = tmp_path / "test.db"
        scanner = FileScanner(str(db_path))
        create_test_files(tmp_path)
        scanner.scan(str(tmp_path), compute_hash=False)
        scanner.close()
        
        cat = Categorizer(str(Path(__file__).parent.parent / 'config' / 'categories.yaml'))
        conn = sqlite3.connect(db_path)
        cat.update_database(conn)
        conn.close()
        
        engine = RuleEngine(str(db_path), str(rules_file))
        mappings = engine.generate_view('ByCategory')
        engine.close()
        
        # Should have 7 mappings (one per test file)
        assert len(mappings) == 7
        # At least one mapping target starts with 'Docs/'
        doc_targets = [m for m in mappings if m['target_path'].startswith('Docs/')]
        assert len(doc_targets) >= 1
        print("✓ Rule engine test passed")

def test_view_generator():
    import yaml
    rules = {
        'views': {
            'ByCategory': {
                'rules': [
                    {'condition': {'category': 'Documents'}, 'target': 'Docs/{name}'},
                    {'condition': {}, 'target': 'Other/{name}'}
                ]
            }
        }
    }
    
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        rules_file = tmp_path / 'rules.yaml'
        with open(rules_file, 'w') as f:
            yaml.dump(rules, f)
        
        db_path = tmp_path / "test.db"
        scanner = FileScanner(str(db_path))
        create_test_files(tmp_path)
        scanner.scan(str(tmp_path), compute_hash=False)
        scanner.close()
        
        cat = Categorizer(str(Path(__file__).parent.parent / 'config' / 'categories.yaml'))
        conn = sqlite3.connect(db_path)
        cat.update_database(conn)
        conn.close()
        
        gen = ViewGenerator(str(db_path), str(rules_file))
        mappings = gen.generate_all_views()
        assert 'ByCategory' in mappings
        assert len(mappings['ByCategory']) == 7
        
        # Generate dry-run report
        report_path = tmp_path / 'report.html'
        gen.create_dry_run_report(str(report_path), mappings)
        assert report_path.exists()
        gen.close()
        print("✓ View generator test passed")

if __name__ == '__main__':
    print("Running integration tests...")
    test_scan()
    test_categorize()
    test_rule_engine()
    test_view_generator()
    print("All tests passed!")