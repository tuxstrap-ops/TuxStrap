"""
TuxStrap Friends & In-Launcher Chat Engine.
Enables local/peer discovery, friend management, group creation,
and direct messaging without needing Discord or external Roblox services.
"""

import json
import time
import socket
import threading
from pathlib import Path
from typing import List, Dict, Any, Optional, Callable
from core.logger import log

FRIENDS_FILE = Path.home() / ".config" / "tuxstrap" / "friends_data.json"
BROADCAST_PORT = 19890

class FriendsManager:
    def __init__(self, data_path: Path = FRIENDS_FILE):
        self.data_path = data_path
        self.username: str = "TuxPlayer"
        self.status: str = "Çevrimiçi"
        self.friends: List[Dict[str, Any]] = []
        self.groups: List[Dict[str, Any]] = []
        self.messages: Dict[str, List[Dict[str, Any]]] = {} # key: friend_name or group_id
        self._listeners: List[Callable[[], None]] = []
        self._load()
        self._start_lan_discovery()

    def add_listener(self, cb: Callable[[], None]):
        self._listeners.append(cb)

    def _notify(self):
        for cb in self._listeners:
            try:
                cb()
            except Exception:
                pass

    def _load(self):
        if self.data_path.exists():
            try:
                with open(self.data_path, "r", encoding="utf-8") as f:
                    d = json.load(f)
                    self.username = d.get("username", "TuxPlayer")
                    self.status = d.get("status", "Çevrimiçi")
                    self.friends = d.get("friends", [])
                    self.groups = d.get("groups", [])
                    self.messages = d.get("messages", {})
                    return
            except Exception as e:
                log(f"[Friends] Load error: {e}", "WARN")

        # Initial demo friend
        self.friends = [
            {"name": "TuxStrapBot", "status": "Roblox Oynuyor (Blade Ball)", "ip": "127.0.0.1"}
        ]
        self.groups = [
            {"id": "general", "name": "TuxStrap Genel Sohbet", "members": [self.username, "TuxStrapBot"]}
        ]
        self.messages = {
            "TuxStrapBot": [
                {"sender": "TuxStrapBot", "text": "TuxStrap v1.0 Ultimate'a hoş geldin! Discord olmadan buradan konuşabiliriz.", "time": time.strftime("%H:%M")}
            ],
            "general": [
                {"sender": "TuxStrapBot", "text": "Burada arkadaşlarınızla takım kurup roblox taktikleri paylaşabilirsiniz!", "time": time.strftime("%H:%M")}
            ]
        }
        self.save()

    def save(self):
        try:
            self.data_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.data_path, "w", encoding="utf-8") as f:
                json.dump({
                    "username": self.username,
                    "status": self.status,
                    "friends": self.friends,
                    "groups": self.groups,
                    "messages": self.messages
                }, f, indent=2, ensure_ascii=False)
        except Exception as e:
            log(f"[Friends Error] Save failed: {e}", "ERROR")

    def set_profile(self, username: str, status: str):
        if username.strip():
            self.username = username.strip()
        if status.strip():
            self.status = status.strip()
        self.save()
        self._notify()

    def add_friend(self, name: str, ip: str = "127.0.0.1") -> bool:
        name = name.strip()
        if not name or name == self.username:
            return False
        for f in self.friends:
            if f["name"].lower() == name.lower():
                return False
        self.friends.append({
            "name": name,
            "status": "Çevrimiçi",
            "ip": ip
        })
        if name not in self.messages:
            self.messages[name] = []
        self.save()
        self._notify()
        log(f"[Friends] Added friend: {name}")
        return True

    def remove_friend(self, name: str):
        self.friends = [f for f in self.friends if f["name"] != name]
        self.save()
        self._notify()

    def create_group(self, group_name: str) -> str:
        group_name = group_name.strip()
        if not group_name:
            return ""
        gid = f"grp_{int(time.time())}"
        self.groups.append({
            "id": gid,
            "name": group_name,
            "members": [self.username]
        })
        self.messages[gid] = []
        self.save()
        self._notify()
        log(f"[Friends] Created group: {group_name}")
        return gid

    def send_message(self, target_key: str, text: str):
        text = text.strip()
        if not text or not target_key:
            return
        if target_key not in self.messages:
            self.messages[target_key] = []
        
        msg = {
            "sender": self.username,
            "text": text,
            "time": time.strftime("%H:%M")
        }
        self.messages[target_key].append(msg)
        self.save()
        self._notify()

    def _start_lan_discovery(self):
        """Broadcasts presence over UDP so peers on LAN can auto-discover."""
        def _listen():
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                s.bind(("0.0.0.0", BROADCAST_PORT))
                while True:
                    data, addr = s.recvfrom(1024)
                    if data:
                        text = data.decode("utf-8", errors="ignore")
                        if text.startswith("TUX_DISCOVER:"):
                            peer_name = text.split("TUX_DISCOVER:")[1].strip()
                            if peer_name and peer_name != self.username:
                                for f in self.friends:
                                    if f["name"].lower() == peer_name.lower():
                                        f["status"] = "Çevrimiçi (LAN)"
                                        f["ip"] = addr[0]
                                        self._notify()
            except Exception:
                pass

        threading.Thread(target=_listen, daemon=True).start()


# Global Singleton
_friends_instance: Optional[FriendsManager] = None

def get_friends_manager() -> FriendsManager:
    global _friends_instance
    if _friends_instance is None:
        _friends_instance = FriendsManager()
    return _friends_instance
