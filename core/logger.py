"""
Central logging system for TuxStrap.
Logs to ~/.config/tuxstrap/tuxstrap.log and streams live events to GUI console.
"""

import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Callable, List, Optional

LOG_DIR = Path.home() / ".config" / "tuxstrap"
LOG_FILE = LOG_DIR / "tuxstrap.log"

_callbacks: List[Callable[[str, str], None]] = []


def init_logger():
    """Initializes log directory and rotates log file if too large."""
    try:
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        if LOG_FILE.exists() and LOG_FILE.stat().st_size > 2 * 1024 * 1024:
            # Rotate if larger than 2MB
            old_log = LOG_DIR / "tuxstrap_old.log"
            LOG_FILE.replace(old_log)
    except Exception:
        pass


def log(msg: str, level: str = "INFO"):
    """Logs message with timestamp and level."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    formatted = f"[{timestamp}] [{level}] {msg}"
    print(formatted)

    try:
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(formatted + "\n")
    except Exception:
        pass

    for cb in _callbacks:
        try:
            cb(formatted, level)
        except Exception:
            pass


def add_log_listener(cb: Callable[[str, str], None]):
    if cb not in _callbacks:
        _callbacks.append(cb)


def get_log_file_path() -> Path:
    return LOG_FILE
