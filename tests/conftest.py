# tests/conftest.py
import sys
from pathlib import Path

# Add repo root to sys.path so tests can import local modules like encontrar_move.py
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
