"""
TuxStrap In-Game X11 HUD Overlay & Global Hotkey Engine.
Renders a translucent, borderless, always-on-top HUD over Roblox.
Supports customizable global toggle hotkeys (F4, Insert, F8, F9, F12, etc.).
"""

import threading
import time
from typing import Optional

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
from gi.repository import Gtk, Gdk, GLib

import Xlib
from Xlib import X, XK
from Xlib.display import Display

from core.logger import log
from core.presets import PRESETS, DEFAULT_PRESET
from core.monitor import get_system_monitor
from core.i18n import t

AVAILABLE_HOTKEYS = ["F4", "Insert", "F8", "F9", "F10", "F11", "F12", "Home", "Page_Up", "grave"]


class OverlayWindow(Gtk.Window):
    def __init__(self, config_manager, launcher):
        super().__init__(type=Gtk.WindowType.TOPLEVEL)
        self.config_manager = config_manager
        self.launcher = launcher
        self.monitor = get_system_monitor()

        self.set_title("TuxStrap HUD")
        self.set_decorated(False)
        self.set_keep_above(True)
        self.set_skip_taskbar_hint(True)
        self.set_skip_pager_hint(True)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_default_size(520, 360)
        self.set_resizable(False)

        # Transparency support
        screen = self.get_screen()
        visual = screen.get_rgba_visual()
        if visual and screen.is_composited():
            self.set_visual(visual)
        self.set_app_paintable(True)

        self.get_style_context().add_class("overlay-window")

        # Layout
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=14)
        main_box.set_margin_start(20)
        main_box.set_margin_end(20)
        main_box.set_margin_top(18)
        main_box.set_margin_bottom(18)
        self.add(main_box)

        # 1. Header (Title + Hotkey info + Close)
        header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        
        title_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        t_icon = Gtk.Label(label="🐧")
        t_label = Gtk.Label(label="TuxStrap HUD")
        t_label.get_style_context().add_class("overlay-title")
        title_box.pack_start(t_icon, False, False, 0)
        title_box.pack_start(t_label, False, False, 0)
        header.pack_start(title_box, False, False, 0)

        current_key = self.config_manager.settings.get("overlay_hotkey", "F4")
        self.badge = Gtk.Label(label=f"Kısayol: [ {current_key} ]")
        self.badge.get_style_context().add_class("overlay-badge")
        header.pack_start(self.badge, True, True, 0)

        close_btn = Gtk.Button(label="✕")
        close_btn.get_style_context().add_class("overlay-close-btn")
        close_btn.connect("clicked", lambda b: self.hide_overlay())
        header.pack_end(close_btn, False, False, 0)
        main_box.pack_start(header, False, False, 0)

        # 2. Stats Row (Ping, CPU Freq, RAM)
        stats_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        stats_box.set_homogeneous(True)

        self.ping_card = self._create_stat_card("🌐 Gecikme (Ping)", "52 ms", "stat-val-ping")
        self.cpu_card = self._create_stat_card("⚡ CPU Performans", "3.70 GHz", "stat-val-cpu")
        self.ram_card = self._create_stat_card("🧠 RAM Kullanımı", "%45", "stat-val-ram")

        stats_box.pack_start(self.ping_card["box"], True, True, 0)
        stats_box.pack_start(self.cpu_card["box"], True, True, 0)
        stats_box.pack_start(self.ram_card["box"], True, True, 0)
        main_box.pack_start(stats_box, False, False, 0)

        # 3. In-Game Preset Switcher
        preset_card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        preset_card.get_style_context().add_class("overlay-card")

        p_header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        p_title = Gtk.Label(label="🎮 Anlık Grafik & FPS Profili")
        p_title.get_style_context().add_class("card-title-small")
        p_header.pack_start(p_title, False, False, 0)
        preset_card.pack_start(p_header, False, False, 0)

        p_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        self.preset_combo = Gtk.ComboBoxText()
        for name in PRESETS.keys():
            self.preset_combo.append_text(name)
        curr = self.config_manager.settings.get("preset", DEFAULT_PRESET)
        if curr in PRESETS:
            self.preset_combo.set_active(list(PRESETS.keys()).index(curr))
        else:
            self.preset_combo.set_active(0)
        
        apply_btn = Gtk.Button(label="⚡ Profile Geç")
        apply_btn.get_style_context().add_class("btn-neon-purple")
        apply_btn.connect("clicked", self._on_apply_preset)

        p_row.pack_start(self.preset_combo, True, True, 0)
        p_row.pack_end(apply_btn, False, False, 0)
        preset_card.pack_start(p_row, False, False, 0)
        main_box.pack_start(preset_card, False, False, 0)

        # 4. Action Row (Emergency Kill, Refresh, Hide)
        act_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        
        self.kill_btn = Gtk.Button(label="⏹️ Roblox'u Anında Kapat")
        self.kill_btn.get_style_context().add_class("btn-danger-neon")
        self.kill_btn.connect("clicked", self._on_emergency_kill)

        hide_btn = Gtk.Button(label="👁️ Gizle (Esc)")
        hide_btn.get_style_context().add_class("btn-secondary-neon")
        hide_btn.connect("clicked", lambda b: self.hide_overlay())

        act_box.pack_start(self.kill_btn, True, True, 0)
        act_box.pack_end(hide_btn, False, False, 0)
        main_box.pack_start(act_box, False, False, 0)

        # Status text
        self.status_lbl = Gtk.Label(label="TuxStrap HUD aktif • Esc ile kapatılabilir")
        self.status_lbl.get_style_context().add_class("overlay-footer-text")
        main_box.pack_end(self.status_lbl, False, False, 0)

        self.connect("key-press-event", self._on_key_press)
        self.monitor.add_listener(self._update_stats_ui)

    def update_hotkey_badge(self, key_name: str):
        self.badge.set_text(f"Kısayol: [ {key_name} ]")

    def _create_stat_card(self, title: str, init_val: str, val_class: str) -> dict:
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        box.get_style_context().add_class("overlay-stat-card")

        t_lbl = Gtk.Label(label=title)
        t_lbl.get_style_context().add_class("stat-title")
        v_lbl = Gtk.Label(label=init_val)
        v_lbl.get_style_context().add_class("stat-value")
        v_lbl.get_style_context().add_class(val_class)

        box.pack_start(t_lbl, False, False, 0)
        box.pack_start(v_lbl, False, False, 0)
        return {"box": box, "title": t_lbl, "val": v_lbl}

    def _update_stats_ui(self, stats: dict):
        def _apply():
            ping = stats.get("ping", 0.0)
            if ping > 0:
                self.ping_card["val"].set_text(f"{ping:.0f} ms")
            cpu_pct = stats.get("cpu_percent", 0.0)
            cpu_freq = stats.get("cpu_freq", 0.0)
            self.cpu_card["val"].set_text(f"{cpu_freq:.2f} GHz (%{cpu_pct:.0f})")
            ram_pct = stats.get("ram_percent", 0.0)
            self.ram_card["val"].set_text(f"%{ram_pct:.0f}")
            return False
        GLib.idle_add(_apply)

    def _on_key_press(self, widget, event):
        if event.keyval == Gdk.KEY_Escape:
            self.hide_overlay()
            return True
        return False

    def _on_apply_preset(self, widget):
        sel = self.preset_combo.get_active_text()
        if sel and sel in PRESETS:
            self.config_manager.settings["preset"] = sel
            self.config_manager.save_tuxstrap_settings()
            self.config_manager.sync_to_sober()
            self.status_lbl.set_text(f"Profil uygulandı: {sel}")
            log(f"[Overlay] In-game preset changed to: {sel}")

    def _on_emergency_kill(self, widget):
        self.status_lbl.set_text("Roblox sonlandırılıyor...")
        self.launcher.kill_game()
        self.hide_overlay()

    def show_overlay(self):
        self.show_all()
        self.present()
        self.set_keep_above(True)

    def hide_overlay(self):
        self.hide()

    def toggle_visibility(self):
        if self.get_visible():
            self.hide_overlay()
        else:
            self.show_overlay()


