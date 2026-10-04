"""
TuxStrap System & Game Real-time Monitor.
Tracks ping latency, CPU stats, and extracts Roblox place history from live logs.
"""

import time
import socket
import threading
from typing import Optional, Callable, Dict, List
import psutil
from core.logger import log

class SystemMonitor:
    def __init__(self, ping_host: str = "1.1.1.1", ping_port: int = 443):
        self.ping_host = ping_host
        self.ping_port = ping_port
        self.current_ping_ms: float = 0.0
        self.current_cpu_percent: float = 0.0
        self.current_ram_percent: float = 0.0
        self.current_cpu_freq_ghz: float = 0.0
        self.is_running: bool = False
        self._thread: Optional[threading.Thread] = None
        self._listeners: List[Callable[[Dict[str, float]], None]] = []

    def add_listener(self, callback: Callable[[Dict[str, float]], None]):
        self._listeners.append(callback)

    def start(self):
        if self.is_running:
            return
        self.is_running = True
        self._thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._thread.start()
        log("[Monitor] Real-time hardware and latency monitor started.")

    def stop(self):
        self.is_running = False

    def measure_ping(self) -> float:
        """Measures TCP handshake RTT in milliseconds to Cloudflare DNS."""
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1.5)
        start = time.perf_counter()
        try:
            s.connect((self.ping_host, self.ping_port))
            rtt = (time.perf_counter() - start) * 1000.0
            s.close()
            return round(rtt, 1)
        except Exception:
            try:
                s.close()
            except Exception:
                pass
            return 0.0

    def _monitor_loop(self):
        while self.is_running:
            try:
                # 1. Ping
                p = self.measure_ping()
                if p > 0:
                    self.current_ping_ms = p

                # 2. CPU / RAM
                self.current_cpu_percent = psutil.cpu_percent(interval=None)
                self.current_ram_percent = psutil.virtual_memory().percent

                # 3. CPU Freq
                freq = psutil.cpu_freq()
                if freq and freq.current:
                    self.current_cpu_freq_ghz = round(freq.current / 1000.0, 2)
                else:
                    self.current_cpu_freq_ghz = 0.0

                stats = {
                    "ping": self.current_ping_ms,
                    "cpu_percent": self.current_cpu_percent,
                    "ram_percent": self.current_ram_percent,
                    "cpu_freq": self.current_cpu_freq_ghz,
                }

                for cb in self._listeners:
                    try:
                        cb(stats)
                    except Exception:
                        pass

            except Exception:
                pass

            time.sleep(1.5)


# Global Singleton
_monitor_instance: Optional[SystemMonitor] = None

def get_system_monitor() -> SystemMonitor:
    global _monitor_instance
    if _monitor_instance is None:
        _monitor_instance = SystemMonitor()
    return _monitor_instance
