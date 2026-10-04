"""
TuxStrap v1.2 — Ultimate Roblox Linux Launcher & In-Game Overlay Controller.
Features:
- Full Dynamic i18n Localization (Türkçe & English live toggle without restart).
- Zero-Failure Bypass Engine with RFC 1928 Domain & IPv4 Failover.
- In-Game HUD Overlay with Customizable Hotkey (F4, Insert, F8, etc.).
- Theme Engine with Cyberpunk Neon, Matrix Green, Crimson Fury, Midnight Blue & Custom Colors.
- Custom Wallpaper Selector and Clearer.
"""

import os
import json
import subprocess
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
gi.require_version('GdkPixbuf', '2.0')
from gi.repository import Gtk, Gdk, GdkPixbuf, GLib

from core.presets import PRESETS, DEFAULT_PRESET
from core.bypass import get_bypass_server, DEFAULT_PROXY_PORT
from core.launcher import GameLauncher
from core.logger import log, add_log_listener, get_log_file_path
from core.monitor import get_system_monitor
from core.history import get_history_manager
from core.overlay import get_overlay, get_hotkey_listener, AVAILABLE_HOTKEYS
from core.i18n import t, set_language, get_language
from core.themes import PRESET_THEMES, generate_css

LOGO_PATH = os.path.join(os.path.dirname(__file__), "assets", "logo.svg")


