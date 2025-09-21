#!/usr/bin/env python3
"""
Simple syntax check for watermark.py
"""

import ast
import sys

def check_syntax(filename):
    """Check if Python file has valid syntax"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            source = f.read()

        ast.parse(source)
        print(f"✓ {filename} has valid Python syntax")
        return True

    except SyntaxError as e:
        print(f"✗ Syntax error in {filename}:")
        print(f"  Line {e.lineno}: {e.text}")
        print(f"  {e.msg}")
        return False

    except Exception as e:
        print(f"✗ Error reading {filename}: {e}")
        return False

if __name__ == "__main__":
    success = check_syntax("watermark.py")
    sys.exit(0 if success else 1)