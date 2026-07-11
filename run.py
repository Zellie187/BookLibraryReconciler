"""
Book Library Reconciler Launcher

Always start the application from here.
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
SRC_FOLDER = PROJECT_ROOT / "src"

# Add src to Python path
sys.path.insert(0, str(SRC_FOLDER))

from main import main


if __name__ == "__main__":
    main()