"""
TuxStrap Internationalization (i18n) Engine.
Clean, modern, esports-grade Turkish (tr) and English (en) localization.
"""

from typing import Dict, Any

TRANSLATIONS: Dict[str, Dict[str, str]] = {
    "tr": {
        "app_title": "TuxStrap",
        "app_subtitle": "Linux İçin Yeni Nesil Roblox İstemcisi • In-Game HUD • Sıfır-Ping Tünel",
        "tab_launcher": "Başlatıcı",
        "tab_history": "Geçmiş",
        "tab_overlay": "HUD Overlay",
        "tab_performance": "Performans",
        "tab_network": "Ağ & Tünel",
        "tab_customization": "Grafik",
        "tab_settings": "Ayarlar",
        "tab_console": "Günlük",
        
        "hero_title": "Roblox Başlatma Merkezi",
        "hero_ready": "Sistem hazır • Tek tıkla oyuna bağlan",
        "btn_launch": "Roblox'u Başlat",
        "btn_kill": "Oyunu Durdur (Kill)",
        "btn_hud_test": "HUD Panelini Aç",
        
        "tile_ping": "AĞ GECİKMESİ",
        "tile_cpu": "CPU FREKANSI",
        "tile_ram": "BELLEK KULLANIMI",
        "tile_bypass": "DPI TÜNEL DURUMU",
        
        "direct_join_title": "Doğrudan Deneyime Katıl",
        "direct_join_desc": "Bir Roblox Place ID veya deneyim linki girerek doğrudan sunucuya bağlanın.",
        "direct_join_placeholder": "Place ID veya Link (örn: 9285238704)",
        "direct_join_btn": "Oyuna Katıl",
        
        "quick_settings": "Hızlı Yapılandırma",
        "active_preset": "Aktif Performans Profili:",
        "bypass_switch": "Dahili ByeDPI Sansür Kırıcı (Sıfır Ping):",
        "gamemode_switch": "3.7+ GHz CPU Turbo Performans Modu:",
        
        "history_title": "Son Oynanan Deneyimler",
        "history_clear": "Geçmişi Temizle",
        "history_empty": "Henüz kayıtlı oyun geçmişi yok. Oynadığınız deneyimler burada listelenecektir.",
        "history_launch": "Başlat",
        
        "overlay_guide_title": "Oyun-İçi X11 HUD Paneli",
        "overlay_guide_desc": "TuxStrap HUD, Roblox çalışırken oyun ekranının üzerine gelen yarı saydam, minimal bir performans göstergesidir.",
        "overlay_test_btn": "HUD Panelini Test Et",
        
        "perf_title": "Performans Profili & FastFlags",
        "perf_gpu_title": "Donanım Hızlandırma & Grafik İşlemci",
        "perf_gpu_lbl": "GPU Tercihi:",
        "perf_vulkan_lbl": "✓ Vulkan ANV Donanım Hızlandırması: AKTİF (Mesa Immediate Mode)",
        
        "net_title": "Sıfır-Ping ByeDPI & DoH Motoru",
        "net_info": "• ByeDPI Parametreleri: -s 2 -o 1 -U (TCP Out-of-Order OOB Split)\n• DoH Sağlayıcıları: Cloudflare (1.1.1.1) + Google (8.8.8.8) + Quad9 Akıllı Çözümleme\n• Yerel Passthrough: Flatpak iç soketi tam korumalıdır.",
        "net_ping_btn": "Ping Testi",
        "net_measuring": "Ölçülüyor...",
        
        "custom_title": "Grafik & Görünüm Özelleştirmeleri",
        "custom_menu_mode": "Roblox Menü Arayüzü:",
        "custom_hidpi": "HiDPI Yüksek Çözünürlüklü Ölçekleme:",
        "custom_discord": "Discord Durum Bildirimi (RPC):",
        
        "settings_title": "TuxStrap Tercihleri",
        "settings_lang": "Dil (Language):",
        "settings_theme": "Arayüz Teması:",
        "settings_hotkey": "Oyun-İçi HUD Kısayol Tuşu:",
        "settings_theme_title": "Arayüz Teması & Arka Plan",
        "settings_accent_lbl": "Özel Vurgu Rengi:",
        "settings_bg": "Özel Arka Plan Resmi:",
        "settings_bg_choose": "Resim Seç...",
        "settings_bg_clear": "Sıfırla",
        
        "console_title": "Sistem & Oyun Günlüğü",
        "console_clear": "Konsolu Temizle"
    },
    "en": {
        "app_title": "TuxStrap",
        "app_subtitle": "Next-Gen Roblox Client for Linux • In-Game HUD • Zero-Ping Bypass",
        "tab_launcher": "Dashboard",
        "tab_history": "History",
        "tab_overlay": "HUD Overlay",
        "tab_performance": "Performance",
        "tab_network": "Network",
        "tab_customization": "Graphics",
        "tab_settings": "Settings",
        "tab_console": "Console",
        
        "hero_title": "Roblox Launch Control",
        "hero_ready": "System ready • 1-click connect to experience",
        "btn_launch": "Launch Roblox",
        "btn_kill": "Stop Game (Kill)",
        "btn_hud_test": "Open HUD Panel",
        
        "tile_ping": "NETWORK LATENCY",
        "tile_cpu": "CPU FREQUENCY",
        "tile_ram": "MEMORY USAGE",
        "tile_bypass": "DPI TUNNEL STATUS",
        
        "direct_join_title": "Direct Experience Join",
        "direct_join_desc": "Paste a Roblox Place ID or experience link to join directly.",
        "direct_join_placeholder": "Place ID or Link (e.g. 9285238704)",
        "direct_join_btn": "Join Game",
        
        "quick_settings": "Quick Configuration",
        "active_preset": "Active Performance Preset:",
        "bypass_switch": "Built-in Zero-Ping ByeDPI Bypass:",
        "gamemode_switch": "3.7+ GHz CPU Turbo Performance Mode:",
        
        "history_title": "Recent Experiences",
        "history_clear": "Clear History",
        "history_empty": "No game history recorded yet. Experiences you join will appear here.",
        "history_launch": "Launch",
        
        "overlay_guide_title": "In-Game X11 HUD Overlay",
        "overlay_guide_desc": "TuxStrap HUD is a translucent, minimal performance overlay displayed directly over Roblox.",
        "overlay_test_btn": "Test HUD Overlay",
        
        "perf_title": "Performance Presets & FastFlags",
        "perf_gpu_title": "Hardware Acceleration & GPU",
        "perf_gpu_lbl": "GPU Preference:",
        "perf_vulkan_lbl": "✓ Vulkan ANV Hardware Acceleration: ACTIVE (Mesa Immediate Mode)",
        
        "net_title": "Zero-Ping ByeDPI & DoH Engine",
        "net_info": "• ByeDPI Flags: -s 2 -o 1 -U (TCP Out-of-Order OOB Split)\n• DoH Resolvers: Cloudflare (1.1.1.1) + Google (8.8.8.8) + Quad9 Smart Resolution\n• Local Passthrough: Flatpak internal socket is fully isolated.",
        "net_ping_btn": "Test Latency",
        "net_measuring": "Measuring...",
        
        "custom_title": "Graphics & Visual Customization",
        "custom_menu_mode": "Roblox Menu Interface:",
        "custom_hidpi": "HiDPI High Resolution Scaling:",
        "custom_discord": "Discord Rich Presence (RPC):",
        
        "settings_title": "TuxStrap Preferences",
        "settings_lang": "Language:",
        "settings_theme": "UI Theme:",
        "settings_hotkey": "In-Game HUD Toggle Key:",
        "settings_theme_title": "UI Theme & Background",
        "settings_accent_lbl": "Custom Accent Color:",
        "settings_bg": "Custom Background Image:",
        "settings_bg_choose": "Choose Image...",
        "settings_bg_clear": "Reset",
        
        "console_title": "System & Game Console",
        "console_clear": "Clear Console"
    }
}

_CURRENT_LANG = "tr"


def set_language(lang_code: str):
    global _CURRENT_LANG
    if lang_code in TRANSLATIONS:
        _CURRENT_LANG = lang_code


def get_language() -> str:
    return _CURRENT_LANG


def t(key: str) -> str:
    return TRANSLATIONS.get(_CURRENT_LANG, TRANSLATIONS["tr"]).get(key, key)
