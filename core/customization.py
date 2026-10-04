"""
Customization manager for TuxStrap.
Handles Roblox client appearance mods (Fonts, Sounds, Cursors) and TuxStrap GUI customization (Background image, CSS).
"""

import os
import shutil
from pathlib import Path
from typing import Dict, List, Optional

SOBER_DATA_DIR = Path.home() / ".var" / "app" / "org.vinegarhq.Sober" / "data" / "sober"
ASSETS_OVERRIDE_DIR = SOBER_DATA_DIR / "content"

# Sample sound definitions
SOUND_PRESETS = {
    "Default (Varsayılan)": None,
    "Classic Oof (Nostaljik 2006 Sesi)": "classic_oof.ogg",
    "Sessiz / Mute": "silent.ogg"
}

CURSOR_PRESETS = {
    "Default (Varsayılan)": None,
    "Classic Arrow (2015 Klasik İmleç)": "classic_arrow.png",
    "Minimal Dot (Nokta / Rekabetçi İmleç)": "minimal_dot.png"
}


class CustomizationManager:
    def __init__(self, config_manager):
        self.config_manager = config_manager

    def set_background_image(self, image_path: str):
        """Sets a custom background image for TuxStrap GUI."""
        if os.path.exists(image_path) or image_path == "":
            self.config_manager.settings["background_image"] = image_path
            self.config_manager.save_tuxstrap_settings()

    def get_background_image(self) -> str:
        return self.config_manager.settings.get("background_image", "")

    def set_home_screen_mode(self, mode: str):
        """Sets Roblox home screen mode: desktop, console, or mobile."""
        valid_modes = ["desktop", "console", "mobile"]
        if mode in valid_modes:
            self.config_manager.settings["home_screen_mode"] = mode
            self.config_manager.save_tuxstrap_settings()
            self.config_manager.sync_to_sober()

    def get_home_screen_mode(self) -> str:
        return self.config_manager.settings.get("home_screen_mode", "desktop")

    def set_hidpi(self, enabled: bool):
        self.config_manager.settings["enable_hidpi"] = enabled
        self.config_manager.save_tuxstrap_settings()
        self.config_manager.sync_to_sober()

    def is_hidpi_enabled(self) -> bool:
        return self.config_manager.settings.get("enable_hidpi", False)
