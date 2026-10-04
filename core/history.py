"""
TuxStrap Roblox Game History & Quick Join Manager.
Tracks recently launched Roblox experiences and enables 1-click relaunch.
"""

import json
import time
from pathlib import Path
from typing import List, Dict, Any
from core.logger import log

HISTORY_FILE = Path.home() / ".config" / "tuxstrap" / "game_history.json"

class GameHistoryManager:
    def __init__(self, history_path: Path = HISTORY_FILE):
        self.history_path = history_path
        self.history: List[Dict[str, Any]] = []
        self.load()

    def load(self):
        if self.history_path.exists():
            try:
                with open(self.history_path, "r", encoding="utf-8") as f:
                    self.history = json.load(f)
            except Exception as e:
                log(f"[History] Failed to load history: {e}", "WARN")
                self.history = []
        else:
            self.history = []

    def save(self):
        try:
            self.history_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.history_path, "w", encoding="utf-8") as f:
                json.dump(self.history, f, indent=2, ensure_ascii=False)
        except Exception as e:
            log(f"[History Error] Could not save history: {e}", "ERROR")

    def record_place(self, place_id: str, title: str = ""):
        if not place_id or place_id == "0":
            return
        
        # Deduplicate
        self.history = [h for h in self.history if str(h.get("place_id")) != str(place_id)]
        
        entry = {
            "place_id": str(place_id),
            "title": title or f"Roblox Deneyimi #{place_id}",
            "timestamp": int(time.time()),
            "date_str": time.strftime("%d.%m.%Y %H:%M")
        }
        self.history.insert(0, entry)
        # Keep last 15
        self.history = self.history[:15]
        self.save()
        log(f"[History] Recorded experience: Place ID {place_id}")

    def clear(self):
        self.history = []
        self.save()

_history_instance = None

def get_history_manager() -> GameHistoryManager:
    global _history_instance
    if _history_instance is None:
        _history_instance = GameHistoryManager()
    return _history_instance
