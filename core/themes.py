"""
TuxStrap Theme & Styling Engine.
Provides presets (Cyberpunk Neon, Matrix Green, Crimson Fury, Midnight Blue)
and supports custom accent colors and background imagery.
"""

from typing import Dict, Any

PRESET_THEMES: Dict[str, Dict[str, str]] = {
    "Cyberpunk Neon": {
        "accent": "#8b5cf6",
        "accent_hover": "#a855f7",
        "secondary": "#3b82f6",
        "bg_dark": "#090b10",
        "card_bg": "rgba(16, 20, 31, 0.75)",
        "card_border": "rgba(139, 92, 246, 0.22)",
        "header_bg": "linear-gradient(135deg, #0e121d 0%, #15102a 50%, #0d1424 100%)",
        "hero_btn": "linear-gradient(135deg, #7c3aed 0%, #3b82f6 100%)",
        "hero_hover": "linear-gradient(135deg, #8b5cf6 0%, #60a5fa 100%)",
        "glow": "rgba(139, 92, 246, 0.45)"
    },
    "Matrix Green": {
        "accent": "#10b981",
        "accent_hover": "#34d399",
        "secondary": "#059669",
        "bg_dark": "#050c08",
        "card_bg": "rgba(6, 26, 17, 0.75)",
        "card_border": "rgba(16, 185, 129, 0.25)",
        "header_bg": "linear-gradient(135deg, #05140b 0%, #062b18 50%, #041209 100%)",
        "hero_btn": "linear-gradient(135deg, #059669 0%, #10b981 100%)",
        "hero_hover": "linear-gradient(135deg, #10b981 0%, #34d399 100%)",
        "glow": "rgba(16, 185, 129, 0.45)"
    },
    "Crimson Fury": {
        "accent": "#ef4444",
        "accent_hover": "#f87171",
        "secondary": "#b91c1c",
        "bg_dark": "#0c0708",
        "card_bg": "rgba(31, 14, 17, 0.75)",
        "card_border": "rgba(239, 68, 68, 0.25)",
        "header_bg": "linear-gradient(135deg, #1b0a0e 0%, #310c14 50%, #18080b 100%)",
        "hero_btn": "linear-gradient(135deg, #dc2626 0%, #ef4444 100%)",
        "hero_hover": "linear-gradient(135deg, #ef4444 0%, #f87171 100%)",
        "glow": "rgba(239, 68, 68, 0.45)"
    },
    "Midnight Blue": {
        "accent": "#0ea5e9",
        "accent_hover": "#38bdf8",
        "secondary": "#1d4ed8",
        "bg_dark": "#070b14",
        "card_bg": "rgba(12, 22, 40, 0.75)",
        "card_border": "rgba(14, 165, 233, 0.25)",
        "header_bg": "linear-gradient(135deg, #081124 0%, #0b1f42 50%, #060e1d 100%)",
        "hero_btn": "linear-gradient(135deg, #0284c7 0%, #2563eb 100%)",
        "hero_hover": "linear-gradient(135deg, #0ea5e9 0%, #3b82f6 100%)",
        "glow": "rgba(14, 165, 233, 0.45)"
    }
}