class GlobalOverlayHotkeyListener:
    """X11 daemon thread that intercepts customizable keys globally."""
    def __init__(self, overlay_window: OverlayWindow, key_name: str = "F4"):
        self.overlay_window = overlay_window
        self.key_name = key_name
        self.is_running = False
        self._thread: Optional[threading.Thread] = None
        self._display: Optional[Display] = None
        self._current_keycode: int = 0

    def start(self):
        if self.is_running:
            return
        self.is_running = True
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()
        log(f"[Hotkey] Global hotkey listener active on [ {self.key_name} ].")

    def stop(self):
        self.is_running = False

    def change_key(self, new_key_name: str):
        self.key_name = new_key_name
        self.overlay_window.update_hotkey_badge(new_key_name)
        if self._display:
            try:
                root = self._display.screen().root
                if self._current_keycode:
                    root.ungrab_key(self._current_keycode, X.AnyModifier)
                keysym = XK.string_to_keysym(new_key_name)
                self._current_keycode = self._display.keysym_to_keycode(keysym)
                root.grab_key(self._current_keycode, X.AnyModifier, 1, X.GrabModeAsync, X.GrabModeAsync)
                log(f"[Hotkey] Hotkey dynamically updated to [ {new_key_name} ].")
            except Exception as e:
                log(f"[Hotkey Error] Failed to update keycode: {e}", "WARN")

    def _loop(self):
        try:
            self._display = Display()
            root = self._display.screen().root
            keysym = XK.string_to_keysym(self.key_name)
            self._current_keycode = self._display.keysym_to_keycode(keysym)

            # Grab current key with AnyModifier
            root.grab_key(self._current_keycode, X.AnyModifier, 1, X.GrabModeAsync, X.GrabModeAsync)

            while self.is_running:
                event = self._display.next_event()
                if event.type == X.KeyPress:
                    if event.detail == self._current_keycode:
                        GLib.idle_add(self.overlay_window.toggle_visibility)
                time.sleep(0.01)

        except Exception as e:
            log(f"[Hotkey Error] Listener failed or X11 unavailable: {e}", "WARN")


# Global Overlay Singleton
_overlay_instance: Optional[OverlayWindow] = None
_hotkey_instance: Optional[GlobalOverlayHotkeyListener] = None

def get_overlay(config_manager, launcher) -> OverlayWindow:
    global _overlay_instance, _hotkey_instance
    if _overlay_instance is None:
        _overlay_instance = OverlayWindow(config_manager, launcher)
        initial_key = config_manager.settings.get("overlay_hotkey", "F4")
        _hotkey_instance = GlobalOverlayHotkeyListener(_overlay_instance, key_name=initial_key)
        _hotkey_instance.start()
    return _overlay_instance

def get_hotkey_listener() -> Optional[GlobalOverlayHotkeyListener]:
    return _hotkey_instance
