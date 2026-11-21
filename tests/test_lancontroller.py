"""
Automated Test Suite for LANController
Verifies all-inclusive standalone architecture, self-healing subsystems,
embedded assets, configuration generation, and core utility functions.
"""

import base64
import json
import os
import sys
from pathlib import Path

# Add project root to path
ROOT_DIR = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(ROOT_DIR))

import LANController


def test_app_metadata():
    """Verify application metadata and exports."""
    assert LANController.APP_NAME == "LANControlFleetManager"
    assert "LANCONTROL" in LANController.APP_TITLE or "LANController" in LANController.APP_TITLE
    assert isinstance(LANController.__all__, list)
    assert len(LANController.__all__) >= 20


def test_embedded_logo_png_validity():
    """Verify that EMBEDDED_LOGO_PNG_B64 decodes to a valid PNG image."""
    b64_str = LANController.EMBEDDED_LOGO_PNG_B64
    assert len(b64_str) > 1000
    png_bytes = base64.b64decode(b64_str)
    # Valid PNG header signature: \x89PNG\r\n\x1a\n
    assert png_bytes[:8] == b"\x89PNG\r\n\x1a\n", "Embedded logo does not match valid PNG signature!"


def test_ensure_app_logo(tmp_path, monkeypatch):
    """Verify self-healing logo extraction."""
    monkeypatch.setattr(LANController, "APP_DIR", tmp_path)
    extracted = LANController.ensure_app_logo()
    assert extracted.exists()
    assert extracted.stat().st_size > 1000
    assert extracted.read_bytes()[:8] == b"\x89PNG\r\n\x1a\n"


def test_generate_session_key():
    """Verify cryptographically secure random session key generation."""
    key1 = LANController.generate_session_key()
    key2 = LANController.generate_session_key()
    assert isinstance(key1, str)
    assert len(key1) >= 40
    assert key1 != key2, "Session keys must be unique"


def test_ensure_default_config(tmp_path, monkeypatch):
    """Verify self-healing default config.json generation."""
    test_cfg_file = tmp_path / "config.json"
    monkeypatch.setattr(LANController, "LOCAL_CONFIG_FILE", test_cfg_file)

    assert not test_cfg_file.exists()
    created_path = LANController.ensure_default_config()
    assert created_path.exists()

    with created_path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    assert "settings" in data
    assert data["settings"]["port"] == 443
    assert data["settings"]["LANonly"] is True
    assert len(data["settings"]["sessionKey"]) >= 32
    assert "domains" in data


def test_lan_ip_detection():
    """Verify IP resolution functions return valid strings without throwing exceptions."""
    ips = LANController.local_ipv4_addresses()
    assert isinstance(ips, list)
    best_ip = LANController.choose_best_lan_ip()
    assert isinstance(best_ip, str)
    assert len(best_ip.split(".")) == 4


def test_is_port_in_use():
    """Verify port usage checker."""
    in_use, msg = LANController.is_port_in_use(65530)
    assert isinstance(in_use, bool)
    assert isinstance(msg, str)


def test_atomic_write_and_load_json(tmp_path):
    """Verify safe atomic JSON write and load operations."""
    target_file = tmp_path / "test_data.json"
    payload = {"status": "ok", "version": 2.5, "nodes": [1, 2, 3]}

    LANController.atomic_write_json(target_file, payload)
    assert target_file.exists()

    loaded = LANController.load_json(target_file)
    assert loaded == payload


if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main(["-v", __file__]))
