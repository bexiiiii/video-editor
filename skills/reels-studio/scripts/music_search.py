#!/usr/bin/env python3
"""CLI wrapper for providers/music_search.py — internet music search (Openverse / Jamendo), see --help."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "providers"))
from music_search import main  # noqa: E402  (resolves to providers/music_search.py)

if __name__ == "__main__":
    main()
