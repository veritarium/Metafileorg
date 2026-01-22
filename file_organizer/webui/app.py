"""
Simple web search interface for the file catalog.
"""
import sqlite3
from flask import Flask, render_template, request, jsonify
import json
import os
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))
from scanner import FileScanner

app = Flask(__name__)

# Configuration
DATABASE = str(Path(__file__).parent.parent / "catalog.db")  # absolute path
VIEWS_ROOT = "./_Views"  # relative to current working directory

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/search')
def search():
    query = request.args.get('q', '').strip()
    category = request.args.get('category', '')
    extension = request.args.get('extension', '')
    size_min = request.args.get('size_min', '')
    size_max = request.args.get('size_max', '')

    # Input validation with error handling
    try:
        limit = int(request.args.get('limit', 100))
        offset = int(request.args.get('offset', 0))

        # Sanity checks
        if limit < 1 or limit > 1000:
            return jsonify({'error': 'Limit must be between 1 and 1000'}), 400
        if offset < 0:
            return jsonify({'error': 'Offset must be non-negative'}), 400
    except ValueError as e:
        return jsonify({'error': f'Invalid numeric parameter: {str(e)}'}), 400

    conn = get_db()
    cursor = conn.cursor()
    
    # Build WHERE clause
    conditions = []
    params = []
    
    if query:
        conditions.append("(name LIKE ? OR path LIKE ?)")
        params.extend([f'%{query}%', f'%{query}%'])
    
    if category:
        conditions.append("category = ?")
        params.append(category)
    
    if extension:
        conditions.append("extension = ?")
        params.append(extension)
    
    if size_min:
        try:
            size_min_int = int(size_min)
            conditions.append("size >= ?")
            params.append(size_min_int)
        except ValueError:
            return jsonify({'error': 'Invalid size_min parameter'}), 400

    if size_max:
        try:
            size_max_int = int(size_max)
            conditions.append("size <= ?")
            params.append(size_max_int)
        except ValueError:
            return jsonify({'error': 'Invalid size_max parameter'}), 400
    
    where_clause = " AND ".join(conditions) if conditions else "1"

    try:
        # Get total count
        cursor.execute(f"SELECT COUNT(*) FROM files WHERE {where_clause}", params)
        total = cursor.fetchone()[0]

        # Get results
        sql = f"""
            SELECT id, path, name, extension, size, created, modified, accessed, category, subcategory
            FROM files
            WHERE {where_clause}
            ORDER BY created DESC
            LIMIT ? OFFSET ?
        """
        params.extend([limit, offset])
        cursor.execute(sql, params)
        rows = cursor.fetchall()

        # Convert rows to dicts
        results = []
        for row in rows:
            results.append(dict(row))

        return jsonify({
            'total': total,
            'results': results,
            'query': query
        })
    except Exception as e:
        logger.error(f"Database error in search: {e}")
        return jsonify({'error': 'Database query failed'}), 500
    finally:
        conn.close()

@app.route('/api/categories')
def categories():
    conn = get_db()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT category FROM files WHERE category IS NOT NULL ORDER BY category")
        categories = [row[0] for row in cursor.fetchall()]
        return jsonify(categories)
    except Exception as e:
        logger.error(f"Database error in categories: {e}")
        return jsonify({'error': 'Failed to retrieve categories'}), 500
    finally:
        conn.close()

@app.route('/api/extensions')
def extensions():
    conn = get_db()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT extension FROM files WHERE extension IS NOT NULL ORDER BY extension")
        extensions = [row[0] for row in cursor.fetchall()]
        return jsonify(extensions)
    except Exception as e:
        logger.error(f"Database error in extensions: {e}")
        return jsonify({'error': 'Failed to retrieve extensions'}), 500
    finally:
        conn.close()
    return jsonify(extensions)

@app.route('/api/duplicates')
def duplicates():
    conn = get_db()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT hash_sha256, GROUP_CONCAT(path) as paths, COUNT(*) as count
            FROM files
            WHERE hash_sha256 IS NOT NULL
            GROUP BY hash_sha256
            HAVING COUNT(*) > 1
            LIMIT 50
        """)
        rows = cursor.fetchall()
        duplicates = []
        for row in rows:
            duplicates.append({
                'hash': row[0],
                'paths': row[1].split(','),
                'count': row[2]
            })
        return jsonify(duplicates)
    except Exception as e:
        logger.error(f"Database error in duplicates: {e}")
        return jsonify({'error': 'Failed to retrieve duplicates'}), 500
    finally:
        conn.close()

@app.route('/api/scan', methods=['POST'])
def scan():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'JSON body required'}), 400
    root = data.get('root')
    if not root:
        return jsonify({'error': 'Missing "root" directory'}), 400
    compute_hash = data.get('compute_hash', False)
    ignore_extensions = data.get('ignore_extensions', [])
    # Convert space-separated strings to list of extensions with dot
    if isinstance(ignore_extensions, str):
        ignore_extensions = ignore_extensions.split()
    # Ensure each extension starts with a dot
    ignore_extensions = [ext if ext.startswith('.') else '.' + ext for ext in ignore_extensions if ext]
    # Ensure root is absolute path
    root_path = Path(root).resolve()
    if not root_path.exists():
        return jsonify({'error': 'Directory does not exist'}), 400
    if not root_path.is_dir():
        return jsonify({'error': 'Path is not a directory'}), 400
    try:
        scanner = FileScanner(DATABASE)
        result = scanner.scan(str(root_path), compute_hash=compute_hash, extensions_ignore=ignore_extensions)
        scanner.close()
        return jsonify({
            'success': True,
            'scanned': result['scanned'],
            'errors': result['errors'],
            'message': f'Scanned {root_path} ({result["scanned"]} files)'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/open/<int:file_id>')
def open_file(file_id):
    conn = get_db()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT path FROM files WHERE id = ?", (file_id,))
        row = cursor.fetchone()
    except Exception as e:
        logger.error(f"Database error in open_file: {e}")
        return jsonify({'error': 'Failed to retrieve file'}), 500
    finally:
        conn.close()
    if row:
        path = row[0]
        # On Windows, we could use os.startfile
        # For now just return path
        return jsonify({'path': path, 'exists': os.path.exists(path)})
    return jsonify({'error': 'File not found'}), 404

if __name__ == '__main__':
    # WARNING: This web interface has no authentication and is intended for LOCAL use only.
    # DO NOT expose this to a network without implementing proper security measures.

    # Ensure database exists
    if not os.path.exists(DATABASE):
        print(f"Database {DATABASE} not found. Run scanner first.")

    # Get configuration from environment variables
    debug_mode = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    port = int(os.getenv('FLASK_PORT', '5000'))

    if debug_mode:
        print("WARNING: Debug mode is enabled. Never use this in production!")

    app.run(debug=debug_mode, port=port, host='127.0.0.1')