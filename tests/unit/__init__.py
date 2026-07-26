"""Ensure kung-fu root is on sys.path when unit tests load."""
from __future__ import annotations

import sys
from pathlib import Path

KUNG_FU_ROOT = Path(__file__).resolve().parents[2]
if str(KUNG_FU_ROOT) not in sys.path:
    sys.path.insert(0, str(KUNG_FU_ROOT))

import bootstrap  # noqa: F401
