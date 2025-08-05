#!/usr/bin/env python3
"""
CLI entry point for the encrypted keylogger.
This script can be run from the project root directory.
"""

import sys
import os
from pathlib import Path

# Add the src directory to Python path
project_root = Path(__file__).parent
src_dir = project_root / "src"
sys.path.insert(0, str(src_dir))

# Import and run the CLI tool
if __name__ == "__main__":
    try:
        from keylogger_cli import main
        main()
    except ImportError as e:
        print(f"Error importing keylogger_cli module: {e}")
        print("Make sure you're running this from the project root directory.")
        sys.exit(1)
    except Exception as e:
        print(f"Error running CLI tool: {e}")
        sys.exit(1)
