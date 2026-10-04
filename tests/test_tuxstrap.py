import sys
import unittest
import json
import shutil
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

TEST_DIR = BASE_DIR / "tests" / "test_env"
TEST_CONFIG_DIR  = TEST_DIR / "config"
TEST_SOBER_DIR   = TEST_DIR / "sober"
TEST_APPDATA_DIR = TEST_DIR / "appdata"

from core.presets import PRESETS, DEFAULT_PRESET
from core.config import ConfigManager
from core.bypass import ByeDPIBridgeServer
from core.history import GameHistoryManager
from core.monitor import SystemMonitor


class TestPresets(unittest.TestCase):
    def test_structure(self):
        self.assertIn(DEFAULT_PRESET, PRESETS)
        for name, p in PRESETS.items():
            self.assertIn("flags", p)
            self.assertIn("graphics_optimization_mode", p)
            self.assertIn("xml_quality", p)
            self.assertIn("xml_saved_quality", p)
            self.assertEqual(p["xml_framecap"], 360 if "Ultra" in name or "Comp" in name else (240 if "Bal" in name else 144))


class TestConfig(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        for d in [TEST_CONFIG_DIR, TEST_SOBER_DIR, TEST_APPDATA_DIR]:
            d.mkdir(parents=True, exist_ok=True)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(TEST_DIR, ignore_errors=True)

    def test_sync(self):
        cfg = ConfigManager(config_dir=TEST_CONFIG_DIR, sober_dir=TEST_SOBER_DIR, appdata_dir=TEST_APPDATA_DIR)
        cfg.settings["preset"] = DEFAULT_PRESET
        cfg.settings["custom_flags"] = {"FFlagDebugDisplayFPS": True}
        cfg.sync_to_sober()

        with open(TEST_SOBER_DIR / "config.json") as f:
            data = json.load(f)
        self.assertTrue(data["fflags"].get("FFlagDebugDisplayFPS"))
        self.assertEqual(data["graphics_optimization_mode"], "performance")
        self.assertFalse(data.get("use_opengl"))

    def test_xml_patch(self):
        xml_file = TEST_APPDATA_DIR / "GlobalBasicSettings_13.xml"
        xml_file.write_text(
            '<roblox>'
            '<int name="FramerateCap">60</int>'
            '<int name="GraphicsQualityLevel">21</int>'
            '<token name="SavedQualityLevel">10</token>'
            '</roblox>'
        )
        cfg = ConfigManager(config_dir=TEST_CONFIG_DIR, sober_dir=TEST_SOBER_DIR, appdata_dir=TEST_APPDATA_DIR)
        cfg.patch_roblox_xml_settings(target_fps=360, quality_level=1, saved_quality=1)

        content = xml_file.read_text()
        self.assertIn('<int name="FramerateCap">360</int>', content)
        self.assertIn('<int name="GraphicsQualityLevel">1</int>', content)
        self.assertIn('<token name="SavedQualityLevel">1</token>', content)


class TestByeDPIBridge(unittest.TestCase):
    def test_bridge_lifecycle(self):
        srv = ByeDPIBridgeServer(port=19992)
        self.assertTrue(srv.start())
        self.assertTrue(srv.is_running)
        srv.stop()
        self.assertFalse(srv.is_running)

    def test_http_connect_private_ip(self):
        """Tests HTTP CONNECT passthrough to private IP (e.g. Sober local socket)."""
        import socket
        import threading

        # Start a local echo server representing Sober's internal UI socket
        echo_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        echo_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        echo_sock.bind(("127.0.0.1", 19994))
        echo_sock.listen(1)

        def echo_worker():
            try:
                conn, _ = echo_sock.accept()
                data = conn.recv(1024)
                conn.sendall(data)
                conn.close()
            except Exception:
                pass
            finally:
                echo_sock.close()

        threading.Thread(target=echo_worker, daemon=True).start()

        srv = ByeDPIBridgeServer(port=19993)
        self.assertTrue(srv.start())

        # Send HTTP CONNECT request through the bridge to 127.0.0.1:19994
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(("127.0.0.1", srv.port))
        client.sendall(b"CONNECT 127.0.0.1:19994 HTTP/1.1\r\nHost: 127.0.0.1:19994\r\n\r\n")

        resp = client.recv(1024)
        self.assertIn(b"200 Connection Established", resp)

        # Send payload and verify echo
        client.sendall(b"HELLO_SOBER")
        echo_resp = client.recv(1024)
        self.assertEqual(echo_resp, b"HELLO_SOBER")

        client.close()
        srv.stop()

    def test_strategy_cycling_and_health(self):
        """Tests that strategy can cycle and verify_health passes local checks."""
        srv = ByeDPIBridgeServer(port=19995)
        self.assertTrue(srv.start())
        self.assertTrue(srv.verify_health(timeout=1.0))

        # Test strategy cycling
        initial_strat = srv.current_strategy["name"]
        new_strat = srv.cycle_strategy()
        self.assertNotEqual(initial_strat, new_strat)
        self.assertTrue(srv.verify_health(timeout=1.0))
        srv.stop()


class TestHistory(unittest.TestCase):
    def test_history_recording(self):
        hist_file = TEST_CONFIG_DIR / "test_hist.json"
        hm = GameHistoryManager(history_path=hist_file)
        hm.record_place("189707", "Natural Disaster Survival")
        self.assertEqual(len(hm.history), 1)
        self.assertEqual(hm.history[0]["place_id"], "189707")

        # Duplicate check
        hm.record_place("189707", "Updated Title")
        self.assertEqual(len(hm.history), 1)
        self.assertEqual(hm.history[0]["title"], "Updated Title")

        hm.clear()
        self.assertEqual(len(hm.history), 0)


class TestMonitor(unittest.TestCase):
    def test_monitor_init(self):
        mon = SystemMonitor()
        self.assertFalse(mon.is_running)


if __name__ == "__main__":
    unittest.main(verbosity=2)
