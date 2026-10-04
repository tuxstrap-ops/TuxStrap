#!/usr/bin/env python3
"""
TuxStrap - Next-Gen Roblox Performance & Zero-Ping Bypass Launcher for Linux Mint.
"""

import sys
import os
import argparse
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

from core.config import ConfigManager
from core.launcher import GameLauncher


def run_cli_launch():
    """Direct CLI launch without GUI."""
    print("🐧 TuxStrap: Doğrudan başlatma modu...")
    cfg = ConfigManager()
    launcher = GameLauncher(cfg)
    launcher.launch()
    if launcher.current_process:
        launcher.current_process.wait()


def run_gui():
    """Launches the GTK3 GUI."""
    import gi
    gi.require_version('Gtk', '3.0')
    from gi.repository import Gtk
    from gui.app import TuxStrapWindow

    cfg = ConfigManager()
    app = TuxStrapWindow(cfg)
    app.show_all()
    Gtk.main()


def main():
    parser = argparse.ArgumentParser(description="TuxStrap - Linux Roblox Launcher & Optimizer")
    parser.add_argument("--launch", action="store_true", help="Roblox'u doğrudan optimize modda başlatır (Arayüzsüz)")
    args = parser.parse_args()

    if args.launch:
        run_cli_launch()
    else:
        run_gui()


if __name__ == "__main__":
    main()