def generate_css(theme_name: str = "Cyberpunk Neon", custom_color: str = "#8b5cf6") -> str:
    th = PRESET_THEMES.get(theme_name, PRESET_THEMES["Cyberpunk Neon"]).copy()
    if theme_name == "Custom" and custom_color:
        th["accent"] = custom_color
        th["accent_hover"] = custom_color
        th["glow"] = custom_color
        th["card_border"] = custom_color
        th["hero_btn"] = f"linear-gradient(135deg, {custom_color} 0%, #1e293b 100%)"

    return f"""
* {{
    font-family: 'Inter', 'Ubuntu', 'Segoe UI', 'Sans-Serif';
    font-size: 13px;
    outline: none;
}}

window {{
    background-color: {th['bg_dark']};
    color: #f1f5f9;
}}

.header-box {{
    background: {th['header_bg']};
    border-bottom: 1px solid {th['card_border']};
    padding: 16px 20px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
}}

.app-title {{
    font-size: 22px;
    font-weight: 800;
    color: #ffffff;
    letter-spacing: -0.5px;
}}

.app-subtitle {{
    font-size: 11px;
    font-weight: 500;
    color: #94a3b8;
    margin-top: 2px;
}}

.status-pill {{
    font-size: 11px;
    font-weight: 600;
    padding: 5px 12px;
    border-radius: 20px;
    background: rgba(15, 23, 42, 0.8);
    border: 1px solid rgba(255, 255, 255, 0.08);
}}

.status-active {{
    color: #34d399;
    border-color: rgba(52, 211, 153, 0.4);
    background: rgba(6, 78, 59, 0.3);
}}

.status-neon-cyan {{
    color: #38bdf8;
    border-color: rgba(56, 189, 248, 0.4);
    background: rgba(12, 74, 110, 0.3);
}}

.status-neon-purple {{
    color: {th['accent']};
    border-color: {th['card_border']};
    background: rgba(15, 23, 42, 0.8);
}}

notebook tab {{
    padding: 10px 18px;
    background-color: transparent;
    color: #94a3b8;
    font-weight: 600;
    font-size: 12px;
    border: none;
    border-bottom: 2px solid transparent;
}}

notebook tab:hover {{
    color: #e2e8f0;
    background-color: rgba(255, 255, 255, 0.03);
}}

notebook tab:checked {{
    color: {th['accent']};
    background-color: rgba(255, 255, 255, 0.04);
    border-bottom: 2px solid {th['accent']};
    font-weight: 700;
}}

.card {{
    background: {th['card_bg']};
    border: 1px solid {th['card_border']};
    border-radius: 12px;
    padding: 18px;
    margin-bottom: 6px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.25);
}}

.card:hover {{
    border-color: {th['accent']};
}}

.card-title {{
    font-size: 15px;
    font-weight: 700;
    color: #f8fafc;
    letter-spacing: -0.2px;
    margin-bottom: 4px;
}}

.card-title-small {{
    font-size: 13px;
    font-weight: 600;
    color: #cbd5e1;
}}

.card-desc {{
    font-size: 11px;
    color: #94a3b8;
}}

button {{
    border-radius: 8px;
    font-weight: 600;
    padding: 8px 16px;
    border: 1px solid transparent;
}}

.btn-launch-hero {{
    background: {th['hero_btn']};
    color: #ffffff;
    font-size: 15px;
    font-weight: 800;
    padding: 14px 24px;
    border-radius: 10px;
    border: 1px solid rgba(255, 255, 255, 0.2);
    box-shadow: 0 4px 20px {th['glow']};
}}

.btn-launch-hero:hover {{
    background: {th['hero_hover']};
}}

.btn-danger-neon {{
    background: linear-gradient(135deg, #dc2626 0%, #991b1b 100%);
    color: #ffffff;
    font-weight: 700;
    padding: 10px 18px;
    border-radius: 8px;
    border: 1px solid rgba(248, 113, 113, 0.4);
}}

.btn-danger-neon:hover {{
    background: linear-gradient(135deg, #ef4444 0%, #b91c1c 100%);
}}

.btn-neon-purple {{
    background: rgba(255, 255, 255, 0.05);
    color: {th['accent']};
    border: 1px solid {th['card_border']};
    border-radius: 8px;
    font-weight: 600;
}}

.btn-neon-purple:hover {{
    background: rgba(255, 255, 255, 0.12);
    color: #ffffff;
    border-color: {th['accent']};
}}

.btn-secondary-neon {{
    background: rgba(15, 23, 42, 0.8);
    color: #94a3b8;
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 8px;
}}

.btn-secondary-neon:hover {{
    background: rgba(30, 41, 59, 0.9);
    color: #f1f5f9;
}}

.stat-tile {{
    background: rgba(15, 23, 42, 0.6);
    border: 1px solid rgba(255, 255, 255, 0.06);
    border-radius: 10px;
    padding: 12px 16px;
}}

.stat-tile-title {{
    font-size: 11px;
    font-weight: 600;
    color: #94a3b8;
    margin-bottom: 2px;
}}

.stat-tile-val {{
    font-size: 18px;
    font-weight: 800;
    color: #ffffff;
}}

.val-green {{ color: #34d399; }}
.val-blue {{ color: #38bdf8; }}
.val-purple {{ color: {th['accent']}; }}

combobox button, entry {{
    background: #111522;
    border: 1px solid {th['card_border']};
    border-radius: 8px;
    color: #f1f5f9;
    padding: 8px 12px;
}}

entry:focus, combobox button:focus {{
    border-color: {th['accent']};
}}

switch {{
    background-color: #1e293b;
    border-radius: 16px;
    border: 1px solid rgba(255, 255, 255, 0.1);
}}

switch:checked {{
    background: {th['hero_btn']};
    border-color: {th['card_border']};
}}

switch slider {{
    background: #ffffff;
    border-radius: 50%;
    margin: 2px;
    min-width: 18px;
    min-height: 18px;
}}

.console-view {{
    background-color: #07090e;
    color: #38bdf8;
    font-family: 'JetBrains Mono', 'Fira Code', 'Monospace';
    font-size: 11px;
    padding: 12px;
    border-radius: 10px;
    border: 1px solid rgba(56, 189, 248, 0.2);
}}

.overlay-window {{
    background-color: rgba(10, 13, 20, 0.94);
    border: 2px solid {th['accent']};
    border-radius: 16px;
    box-shadow: 0 10px 40px rgba(0, 0, 0, 0.8), 0 0 25px {th['glow']};
}}

.overlay-title {{
    font-size: 16px;
    font-weight: 800;
    color: #ffffff;
}}

.overlay-badge {{
    font-size: 11px;
    font-weight: 700;
    color: {th['accent']};
    background: rgba(255, 255, 255, 0.08);
    border: 1px solid {th['card_border']};
    border-radius: 6px;
    padding: 3px 8px;
}}

.overlay-close-btn {{
    background: rgba(255, 255, 255, 0.08);
    color: #94a3b8;
    font-weight: 800;
    padding: 4px 10px;
    border-radius: 6px;
}}

.overlay-close-btn:hover {{
    background: rgba(239, 68, 68, 0.3);
    color: #ef4444;
}}

.overlay-card {{
    background: rgba(18, 22, 34, 0.85);
    border: 1px solid {th['card_border']};
    border-radius: 10px;
    padding: 12px;
}}

.overlay-stat-card {{
    background: rgba(14, 18, 28, 0.85);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 8px;
    padding: 10px;
}}

.stat-title {{
    font-size: 10px;
    font-weight: 600;
    color: #94a3b8;
}}

.stat-value {{
    font-size: 15px;
    font-weight: 800;
}}

.stat-val-ping {{ color: #34d399; }}
.stat-val-cpu {{ color: #38bdf8; }}
.stat-val-ram {{ color: {th['accent']}; }}
.overlay-footer-text {{ font-size: 10px; color: #64748b; }}
"""
