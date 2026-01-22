"""
Generate virtual folder structure based on rules.
"""
import sqlite3
import json
import yaml
from pathlib import Path, PureWindowsPath
import logging
from typing import List, Dict, Any
from rule_engine import RuleEngine

logger = logging.getLogger(__name__)

class ViewGenerator:
    def __init__(self, db_path: str, rules_path: str):
        self.db_path = db_path
        self.rules_path = rules_path
        self.rule_engine = RuleEngine(db_path, rules_path)
    
    def generate_for_view(self, view_name: str) -> List[Dict]:
        """Generate mapping for a single view."""
        return self.rule_engine.generate_view(view_name)
    
    def generate_all_views(self) -> Dict[str, List[Dict]]:
        """Generate mapping for all views defined in rules."""
        with open(self.rules_path, 'r', encoding='utf-8') as f:
            rules = json.load(f) if self.rules_path.endswith('.json') else yaml.safe_load(f)
        
        views = rules.get('views', {})
        result = {}
        for view_name in views.keys():
            try:
                result[view_name] = self.generate_for_view(view_name)
            except Exception as e:
                logger.error(f"Failed to generate view '{view_name}': {e}")
                result[view_name] = []
        return result
    
    def create_dry_run_report(self, output_path: str, view_mappings: Dict[str, List[Dict]]):
        """Generate an HTML report showing proposed changes."""
        import html
        from datetime import datetime
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Virtual Organization Dry‑Run Report</title>
            <style>
                body {{ font-family: sans-serif; margin: 2em; }}
                h1 {{ color: #333; }}
                .view {{ margin-bottom: 2em; border: 1px solid #ccc; padding: 1em; }}
                .view h2 {{ margin-top: 0; }}
                table {{ border-collapse: collapse; width: 100%; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
                tr:hover {{ background-color: #f9f9f9; }}
                .count {{ font-weight: bold; color: #555; }}
                .timestamp {{ color: #777; font-size: 0.9em; }}
            </style>
        </head>
        <body>
            <h1>Virtual Organization Dry‑Run Report</h1>
            <p class="timestamp">Generated {datetime.now().isoformat()}</p>
            <p>This report shows how files will be organized in each virtual view.
               No actual files have been moved; only symbolic links will be created.</p>
        """
        
        total_links = 0
        for view_name, mappings in view_mappings.items():
            html_content += f"""
            <div class="view">
                <h2>View: {html.escape(view_name)}</h2>
                <p class="count">{len(mappings)} files</p>
                <table>
                    <thead>
                        <tr>
                            <th>Source Path</th>
                            <th>Virtual Path</th>
                        </tr>
                    </thead>
                    <tbody>
            """
            for mapping in mappings[:100]:  # limit to first 100 rows per view
                src = html.escape(mapping['source_path'])
                tgt = html.escape(mapping['target_path'])
                html_content += f"""
                        <tr>
                            <td><code>{src}</code></td>
                            <td><code>{tgt}</code></td>
                        </tr>
                """
            if len(mappings) > 100:
                html_content += f"""
                        <tr>
                            <td colspan="2"><em>… and {len(mappings) - 100} more files</em></td>
                        </tr>
                """
            html_content += """
                    </tbody>
                </table>
            </div>
            """
            total_links += len(mappings)
        
        html_content += f"""
            <div style="margin-top: 2em; padding: 1em; background-color: #e8f4fd; border-radius: 5px;">
                <h3>Summary</h3>
                <p>Total virtual links to create: <strong>{total_links}</strong></p>
                <p>Total unique source files: <strong>{self._count_unique_files(view_mappings)}</strong></p>
                <p>No changes will be made to the original files.</p>
            </div>
        </body>
        </html>
        """
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        logger.info(f"Dry‑run report written to {output_path}")
    
    def _count_unique_files(self, view_mappings: Dict[str, List[Dict]]) -> int:
        unique_paths = set()
        for mappings in view_mappings.values():
            for mapping in mappings:
                unique_paths.add(mapping['source_path'])
        return len(unique_paths)
    
    def close(self):
        self.rule_engine.close()


if __name__ == "__main__":
    # Example usage
    import yaml
    import sys
    
    if len(sys.argv) < 4:
        print("Usage: python view_generator.py <db> <rules> <output_html>")
        sys.exit(1)
    
    db = sys.argv[1]
    rules = sys.argv[2]
    out = sys.argv[3]
    
    gen = ViewGenerator(db, rules)
    mappings = gen.generate_all_views()
    gen.create_dry_run_report(out, mappings)
    gen.close()
    print(f"Report generated: {out}")