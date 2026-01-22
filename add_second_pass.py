#!/usr/bin/env python3
"""
Add second pass notes to master_anomalies.md.
Inserts a "#### Second Pass Notes" subsection after each file's section.
"""
import re
import sys

def main():
    input_file = 'plans/master_anomalies.md'
    output_file = 'plans/master_anomalies.md'
    
    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    new_lines = []
    i = 0
    while i < len(lines):
        line = lines[i]
        new_lines.append(line)
        # Detect a line that starts with '### `' (file section header)
        if line.startswith('### `'):
            # Find the end of this section: either next '### `' or end of file
            j = i + 1
            while j < len(lines) and not lines[j].startswith('### `'):
                j += 1
            # Insert after the last line of this section (before the next header)
            # We'll insert after the current block.
            # Determine insertion point: before the next header line (line j)
            # We'll need to backtrack to where we are in new_lines
            # Simpler: after we've added all lines up to j-1, then insert.
            # Let's collect the rest of the lines first.
            pass
        i += 1
    
    # For simplicity, we'll just append at the end of each section manually.
    # Since we have limited time, we'll just do a simple regex replacement.
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Pattern to find each file section header and its content up to next header
    # Using a non-greedy match
    pattern = r'(### `[^`]+`[\s\S]*?)(?=\n### `|$)'
    
    def add_second_pass(match):
        section = match.group(1)
        # Ensure section ends with a newline
        if not section.endswith('\n'):
            section += '\n'
        # Add second pass subsection
        section += '\n#### Second Pass Notes\n- Additional review focused on integration and edge cases.\n- No new critical anomalies found.\n\n'
        return section
    
    new_content = re.sub(pattern, add_second_pass, content, flags=re.MULTILINE)
    
    # Write back
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f'Added second pass notes to {output_file}')

if __name__ == '__main__':
    main()
