"""
Main entry point for the File Organizer tool.
"""
import argparse
import sys
import os
import sqlite3
from pathlib import Path
import logging

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from scanner import FileScanner
from categorizer import Categorizer
from database import CatalogDatabase
from rule_engine import RuleEngine
from view_generator import ViewGenerator
from link_creator import LinkCreator

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def scan_command(args):
    """Scan a directory and populate database."""
    scanner = FileScanner(args.db)
    try:
        scanner.scan(args.root, compute_hash=args.hash, extensions_ignore=args.ignore)
        
        # Categorize
        if not args.no_categorize:
            cat = Categorizer(args.categories)
            cat.update_database(scanner.conn)
        
        # Duplicate detection
        if args.detect_duplicates:
            if not args.hash:
                logger.warning("Duplicate detection requires hash computation. Skipping.")
            else:
                db = CatalogDatabase(args.db)
                duplicates = db.find_duplicates()
                db.close()
                logger.info(f"Found {len(duplicates)} duplicate groups.")
        
        logger.info(f"Scan completed. Database: {args.db}")
    finally:
        scanner.close()

def categorize_command(args):
    """Run categorization on existing database."""
    cat = Categorizer(args.categories)
    conn = sqlite3.connect(args.db)
    cat.update_database(conn)
    conn.close()
    logger.info("Categorization complete.")

def duplicates_command(args):
    """Find duplicate files in database."""
    db = CatalogDatabase(args.db)
    duplicates = db.find_duplicates(threshold_mb=args.threshold_mb)
    db.close()
    logger.info(f"Found {len(duplicates)} duplicate groups.")

def generate_command(args):
    """Generate virtual view mappings."""
    engine = RuleEngine(args.db, args.rules)
    mappings = engine.generate_view(args.view)
    engine.close()
    
    # Save mappings as JSON
    import json
    with open(args.output, 'w') as f:
        json.dump(mappings, f, indent=2)
    logger.info(f"Generated {len(mappings)} mappings for view '{args.view}' -> {args.output}")

def dryrun_command(args):
    """Create a dry‑run HTML report."""
    gen = ViewGenerator(args.db, args.rules)
    mappings = gen.generate_all_views()
    gen.create_dry_run_report(args.output, mappings)
    gen.close()
    logger.info(f"Dry‑run report written to {args.output}")

def link_command(args):
    """Create symbolic links for a view."""
    import json
    with open(args.mappings, 'r') as f:
        mappings = json.load(f)
    
    creator = LinkCreator(args.db, views_root=args.views_root)
    created, errors = creator.create_links(mappings, args.view, dry_run=args.dry_run)
    creator.close()
    
    if args.dry_run:
        logger.info(f"[DRY‑RUN] Would create {created} links, {errors} errors.")
    else:
        logger.info(f"Created {created} links, {errors} errors.")

def web_command(args):
    """Start the web search interface."""
    from webui.app import app
    app.run(debug=args.debug, port=args.port)

def main():
    parser = argparse.ArgumentParser(description="Virtual File Organization Tool")
    subparsers = parser.add_subparsers(dest='command', required=True)
    
    # scan
    scan_parser = subparsers.add_parser('scan', help='Scan a directory')
    scan_parser.add_argument('root', help='Root directory to scan')
    scan_parser.add_argument('--db', default='catalog.db', help='Database path')
    scan_parser.add_argument('--hash', action='store_true', help='Compute SHA‑256 hash')
    scan_parser.add_argument('--detect-duplicates', action='store_true', help='Run duplicate detection after scanning (requires --hash)')
    scan_parser.add_argument('--ignore', nargs='*', default=[], help='Extensions to ignore')
    scan_parser.add_argument('--no-categorize', action='store_true', help='Skip categorization')
    scan_parser.add_argument('--categories', default='config/categories.yaml', help='Category mapping')
    
    # categorize
    cat_parser = subparsers.add_parser('categorize', help='Categorize files in database')
    cat_parser.add_argument('--db', default='catalog.db', help='Database path')
    cat_parser.add_argument('--categories', default='config/categories.yaml', help='Category mapping')
    
    # generate
    gen_parser = subparsers.add_parser('generate', help='Generate virtual view mappings')
    gen_parser.add_argument('view', help='View name')
    gen_parser.add_argument('--db', default='catalog.db', help='Database path')
    gen_parser.add_argument('--rules', default='config/views.yaml', help='Rules file')
    gen_parser.add_argument('--output', default='mappings.json', help='Output JSON file')
    
    # dryrun
    dryrun_parser = subparsers.add_parser('dryrun', help='Generate dry‑run HTML report')
    dryrun_parser.add_argument('--db', default='catalog.db', help='Database path')
    dryrun_parser.add_argument('--rules', default='config/views.yaml', help='Rules file')
    dryrun_parser.add_argument('--output', default='dryrun_report.html', help='Output HTML file')
    
    # link
    link_parser = subparsers.add_parser('link', help='Create symbolic links')
    link_parser.add_argument('view', help='View name')
    link_parser.add_argument('--mappings', required=True, help='JSON mappings file')
    link_parser.add_argument('--db', default='catalog.db', help='Database path')
    link_parser.add_argument('--views-root', default='./_Views', help='Root for virtual views')
    link_parser.add_argument('--dry-run', action='store_true', help='Only log, do not create links')
    
    # duplicates
    dup_parser = subparsers.add_parser('duplicates', help='Find duplicate files')
    dup_parser.add_argument('--db', default='catalog.db', help='Database path')
    dup_parser.add_argument('--threshold-mb', type=int, default=10, help='Minimum file size in MB to consider')
    
    # web
    web_parser = subparsers.add_parser('web', help='Start web search interface')
    web_parser.add_argument('--port', type=int, default=5000, help='Port to listen on')
    web_parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    
    args = parser.parse_args()
    
    if args.command == 'scan':
        scan_command(args)
    elif args.command == 'categorize':
        categorize_command(args)
    elif args.command == 'generate':
        generate_command(args)
    elif args.command == 'dryrun':
        dryrun_command(args)
    elif args.command == 'link':
        link_command(args)
    elif args.command == 'duplicates':
        duplicates_command(args)
    elif args.command == 'web':
        web_command(args)
    else:
        parser.print_help()

if __name__ == '__main__':
    main()