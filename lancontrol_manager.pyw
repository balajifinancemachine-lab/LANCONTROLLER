#!/usr/bin/env pythonw
"""
LANControl Manager (Compatibility Proxy for LANController)
===========================================================
Seamless backward-compatibility launcher that delegates directly to
LANController.pyw, ensuring all legacy scripts, tasks, and shortcuts work.
"""

from __future__ import annotations

import runpy
from pathlib import Path

# Re-export all public API symbols from LANController
from LANController import *

if __name__ == "__main__":
    target = Path(__file__).parent / "LANController.pyw"
    if target.exists():
        runpy.run_path(str(target), run_name="__main__")
    else:
        main()
