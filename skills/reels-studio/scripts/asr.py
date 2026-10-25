#!/usr/bin/env python3
"""CLI wrapper for providers/asr.py — see that module (or --help) for the provider chain."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "providers"))
from asr import main  # noqa: E402  (resolves to providers/asr.py, which is first on sys.path)

if __name__ == "__main__":
    main()
