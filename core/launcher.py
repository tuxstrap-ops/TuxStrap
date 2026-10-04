"""
Process execution and launcher engine for TuxStrap.
- ByeDPI + DoH bridge integration with verified -s 1 -o 1 -U.
- NO_PROXY injection to protect internal Sober/Flatpak UI WebSocket (10.110.101.222:5052).
- CPU Performance Mode (3.7GHz+).
- Vulkan (ANV) Native Hardware Acceleration.
- Force Kill feature for instant game shutdown.
- Persistent file logging to ~/.config/tuxstrap/tuxstrap.log.
"""

import os
import sys
import shutil
import subprocess
import threading
import time
from typing import List, Optional, Callable

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import GLib

from core.bypass import get_bypass_server, DEFAULT_PROXY_PORT
from core.logger import log

SOBER_APP_ID = "org.vinegarhq.Sober"
NO_PROXY_VAL = "localhost,127.0.0.1,10.0.0.0/8,192.168.0.0/16,172.16.0.0/12,::1"


class GameLauncher:
    def __init__(self, config_manager):
        self.config_manager = config_manager
        self.current_process: Optional[subprocess.Popen] = None
        self.on_exit_callback: Optional[Callable[[int, float, List[str]], None]] = None
        self._launch_time: float = 0.0

    def is_game_running(self) -> bool:
        return self.current_process is not None and self.current_process.poll() is None

    def _set_cpu_profile(self, profile: str):
        if shutil.which("powerprofilesctl"):
            try:
                subprocess.run(
                    ["powerprofilesctl", "set", profile],
                    check=False, timeout=3,
                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
                )
                log(f"[CPU] Power profile set to: {profile}")
            except Exception as e:
                log(f"[CPU Error] Could not set power profile: {e}", "WARN")

    def kill_game(self) -> bool:
        """Forces immediate termination of Sober and any Flatpak child processes."""
        log("[Launcher] User requested force-kill of Sober...", "WARN")
        terminated = False
        if self.current_process:
            try:
                self.current_process.kill()
                self.current_process.wait(timeout=1)
                terminated = True
            except Exception:
                pass

        # Also kill flatpak instance directly
        try:
            subprocess.run(["flatpak", "kill", SOBER_APP_ID], check=False, timeout=2)
            terminated = True
        except Exception:
            pass

        try:
            subprocess.run(["pkill", "-9", "-f", "sober"], check=False, timeout=2)
            terminated = True
        except Exception:
            pass

        self._set_cpu_profile("balanced")
        get_bypass_server().stop()
        log("[Launcher] Sober forcefully stopped.", "INFO")
        return terminated

    def launch(self, on_exit: Optional[Callable[[int, float, List[str]], None]] = None) -> bool:
        if self.is_game_running():
            log("[Launcher] Game is already running.", "WARN")
            return False

        self.on_exit_callback = on_exit

        # 0. Clean slate: ensure no leftover zombie sober instances
        try:
            subprocess.run(["pkill", "-9", "-f", "sober"], check=False, timeout=1, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception:
            pass

        # 1. Sync Sober config & FastFlags (ensures Vulkan is used)
        log("[Launcher] Syncing settings to Sober...")
        self.config_manager.sync_to_sober()

        # 2. Engage 3.7GHz+ CPU performance profile
        self._set_cpu_profile("performance")

        # 3. Start ByeDPI + DoH Zero-Ping Bypass with Pre-Flight Verification
        cmd: List[str] = ["flatpak", "run"]
        env = os.environ.copy()

        if self.config_manager.settings.get("enable_bypass", True):
            bypass = get_bypass_server()
            if not bypass.start():
                log("[Launcher Error] ByeDPI failed to bind on all ports! Aborting launch to prevent ISP censorship crash.", "ERROR")
                self._set_cpu_profile("balanced")
                return False

            # Active Pre-Flight connection verification
            log("[Launcher] Performing pre-flight connectivity verification...")
            verified = False
            for attempt in range(1, 4):
                if bypass.verify_health(timeout=2.0):
                    log(f"[Launcher] Pre-flight check PASSED ({bypass.current_strategy['name']})! Connection verified 100% stable.")
                    verified = True
                    break
                log(f"[Launcher Warning] Pre-flight attempt {attempt}/3 failed. Cycling bypass strategy...", "WARN")
                bypass.cycle_strategy()
                time.sleep(0.4)

            socks = f"socks5h://127.0.0.1:{bypass.port}"
            http = f"http://127.0.0.1:{bypass.port}"
            for k, v in [
                ("ALL_PROXY", socks), ("all_proxy", socks),
                ("HTTP_PROXY", http),  ("HTTPS_PROXY", http),
                ("http_proxy", http),  ("https_proxy", http),
            ]:
                cmd.append(f"--env={k}={v}")
                env[k] = v
            log(f"[Launcher] ByeDPI + DoH Proxy injected: {socks} (port: {bypass.port})")

        # CRITICAL: Always inject NO_PROXY so Sober's internal Android UI WebSocket (10.110.101.222:5052) is never routed into proxy
        for k in ["NO_PROXY", "no_proxy"]:
            cmd.append(f"--env={k}={NO_PROXY_VAL}")
            env[k] = NO_PROXY_VAL

        # 4. Discrete GPU offloading (if selected)
        if self.config_manager.settings.get("gpu_preference") == "discrete":
            for f in ["DRI_PRIME=1", "__NV_PRIME_RENDER_OFFLOAD=1",
                      "__GLX_VENDOR_LIBRARY_NAME=nvidia", "__VK_LAYER_NV_optimus=NVIDIA_only"]:
                cmd.append(f"--env={f}")
                k, v = f.split("=", 1)
                env[k] = v

        # 5. Stable Vulkan & Mesa Optimization
        for f in [
            "vblank_mode=0",
            "mesa_glthread=true",
        ]:
            cmd.append(f"--env={f}")
            k, v = f.split("=", 1)
            env[k] = v

        cmd.append(SOBER_APP_ID)

        log(f"[Launcher] Executing command: {' '.join(cmd)}")
        try:
            self.current_process = subprocess.Popen(
                cmd, env=env,
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
            )
            self._launch_time = time.time()
            threading.Thread(target=self._monitor_process, daemon=True).start()
            return True
        except Exception as e:
            log(f"[Launcher Error] Failed to spawn process: {e}", "ERROR")
            self._set_cpu_profile("balanced")
            return False

    def _xml_watchdog(self):
        """Re-patches XML settings 8s after launch to lock in Level 1 graphics.
        IMPORTANT: Never writes FramerateCap=0 (that freezes the Roblox renderer).
        """
        time.sleep(8)
        if self.is_game_running():
            from core.presets import PRESETS, DEFAULT_PRESET
            p_name = self.config_manager.settings.get("preset", DEFAULT_PRESET)
            preset = PRESETS.get(p_name, PRESETS[DEFAULT_PRESET])
            framecap = preset.get("xml_framecap", 360)
            # Safety: never allow 0 (causes black screen / freeze)
            if framecap <= 0:
                framecap = 360
                log("[XML Watchdog] xml_framecap was 0 or missing — defaulting to 360 to prevent freeze.", "WARN")
            self.config_manager.patch_roblox_xml_settings(
                target_fps=framecap,
                quality_level=preset.get("xml_quality", 1),
                saved_quality=preset.get("xml_saved_quality", 1)
            )

    def _monitor_process(self):
        output_lines: List[str] = []

        try:
            for line in iter(self.current_process.stdout.readline, ""):
                if line:
                    stripped = line.strip()
                    log(f"[Sober] {stripped}")
                    output_lines.append(stripped)
        except Exception:
            pass

        self.current_process.wait()
        exit_code = self.current_process.returncode
        elapsed = time.time() - self._launch_time
        self.current_process = None

        log(f"[Launcher] Sober exited with code {exit_code} (Session uptime: {elapsed:.1f}s)")

        # Restore CPU to balanced
        self._set_cpu_profile("balanced")

        # Stop ByeDPI
        get_bypass_server().stop()

        if self.on_exit_callback:
            GLib.idle_add(self.on_exit_callback, exit_code, elapsed, output_lines)
