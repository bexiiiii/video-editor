#!/usr/bin/env python3
"""CLI wrapper for providers/broll.py — automatic topic B-roll (client clip → screen capture → stock → slot), see --help."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "providers"))
from broll import main  # noqa: E402  (resolves to providers/broll.py)

if __name__ == "__main__":
    main()
