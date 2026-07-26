"""Add kung-fu root to sys.path."""
from __future__ import annotations

import sys
from pathlib import Path

KUNG_FU_ROOT = Path(__file__).resolve().parent
if str(KUNG_FU_ROOT) not in sys.path:
    sys.path.insert(0, str(KUNG_FU_ROOT))