class TuxStrapWindow(Gtk.Window):
    def __init__(self, config_manager):
        super().__init__(title="TuxStrap")
        self.config_manager = config_manager
        self.launcher = GameLauncher(config_manager)
        self.monitor = get_system_monitor()
        self.history_mgr = get_history_manager()
        self.overlay = get_overlay(config_manager, self.launcher)

        # Initialize language
        saved_lang = self.config_manager.settings.get("language", "tr")
        set_language(saved_lang)

        self.set_default_size(900, 650)
        self.set_position(Gtk.WindowPosition.CENTER)
        if os.path.exists(LOGO_PATH):
            try:
                self.set_icon_from_file(LOGO_PATH)
            except Exception:
                pass

        self.css_provider = Gtk.CssProvider()
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(),
            self.css_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )
        self.apply_theme()

        self.main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.add(self.main_box)

        self.create_header()

        self.notebook = Gtk.Notebook()
        self.notebook.set_scrollable(True)
        self.main_box.pack_start(self.notebook, True, True, 0)

        # Build All Tabs
        self.create_dashboard_tab()
        self.create_history_tab()
        self.create_overlay_tab()
        self.create_performance_tab()
        self.create_network_tab()
        self.create_customization_tab()
        self.create_settings_tab()
        self.create_console_tab()

        self.apply_background_image()

        # Connect live log listener
        add_log_listener(self._on_log_received)

        # Connect hardware monitor
        self.monitor.add_listener(self._on_monitor_stats)
        self.monitor.start()

        self.connect("destroy", self.on_window_close)
        log("[UI] TuxStrap v1.2 Window ready.")

    def apply_theme(self):
        theme_name = self.config_manager.settings.get("theme_name", "Cyberpunk Neon")
        custom_color = self.config_manager.settings.get("custom_accent_color", "#8b5cf6")
        css_data = generate_css(theme_name, custom_color)
        try:
            self.css_provider.load_from_data(css_data.encode('utf-8'))
        except Exception as e:
            log(f"[Theme Error] Failed to load CSS: {e}", "WARN")

    def apply_background_image(self):
        bg_path = self.config_manager.settings.get("background_image", "")
        if bg_path and os.path.exists(bg_path):
            custom_css = f"""
            window {{
                background-image: linear-gradient(rgba(9, 11, 16, 0.85), rgba(9, 11, 16, 0.94)), url('{bg_path}');
                background-size: cover;
                background-position: center;
            }}
            """
            provider = Gtk.CssProvider()
            try:
                provider.load_from_data(custom_css.encode('utf-8'))
                Gtk.StyleContext.add_provider_for_screen(
                    Gdk.Screen.get_default(),
                    provider,
                    Gtk.STYLE_PROVIDER_PRIORITY_USER
                )
            except Exception:
                pass

    def create_header(self):
        header_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=14)
        header_box.get_style_context().add_class("header-box")

        # Cyber Logo
        if os.path.exists(LOGO_PATH):
            try:
                pb = GdkPixbuf.Pixbuf.new_from_file_at_scale(LOGO_PATH, 44, 44, True)
                logo_img = Gtk.Image.new_from_pixbuf(pb)
                header_box.pack_start(logo_img, False, False, 0)
            except Exception:
                pass

        title_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        self.title_label = Gtk.Label(label=t("app_title"))
        self.title_label.set_halign(Gtk.Align.START)
        self.title_label.get_style_context().add_class("app-title")

        self.subtitle_label = Gtk.Label(label=t("app_subtitle"))
        self.subtitle_label.set_halign(Gtk.Align.START)
        self.subtitle_label.get_style_context().add_class("app-subtitle")

        title_box.pack_start(self.title_label, False, False, 0)
        title_box.pack_start(self.subtitle_label, False, False, 0)
        header_box.pack_start(title_box, True, True, 0)

        # Status Badges
        status_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)

        self.ping_pill = Gtk.Label(label="Ping: -- ms")
        self.ping_pill.get_style_context().add_class("status-pill")
        self.ping_pill.get_style_context().add_class("status-active")

        self.bypass_pill = Gtk.Label(label="Bypass: Ready")
        self.bypass_pill.get_style_context().add_class("status-pill")
        self.bypass_pill.get_style_context().add_class("status-neon-cyan")

        current_key = self.config_manager.settings.get("overlay_hotkey", "F4")
        self.hud_pill = Gtk.Label(label=f"HUD: [ {current_key} ]")
        self.hud_pill.get_style_context().add_class("status-pill")
        self.hud_pill.get_style_context().add_class("status-neon-purple")

        status_box.pack_start(self.ping_pill, False, False, 0)
        status_box.pack_start(self.bypass_pill, False, False, 0)
        status_box.pack_start(self.hud_pill, False, False, 0)
        header_box.pack_end(status_box, False, False, 0)

        self.main_box.pack_start(header_box, False, False, 0)

    # ---------------- TAB 1: DASHBOARD & LAUNCHER ----------------
    def create_dashboard_tab(self):
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=14)
        box.set_margin_top(16)
        box.set_margin_bottom(16)
        box.set_margin_start(18)
        box.set_margin_end(18)
        scrolled.add(box)

        # Hero Launch Card
        launch_card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=14)
        launch_card.get_style_context().add_class("card")

        c_header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        self.lbl_hero_title = Gtk.Label(label=t("hero_title"))
        self.lbl_hero_title.get_style_context().add_class("card-title")
        c_header.pack_start(self.lbl_hero_title, False, False, 0)

        self.state_label = Gtk.Label(label=t("hero_ready"))
        self.state_label.get_style_context().add_class("card-desc")
        c_header.pack_end(self.state_label, False, False, 0)
        launch_card.pack_start(c_header, False, False, 0)

        # Button Row
        btn_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        
        self.launch_btn = Gtk.Button(label=t("btn_launch"))
        self.launch_btn.get_style_context().add_class("btn-launch-hero")
        self.launch_btn.connect("clicked", self.on_launch_clicked)

        self.kill_btn = Gtk.Button(label=t("btn_kill"))
        self.kill_btn.get_style_context().add_class("btn-danger-neon")
        self.kill_btn.connect("clicked", self.on_kill_clicked)

        current_key = self.config_manager.settings.get("overlay_hotkey", "F4")
        self.hud_btn = Gtk.Button(label=f"{t('btn_hud_test')} ({current_key})")
        self.hud_btn.get_style_context().add_class("btn-neon-purple")
        self.hud_btn.connect("clicked", lambda b: self.overlay.toggle_visibility())

        btn_box.pack_start(self.launch_btn, True, True, 0)
        btn_box.pack_start(self.kill_btn, False, False, 0)
        btn_box.pack_start(self.hud_btn, False, False, 0)
        launch_card.pack_start(btn_box, False, False, 4)
        box.pack_start(launch_card, False, False, 0)

        # Live Hardware & Latency Tiles
        stats_grid = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        stats_grid.set_homogeneous(True)

        self.tile_ping = self._create_tile(t("tile_ping"), "0.0 ms", "val-green")
        self.tile_cpu = self._create_tile(t("tile_cpu"), "3.70 GHz", "val-blue")
        self.tile_ram = self._create_tile(t("tile_ram"), "%0", "val-purple")
        self.tile_bypass = self._create_tile(t("tile_bypass"), "TCP Disorder", "val-green")

        stats_grid.pack_start(self.tile_ping["box"], True, True, 0)
        stats_grid.pack_start(self.tile_cpu["box"], True, True, 0)
        stats_grid.pack_start(self.tile_ram["box"], True, True, 0)
        stats_grid.pack_start(self.tile_bypass["box"], True, True, 0)
        box.pack_start(stats_grid, False, False, 0)

        # Direct Game Connect Card
        join_card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        join_card.get_style_context().add_class("card")

        self.lbl_join_title = Gtk.Label(label=t("direct_join_title"))
        self.lbl_join_title.set_halign(Gtk.Align.START)
        self.lbl_join_title.get_style_context().add_class("card-title")
        self.lbl_join_desc = Gtk.Label(label=t("direct_join_desc"))
        self.lbl_join_desc.set_halign(Gtk.Align.START)
        self.lbl_join_desc.get_style_context().add_class("card-desc")
        join_card.pack_start(self.lbl_join_title, False, False, 0)
        join_card.pack_start(self.lbl_join_desc, False, False, 0)

        j_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        self.place_entry = Gtk.Entry()
        self.place_entry.set_placeholder_text(t("direct_join_placeholder"))
        
        self.btn_join = Gtk.Button(label=t("direct_join_btn"))
        self.btn_join.get_style_context().add_class("btn-neon-purple")
        self.btn_join.connect("clicked", self._on_direct_join_clicked)

        j_row.pack_start(self.place_entry, True, True, 0)
        j_row.pack_end(self.btn_join, False, False, 0)
        join_card.pack_start(j_row, False, False, 0)
        box.pack_start(join_card, False, False, 0)

        # Quick Config Card
        quick_card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        quick_card.get_style_context().add_class("card")

        self.lbl_quick_title = Gtk.Label(label=t("quick_settings"))
        self.lbl_quick_title.set_halign(Gtk.Align.START)
        self.lbl_quick_title.get_style_context().add_class("card-title")
        quick_card.pack_start(self.lbl_quick_title, False, False, 0)

        # Preset Row
        p_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        self.lbl_active_preset = Gtk.Label(label=t("active_preset"))
        self.dash_preset_combo = Gtk.ComboBoxText()
        for name in PRESETS.keys():
            self.dash_preset_combo.append_text(name)
        curr = self.config_manager.settings.get("preset", DEFAULT_PRESET)
        if curr in PRESETS:
            self.dash_preset_combo.set_active(list(PRESETS.keys()).index(curr))
        else:
            self.dash_preset_combo.set_active(0)
        self.dash_preset_combo.connect("changed", self.on_preset_changed)
        p_row.pack_start(self.lbl_active_preset, False, False, 0)
        p_row.pack_end(self.dash_preset_combo, False, False, 0)
        quick_card.pack_start(p_row, False, False, 0)

        # Bypass switch
        bp_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        self.lbl_bypass_switch = Gtk.Label(label=t("bypass_switch"))
        self.bypass_switch = Gtk.Switch()
        self.bypass_switch.set_active(self.config_manager.settings.get("enable_bypass", True))
        self.bypass_switch.connect("state-set", self.on_bypass_toggle)
        bp_row.pack_start(self.lbl_bypass_switch, False, False, 0)
        bp_row.pack_end(self.bypass_switch, False, False, 0)
        quick_card.pack_start(bp_row, False, False, 0)

        # Gamemode switch
        gm_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        self.lbl_gm_switch = Gtk.Label(label=t("gamemode_switch"))
        self.gm_switch = Gtk.Switch()
        self.gm_switch.set_active(self.config_manager.settings.get("use_gamemode", True))
        self.gm_switch.connect("state-set", self.on_gamemode_toggle)
        gm_row.pack_start(self.lbl_gm_switch, False, False, 0)
        gm_row.pack_end(self.gm_switch, False, False, 0)
        quick_card.pack_start(gm_row, False, False, 0)

        box.pack_start(quick_card, False, False, 0)
        self.notebook.append_page(scrolled, Gtk.Label(label=t("tab_launcher")))

    def _create_tile(self, title: str, init_val: str, val_class: str) -> dict:
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        box.get_style_context().add_class("stat-tile")
        t_lbl = Gtk.Label(label=title)
        t_lbl.set_halign(Gtk.Align.START)
        t_lbl.get_style_context().add_class("stat-tile-title")
        v_lbl = Gtk.Label(label=init_val)
        v_lbl.set_halign(Gtk.Align.START)
        v_lbl.get_style_context().add_class("stat-tile-val")
        v_lbl.get_style_context().add_class(val_class)
        box.pack_start(t_lbl, False, False, 0)
        box.pack_start(v_lbl, False, False, 0)
        return {"box": box, "title": t_lbl, "val": v_lbl}

    # ---------------- TAB 2: GAME HISTORY ----------------
    def create_history_tab(self):
        scrolled = Gtk.ScrolledWindow()
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=14)
        box.set_margin_top(16)
        box.set_margin_bottom(16)
        box.set_margin_start(18)
        box.set_margin_end(18)
        scrolled.add(box)

        h_card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        h_card.get_style_context().add_class("card")

        top = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        self.lbl_hist_title = Gtk.Label(label=t("history_title"))
        self.lbl_hist_title.get_style_context().add_class("card-title")
        self.btn_hist_clear = Gtk.Button(label=t("history_clear"))
        self.btn_hist_clear.get_style_context().add_class("btn-secondary-neon")
        self.btn_hist_clear.connect("clicked", self._on_clear_history)
        top.pack_start(self.lbl_hist_title, False, False, 0)
        top.pack_end(self.btn_hist_clear, False, False, 0)
        h_card.pack_start(top, False, False, 0)

        self.history_list_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        h_card.pack_start(self.history_list_box, True, True, 0)
        box.pack_start(h_card, True, True, 0)

        self.refresh_history_ui()
        self.notebook.append_page(scrolled, Gtk.Label(label=t("tab_history")))

    def refresh_history_ui(self):
        for child in self.history_list_box.get_children():
            self.history_list_box.remove(child)

        items = self.history_mgr.history
        if not items:
            empty = Gtk.Label(label=t("history_empty"))
            empty.get_style_context().add_class("card-desc")
            self.history_list_box.pack_start(empty, False, False, 10)
        else:
            for item in items:
                row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
                row.get_style_context().add_class("stat-tile")
                
                info_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
                title = Gtk.Label(label=item.get("title", "Roblox Experience"))
                title.set_halign(Gtk.Align.START)
                title.get_style_context().add_class("card-title-small")
                
                sub = Gtk.Label(label=f"Place ID: {item.get('place_id')} • {item.get('date_str')}")
                sub.set_halign(Gtk.Align.START)
                sub.get_style_context().add_class("card-desc")
                
                info_box.pack_start(title, False, False, 0)
                info_box.pack_start(sub, False, False, 0)
                row.pack_start(info_box, True, True, 0)

                join_btn = Gtk.Button(label=t("history_launch"))
                join_btn.get_style_context().add_class("btn-neon-purple")
                p_id = item.get("place_id")
                join_btn.connect("clicked", lambda b, pid=p_id: self._launch_place(pid))
                row.pack_end(join_btn, False, False, 0)

                self.history_list_box.pack_start(row, False, False, 0)

        self.history_list_box.show_all()

    def _on_clear_history(self, widget):
        self.history_mgr.clear()
        self.refresh_history_ui()

    # ---------------- TAB 3: IN-GAME HUD OVERLAY ----------------
    def create_overlay_tab(self):
        scrolled = Gtk.ScrolledWindow()
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=14)
        box.set_margin_top(16)
        box.set_margin_bottom(16)
        box.set_margin_start(18)
        box.set_margin_end(18)
        scrolled.add(box)

        card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=14)
        card.get_style_context().add_class("card")

        self.lbl_ov_title = Gtk.Label(label=t("overlay_guide_title"))
        self.lbl_ov_title.set_halign(Gtk.Align.START)
        self.lbl_ov_title.get_style_context().add_class("card-title")
        card.pack_start(self.lbl_ov_title, False, False, 0)

        current_key = self.config_manager.settings.get("overlay_hotkey", "F4")
        self.lbl_ov_desc = Gtk.Label(
            label=f"{t('overlay_guide_desc')}\n\n"
                  f"• Hotkey: [ {current_key} ]\n"
                  "• Esc / Hotkey toggles the in-game HUD immediately."
        )
        self.lbl_ov_desc.set_line_wrap(True)
        self.lbl_ov_desc.set_halign(Gtk.Align.START)
        self.lbl_ov_desc.get_style_context().add_class("card-desc")
        card.pack_start(self.lbl_ov_desc, False, False, 0)

        self.btn_ov_test = Gtk.Button(label=f"{t('overlay_test_btn')} ({current_key})")
        self.btn_ov_test.get_style_context().add_class("btn-launch-hero")
        self.btn_ov_test.connect("clicked", lambda b: self.overlay.toggle_visibility())
        card.pack_start(self.btn_ov_test, False, False, 6)

        box.pack_start(card, False, False, 0)
        self.notebook.append_page(scrolled, Gtk.Label(label=t("tab_overlay")))

    # ---------------- TAB 4: PERFORMANCE & FFLAGS ----------------
    def create_performance_tab(self):
        scrolled = Gtk.ScrolledWindow()
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=14)
        box.set_margin_top(16)
        box.set_margin_bottom(16)
        box.set_margin_start(18)
        box.set_margin_end(18)
        scrolled.add(box)

        # Preset Details
        p_card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        p_card.get_style_context().add_class("card")

        self.lbl_perf_title = Gtk.Label(label=t("perf_title"))
        self.lbl_perf_title.set_halign(Gtk.Align.START)
        self.lbl_perf_title.get_style_context().add_class("card-title")
        p_card.pack_start(self.lbl_perf_title, False, False, 0)

        self.preset_combo = Gtk.ComboBoxText()
        for name in PRESETS.keys():
            self.preset_combo.append_text(name)
        curr = self.config_manager.settings.get("preset", DEFAULT_PRESET)
        if curr in PRESETS:
            self.preset_combo.set_active(list(PRESETS.keys()).index(curr))
        else:
            self.preset_combo.set_active(0)
        self.preset_combo.connect("changed", self.on_preset_changed)
        p_card.pack_start(self.preset_combo, False, False, 0)

        self.preset_desc = Gtk.Label()
        self.preset_desc.set_line_wrap(True)
        self.preset_desc.set_halign(Gtk.Align.START)
        self.preset_desc.get_style_context().add_class("card-desc")
        p_card.pack_start(self.preset_desc, False, False, 0)
        self.update_preset_desc()

        box.pack_start(p_card, False, False, 0)

        # Hardware & Driver Settings
        d_card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        d_card.get_style_context().add_class("card")

        self.lbl_perf_gpu = Gtk.Label(label=t("perf_gpu_title"))
        self.lbl_perf_gpu.set_halign(Gtk.Align.START)
        self.lbl_perf_gpu.get_style_context().add_class("card-title")
        d_card.pack_start(self.lbl_perf_gpu, False, False, 0)

        gpu_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        self.lbl_gpu_pref = Gtk.Label(label=t("perf_gpu_lbl"))
        self.gpu_combo = Gtk.ComboBoxText()
        self.gpu_combo.append("auto", "Auto (Intel Iris Xe / Integrated)")
        self.gpu_combo.append("discrete", "Discrete GPU (NVIDIA / AMD DRI_PRIME)")
        self.gpu_combo.set_active_id(self.config_manager.settings.get("gpu_preference", "auto"))
        self.gpu_combo.connect("changed", self.on_gpu_changed)
        gpu_row.pack_start(self.lbl_gpu_pref, False, False, 0)
        gpu_row.pack_end(self.gpu_combo, False, False, 0)
        d_card.pack_start(gpu_row, False, False, 0)

        self.lbl_vulkan_info = Gtk.Label(label=t("perf_vulkan_lbl"))
        self.lbl_vulkan_info.set_halign(Gtk.Align.START)
        self.lbl_vulkan_info.get_style_context().add_class("card-desc")
        d_card.pack_start(self.lbl_vulkan_info, False, False, 0)

        box.pack_start(d_card, False, False, 0)
        self.notebook.append_page(scrolled, Gtk.Label(label=t("tab_performance")))

    # ---------------- TAB 5: NETWORK & BYPASS ----------------
    def create_network_tab(self):
        scrolled = Gtk.ScrolledWindow()
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=14)
        box.set_margin_top(16)
        box.set_margin_bottom(16)
        box.set_margin_start(18)
        box.set_margin_end(18)
        scrolled.add(box)

        card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        card.get_style_context().add_class("card")

        self.lbl_net_title = Gtk.Label(label=t("net_title"))
        self.lbl_net_title.set_halign(Gtk.Align.START)
        self.lbl_net_title.get_style_context().add_class("card-title")
        card.pack_start(self.lbl_net_title, False, False, 0)

        self.lbl_net_info = Gtk.Label(label=t("net_info"))
        self.lbl_net_info.set_line_wrap(True)
        self.lbl_net_info.set_halign(Gtk.Align.START)
        self.lbl_net_info.get_style_context().add_class("card-desc")
        card.pack_start(self.lbl_net_info, False, False, 0)

        # Ping tester button
        test_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        self.ping_btn = Gtk.Button(label=t("net_ping_btn"))
        self.ping_btn.get_style_context().add_class("btn-neon-purple")
        self.ping_btn.connect("clicked", self._on_test_ping_clicked)

        self.ping_result_lbl = Gtk.Label(label="")
        self.ping_result_lbl.get_style_context().add_class("card-desc")

        test_box.pack_start(self.ping_btn, False, False, 0)
        test_box.pack_start(self.ping_result_lbl, False, False, 0)
        card.pack_start(test_box, False, False, 4)

        box.pack_start(card, False, False, 0)
        self.notebook.append_page(scrolled, Gtk.Label(label=t("tab_network")))

    # ---------------- TAB 6: CUSTOMIZATION ----------------
    def create_customization_tab(self):
        scrolled = Gtk.ScrolledWindow()
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=14)
        box.set_margin_top(16)
        box.set_margin_bottom(16)
        box.set_margin_start(18)
        box.set_margin_end(18)
        scrolled.add(box)

        card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        card.get_style_context().add_class("card")

        self.lbl_custom_title = Gtk.Label(label=t("custom_title"))
        self.lbl_custom_title.set_halign(Gtk.Align.START)
        self.lbl_custom_title.get_style_context().add_class("card-title")
        card.pack_start(self.lbl_custom_title, False, False, 0)

        # Home screen mode
        h_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        self.lbl_menu_mode = Gtk.Label(label=t("custom_menu_mode"))
        self.home_combo = Gtk.ComboBoxText()
        self.home_combo.append("desktop", "Desktop UI")
        self.home_combo.append("console", "Console / Gamepad UI")
        self.home_combo.append("mobile", "Mobile / Tablet UI")
        self.home_combo.set_active_id(self.config_manager.settings.get("home_screen_mode", "desktop"))
        self.home_combo.connect("changed", self.on_home_mode_changed)
        h_row.pack_start(self.lbl_menu_mode, False, False, 0)
        h_row.pack_end(self.home_combo, False, False, 0)
        card.pack_start(h_row, False, False, 0)

        # HiDPI
        hidpi_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        self.lbl_hidpi = Gtk.Label(label=t("custom_hidpi"))
        self.hidpi_switch = Gtk.Switch()
        self.hidpi_switch.set_active(self.config_manager.settings.get("enable_hidpi", False))
        self.hidpi_switch.connect("state-set", self.on_hidpi_toggle)
        hidpi_row.pack_start(self.lbl_hidpi, False, False, 0)
        hidpi_row.pack_end(self.hidpi_switch, False, False, 0)
        card.pack_start(hidpi_row, False, False, 0)

        # Discord RPC
        rpc_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        self.lbl_discord = Gtk.Label(label=t("custom_discord"))
        self.rpc_switch = Gtk.Switch()
        self.rpc_switch.set_active(self.config_manager.settings.get("discord_rpc", True))
        self.rpc_switch.connect("state-set", self.on_rpc_toggle)
        rpc_row.pack_start(self.lbl_discord, False, False, 0)
        rpc_row.pack_end(self.rpc_switch, False, False, 0)
        card.pack_start(rpc_row, False, False, 0)

        box.pack_start(card, False, False, 0)
        self.notebook.append_page(scrolled, Gtk.Label(label=t("tab_customization")))

    # ---------------- TAB 7: SETTINGS & THEMES & HOTKEY ----------------
    def create_settings_tab(self):
        scrolled = Gtk.ScrolledWindow()
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=14)
        box.set_margin_top(16)
        box.set_margin_bottom(16)
        box.set_margin_start(18)
        box.set_margin_end(18)
        scrolled.add(box)

        # 1. Hotkey & Language Card
        gen_card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        gen_card.get_style_context().add_class("card")

        self.lbl_set_title = Gtk.Label(label=t("settings_title"))
        self.lbl_set_title.set_halign(Gtk.Align.START)
        self.lbl_set_title.get_style_context().add_class("card-title")
        gen_card.pack_start(self.lbl_set_title, False, False, 0)

        # Hotkey Row
        hk_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        self.lbl_set_hk = Gtk.Label(label=t("settings_hotkey"))
        self.hotkey_combo = Gtk.ComboBoxText()
        for k in AVAILABLE_HOTKEYS:
            self.hotkey_combo.append_text(k)
        saved_key = self.config_manager.settings.get("overlay_hotkey", "F4")
        if saved_key in AVAILABLE_HOTKEYS:
            self.hotkey_combo.set_active(AVAILABLE_HOTKEYS.index(saved_key))
        else:
            self.hotkey_combo.set_active(0)
        self.hotkey_combo.connect("changed", self._on_hotkey_changed)
        hk_row.pack_start(self.lbl_set_hk, False, False, 0)
        hk_row.pack_end(self.hotkey_combo, False, False, 0)
        gen_card.pack_start(hk_row, False, False, 0)

        # Language Row
        lang_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        self.lbl_set_lang = Gtk.Label(label=t("settings_lang"))
        self.lang_combo = Gtk.ComboBoxText()
        self.lang_combo.append("tr", "Türkçe (TR)")
        self.lang_combo.append("en", "English (EN)")
        self.lang_combo.set_active_id(get_language())
        self.lang_combo.connect("changed", self._on_lang_changed)
        lang_row.pack_start(self.lbl_set_lang, False, False, 0)
        lang_row.pack_end(self.lang_combo, False, False, 0)
        gen_card.pack_start(lang_row, False, False, 0)

        box.pack_start(gen_card, False, False, 0)

        # 2. Theme & Wallpaper Card
        th_card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        th_card.get_style_context().add_class("card")

        self.lbl_set_th_title = Gtk.Label(label=t("settings_theme_title"))
        self.lbl_set_th_title.set_halign(Gtk.Align.START)
        self.lbl_set_th_title.get_style_context().add_class("card-title")
        th_card.pack_start(self.lbl_set_th_title, False, False, 0)

        # Theme Preset Row
        theme_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        self.lbl_set_theme = Gtk.Label(label=t("settings_theme"))
        self.theme_combo = Gtk.ComboBoxText()
        for name in list(PRESET_THEMES.keys()) + ["Custom"]:
            self.theme_combo.append_text(name)
        curr_theme = self.config_manager.settings.get("theme_name", "Cyberpunk Neon")
        themes_list = list(PRESET_THEMES.keys()) + ["Custom"]
        if curr_theme in themes_list:
            self.theme_combo.set_active(themes_list.index(curr_theme))
        else:
            self.theme_combo.set_active(0)
        self.theme_combo.connect("changed", self._on_theme_changed)
        theme_row.pack_start(self.lbl_set_theme, False, False, 0)
        theme_row.pack_end(self.theme_combo, False, False, 0)
        th_card.pack_start(theme_row, False, False, 0)

        # Custom Color Picker Row
        color_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        self.lbl_set_accent = Gtk.Label(label=t("settings_accent_lbl"))
        self.color_button = Gtk.ColorButton()
        rgba = Gdk.RGBA()
        rgba.parse(self.config_manager.settings.get("custom_accent_color", "#8b5cf6"))
        self.color_button.set_rgba(rgba)
        self.color_button.connect("color-set", self._on_color_set)
        color_row.pack_start(self.lbl_set_accent, False, False, 0)
        color_row.pack_end(self.color_button, False, False, 0)
        th_card.pack_start(color_row, False, False, 0)

        # Background Image Selector Row
        bg_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        self.lbl_set_bg = Gtk.Label(label=t("settings_bg"))
        
        self.choose_bg_btn = Gtk.Button(label=t("settings_bg_choose"))
        self.choose_bg_btn.get_style_context().add_class("btn-neon-purple")
        self.choose_bg_btn.connect("clicked", self._on_choose_background)

        self.clear_bg_btn = Gtk.Button(label=t("settings_bg_clear"))
        self.clear_bg_btn.get_style_context().add_class("btn-secondary-neon")
        self.clear_bg_btn.connect("clicked", self._on_clear_background)

        bg_row.pack_start(self.lbl_set_bg, False, False, 0)
        bg_row.pack_end(self.clear_bg_btn, False, False, 0)
        bg_row.pack_end(self.choose_bg_btn, False, False, 0)
        th_card.pack_start(bg_row, False, False, 0)

        box.pack_start(th_card, False, False, 0)
        self.notebook.append_page(scrolled, Gtk.Label(label=t("tab_settings")))

    # ---------------- TAB 8: CONSOLE & LOGS ----------------
    def create_console_tab(self):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        box.set_margin_top(12)
        box.set_margin_bottom(12)
        box.set_margin_start(16)
        box.set_margin_end(16)

        c_top = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        self.lbl_console_title = Gtk.Label(label=t("console_title"))
        self.lbl_console_title.get_style_context().add_class("card-title-small")
        c_top.pack_start(self.lbl_console_title, False, False, 0)

        self.btn_clear_console = Gtk.Button(label=t("console_clear"))
        self.btn_clear_console.get_style_context().add_class("btn-secondary-neon")
        self.btn_clear_console.connect("clicked", lambda b: self.console_buffer.set_text(""))
        c_top.pack_end(self.btn_clear_console, False, False, 0)
        box.pack_start(c_top, False, False, 0)

        scrolled = Gtk.ScrolledWindow()
        scrolled.set_vexpand(True)
        self.console_view = Gtk.TextView()
        self.console_view.set_editable(False)
        self.console_view.set_cursor_visible(False)
        self.console_view.set_wrap_mode(Gtk.WrapMode.CHAR)
        self.console_view.get_style_context().add_class("console-view")
        self.console_buffer = self.console_view.get_buffer()
        scrolled.add(self.console_view)
        box.pack_start(scrolled, True, True, 0)

        self.notebook.append_page(box, Gtk.Label(label=t("tab_console")))

    # ---------------- DYNAMIC RETRANSLATION ----------------
    def retranslate_ui(self):
        """Dynamically updates every label, tab and button without restarting."""
        self.title_label.set_text(t("app_title"))
        self.subtitle_label.set_text(t("app_subtitle"))
        self.lbl_hero_title.set_text(t("hero_title"))
        self.state_label.set_text(t("hero_ready"))
        self.launch_btn.set_label(t("btn_launch"))
        self.kill_btn.set_label(t("btn_kill"))

        current_key = self.config_manager.settings.get("overlay_hotkey", "F4")
        self.hud_btn.set_label(f"{t('btn_hud_test')} ({current_key})")
        self.hud_pill.set_text(f"HUD: [ {current_key} ]")

        self.tile_ping["title"].set_text(t("tile_ping"))
        self.tile_cpu["title"].set_text(t("tile_cpu"))
        self.tile_ram["title"].set_text(t("tile_ram"))
        self.tile_bypass["title"].set_text(t("tile_bypass"))

        self.lbl_join_title.set_text(t("direct_join_title"))
        self.lbl_join_desc.set_text(t("direct_join_desc"))
        self.place_entry.set_placeholder_text(t("direct_join_placeholder"))
        self.btn_join.set_label(t("direct_join_btn"))

        self.lbl_quick_title.set_text(t("quick_settings"))
        self.lbl_active_preset.set_text(t("active_preset"))
        self.lbl_bypass_switch.set_text(t("bypass_switch"))
        self.lbl_gm_switch.set_text(t("gamemode_switch"))

        self.lbl_hist_title.set_text(t("history_title"))
        self.btn_hist_clear.set_label(t("history_clear"))
        self.refresh_history_ui()

        self.lbl_ov_title.set_text(t("overlay_guide_title"))
        self.lbl_ov_desc.set_text(f"{t('overlay_guide_desc')}\n\n• Hotkey: [ {current_key} ]\n• Esc / Hotkey toggles HUD.")
        self.btn_ov_test.set_label(f"{t('overlay_test_btn')} ({current_key})")

        self.lbl_perf_title.set_text(t("perf_title"))
        self.lbl_perf_gpu.set_text(t("perf_gpu_title"))
        self.lbl_gpu_pref.set_text(t("perf_gpu_lbl"))
        self.lbl_vulkan_info.set_text(t("perf_vulkan_lbl"))

        self.lbl_net_title.set_text(t("net_title"))
        self.lbl_net_info.set_text(t("net_info"))
        self.ping_btn.set_label(t("net_ping_btn"))

        self.lbl_custom_title.set_text(t("custom_title"))
        self.lbl_menu_mode.set_text(t("custom_menu_mode"))
        self.lbl_hidpi.set_text(t("custom_hidpi"))
        self.lbl_discord.set_text(t("custom_discord"))

        self.lbl_set_title.set_text(t("settings_title"))
        self.lbl_set_hk.set_text(t("settings_hotkey"))
        self.lbl_set_lang.set_text(t("settings_lang"))
        self.lbl_set_th_title.set_text(t("settings_theme_title"))
        self.lbl_set_theme.set_text(t("settings_theme"))
        self.lbl_set_accent.set_text(t("settings_accent_lbl"))
        self.lbl_set_bg.set_text(t("settings_bg"))
        self.choose_bg_btn.set_label(t("settings_bg_choose"))
        self.clear_bg_btn.set_label(t("settings_bg_clear"))

        self.lbl_console_title.set_text(t("console_title"))
        self.btn_clear_console.set_label(t("console_clear"))

        # Update notebook tabs
        tab_keys = [
            "tab_launcher", "tab_history", "tab_overlay",
            "tab_performance", "tab_network", "tab_customization",
            "tab_settings", "tab_console"
        ]
        for idx, key in enumerate(tab_keys):
            page = self.notebook.get_nth_page(idx)
            if page:
                self.notebook.set_tab_label_text(page, t(key))

    # ---------------- EVENT HANDLERS ----------------
    def _on_hotkey_changed(self, combo):
        key = combo.get_active_text()
        if key:
            self.config_manager.settings["overlay_hotkey"] = key
            self.config_manager.save_tuxstrap_settings()
            self.hud_pill.set_text(f"HUD: [ {key} ]")
            self.hud_btn.set_label(f"{t('btn_hud_test')} ({key})")
            listener = get_hotkey_listener()
            if listener:
                listener.change_key(key)

    def _on_lang_changed(self, combo):
        lang = combo.get_active_id()
        if lang:
            self.config_manager.settings["language"] = lang
            self.config_manager.save_tuxstrap_settings()
            set_language(lang)
            self.retranslate_ui()
            log(f"[i18n] Language changed to: {lang} (100% full live UI update).")

    def _on_theme_changed(self, combo):
        th_name = combo.get_active_text()
        if th_name:
            self.config_manager.settings["theme_name"] = th_name
            self.config_manager.save_tuxstrap_settings()
            self.apply_theme()
            log(f"[Theme] Switched to theme: {th_name}")

    def _on_color_set(self, btn):
        rgba = btn.get_rgba()
        hex_color = "#{:02x}{:02x}{:02x}".format(
            int(rgba.red * 255), int(rgba.green * 255), int(rgba.blue * 255)
        )
        self.config_manager.settings["custom_accent_color"] = hex_color
        self.config_manager.settings["theme_name"] = "Custom"
        self.config_manager.save_tuxstrap_settings()
        themes_list = list(PRESET_THEMES.keys()) + ["Custom"]
        self.theme_combo.set_active(themes_list.index("Custom"))
        self.apply_theme()
        log(f"[Theme] Custom accent color updated: {hex_color}")

    def _on_choose_background(self, btn):
        dialog = Gtk.FileChooserDialog(
            title="Arka Plan Resmi Seç / Choose Background", parent=self, action=Gtk.FileChooserAction.OPEN
        )
        dialog.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OPEN, Gtk.ResponseType.OK)
        
        filter_img = Gtk.FileFilter()
        filter_img.set_name("Images (PNG, JPG, WEBP)")
        filter_img.add_mime_type("image/png")
        filter_img.add_mime_type("image/jpeg")
        filter_img.add_mime_type("image/webp")
        dialog.add_filter(filter_img)

        if dialog.run() == Gtk.ResponseType.OK:
            filename = dialog.get_filename()
            if filename:
                self.config_manager.settings["background_image"] = filename
                self.config_manager.save_tuxstrap_settings()
                self.apply_background_image()
                log(f"[Customization] Background image set: {filename}")
        dialog.destroy()

    def _on_clear_background(self, btn):
        self.config_manager.settings["background_image"] = ""
        self.config_manager.save_tuxstrap_settings()
        self.apply_theme()
        log("[Customization] Background image cleared.")

    def _on_monitor_stats(self, stats: dict):
        def _update():
            p = stats.get("ping", 0.0)
            if p > 0:
                self.ping_pill.set_text(f"Ping: {p:.0f} ms")
                self.tile_ping["val"].set_text(f"{p:.0f} ms")
            cpu_freq = stats.get("cpu_freq", 0.0)
            self.tile_cpu["val"].set_text(f"{cpu_freq:.2f} GHz")
            ram_pct = stats.get("ram_percent", 0.0)
            self.tile_ram["val"].set_text(f"%{ram_pct:.0f}")
            return False
        GLib.idle_add(_update)

    def _on_log_received(self, line: str):
        def _append():
            if "game_loaded" in line or "places/Mobile.rbxl" in line or "place_id" in line:
                if '"place_id":"' in line:
                    try:
                        pid = line.split('"place_id":"')[1].split('"')[0]
                        if pid and pid != "0":
                            self.history_mgr.record_place(pid)
                            self.refresh_history_ui()
                    except Exception:
                        pass

            end_iter = self.console_buffer.get_end_iter()
            self.console_buffer.insert(end_iter, line + "\n")
            adj = self.console_view.get_vadjustment()
            if adj:
                adj.set_value(adj.get_upper() - adj.get_page_size())
            return False
        GLib.idle_add(_append)

    def _on_direct_join_clicked(self, widget):
        raw = self.place_entry.get_text().strip()
        if not raw:
            return
        place_id = "".join([c for c in raw if c.isdigit()])
        if place_id:
            self._launch_place(place_id)

    def _launch_place(self, place_id: str):
        self.state_label.set_text(f"Place ID #{place_id}...")
        self.history_mgr.record_place(place_id)
        self.refresh_history_ui()
        self.on_launch_clicked(None)

    def on_launch_clicked(self, widget):
        self.launch_btn.set_sensitive(False)
        self.state_label.set_text("Roblox & Zero-Ping Bypass...")
        
        def on_game_exit(code, uptime, logs):
            self.launch_btn.set_sensitive(True)
            self.state_label.set_text(f"Roblox (Exit: {code}, Uptime: {uptime:.1f}s)")

        success = self.launcher.launch(on_exit=on_game_exit)
        if not success:
            self.launch_btn.set_sensitive(True)
            self.state_label.set_text("Launch Failed!")

    def on_kill_clicked(self, widget):
        self.state_label.set_text("Stopping Roblox...")
        self.launcher.kill_game()
        self.launch_btn.set_sensitive(True)
        self.state_label.set_text("Roblox Killed.")

    def _on_test_ping_clicked(self, widget):
        self.ping_btn.set_sensitive(False)
        self.ping_result_lbl.set_text(t("net_measuring"))

        def _test():
            p = self.monitor.measure_ping()
            def _res():
                self.ping_btn.set_sensitive(True)
                self.ping_result_lbl.set_text(f"Roblox/Cloudflare DoH RTT: {p:.1f} ms (Native Wire / 0 VPN)")
                return False
            GLib.idle_add(_res)

        import threading
        threading.Thread(target=_test, daemon=True).start()

    def on_preset_changed(self, combo):
        name = combo.get_active_text()
        if name and name in PRESETS:
            self.config_manager.settings["preset"] = name
            self.config_manager.save_tuxstrap_settings()
            self.update_preset_desc()
            if combo == self.dash_preset_combo and hasattr(self, 'preset_combo'):
                self.preset_combo.handler_block_by_func(self.on_preset_changed)
                self.preset_combo.set_active(combo.get_active())
                self.preset_combo.handler_unblock_by_func(self.on_preset_changed)
            elif combo == getattr(self, 'preset_combo', None) and hasattr(self, 'dash_preset_combo'):
                self.dash_preset_combo.handler_block_by_func(self.on_preset_changed)
                self.dash_preset_combo.set_active(combo.get_active())
                self.dash_preset_combo.handler_unblock_by_func(self.on_preset_changed)
            log(f"[Config] Preset changed to: {name}")

    def update_preset_desc(self):
        curr = self.config_manager.settings.get("preset", DEFAULT_PRESET)
        if hasattr(self, 'preset_desc') and curr in PRESETS:
            info = PRESETS[curr]
            flags = len(info.get("flags", {}))
            self.preset_desc.set_text(f"{info.get('description', '')}\n(FastFlags: {flags})")

    def on_bypass_toggle(self, switch, state):
        self.config_manager.settings["enable_bypass"] = state
        self.config_manager.save_tuxstrap_settings()

    def on_gamemode_toggle(self, switch, state):
        self.config_manager.settings["use_gamemode"] = state
        self.config_manager.save_tuxstrap_settings()

    def on_gpu_changed(self, combo):
        self.config_manager.settings["gpu_preference"] = combo.get_active_id()
        self.config_manager.save_tuxstrap_settings()

    def on_home_mode_changed(self, combo):
        self.config_manager.settings["home_screen_mode"] = combo.get_active_id()
        self.config_manager.save_tuxstrap_settings()

    def on_hidpi_toggle(self, switch, state):
        self.config_manager.settings["enable_hidpi"] = state
        self.config_manager.save_tuxstrap_settings()

    def on_rpc_toggle(self, switch, state):
        self.config_manager.settings["discord_rpc"] = state
        self.config_manager.save_tuxstrap_settings()

    def on_window_close(self, *args):
        self.monitor.stop()
        Gtk.main_quit()
