"""
Configuration manager for TuxStrap and Sober.
"""

import os
import re
import json
from pathlib import Path
from typing import Dict, Any, Optional
from core.presets import PRESETS, DEFAULT_PRESET
from core.logger import log


def get_tuxstrap_config_dir() -> Path:
    override = os.environ.get("TUXSTRAP_CONFIG_DIR")
    return Path(override) if override else Path.home() / ".config" / "tuxstrap"


def get_sober_config_dir() -> Path:
    override = os.environ.get("SOBER_CONFIG_DIR")
    return Path(override) if override else Path.home() / ".var" / "app" / "org.vinegarhq.Sober" / "config" / "sober"


def get_sober_appdata_dir() -> Path:
    override = os.environ.get("SOBER_APPDATA_DIR")
    return Path(override) if override else Path.home() / ".var" / "app" / "org.vinegarhq.Sober" / "data" / "sober" / "appData"


def strip_json_comments(text: str) -> str:
    return "\n".join(
        line for line in text.splitlines()
        if not line.strip().startswith("//") and not line.strip().startswith("#")
    )


DEFAULT_SETTINGS: Dict[str, Any] = {
    "preset": DEFAULT_PRESET,
    "custom_flags": {},
    "use_gamemode": True,
    "enable_bypass": True,
    "home_screen_mode": "desktop",
    "enable_hidpi": False,
    "show_server_location": True,
    "background_image": "",
    "discord_rpc": True,
    "gpu_preference": "auto",
    "use_opengl": False,  # Vulkan (ANV) is Sober's native renderer; OpenGL causes black screen on Intel Iris Xe
}


class ConfigManager:
    def __init__(self, config_dir: Optional[Path] = None,
                 sober_dir: Optional[Path] = None,
                 appdata_dir: Optional[Path] = None):
        self.config_dir = config_dir or get_tuxstrap_config_dir()
        self.sober_dir = sober_dir or get_sober_config_dir()
        self.appdata_dir = appdata_dir or get_sober_appdata_dir()
        self.config_path = self.config_dir / "settings.json"
        self.sober_config_path = self.sober_dir / "config.json"
        self.settings_xml_path = self.appdata_dir / "GlobalBasicSettings_13.xml"
        self.settings: Dict[str, Any] = {}
        self.load_tuxstrap_settings()

    def load_tuxstrap_settings(self) -> Dict[str, Any]:
        try:
            self.config_dir.mkdir(parents=True, exist_ok=True)
            if self.config_path.exists():
                with open(self.config_path, "r", encoding="utf-8") as f:
                    self.settings = {**DEFAULT_SETTINGS, **json.load(f)}
                    return self.settings
        except Exception as e:
            log(f"[Config] Notice: {e}", "WARN")
        self.settings = DEFAULT_SETTINGS.copy()
        try:
            self.save_tuxstrap_settings()
        except Exception:
            pass
        return self.settings

    def save_tuxstrap_settings(self):
        try:
            self.config_dir.mkdir(parents=True, exist_ok=True)
            tmp = self.config_path.with_suffix(".tmp")
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(self.settings, f, indent=2, ensure_ascii=False)
            tmp.replace(self.config_path)
        except Exception as e:
            log(f"[Config Warning] Could not save settings: {e}", "WARN")

    def load_sober_config(self) -> Dict[str, Any]:
        if self.sober_config_path.exists():
            try:
                with open(self.sober_config_path, "r", encoding="utf-8") as f:
                    return json.loads(strip_json_comments(f.read()))
            except Exception as e:
                log(f"[Config Error] Sober config parse error: {e}", "ERROR")
        return {}

    def patch_roblox_xml_settings(self, target_fps: int = 0, quality_level: int = 1, saved_quality: int = 1):
        if not self.settings_xml_path.exists():
            return

        try:
            with open(self.settings_xml_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()

            content = re.sub(
                r'<int name="FramerateCap">-?\d+</int>',
                f'<int name="FramerateCap">{target_fps}</int>',
                content
            )
            content = re.sub(
                r'<token name="SavedQualityLevel">\d+</token>',
                f'<token name="SavedQualityLevel">{saved_quality}</token>',
                content
            )
            content = re.sub(
                r'<int name="GraphicsQualityLevel">\d+</int>',
                f'<int name="GraphicsQualityLevel">{quality_level}</int>',
                content
            )
            content = re.sub(
                r'<bool name="MaxQualityEnabled">(true|false)</bool>',
                '<bool name="MaxQualityEnabled">false</bool>',
                content
            )
            content = re.sub(
                r'<bool name="ReducedMotion">(true|false)</bool>',
                '<bool name="ReducedMotion">true</bool>',
                content
            )

            tmp = self.settings_xml_path.with_suffix(".tmp")
            with open(tmp, "w", encoding="utf-8") as f:
                f.write(content)
            tmp.replace(self.settings_xml_path)

            log(f"[XML Engine] Patched → FramerateCap={target_fps}, Quality={quality_level}, SavedQuality={saved_quality}")
        except Exception as e:
            log(f"[XML Engine Error] {e}", "ERROR")

    def sync_to_sober(self):
        self.sober_dir.mkdir(parents=True, exist_ok=True)
        sober_data = self.load_sober_config()

        preset_name = self.settings.get("preset", DEFAULT_PRESET)
        active_preset = PRESETS.get(preset_name, PRESETS[DEFAULT_PRESET])
        active_flags = {**active_preset.get("flags", {}), **self.settings.get("custom_flags", {})}

        sober_data["fflags"] = active_flags
        sober_data["graphics_optimization_mode"] = active_preset.get("graphics_optimization_mode", "performance")
        sober_data["enable_gamemode"] = self.settings.get("use_gamemode", True)
        sober_data["enable_hidpi"] = self.settings.get("enable_hidpi", False)
        sober_data["server_location_indicator_enabled"] = self.settings.get("show_server_location", True)
        sober_data["discord_rpc_enabled"] = self.settings.get("discord_rpc", True)

        # Vulkan (ANV) is Sober's official renderer. OpenGL must be false to avoid black screen.
        sober_data["use_opengl"] = self.settings.get("use_opengl", False)

        mode = self.settings.get("home_screen_mode", "desktop")
        sober_data["use_console_experience"] = (mode == "console")
        sober_data["enable_mobile_home_screen"] = (mode == "mobile")

        tmp = self.sober_config_path.with_suffix(".tmp")
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(sober_data, f, indent=4, ensure_ascii=False)
        tmp.replace(self.sober_config_path)

        self.patch_roblox_xml_settings(
            target_fps=active_preset.get("xml_framecap", 0),
            quality_level=active_preset.get("xml_quality", 1),
            saved_quality=active_preset.get("xml_saved_quality", 1)
        )

        log(f"[Config] Synced to Sober → {len(active_flags)} FFlags, Vulkan={not sober_data['use_opengl']}, GraphicsMode={sober_data['graphics_optimization_mode']}")
