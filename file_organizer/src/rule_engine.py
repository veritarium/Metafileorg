"""
Rule engine for defining virtual views.
"""
import yaml
import sqlite3
from pathlib import Path, PureWindowsPath
import re
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import logging
import math
import operator

logger = logging.getLogger(__name__)

class RuleEngine:
    """
    Evaluates rules against file metadata to determine target paths for virtual views.
    """
    
    def __init__(self, db_path: str, rules_path: str):
        self.db_path = db_path
        self.rules = self._load_rules(rules_path)
        self.conn = sqlite3.connect(db_path)
    
    def _load_rules(self, path: str) -> Dict:
        with open(path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def evaluate_rule(self, rule: Dict, file_row: Dict) -> Optional[str]:
        """
        Evaluate a single rule against file metadata.
        If the rule matches, return the target path (relative to view root).
        Otherwise return None.
        """
        # Condition evaluation
        condition = rule.get('condition')
        if condition and not self._evaluate_condition(condition, file_row):
            return None
        
        # Compute target path
        template = rule.get('target', '')
        if not template:
            return None
        
        return self._render_template(template, file_row)
    
    def _evaluate_condition(self, condition: Any, file_row: Dict) -> bool:
        """Evaluate a condition expression."""
        if isinstance(condition, dict):
            # Assume AND of multiple key‑value pairs
            for key, expected in condition.items():
                if not self._evaluate_key_value(key, expected, file_row):
                    return False
            return True
        elif isinstance(condition, list):
            # List of sub‑conditions (AND)
            for sub in condition:
                if not self._evaluate_condition(sub, file_row):
                    return False
            return True
        else:
            # Simple truthy check
            return bool(condition)
    
    def _evaluate_key_value(self, key: str, expected, file_row: Dict) -> bool:
        """Evaluate a single key‑value condition, supporting operators."""
        actual = file_row.get(key)
        # If expected is a string containing operators
        if isinstance(expected, str):
            return self._evaluate_expression(actual, expected, file_row)
        else:
            # Fall back to simple comparison
            return self._compare(actual, expected)
    
    def _evaluate_expression(self, actual, expression: str, file_row: Dict) -> bool:
        """
        Evaluate an expression like ">= 102400", ">= now - 30 days", 
        ">= 102400 and size < 1048576", etc.
        """
        # Normalize spaces
        expr = expression.strip()
        # If expression contains ' and ' or ' or ' we split (simple support for AND/OR)
        # For simplicity, we only support AND for now.
        if ' and ' in expr:
            parts = [p.strip() for p in expr.split(' and ')]
            return all(self._evaluate_expression(actual, p, file_row) for p in parts)
        if ' or ' in expr:
            parts = [p.strip() for p in expr.split(' or ')]
            return any(self._evaluate_expression(actual, p, file_row) for p in parts)
        
        # Parse comparison operator
        # Patterns: operator number, operator "now - X days", operator variable
        # Supported operators: <, >, <=, >=, ==, !=
        m = re.match(r'^\s*(<|>|<=|>=|==|!=)\s*(.+)$', expr)
        if m:
            op_str, rhs = m.groups()
            # Evaluate right-hand side
            rhs_val = self._eval_rhs(rhs, file_row)
            # Convert actual to appropriate type
            actual_val = self._coerce_to_number(actual)
            if actual_val is None:
                return False
            # Perform comparison
            op_map = {
                '<': operator.lt,
                '>': operator.gt,
                '<=': operator.le,
                '>=': operator.ge,
                '==': operator.eq,
                '!=': operator.ne,
            }
            try:
                return op_map[op_str](actual_val, rhs_val)
            except (TypeError, ValueError):
                return False
        
        # If no operator, fall back to simple comparison
        return self._compare(actual, expression)
    
    def _eval_rhs(self, rhs: str, file_row: Dict):
        """Evaluate right-hand side expression to a numeric or datetime value."""
        rhs = rhs.strip()
        # Check for "now - X days"
        now_match = re.match(r'now\s*-\s*(\d+)\s*days?', rhs, re.IGNORECASE)
        if now_match:
            days = int(now_match.group(1))
            return (datetime.now() - timedelta(days=days)).timestamp()
        # Check for "now"
        if rhs.lower() == 'now':
            return datetime.now().timestamp()
        # Check for numeric
        try:
            return int(rhs)
        except ValueError:
            try:
                return float(rhs)
            except ValueError:
                pass
        # Could be a column reference
        if rhs in file_row:
            return self._coerce_to_number(file_row[rhs])
        # Return as string
        return rhs
    
    def _coerce_to_number(self, value):
        """Try to convert value to int or float."""
        if value is None:
            return None
        if isinstance(value, (int, float)):
            return value
        try:
            return int(value)
        except ValueError:
            try:
                return float(value)
            except ValueError:
                return None
    
    def _compare(self, actual, expected) -> bool:
        """Compare actual value with expected pattern."""
        if isinstance(expected, str) and expected.startswith('/') and expected.endswith('/'):
            # Regex pattern
            pattern = expected[1:-1]
            return bool(re.match(pattern, str(actual), re.IGNORECASE))
        elif isinstance(expected, str) and '*' in expected:
            # Wildcard pattern (convert to regex)
            pattern = '^' + re.escape(expected).replace('\\*', '.*') + '$'
            return bool(re.match(pattern, str(actual), re.IGNORECASE))
        else:
            # Exact match (case‑insensitive for strings)
            if isinstance(actual, str) and isinstance(expected, str):
                return actual.lower() == expected.lower()
            return actual == expected
    
    def _render_template(self, template: str, file_row: Dict) -> str:
        """Render a path template using file metadata."""
        # Replace placeholders like {category}, {year}, etc.
        def replace(match):
            key = match.group(1)
            # Special handlers
            if key == 'year':
                dt = self._parse_date(file_row.get('created'))
                return dt.strftime('%Y') if dt else 'Unknown'
            if key == 'month':
                dt = self._parse_date(file_row.get('created'))
                return dt.strftime('%m') if dt else '00'
            if key == 'month_name':
                dt = self._parse_date(file_row.get('created'))
                return dt.strftime('%B') if dt else 'Unknown'
            if key == 'day':
                dt = self._parse_date(file_row.get('created'))
                return dt.strftime('%d') if dt else '00'
            # Direct attribute
            value = file_row.get(key, '')
            # Sanitize for filesystem
            return self._sanitize(str(value))
        
        result = re.sub(r'\{(\w+)\}', replace, template)
        # Ensure no double slashes
        result = re.sub(r'/+', '/', result)
        return result.strip('/')
    
    def _parse_date(self, timestamp: float) -> Optional[datetime]:
        if timestamp:
            try:
                return datetime.fromtimestamp(timestamp)
            except (ValueError, OSError):
                pass
        return None
    
    def _sanitize(self, text: str) -> str:
        """Replace characters that are invalid in Windows filenames."""
        invalid = r'[<>:"/\\|?*]'
        return re.sub(invalid, '_', text)
    
    def generate_view(self, view_name: str) -> List[Dict]:
        """
        Generate the mapping for a given view.
        Returns list of dicts with keys: source_path, target_path, view_name.
        """
        view_config = self.rules.get('views', {}).get(view_name)
        if not view_config:
            raise ValueError(f"View '{view_name}' not found in rules.")
        
        rules = view_config.get('rules', [])
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM files")
        columns = [col[0] for col in cursor.description]
        rows = cursor.fetchall()
        
        mappings = []
        for row in rows:
            file_row = dict(zip(columns, row))
            for rule in rules:
                target = self.evaluate_rule(rule, file_row)
                if target:
                    mappings.append({
                        'source_path': file_row['path'],
                        'target_path': target,
                        'view_name': view_name
                    })
                    break  # first matching rule wins
        
        return mappings
    
    def close(self):
        self.conn.close()


if __name__ == "__main__":
    # Example rule file structure
    example_rules = """
views:
  ByCategory:
    rules:
      - condition:
          category: Documents
        target: "Documents/{subcategory}/{name}"
      - condition:
          category: Images
        target: "Images/{subcategory}/{name}"
      - condition: {}
        target: "Miscellaneous/{name}"
  ByDate:
    rules:
      - condition: {}
        target: "{year}/{month_name}/{name}"
    """
    
    # Write example rules
    with open('config/example_rules.yaml', 'w') as f:
        f.write(example_rules)
    
    print("Example rules written to config/example_rules.yaml")
