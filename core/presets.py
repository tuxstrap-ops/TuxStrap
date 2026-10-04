"""
TuxStrap Performance Presets and FastFlags definitions.
FramerateCap is explicitly set to 360 (setting to 0 causes Roblox renderer to render 0 FPS = Black Screen freeze).
"""

from typing import Dict, Any

PRESETS: Dict[str, Dict[str, Any]] = {
    "Ultra FPS Boost (Patates Modu)": {
        "description": "Grafik kalitesini en alt seviyeye çeker, tüm gereksiz render yükünü kapatır. Oynanabilir ama görsel açıdan çok yalın.",
        "xml_quality": 1,
        "xml_saved_quality": 1,
        "xml_framecap": 240,
        "flags": {
            "DFIntTaskSchedulerTargetFps": 240,
            "FFlagTaskSchedulerLimitTargetFpsTo2402": False,
            "FFlagDebugDisplayFPS": True,
            "DFFlagDisableDPIScale": True,
            "FIntRenderShadowIntensity": 0,
            "FFlagGlobalWindActivated": False,
            "DFIntCSGLevelOfDetailSwitchingDistance": 0,
            "DFIntCSGLevelOfDetailSwitchingDistanceL12": 0,
            "DFIntCSGLevelOfDetailSwitchingDistanceL23": 0,
            "DFIntCSGLevelOfDetailSwitchingDistanceL34": 0,
            "FIntFRMMaxGrassDistance": 0,
            "FIntFRMMinGrassDistance": 0,
        },
        "graphics_optimization_mode": "performance"
    },
    "Competitive (Rekabetçi Mod)": {
        "description": "Oynanabilir görsel kalite ile yüksek ve stabil FPS dengesi. Taktikal ve rekabetçi oyun için.",
        "xml_quality": 3,
        "xml_saved_quality": 3,
        "xml_framecap": 240,
        "flags": {
            "DFIntTaskSchedulerTargetFps": 240,
            "FFlagTaskSchedulerLimitTargetFpsTo2402": False,
            "FFlagDebugDisplayFPS": True,
            "DFFlagDisableDPIScale": True,
            "FFlagGlobalWindActivated": False,
            "DFIntCSGLevelOfDetailSwitchingDistance": 100,
            "DFIntCSGLevelOfDetailSwitchingDistanceL12": 100,
            "DFIntCSGLevelOfDetailSwitchingDistanceL23": 200,
            "DFIntCSGLevelOfDetailSwitchingDistanceL34": 400,
            "FIntFRMMaxGrassDistance": 0,
            "FIntFRMMinGrassDistance": 0,
        },
        "graphics_optimization_mode": "performance"
    },
    "Balanced (Dengeli Mod)": {
        "description": "Akıcı FPS ile yeterli görsel kaliteyi dengeler.",
        "xml_quality": 5,
        "xml_saved_quality": 5,
        "xml_framecap": 240,
        "flags": {
            "DFIntCSGLevelOfDetailSwitchingDistance": 250,
            "DFIntCSGLevelOfDetailSwitchingDistanceL12": 250,
            "DFIntCSGLevelOfDetailSwitchingDistanceL23": 500,
            "DFIntCSGLevelOfDetailSwitchingDistanceL34": 1000,
            "FIntFRMMaxGrassDistance": 100,
            "FFlagFastGPULightCulling3": True,
            "FFlagDebugDisplayFPS": True,
        },
        "graphics_optimization_mode": "balanced"
    },
    "Maximum Quality (Yüksek Görsellik)": {
        "description": "Tam görsel kalite. Sadece güçlü sistemler için.",
        "xml_quality": 10,
        "xml_saved_quality": 10,
        "xml_framecap": 144,
        "flags": {
            "FFlagFastGPULightCulling3": True,
            "FFlagDebugDisplayFPS": True,
        },
        "graphics_optimization_mode": "quality"
    }
}

DEFAULT_PRESET = "Ultra FPS Boost (Patates Modu)"
