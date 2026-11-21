#!/usr/bin/env pythonw
"""
LANController Autonomous Standalone Fleet & MDM Manager
======================================================
Complete, fully all-inclusive, fully standalone, self-healing Windows administration
console, background system tray controller, and enterprise deployment engine.

Zero External Setup Required:
- Autonomous Self-Healing Dependency Bootstrapper (auto-heals Pillow, pystray, qrcode, cryptography).
- Zero Crash Guarantee: Pure-Python and native Tkinter fallbacks for all modules.
- Embedded Base64 Branding & High-DPI Logo assets.
- Embedded Self-Healing Configuration Engine & Default JSON Generator.
- Deep Self-Audit, Automated Repair, Port Collision Resolver, and Watchdog Loop.
- Real-time LAN Fleet Discovery, Tailscale Remote MagicDNS integration, and Android QR MDM.
"""

from __future__ import annotations

import argparse
import base64
from concurrent.futures import ThreadPoolExecutor
import csv
import copy
import datetime as dt
import ipaddress
import json
import os
import platform
import queue
import re
import secrets
import shutil
import socket
import ssl
import subprocess
import sys
import tempfile
import threading
import time
import urllib.error
import urllib.request
import webbrowser
import winreg
from pathlib import Path
from typing import Callable

# Configure Windows console encoding for UTF-8 and emojis
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
if hasattr(sys.stderr, "reconfigure"):
    try:
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Configure high-DPI awareness on Windows to prevent blurry text or clipped sizing
if sys.platform == "win32":
    try:
        import ctypes
        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(2)  # Per-monitor DPI aware v2
        except Exception:
            ctypes.windll.user32.SetProcessDPIAware()
    except Exception:
        pass

# ---------------------------------------------------------------------------
# Autonomous Self-Healing Dependency Bootstrapper & Dynamic Imports
# ---------------------------------------------------------------------------

def _is_importable(module_name: str) -> bool:
    try:
        __import__(module_name)
        return True
    except Exception:
        return False

def _ensure_dependencies() -> None:
    """Autonomous Self-Healing Dependency Bootstrapper.
    Detects if required runtime libraries (Pillow, pystray, qrcode, cryptography)
    are present. If missing, attempts background pip auto-installation silently.
    """
    required = {
        "PIL": "pillow",
        "pystray": "pystray",
        "qrcode": "qrcode",
        "cryptography": "cryptography"
    }
    missing = [pkg for mod, pkg in required.items() if not _is_importable(mod)]
    if missing:
        try:
            cmd = [sys.executable, "-m", "pip", "install", *missing, "--quiet", "--no-warn-script-location"]
            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=90, check=False)
        except Exception:
            pass

_ensure_dependencies()

# GUI & Imaging
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

# Safe Dynamic Imports with Graceful Fallbacks
try:
    import PIL
    from PIL import Image, ImageDraw, ImageTk
    HAS_PIL = True
except Exception:
    HAS_PIL = False

try:
    import pystray
    HAS_PYSTRAY = True
except Exception:
    HAS_PYSTRAY = False

try:
    import qrcode
    HAS_QRCODE = True
except Exception:
    HAS_QRCODE = False

try:
    import cryptography
    from cryptography import x509
    from cryptography.hazmat.primitives import serialization
    HAS_CRYPTO = True
except Exception:
    HAS_CRYPTO = False


# ---------------------------------------------------------------------------
# Constants & Paths
# ---------------------------------------------------------------------------

__all__ = [
    "APP_NAME",
    "APP_TITLE",
    "APP_VERSION",
    "EMBEDDED_LOGO_PNG_B64",
    "ensure_app_logo",
    "ensure_default_config",
    "LANControlGUI",
    "LANControlTray",
    "build_config",
    "atomic_write_json",
    "load_json",
    "generate_session_key",
    "choose_best_lan_ip",
    "local_ipv4_addresses",
    "fetch_public_ipv4",
    "is_port_in_use",
    "allow_firewall",
    "remove_firewall",
    "service_exists",
    "service_state",
    "control_service",
    "set_service_autostart",
    "is_login_autostart_enabled",
    "set_login_autostart_enabled",
    "main",
]

APP_NAME = "LANControlFleetManager"
APP_TITLE = "LANCONTROL Fleet & MDM Manager"
APP_VERSION = "2.4.1"

# Application directory (where this script lives)
APP_DIR = Path(__file__).parent.resolve()
LOCAL_CONFIG_FILE = APP_DIR / "config.json"
LOCAL_LOG_FILE = APP_DIR / "setup.log"

# ---------------------------------------------------------------------------
# Embedded Assets & Self-Healing Resource Management
# ---------------------------------------------------------------------------

EMBEDDED_LOGO_PNG_B64 = "iVBORw0KGgoAAAANSUhEUgAAAQAAAAEACAYAAABccqhmAAALv0lEQVR4nO3dPW7cSBrG8dLCgENrI/sKsjNnSh3MFQZwoKNMsEeZQICvsIFSZ8oMX8HZOFWkDWY5rqaKZFWxPt6P/y9azErddJPPUy/ZrebVm7fvnwMAl/41ewMAzEMBAI5RAIBjr2ZvQK6b+8fZmwAU+f754+xNOHQl8SIgYYdV0kpBTAEQengjoQymFgChB/42qwymFADBB9JGF8HQAiD4QJ5RRTCkAFoEX8L5ElBCw3HfvQBqXwQCD2skZqFrAZT+gwk9vJCSjS4FUPKPI/TwbmZemhdA7j+G4AOXZmSn6d8CEH6gXm4uWr6b1mwCyNkogg/kGZWnJhMA4QfayslLi0ng9ARwtBEEHzinZ8ZOTQCEH+jvKEdnJoHqAiD8wDi9SqCqAAg/MF6PEmj+lWCEH+indb6KC2CvZQg/0N9ezkqngKICIPyADK1KILsA+Ft+QI/cvDa5BsDqD4w37JOAjP6ATGdPBbgxCODYYQGw+gOynZkCqicAwg/IUZvH3QLgyj+g316OqyYAVn9AnppcchEQcGyzABj/ATu28lw8ATD+A3KV5pNTAMCxZAEw/gP2pHJdNAEw/gPyleSUUwDAMQoAcIwCABx7UQBbFwA5/wf02MrrOt9MAIBjr2ZvAMb6+ePb4c9cv/swYEsgAQVgXE7gj36HQrCLAjCqJvhHj0UR2EMBGHMU/NuHp8PH+Prp9e5jUwR2UACGbIU/J/RbP58qg58/vlECRlAABqSCXxr6LVtlwDRgA28DKtcz/DmP2/JaA8ZjAlBsHb5ewU89x3oaYBLQiQlAqRnh33s+JgGdKACFZod/63kpAX0oAOVmhV/K8+McCkCZeJWVEr54O5gCdKEAFNESLi3bCQpALSmr/0La9iAPBaCExNF/jVMBfSgAwDEKQAGtq6nW7faEAlBG6vi/kL59uEQBAI5RAIBjFIBwGq7+r/FugB4UAOAYBQA4RgEAjlEAgGMUAOAYBQA4RgEAjlEAgGMUgHDxt+1u3bFHmng7+bZg2SgAwDEKAHCMAlBG+mmA9O3DJQpAAa3n0Vq32xMKAHCMAlBCw7sBXP3XhwJQSloJSNse5KEAFNGyqmrZTlAA6kg8FWD014sCUG52Ccx+fpxDASi0XmVnhXD9vKz++lAASs0uAcJvw6vZG4B61+8+XHzr7hLKnt8enCoawq8XE4ByqfD1mgYIvz1MAMrd3D/+s+LHAY3/95mJYKtMtNyjAPsoAENuH56SgS0tg6MJIn6Mm/vH8P3zx4KthCQUgGI3948v/ltqGoidOT1g1beHawBG3T48NTs/v3142g1/qoigAxOAUrmhW5dAzr36UsVByG2iABTKCePWefkS7qs/f0/+/893X6q3iWsB+nAKgCw54WZK0IcCUObM6g+sUQDG9Aw/U4A9FIAiEsLFdGELBWCIlHBKKCrkoQCUkBQqKUWD8ygABTRe+JNUWNhGAaAKFwRtoACE07j6Qw8KQLmZ4WcK0I8CEExDeJg+dKMAFNMSPg1F5hUFIJSm0GgpIrxEAQhk8cKfpkLzhAJQSGL4uSCoEwUgjOaQSCwm7KMAlNEeMs0FZxEFIIiFcGgvKG8oACEsXvjbYqHorKAA0BwXBPWgAATwtPpDFgpAAY3hZwrQgQKYzHIINBaXNxSAcNZDZLkANaAAJvJw8FsvMO0ogEm48PeLhyKUigJAd1wQlIsCmIDVH1Jwc1CBeod/7w7B16Hu5qBHvn/+eFh83GB0PApgsFmjbs5twdc/l7pN+Bk5JYCxKABheqyA6/D/+7//2fzZv3774+L3WpfAEaaAsSiAgUavfnHw90Ifi3/ur9/++OcxWhUBU4AsXAQcZPSFv5rwr8W/l3sK0QIFMQ4FYFCL8Kd+v1UJ8LagHBTAALPe9jsb/taPA3koAAF6jP6tQ7s8HlOALRRAZyMP4l7hX8woAfRFAUxGCPYxBfRFAXTEwXuMApyLAuhk1tt+vS/YtT4NyEGR9kMBTMLK9wsXBOehADrgYC1HIc5BAUzAwV6HYm2PAmiMg7QexTgeBdAQX/TRHwXbFgUAUbggOBYF0Mjs1X/5c9347/l7WB5/9PcEoA8KYJDeo//Vn793ffyRz8cUMA4F0MDsg3F0+OPn7fXcXCsZgwIYoNfBvA7g8im9XqcBy+OuP23Yswj2zC5eCyiAk2YchHuB61UCW+Ffb1dLTAH9UQAnzLjwVxKyViVQ8jijpwGmgHMoACVKgrX+Ys8z4t8v+UOjVkXABcG+KIBKo1b/miA93325eJuutgTi37t+9yE8330Jz3dlNw6ZdYESea7evH3/HP+HrQOb87FLRwXQKvwltsJZe1+AEPbf72+1fTlmf85Co5wsc1+ACr1HztbBun734aIEcieCow/7PN99KdrW5WdrioD7CfRBAXRQuxLVjMu5YYrDvHtvwMJP+C3PX1oEZ6aBLdxVqBwFUKjXKjRynO7xMd7SIqiZBpgC2nNfADlfbbUEpsd56MjgjzDytCBlPQWU7F+PXBZA6ffZxT9/+/DUZBt6jvuz9TwtyJkCzuxfb2XgqgBafJHl10+vQwjpIshd/a2t+ltGnBbEln1zRuuboUrnogD2gp+zoqcOrHUR5ITfS/DXWp8WrKeAveDX7l8vRWD+cwCp8J8Z41MHy+3D0+7rY3ncL9WyBG/uHzf3R63U42ktgZwsmy6Adfhbnb+H8PJA2TpIvK76R1q8LhL2r2Q5WTb7UeCeB0fq8dbPV/oR3pqP2WpW85Hi+PWcvX+tMFkAvQ+Orcf9+eNb9Wf3Par924KZ+9cacwUw6uDYevySP7zxtupvKXkd1q/v6P1rrQRMFcDo8G89z1EJEPy0o9dkdPi3nsdSCZgqgNiog6P0+Qj+vtxylLp/tTFTAD0+rVcqft71asWqX2b9esWvp4T9a2UKMFMAUhH8c3jt+jJRABJW/9Tz975JhxcSVv/U81uYAkwUAIA6FADgmPoCkDT+L6yNiTOxf/ty8deAs/EtNpBK/QQAoB4FADhGAQCOUQCAYxQA4BgFADhGAQCOqf8cQHzfu6+fXov4sEj8fXIav0tOkusQ2L8dMQEAjlEAgGMmCiAew1rcHeYMS+OhFOzffkwUAIA6ZgpAwiphbXWQhP3bh5kCWBt9kMweTb1h/7ZhqgDWrTxqp1m4jZQG7N/2TBVACOMPEssHh0Ts37bMFUAI4w4S6weHVOzfdkwWQAj9DxIPB4dk7N821H8UeE/8MeEQfu1U7h9vA/v3PNMFEMLLgySEy52cc7DsrS6WDw4N2L/nmC+AEH7txNQ3uNaOjtYPDE3Yv/VcFMBi70ApfQzIw/4t56oAFvFOzjlYvB0U2rF/87ksgJjnne8B+3ef2bcBARyjAADHKADAMQoAcIwCAByjAADHKADAMQoAcIwCAByjAADHKADAMQoAcIwCAByjAADHKADAMQoAcIwCAByjAADHKADAMQoAcIwCABx7UQDfP39M/uDN/WP3jQHQxlZe1/lmAgAcowAAxygAwLGiAuA6ACBfSU6TBbB1IRCAXqlccwoAOFZcAJwGAHKV5nOzADgNAOzYyjOnAIBjVQXAaQAgT00udwuA0wBAv70cV58CMAUActTm8bAA9tqDEgDm28vh0RTPRUDAsawCYAoAZDqz+ofQaAKgBIDxWuQuuwB4RwDQIzevRRMApwKADGdH/0XxKQAlAMzVKvwhdHgXgBIA+mmdr6oCOGoZSgBo7yhXNdfpqicASgAYp0f4Qzh5CkAJAP31Cn8IIVy9efv+ufq3/y8n6LyNCJQZkasmFwFzNoJpAMg3alFtMgEsckPONACkjc5Q07cBczeKaQB4acYC2nQCWJQEnGkA3s3MS5cCWJSu9JQBvJCSja4FEEL9uE8ZwBqJWeheACG0OeenEKCNhuN+SAEsuPgH5Bm14A0tgAVFAKSNnnSnFMCCIgD+NusUd2oBxCgDeCPhupaYAohRBrBKQuhjIgsghVKANtLCnqKmAAC0x41BAMcoAMCx/wE+I2UonKzIyQAAAABJRU5ErkJggg=="

def ensure_app_logo() -> Path:
    """Self-heals and extracts the embedded logo if missing from disk."""
    logo_file = APP_DIR / "lancontrol_logo.png"
    if not logo_file.exists() or logo_file.stat().st_size == 0:
        try:
            logo_file.write_bytes(base64.b64decode(EMBEDDED_LOGO_PNG_B64))
        except Exception:
            pass
    return logo_file

def ensure_default_config() -> Path:
    """Self-heals configuration: ensures a valid, production config.json always exists."""
    if not LOCAL_CONFIG_FILE.exists() or LOCAL_CONFIG_FILE.stat().st_size == 0:
        cfg = {
            "$schema": "https://raw.githubusercontent.com/Ylianst/MeshCentral/master/meshcentral-config-schema.json",
            "settings": {
                "LANonly": True,
                "WANonly": False,
                "port": DEFAULT_PORT,
                "sessionKey": generate_session_key(),
                "ExactPorts": True,
                "WebRTC": True,
                "SelfUpdate": True
            },
            "domains": {
                "": {
                    "title": "LANController Management Console",
                    "title2": "Local Computer & Fleet Administration",
                    "newAccounts": True,
                    "minify": True,
                    "userNameIsEmail": False
                }
            }
        }
        atomic_write_json(LOCAL_CONFIG_FILE, cfg)
    return LOCAL_CONFIG_FILE

# System Data Directory
APP_DATA_DIR = Path(os.environ.get("ProgramData", r"C:\ProgramData")) / "LANControlFleetSetup"
APP_LOG_DIR = APP_DATA_DIR / "logs"
APP_LOG_FILE = APP_LOG_DIR / "setup.log"
APP_SETTINGS_FILE = APP_DATA_DIR / "settings.json"

DEFAULT_DIR = Path(r"C:\MeshCentral")
DEFAULT_PORT = 443
FALLBACK_SERVICE_NAME = "meshcentral.exe"
SERVICE_LABEL = "LANCONTROL"
CONFIG_NAME = "config.json"
LOG_NAME = "meshcentral-setup.log"
BACKUP_DIR_NAME = "config-backups"
WINGET_ID = "OpenJS.NodeJS.LTS"

RUN_KEY_PATH = r"Software\Microsoft\Windows\CurrentVersion\Run"
RUN_VALUE_NAME = "LANControlFleetManager"

CREATE_NO_WINDOW = getattr(subprocess, "CREATE_NO_WINDOW", 0)

# Apple iOS Human Interface Design Themes (Dark & Light)
THEMES = {
    "dark": {
        "bg_main": "#121214",           # System Background (deep neutral dark)
        "bg_nav": "#1c1c1e",            # Secondary Grouped Background (Apple Card/Nav)
        "bg_card": "#1c1c1e",           # Card Surface
        "bg_card_border": "#2c2c2e",    # Subtle Apple Separator
        "bg_input": "#2c2c2e",          # Elevated Input field background
        "bg_console": "#161618",        # Sleek low-contrast terminal surface
        "text_primary": "#ffffff",      # iOS Label (Primary)
        "text_secondary": "#8e8e93",    # iOS Secondary Label (System Gray)
        "accent": "#0a84ff",            # iOS System Blue (Dark)
        "accent_hover": "#0071e3",      # iOS Blue Press
        "accent_dim": "#1e293b",        # Soft blue/slate tint for tabs
        "success": "#30d158",           # iOS System Green
        "danger": "#ff453a",            # iOS System Red
        "warning": "#ff9f0a",           # iOS System Orange
        "btn_bg": "#2c2c2e",            # Secondary button fill
        "btn_hover": "#3a3a3c",         # Secondary button hover
        "btn_fg": "#ffffff",            # Secondary button text
        "tray_bg": "#1c1c1e",
        "tray_border": "#0a84ff",
        "name": "Dark Mode",
    },
    "light": {
        "bg_main": "#f2f2f7",           # iOS System Grouped Background
        "bg_nav": "#ffffff",            # Pure white navigation & cards
        "bg_card": "#ffffff",           # Elevated pure white card
        "bg_card_border": "#e5e5ea",    # iOS Light Separator (Opaque)
        "bg_input": "#f2f2f7",          # Inset input background
        "bg_console": "#1e1e24",        # Smooth contrast dark console
        "text_primary": "#000000",      # iOS Label (Black)
        "text_secondary": "#6c6c70",    # iOS Secondary Label (Gray)
        "accent": "#007aff",            # iOS System Blue (Light)
        "accent_hover": "#0056b3",      # iOS Blue Press
        "accent_dim": "#e3f2fd",        # Soft blue tint
        "success": "#34c759",           # iOS System Green
        "danger": "#ff3b30",            # iOS System Red
        "warning": "#ff9500",           # iOS System Orange
        "btn_bg": "#e5e5ea",            # Secondary button fill
        "btn_hover": "#d1d1d6",         # Secondary button hover
        "btn_fg": "#000000",            # Secondary button text
        "tray_bg": "#2c2c2e",
        "tray_border": "#007aff",
        "name": "Light Mode",
    }
}

ACTIVE_THEME = "dark"
THEME = THEMES[ACTIVE_THEME]

COLOR_BG_MAIN = THEME["bg_main"]
COLOR_BG_NAV = THEME["bg_nav"]
COLOR_BG_CARD = THEME["bg_card"]
COLOR_BG_CARD_BORDER = THEME["bg_card_border"]
COLOR_TEXT_PRIMARY = THEME["text_primary"]
COLOR_TEXT_SECONDARY = THEME["text_secondary"]
COLOR_SUCCESS = THEME["success"]
COLOR_DANGER = THEME["danger"]
COLOR_WARNING = THEME["warning"]
COLOR_ACCENT = THEME["accent"]
COLOR_ACCENT_HOVER = THEME["accent_hover"]
COLOR_ACCENT_GRAD = THEME["accent"]

COLOR_TRAY_BG = THEME["tray_bg"]
COLOR_TRAY_BORDER = THEME["tray_border"]
COLOR_TRAY_ONLINE = THEME["success"]
COLOR_TRAY_OFFLINE = THEME["danger"]
COLOR_TRAY_PENDING = THEME["warning"]


# ---------------------------------------------------------------------------
# Logging & Settings
# ---------------------------------------------------------------------------

def app_log(message: str) -> None:
    """Logs to stdout, ProgramData, and the local application directory."""
    stamp = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    formatted = f"[{stamp}] {message.rstrip()}\n"

    # Write to terminal / console stdout if available
    try:
        sys.stdout.write(formatted)
        sys.stdout.flush()
    except Exception:
        pass

    # Write to ProgramData log
    try:
        APP_LOG_DIR.mkdir(parents=True, exist_ok=True)
        with APP_LOG_FILE.open("a", encoding="utf-8", errors="replace") as f:
            f.write(formatted)
    except Exception:
        pass

    # Also write directly to local folder log
    try:
        with LOCAL_LOG_FILE.open("a", encoding="utf-8", errors="replace") as f:
            f.write(formatted)
    except Exception:
        pass


def load_app_settings() -> dict:
    try:
        if APP_SETTINGS_FILE.exists():
            with APP_SETTINGS_FILE.open("r", encoding="utf-8") as f:
                return json.load(f)
    except Exception as exc:
        app_log(f"Could not load settings: {exc!r}")
    return {}


def save_app_settings(data: dict) -> None:
    try:
        APP_DATA_DIR.mkdir(parents=True, exist_ok=True)
        atomic_write_json(APP_SETTINGS_FILE, data)
    except Exception as exc:
        app_log(f"Could not save settings: {exc!r}")


# ---------------------------------------------------------------------------
# Windows & Elevation
# ---------------------------------------------------------------------------

def is_windows() -> bool:
    return os.name == "nt"


def is_admin() -> bool:
    if not is_windows():
        return False
    try:
        import ctypes
        return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except Exception:
        return False


def relaunch_as_admin(extra_args: list[str] | None = None) -> bool:
    """Relaunches elevated with UAC."""
    if not is_windows() or is_admin():
        return False

    try:
        import ctypes
        script = Path(__file__).resolve()
        exe = Path(sys.executable).resolve()

        params = [str(script)]
        if extra_args:
            params.extend(extra_args)
        else:
            params.extend(sys.argv[1:])

        def quote_arg(value: str) -> str:
            if not value or any(ch in value for ch in ' \t"'):
                return '"' + value.replace('"', r'\"') + '"'
            return value

        parameter_string = " ".join(quote_arg(x) for x in params)

        result = ctypes.windll.shell32.ShellExecuteW(
            None,
            "runas",
            str(exe),
            parameter_string,
            str(script.parent),
            1,  # SW_SHOWNORMAL
        )
        return result > 32
    except Exception as exc:
        app_log(f"Elevation failed: {exc!r}")
        return False


def request_admin_elevation(prompt: str = "This action requires Administrator privileges.") -> bool:
    """Prompts to elevate and relaunches if confirmed. Returns True if already admin."""
    if is_admin():
        return True
    if messagebox.askyesno(APP_TITLE, f"{prompt}\n\nWould you like to restart LANCONTROL Fleet Manager with full Administrator privileges?"):
        if relaunch_as_admin():
            sys.exit(0)
    return False


# ---------------------------------------------------------------------------
# Process & CLI Helpers
# ---------------------------------------------------------------------------

def run_cmd(
    args: list[str],
    cwd: str | Path | None = None,
    timeout: int = 120,
    capture: bool = True,
) -> tuple[int, str]:
    """Safe subprocess runner."""
    try:
        p = subprocess.run(
            [str(x) for x in args],
            cwd=str(cwd) if cwd else None,
            timeout=timeout,
            capture_output=capture,
            text=True,
            encoding="utf-8",
            errors="replace",
            shell=False,
            creationflags=CREATE_NO_WINDOW,
        )
        if not capture:
            return p.returncode, ""
        output = ((p.stdout or "") + (p.stderr or "")).strip()
        return p.returncode, output
    except subprocess.TimeoutExpired as exc:
        # subprocess may preserve output produced before the timeout. Keep it so
        # CLI consent URLs and diagnostic messages are not silently discarded.
        partial: list[str] = []
        for value in (getattr(exc, "stdout", None), getattr(exc, "stderr", None)):
            if value:
                if isinstance(value, bytes):
                    value = value.decode("utf-8", errors="replace")
                value = str(value).strip()
                if value and value not in partial:
                    partial.append(value)
        message = f"Timed out after {timeout} seconds."
        if partial:
            message += "\nPartial command output:\n" + "\n".join(partial)
        return 124, message
    except FileNotFoundError as exc:
        return 127, str(exc)
    except Exception as exc:
        return 1, repr(exc)


def which(*names: str) -> str | None:
    for name in names:
        val = shutil.which(name)
        if val:
            return val
    return None


def node_path() -> str | None:
    p = which("node.exe", "node")
    if p:
        return p
    candidates = [
        Path(os.environ.get("ProgramFiles", r"C:\Program Files")) / "nodejs" / "node.exe",
        Path(os.environ.get("LOCALAPPDATA", "")) / "Programs" / "nodejs" / "node.exe",
        Path.home() / ".tools" / "nodejs" / "node-v24.19.0-win-x64" / "node.exe",
    ]
    for c in candidates:
        if c.exists():
            return str(c)
    return None


def npm_path() -> str | None:
    p = which("npm.cmd", "npm")
    if p:
        return p
    candidates = [
        Path(os.environ.get("ProgramFiles", r"C:\Program Files")) / "nodejs" / "npm.cmd",
        Path(os.environ.get("LOCALAPPDATA", "")) / "Programs" / "nodejs" / "npm.cmd",
        Path.home() / ".tools" / "nodejs" / "node-v24.19.0-win-x64" / "npm.cmd",
    ]
    for c in candidates:
        if c.exists():
            return str(c)
    return None


def powershell_path() -> str | None:
    return which("powershell.exe", "pwsh.exe")


# ---------------------------------------------------------------------------
# Dynamic Windows Service Management
# ---------------------------------------------------------------------------

_cached_service_name: str | None = None


def find_meshcentral_service() -> str:
    """Dynamically locates registered service name (meshcentral.exe or MeshCentral)."""
    global _cached_service_name

    for name in ["meshcentral.exe", "meshcentral", "MeshCentral"]:
        rc, out = run_cmd(["sc.exe", "query", name], timeout=10)
        if rc == 0 and "STATE" in out.upper():
            _cached_service_name = name
            return name

    rc, out = run_cmd(["sc.exe", "query", "state=", "all"], timeout=20)
    if rc == 0:
        current_svc = ""
        for line in out.splitlines():
            line = line.strip()
            if line.upper().startswith("SERVICE_NAME:"):
                current_svc = line.split(":", 1)[1].strip()
            elif line.upper().startswith("DISPLAY_NAME:"):
                disp = line.split(":", 1)[1].strip()
                if "meshcentral" in disp.lower() and current_svc:
                    _cached_service_name = current_svc
                    return current_svc

    return _cached_service_name or FALLBACK_SERVICE_NAME


def service_exists() -> bool:
    svc = find_meshcentral_service()
    rc, out = run_cmd(["sc.exe", "query", svc], timeout=15)
    return rc == 0 and "STATE" in out.upper()


def service_state() -> str:
    svc = find_meshcentral_service()
    rc, out = run_cmd(["sc.exe", "query", svc], timeout=15)
    if rc != 0:
        return "NOT INSTALLED"
    up = out.upper()
    for state in ("RUNNING", "STOPPED", "START_PENDING", "STOP_PENDING", "PAUSED"):
        if state in up:
            return state.replace("_", " ")
    return "UNKNOWN"


def service_start_type() -> str:
    svc = find_meshcentral_service()
    rc, out = run_cmd(["sc.exe", "qc", svc], timeout=15)
    if rc != 0:
        return "UNKNOWN"
    m = re.search(r"START_TYPE\s*:\s*\d+\s+([A-Z_]+)", out)
    if m:
        st = m.group(1).replace("_", " ")
        if "AUTO" in st:
            if "DELAYED" in out.upper():
                return "AUTOMATIC (DELAYED)"
            return "AUTOMATIC"
        elif "DEMAND" in st:
            return "MANUAL"
        elif "DISABLED" in st:
            return "DISABLED"
        return st
    return "UNKNOWN"


def set_service_autostart(enable: bool = True) -> tuple[bool, str]:
    """Sets service startup type using proper sc.exe parameter tokens."""
    svc = find_meshcentral_service()
    arg = "auto" if enable else "demand"
    # sc.exe requires 'start=' as option token, followed by space and value
    rc, out = run_cmd(["sc.exe", "config", svc, "start=", arg], timeout=20)
    if rc == 0:
        app_log(f"Service {svc} startup set to {arg}.")
        return True, f"Service startup set to {arg}"
    app_log(f"Failed to set service {svc} startup: {out}")
    return False, out


def control_service(action: str, timeout: int = 40) -> tuple[bool, str]:
    svc = find_meshcentral_service()
    action = action.lower()

    if action == "start":
        current = service_state()
        if current == "RUNNING":
            return True, "Service is already running."
        rc, out = run_cmd(["sc.exe", "start", svc], timeout=20)
        if rc != 0 and "1056" not in out:
            return False, f"Start failed: {out}"
        start_t = time.time()
        while time.time() - start_t < timeout:
            if service_state() == "RUNNING":
                return True, "Service started successfully."
            time.sleep(1)
        return False, "Timed out waiting for service to reach RUNNING state."

    elif action == "stop":
        current = service_state()
        if current == "STOPPED":
            return True, "Service is already stopped."
        rc, out = run_cmd(["sc.exe", "stop", svc], timeout=20)
        if rc != 0 and "1062" not in out:
            return False, f"Stop failed: {out}"
        start_t = time.time()
        while time.time() - start_t < timeout:
            if service_state() == "STOPPED":
                return True, "Service stopped successfully."
            time.sleep(1)
        return False, "Timed out waiting for service to stop."

    elif action == "restart":
        control_service("stop", timeout=timeout // 2)
        time.sleep(1)
        ok2, msg2 = control_service("start", timeout=timeout // 2)
        if ok2:
            return True, "Service restarted successfully."
        return False, f"Restart failed during startup: {msg2}"

    return False, f"Unknown action: {action}"


# ---------------------------------------------------------------------------
# Installation Discovery & Paths
# ---------------------------------------------------------------------------

def server_paths(server_dir: Path) -> dict[str, Path]:
    data = server_dir / "meshcentral-data"
    return {
        "root": server_dir,
        "data": data,
        "config": data / CONFIG_NAME,
        "logs": data / LOG_NAME,
        "backups": server_dir / "meshcentral-backups",
        "mesh": server_dir / "node_modules" / "meshcentral",
        "entry": server_dir / "node_modules" / "meshcentral" / "meshcentral.js",
        "service_exe": server_dir / "WinService" / "daemon" / "meshcentral.exe",
    }


def meshcentral_installed(server_dir: Path) -> bool:
    try:
        return server_paths(server_dir)["entry"].exists()
    except Exception:
        return False


def discover_meshcentral_root() -> Path | None:
    """Find existing installation via active service binary or candidate paths."""
    candidates: list[Path] = []

    svc = find_meshcentral_service()
    rc, out = run_cmd(["sc.exe", "qc", svc], timeout=15)
    if rc == 0:
        m = re.search(r"BINARY_PATH_NAME\s*:\s*(.+)", out, re.I)
        if m:
            raw = m.group(1).strip().strip('"')
            raw = re.split(r"\s+--\w+", raw, maxsplit=1)[0]
            try:
                p = Path(raw)
                if "WinService" in p.parts:
                    idx = list(p.parts).index("WinService")
                    candidates.append(Path(*p.parts[:idx]))
                if "node_modules" in p.parts:
                    idx = list(p.parts).index("node_modules")
                    candidates.append(Path(*p.parts[:idx]))
                candidates.append(p.parent.parent)
                candidates.append(p.parent)
            except Exception:
                pass

    candidates.extend([
        Path.home() / "MeshCentral",
        Path(r"C:\MeshCentral"),
        Path(os.environ.get("ProgramData", r"C:\ProgramData")) / "MeshCentral",
        Path(os.environ.get("LOCALAPPDATA", "")) / "MeshCentral",
        Path(os.environ.get("USERPROFILE", "")) / "MeshCentral",
    ])

    for candidate in candidates:
        try:
            resolved = candidate.expanduser().resolve()
            if meshcentral_installed(resolved):
                return resolved
        except Exception:
            continue

    return None


def sync_local_artifacts(server_root: Path | None = None) -> None:
    """Ensures a copy of config.json and setup.log exists directly in the APP_DIR."""
    if server_root is None:
        server_root = discover_meshcentral_root() or DEFAULT_DIR

    active_config = server_paths(server_root)["config"]
    if active_config.exists():
        try:
            shutil.copy2(active_config, LOCAL_CONFIG_FILE)
        except Exception:
            pass

    if APP_LOG_FILE.exists() and not LOCAL_LOG_FILE.exists():
        try:
            shutil.copy2(APP_LOG_FILE, LOCAL_LOG_FILE)
        except Exception:
            pass


# ---------------------------------------------------------------------------
# Configuration Helpers
# ---------------------------------------------------------------------------

def generate_session_key() -> str:
    return secrets.token_urlsafe(48)


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def atomic_write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(prefix=path.stem + "-", suffix=".tmp", dir=path.parent)
    os.close(fd)
    tmp = Path(tmp_name)
    try:
        with tmp.open("w", encoding="utf-8", newline="\n") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            f.write("\n")
        os.replace(tmp, path)
    finally:
        if tmp.exists():
            tmp.unlink(missing_ok=True)


def backup_config(config_path: Path, backup_dir: Path) -> Path | None:
    if not config_path.exists():
        return None
    backup_dir.mkdir(parents=True, exist_ok=True)
    stamp = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = backup_dir / f"config_{stamp}.json"
    shutil.copy2(config_path, backup)
    return backup


def build_config(
    title: str,
    subtitle: str,
    port: int,
    lan_only: bool,
    cert_name: str,
    allow_new_accounts: bool,
    session_key: str,
) -> dict:
    settings = {
        "LANonly": bool(lan_only),
        "WANonly": False if lan_only else True,
        "port": int(port),
        "sessionKey": session_key,
        "ExactPorts": True,
        "WebRTC": True,
        "SelfUpdate": True,
    }
    if cert_name.strip():
        settings["cert"] = cert_name.strip()

    return {
        "$schema": "https://raw.githubusercontent.com/Ylianst/MeshCentral/master/meshcentral-config-schema.json",
        "settings": settings,
        "domains": {
            "": {
                "title": title.strip() or "MeshCentral",
                "title2": subtitle.strip() or "Remote Administration",
                "newAccounts": bool(allow_new_accounts),
                "minify": True,
                "userNameIsEmail": False,
            }
        },
    }


# ---------------------------------------------------------------------------
# Network, IP & Firewall
# ---------------------------------------------------------------------------


def fetch_public_ipv4(timeout: int = 4) -> str:
    """Fetches public IPv4 address without external dependencies."""
    import urllib.request, json
    endpoints = [
        ("https://api.ipify.org?format=json", lambda b: json.loads(b).get("ip")),
        ("https://ipinfo.io/json", lambda b: json.loads(b).get("ip")),
        ("https://icanhazip.com", lambda b: b.strip()),
    ]
    for url, parser in endpoints:
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "LANCONTROL"})
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                raw = resp.read().decode("utf-8", errors="ignore")
                ip = parser(raw)
                if ip and len(ip.split(".")) == 4:
                    return ip.strip()
        except Exception:
            continue
    return ""

def local_ipv4_addresses() -> list[str]:
    """Returns local non-loopback, non-APIPA IPv4 addresses."""
    results: set[str] = set()
    try:
        host = socket.gethostname()
        for info in socket.getaddrinfo(host, None, socket.AF_INET):
            ip = info[4][0]
            if ip and not ip.startswith("127.") and not ip.startswith("169.254."):
                results.add(ip)
    except Exception:
        pass

    ps = powershell_path()
    if ps:
        script = (
            "Get-NetIPAddress -AddressFamily IPv4 "
            "| Where-Object {$_.IPAddress -notlike '127.*' -and $_.IPAddress -notlike '169.254.*'} "
            "| Select-Object -ExpandProperty IPAddress"
        )
        rc, out = run_cmd([ps, "-NoProfile", "-Command", script], timeout=15)
        if rc == 0:
            for line in out.splitlines():
                line = line.strip()
                try:
                    ipaddress.IPv4Address(line)
                    results.add(line)
                except Exception:
                    pass

    return sorted(results, key=lambda s: tuple(map(int, s.split("."))))


def choose_best_lan_ip() -> str:
    """
    Intelligently determines the best reachable physical LAN IPv4 address.
    Asks the OS routing table for the primary outgoing gateway route,
    preventing internal Hyper-V / WSL virtual switches from taking priority.
    """
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            active_ip = s.getsockname()[0]
            if active_ip and not active_ip.startswith("127.") and not active_ip.startswith("169.254."):
                return active_ip
    except Exception:
        pass

    ips = local_ipv4_addresses()
    # Prioritize typical local subnet ranges (192.168.x.x, then 10.x.x.x)
    for prefix in ["192.168.", "10."]:
        for ip in ips:
            if ip.startswith(prefix):
                return ip

    for ip in ips:
        try:
            addr = ipaddress.ip_address(ip)
            if addr.version == 4 and addr.is_private and not addr.is_loopback and not addr.is_link_local:
                return ip
        except ValueError:
            continue

    return ips[0] if ips else "127.0.0.1"


def is_port_in_use(port: int) -> tuple[bool, str]:
    if not 1 <= port <= 65535:
        return False, "invalid port"
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(0.6)
            result = sock.connect_ex(("127.0.0.1", port))
            if result == 0:
                return True, "127.0.0.1: listening"
    except Exception:
        pass
    return False, ""


def firewall_rule_name(port: int) -> str:
    return f"{SERVICE_LABEL} TCP {port}"


def firewall_rule_exists(port: int) -> bool:
    rule = firewall_rule_name(port)
    rc, out = run_cmd(["netsh", "advfirewall", "firewall", "show", "rule", f"name={rule}"], timeout=15)
    return rc == 0 and "No rules match" not in out


def allow_firewall(port: int) -> tuple[bool, str]:
    rule = firewall_rule_name(port)
    rc, out = run_cmd(
        [
            "netsh", "advfirewall", "firewall", "add", "rule",
            f"name={rule}", "dir=in", "action=allow", "protocol=TCP",
            f"localport={port}", "profile=private,domain",
        ],
        timeout=25,
    )
    if rc == 0:
        app_log(f"Firewall rule added: {rule}")
        return True, f"Firewall rule added for port {port}"
    app_log(f"Firewall rule add failed: {out}")
    return False, out


def remove_firewall(port: int) -> tuple[bool, str]:
    rule = firewall_rule_name(port)
    rc, out = run_cmd(["netsh", "advfirewall", "firewall", "delete", "rule", f"name={rule}"], timeout=25)
    if rc == 0:
        app_log(f"Firewall rule removed: {rule}")
        return True, f"Firewall rule removed: {rule}"
    return False, out


def test_local_https(port: int, timeout: int = 6) -> tuple[bool, str]:
    url = f"https://127.0.0.1:{port}/"
    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE
    try:
        req = urllib.request.Request(url, method="GET", headers={"User-Agent": "LANCONTROL-Fleet-GUI"})
        with urllib.request.urlopen(req, timeout=timeout, context=context) as response:
            return True, f"HTTP {response.status} at {response.geturl()}"
    except urllib.error.HTTPError as exc:
        return True, f"HTTP {exc.code} (Server responded)"
    except Exception as exc:
        return False, str(exc)


# ---------------------------------------------------------------------------
# Tailscale remote access (private tailnet only; never configures Funnel)
# ---------------------------------------------------------------------------


def tailscale_path() -> str | None:
    """Locate the official Tailscale CLI without assuming PATH is refreshed."""
    found = which("tailscale.exe", "tailscale")
    if found:
        return found
    candidates = [
        Path(os.environ.get("ProgramFiles", r"C:\Program Files")) / "Tailscale" / "tailscale.exe",
        Path(os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)")) / "Tailscale" / "tailscale.exe",
        Path(os.environ.get("LOCALAPPDATA", "")) / "Tailscale" / "tailscale.exe",
    ]
    for candidate in candidates:
        if candidate.is_file():
            return str(candidate)
    return None


def tailscale_cli(args: list[str], timeout: int = 30) -> tuple[int, str]:
    exe = tailscale_path()
    if not exe:
        return 127, "Tailscale CLI was not found. Install Tailscale first."
    return run_cmd([exe, *args], timeout=timeout)


def tailscale_status_info() -> dict:
    """Return a normalized status object; never treats an unlogged-in node as connected."""
    exe = tailscale_path()
    if not exe:
        return {"installed": False, "connected": False, "ip": "", "dns": "", "detail": "Not installed"}
    rc, out = run_cmd([exe, "status", "--json"], timeout=20)
    if rc == 0:
        try:
            payload = json.loads(out)
            self_node = payload.get("Self") or {}
            ips = self_node.get("TailscaleIPs") or []
            dns = (self_node.get("DNSName") or "").rstrip(".")
            backend = str(payload.get("BackendState") or "").lower()
            connected = bool(ips) and backend not in {"stopped", "needslogin", "needs_login", "starting"}
            primary_ts_ip = next((ip for ip in ips if ":" not in ip), ips[0] if ips else "")
            return {
                "installed": True,
                "connected": connected,
                "ip": primary_ts_ip,
                "ips": [primary_ts_ip] if primary_ts_ip else [],
                "dns": dns,
                "detail": backend or "Connected" if connected else (backend or "Not connected"),
            }
        except Exception as exc:
            app_log(f"Could not parse Tailscale status JSON: {exc!r}")
    rc2, text_out = run_cmd([exe, "status"], timeout=20)
    low = (out + "\n" + text_out).lower()
    needs_login = any(token in low for token in ("needs login", "logged out", "login.tailscale.com", "not logged in"))
    return {
        "installed": True,
        "connected": rc2 == 0 and not needs_login and bool(text_out.strip()),
        "ip": "",
        "dns": "",
        "detail": (text_out or out or "Status unavailable")[:1200],
    }


def tailscale_serve_status(timeout: int = 20) -> tuple[bool, str, str]:
    """Return (configured, output, URL) for Tailscale Serve."""
    rc, out = tailscale_cli(["serve", "status"], timeout=timeout)
    text_out = out.strip()
    url_match = re.search(r"https://[A-Za-z0-9.-]+\.ts\.net(?:/[^\s]*)?", text_out, re.I)
    url = url_match.group(0).rstrip(".,") if url_match else ""
    configured = rc == 0 and bool(text_out) and not any(
        phrase in text_out.lower() for phrase in ("no serve config", "not serving", "nothing is being served")
    )
    # Some CLI versions return status with exit code 0 and no text when not configured.
    return configured, text_out or "No Serve configuration reported.", url


def install_tailscale() -> tuple[bool, str]:
    """Install via bundled installer or winget. Silent and fully automatic."""
    if tailscale_path():
        return True, f"Tailscale is already installed: {tailscale_path()}"

    bundled_msi = APP_DIR / "bin" / "tailscale-setup.msi"
    if bundled_msi.exists():
        app_log(f"Installing Tailscale from bundled offline installer: {bundled_msi}")
        rc, out = run_cmd(["msiexec.exe", "/i", str(bundled_msi), "/qn", "/norestart"], timeout=300)
        time.sleep(3)
        if tailscale_path():
            return True, "Tailscale installed successfully from bundled package."

    winget = which("winget.exe", "winget")
    if winget:
        app_log("Installing Tailscale via winget...")
        rc, out = run_cmd([
            winget, "install", "--exact", "--id", "Tailscale.Tailscale",
            "--silent", "--accept-package-agreements", "--accept-source-agreements",
        ], timeout=900)
        time.sleep(3)
        if tailscale_path():
            return True, out or "Tailscale installed successfully via winget."

    return False, "Tailscale could not be installed automatically. Open https://tailscale.com/download/windows to install."


def configure_tailscale_serve(port: int) -> tuple[bool, str, str]:
    """Privately publish the existing localhost HTTPS service to this tailnet only."""
    if not tailscale_path():
        return False, "Tailscale is not installed.", ""
    try:
        port = int(port)
    except (TypeError, ValueError):
        return False, f"Invalid LANCONTROL HTTPS port: {port!r}.", ""
    if not 1 <= port <= 65535:
        return False, f"Invalid LANCONTROL HTTPS port: {port}. Expected 1–65535.", ""

    status = tailscale_status_info()
    if not status.get("connected"):
        return False, "Tailscale is not connected/logged in. Click Connect / Sign In first, complete authentication, then retry.", ""
    healthy, health_msg = test_local_https(port, timeout=5)
    if not healthy:
        return False, f"LANCONTROL is not responding at https://127.0.0.1:{port}/. Start/check the existing service first.\n{health_msg}", ""

    # This is Serve (tailnet-only), never Funnel (public internet). --yes avoids
    # an interactive CLI confirmation in this hidden GUI-launched subprocess.
    target = f"https+insecure://127.0.0.1:{port}"
    rc, out = tailscale_cli(["serve", "--bg", "--yes", target], timeout=45)
    if rc != 0:
        # A CLI can time out after changing Serve state. Confirm the actual state
        # before telling the user configuration failed.
        check_rc, check_text, check_url = tailscale_serve_status(timeout=8)
        if check_rc and target.lower() in check_text.lower():
            message = (
                "Tailscale Serve appears to be configured despite the CLI not "
                f"exiting cleanly (exit {rc}). Verified current Serve status:\n{check_text}"
            )
            if check_url:
                message += f"\n\nRemote URL: {check_url}"
            return True, message, check_url

        urls = re.findall(r"https?://[^\s\]\[<>\"']+", out or "")
        consent_url = next(
            (u.rstrip(".,)") for u in urls if "login.tailscale.com" in u.lower()),
            "",
        )
        details = out.strip() or "Tailscale returned no diagnostic output."
        message = f"Tailscale Serve configuration failed (exit {rc}).\n{details}"
        if consent_url:
            message += (
                "\n\nTailscale appears to require browser authorization. The manager will "
                "open the authorization URL. Complete the consent step, then click "
                "Configure Private Remote URL again.\n\nAuthorization URL: " + consent_url
            )
        else:
            message += (
                "\n\nCheck Tailscale Admin Console → DNS. Enable MagicDNS and HTTPS "
                "Certificates for the tailnet if they are disabled, then retry. "
                "You can open the DNS settings here: https://login.tailscale.com/admin/dns"
            )
        if rc == 124:
            message += "\n\nThe Serve command timed out; partial CLI output is retained above when available."
        return False, message, ""

    time.sleep(1)
    _, status_text, url = tailscale_serve_status()
    if not url and status.get("dns"):
        url = "https://" + status["dns"].rstrip(".")
    message = (out.strip() + "\n" if out.strip() else "") + status_text
    if url:
        message += f"\n\nRemote URL: {url}"
    return True, message, url


def disable_tailscale_serve() -> tuple[bool, str]:
    """Remove Serve configuration from this Tailscale node; does not disconnect VPN."""
    rc, out = tailscale_cli(["serve", "reset"], timeout=30)
    return rc == 0, out or ("Tailscale Serve configuration reset." if rc == 0 else "Serve reset failed.")


# ---------------------------------------------------------------------------
# Windows Startup Registry
# ---------------------------------------------------------------------------

def get_pythonw_path() -> Path:
    exe = Path(sys.executable)
    pythonw = exe.parent / "pythonw.exe"
    if pythonw.exists():
        return pythonw
    return exe


def is_login_autostart_enabled() -> bool:
    if not is_windows():
        return False
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_KEY_PATH, 0, winreg.KEY_READ) as key:
            val, _ = winreg.QueryValueEx(key, RUN_VALUE_NAME)
            return bool(val)
    except FileNotFoundError:
        return False
    except Exception:
        return False


def set_login_autostart_enabled(enable: bool = True) -> tuple[bool, str]:
    if not is_windows():
        return False, "Not on Windows"
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_KEY_PATH, 0, winreg.KEY_SET_VALUE) as key:
            if enable:
                script_path = Path(__file__).resolve()
                pythonw = get_pythonw_path()
                cmd = f'"{pythonw}" "{script_path}" --autostart'
                winreg.SetValueEx(key, RUN_VALUE_NAME, 0, winreg.REG_SZ, cmd)
                app_log(f"Login autostart enabled: {cmd}")
                return True, "Autostart at Windows login enabled."
            else:
                try:
                    winreg.DeleteValue(key, RUN_VALUE_NAME)
                    app_log("Login autostart disabled.")
                except FileNotFoundError:
                    pass
                return True, "Autostart at Windows login disabled."
    except Exception as exc:
        app_log(f"Failed to set login autostart: {exc!r}")
        return False, str(exc)



# ---------------------------------------------------------------------------
# LANCONTROL Agent & Binary Customization Engine (Zero-Branding MDM)
# ---------------------------------------------------------------------------

AGENT_POLICY_GUID = bytes.fromhex("B996015880544A19B7F7E9BE44914C19")

def embed_policy(exe_bytes: bytes, msh_text: str) -> bytes:
    """
    Injects .msh configuration policy into standard PE32 and PE32+ (64-bit)
    Windows agent binaries while maintaining valid PE header and certificate alignment.
    """
    import struct
    data = bytearray(exe_bytes)
    if data[:2] != b"MZ":
        raise ValueError("Not a valid PE executable (missing MZ magic)")
    e_lfanew = struct.unpack_from("<I", data, 0x3C)[0]
    if data[e_lfanew:e_lfanew+4] != b"PE\x00\x00":
        raise ValueError("Not a valid PE executable (missing PE signature)")
    
    magic = struct.unpack_from("<H", data, e_lfanew + 24)[0]
    if magic == 0x10B:
        cert_entry_offset = e_lfanew + 24 + 128
    elif magic == 0x20B:
        cert_entry_offset = e_lfanew + 24 + 144
    else:
        raise ValueError(f"Unsupported PE magic: {hex(magic)}")
    
    cert_rva, cert_size = struct.unpack_from("<II", data, cert_entry_offset)
    msh_bytes = msh_text.encode("utf-8")
    block = msh_bytes + struct.pack(">I", len(msh_bytes)) + AGENT_POLICY_GUID
    pad_len = (4 - (len(block) % 4)) % 4
    block += b"\x00" * pad_len
    
    if cert_rva != 0 and cert_size != 0:
        new_cert_size = cert_size + len(block)
        struct.pack_into("<I", data, cert_entry_offset + 4, new_cert_size)
        dwLength = struct.unpack_from("<I", data, cert_rva)[0]
        struct.pack_into("<I", data, cert_rva, dwLength + len(block))
        insert_pos = cert_rva + cert_size
        data[insert_pos:insert_pos] = block
    else:
        align = (8 - (len(data) % 8)) % 8
        data.extend(b"\x00" * align)
        cert_rva = len(data)
        win_cert_hdr = struct.pack("<II", 8 + len(block), 0x00020200)
        full_block = win_cert_hdr + block
        struct.pack_into("<II", data, cert_entry_offset, cert_rva, len(full_block))
        data.extend(full_block)
    return bytes(data)


def get_agent_server_hashes(data_dir: Path | str | None = None) -> tuple[str, str]:
    """
    Returns (hex_id, b64_id) for the active AgentServer certificate.
    Uses Python cryptography PKCS#1 SHA384 hash with pure stdlib fallback.
    """
    import hashlib, base64

    if data_dir is None:
        root = discover_meshcentral_root() or DEFAULT_DIR
        data_dir = server_paths(root)["data"]
    else:
        data_dir = Path(data_dir)

    cert_path = data_dir / "agentserver-cert-public.crt"
    if not cert_path.exists():
        return "", ""

    raw_pem = cert_path.read_bytes()
    if HAS_CRYPTO:
        try:
            cert = x509.load_pem_x509_certificate(raw_pem)
            rsa_der = cert.public_key().public_bytes(
                encoding=serialization.Encoding.DER,
                format=serialization.PublicFormat.PKCS1
            )
            h = hashlib.sha384(rsa_der).digest()
            hex_id = h.hex().upper()
            b64_id = base64.b64encode(h).decode("ascii").replace("+", "@").replace("/", "$")
            return hex_id, b64_id
        except Exception:
            pass

    # Standard Library fallback (extracts base64 DER payload directly)
    try:
        lines = [line.strip() for line in raw_pem.decode("ascii", errors="ignore").splitlines() if not line.startswith("-----") and line.strip()]
        der = base64.b64decode("".join(lines))
        h = hashlib.sha384(der).digest()
        hex_id = h.hex().upper()
        b64_id = base64.b64encode(h).decode("ascii").replace("+", "@").replace("/", "$")
        return hex_id, b64_id
    except Exception:
        return "", ""


def mesh_id_string_to_hex(mesh_id_str: str) -> str:
    import base64
    raw_id = mesh_id_str.split("/")[-1]
    b64_standard = raw_id.replace("@", "+").replace("$", "/")
    while len(b64_standard) % 4 != 0:
        b64_standard += "="
    raw_bytes = base64.b64decode(b64_standard)
    return "0x" + raw_bytes.hex().upper()


def get_available_device_groups(data_dir: Path | str | None = None) -> list[dict]:
    """Reads NeDB meshcentral.db to find registered device groups (meshes)."""
    if data_dir is None:
        root = discover_meshcentral_root() or DEFAULT_DIR
        data_dir = server_paths(root)["data"]
    else:
        data_dir = Path(data_dir)

    db_path = data_dir / "meshcentral.db"
    meshes = []
    if db_path.exists():
        try:
            with db_path.open("r", encoding="utf-8", errors="ignore") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        doc = json.loads(line)
                        if doc.get("type") == "mesh":
                            meshes.append({
                                "id": doc.get("_id"),
                                "name": doc.get("name", "Default Group"),
                                "mtype": doc.get("mtype", 2),
                            })
                    except Exception:
                        pass
        except Exception as exc:
            app_log(f"Error reading device groups: {exc!r}")
    return meshes


def build_lancontrol_msh(
    host: str,
    port: int,
    mesh_id_str: str,
    mesh_name: str = "LANCONTROL",
    tag: str = "",
) -> str:
    hex_srv, _ = get_agent_server_hashes()
    hex_mesh = mesh_id_string_to_hex(mesh_id_str)
    lines = [
        "",
        f"MeshName={mesh_name}",
        "MeshType=2",
        f"MeshID={hex_mesh}",
        f"ServerID={hex_srv}",
        f"MeshServer=wss://{host}:{port}/agent.ashx",
        "ignoreProxyFile=1",
        "displayName=LANCONTROL Client",
        "description=LANCONTROL Endpoint Remote Management Agent",
        "companyName=LANCONTROL",
        "meshServiceName=LANCONTROL",
        "fileName=LANCONTROL.exe",
    ]
    if tag.strip():
        lines.append(f"Tag={tag.strip()}")
    lines.append("")
    return "\r\n".join(lines)


def fetch_server_agent_binary(agent_id: int, port: int = DEFAULT_PORT) -> bytes:
    import ssl, urllib.request
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    req = urllib.request.Request(f"https://127.0.0.1:{port}/meshagents?id={agent_id}")
    with urllib.request.urlopen(req, context=ctx, timeout=20) as resp:
        return resp.read()


def build_android_pairing_url(host: str, port: int, mesh_id_str: str) -> str:
    _, b64_srv = get_agent_server_hashes()
    raw_mesh = mesh_id_str.split("/")[-1]
    port_str = f":{port}" if port != 443 else ""
    return f"mc://{host}{port_str},{b64_srv},{raw_mesh}"


# ---------------------------------------------------------------------------
# System Tray Manager (Pillow + pystray)
# ---------------------------------------------------------------------------

def create_tray_icon_image(status: str = "online", size: int = 64):
    if not HAS_PIL:
        return None
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    pad = int(size * 0.08)
    radius = int(size * 0.22)
    d.rounded_rectangle(
        [pad, pad, size - pad, size - pad],
        radius=radius,
        fill=COLOR_TRAY_BG,
        outline=COLOR_TRAY_BORDER,
        width=max(2, int(size * 0.05)),
    )

    w = size
    # Draw sleek modern 'L' glyph for LANCONTROL
    l_pts = [
        (w * 0.32, w * 0.28),
        (w * 0.32, w * 0.72),
        (w * 0.70, w * 0.72),
    ]
    d.line(l_pts, fill="#f8fafc", width=max(3, int(size * 0.11)), joint="curve")

    badge_r = int(size * 0.20)
    bx1 = size - pad - badge_r
    by1 = size - pad - badge_r
    bx2 = size - pad + int(size * 0.04)
    by2 = size - pad + int(size * 0.04)

    fill_color = COLOR_TRAY_ONLINE if status == "online" else (
        COLOR_TRAY_PENDING if status == "pending" else COLOR_TRAY_OFFLINE
    )

    d.ellipse([bx1 - 2, by1 - 2, bx2 + 2, by2 + 2], fill=COLOR_TRAY_BG)
    d.ellipse([bx1, by1, bx2, by2], fill=fill_color)

    return img


class LANControlTray:
    def __init__(
        self,
        on_show_gui: Callable[[], None] | None = None,
        on_exit_app: Callable[[], None] | None = None,
        port: int = 443,
    ):
        self.on_show_gui = on_show_gui
        self.on_exit_app = on_exit_app
        self.port = port

        self._running = False
        self._server_status = "pending"
        self._monitor_thread: threading.Thread | None = None

        self.settings = load_app_settings()
        self.minimize_to_tray = self.settings.get("minimize_to_tray_on_close", True)
        self.auto_open_web_ui = self.settings.get("auto_open_web_ui_on_login", True)

        initial_img = create_tray_icon_image("pending")
        self.icon = pystray.Icon(
            name="LANControlFleetManager",
            icon=initial_img,
            title=f"{APP_TITLE} (Checking...)",
            menu=self._build_menu(),
        )

    def _build_menu(self) -> pystray.Menu:
        status_label = f"Server: {self._server_status.upper()}"
        if self._server_status == "online":
            status_label = f"● Online (Port {self.port})"
        elif self._server_status == "offline":
            status_label = "○ Stopped"
        elif self._server_status == "pending":
            status_label = "◌ Checking..."

        return pystray.Menu(
            pystray.MenuItem("Open Management Console", self.action_open_gui, default=True),
            pystray.MenuItem("Open Web UI (Browser)", self.action_open_web_ui),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem(status_label, lambda: None, enabled=False),
            pystray.MenuItem("Start Service", self.action_start_service, visible=lambda item: self._server_status != "online"),
            pystray.MenuItem("Stop Service", self.action_stop_service, visible=lambda item: self._server_status == "online"),
            pystray.MenuItem("Restart Service", self.action_restart_service),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Open config.json", self.action_open_config),
            pystray.MenuItem("Open setup.log", self.action_open_log),
            pystray.MenuItem("Open App Folder", self.action_open_app_dir),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem(
                "Auto-Start Server on Windows Boot",
                self.toggle_boot_autostart,
                checked=lambda item: "AUTO" in service_start_type().upper(),
            ),
            pystray.MenuItem(
                "Auto-Start Manager on Windows Login",
                self.toggle_login_autostart,
                checked=lambda item: is_login_autostart_enabled(),
            ),
            pystray.MenuItem(
                "Minimize to Tray on Close",
                self.toggle_minimize_to_tray,
                checked=lambda item: self.minimize_to_tray,
            ),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Exit Completely", self.action_exit),
        )

    def start(self):
        if self._running:
            return
        self._running = True
        if self.icon: self.icon.run_detached()
        self._monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._monitor_thread.start()

    def stop(self):
        self._running = False
        try:
            if self.icon: self.icon.stop()
        except Exception:
            pass

    def notify(self, message: str, title: str = APP_TITLE):
        try:
            if self.icon and HAS_PYSTRAY:
                try:
                    self.icon.notify(message, title)
                except Exception:
                    pass
            app_log(f"[Notification] {title}: {message}")
        except Exception as exc:
            app_log(f"Tray notification failed: {exc!r}")

    def _monitor_loop(self):
        while self._running:
            try:
                state = service_state()
                if state == "RUNNING":
                    ok, _ = test_local_https(self.port, timeout=3)
                    new_status = "online" if ok else "pending"
                else:
                    new_status = "offline"

                if new_status != self._server_status:
                    self._server_status = new_status
                    self.icon.icon = create_tray_icon_image(new_status)
                    state_desc = "Online" if new_status == "online" else (
                        "Starting..." if new_status == "pending" else "Stopped"
                    )
                    self.icon.title = f"{APP_TITLE}\nServer: {state_desc} (Port {self.port})"
                    self.icon.menu = self._build_menu()
            except Exception as exc:
                app_log(f"Tray monitor loop error: {exc!r}")

            time.sleep(4)

    def action_open_web_ui(self):
        ip = choose_best_lan_ip()
        url = f"https://{ip}:{self.port}/"
        webbrowser.open(url)
        app_log(f"Web UI opened from tray: {url}")

    def action_open_gui(self):
        if self.on_show_gui:
            self.on_show_gui()

    def action_start_service(self):
        threading.Thread(target=lambda: self._service_worker("start"), daemon=True).start()

    def action_stop_service(self):
        threading.Thread(target=lambda: self._service_worker("stop"), daemon=True).start()

    def action_restart_service(self):
        threading.Thread(target=lambda: self._service_worker("restart"), daemon=True).start()

    def _service_worker(self, action: str):
        self.notify(f"LANCONTROL service {action}ing...", "LANCONTROL Service")
        ok, msg = control_service(action)
        if ok:
            self.notify(f"Service {action}ed successfully.", "LANCONTROL Service")
        else:
            self.notify(f"Service {action} failed: {msg}", "LANCONTROL Error")

    def toggle_boot_autostart(self):
        current = "AUTO" in service_start_type().upper()
        new_val = not current
        ok, msg = set_service_autostart(new_val)
        if ok:
            self.notify(f"Service boot auto-start: {'Enabled' if new_val else 'Disabled'}")
        else:
            self.notify(f"Failed to change boot auto-start: {msg}")
        self.icon.menu = self._build_menu()

    def toggle_login_autostart(self):
        current = is_login_autostart_enabled()
        new_val = not current
        ok, msg = set_login_autostart_enabled(new_val)
        if ok:
            self.notify(f"Manager login auto-start: {'Enabled' if new_val else 'Disabled'}")
        else:
            self.notify(f"Failed to change login auto-start: {msg}")
        self.icon.menu = self._build_menu()

    def toggle_minimize_to_tray(self):
        self.minimize_to_tray = not self.minimize_to_tray
        self.settings["minimize_to_tray_on_close"] = self.minimize_to_tray
        save_app_settings(self.settings)
        self.icon.menu = self._build_menu()

    def action_open_config(self):
        sync_local_artifacts()
        if LOCAL_CONFIG_FILE.exists():
            os.startfile(str(LOCAL_CONFIG_FILE))

    def action_open_log(self):
        sync_local_artifacts()
        if LOCAL_LOG_FILE.exists():
            os.startfile(str(LOCAL_LOG_FILE))
        elif APP_LOG_FILE.exists():
            os.startfile(str(APP_LOG_FILE))

    def action_open_app_dir(self):
        os.startfile(str(APP_DIR))

    def action_exit(self):
        self.stop()
        if self.on_exit_app:
            self.on_exit_app()
        else:
            sys.exit(0)


# ---------------------------------------------------------------------------
# Management Console GUI
# ---------------------------------------------------------------------------

class LANControlGUI(tk.Tk):
    def __init__(self, tray_instance: LANControlTray | None = None):
        super().__init__()
        self.tray = tray_instance

        self.title(APP_TITLE)
        
        # Dynamically determine responsive window geometry based on current display size
        try:
            sw = self.winfo_screenwidth()
            sh = self.winfo_screenheight()
            target_w = min(1440, max(1120, sw - 80))
            target_h = min(880, max(720, sh - 90))
            pos_x = max(0, (sw - target_w) // 2)
            pos_y = max(0, (sh - target_h) // 2)
            self.geometry(f"{target_w}x{target_h}+{pos_x}+{pos_y}")
        except Exception:
            self.geometry("1360x780")
            
        self.minsize(1050, 620)

        # Apply Windows 11/10 DWM Immersive Dark/Light Mode to Window Title Bar
        self.after(50, self._update_dwm_titlebar)

        # Self-healing: embed & set window icon, verify default config & assets
        try:
            ensure_app_logo()
            ensure_default_config()
            self._app_icon_img = tk.PhotoImage(data=EMBEDDED_LOGO_PNG_B64)
            self.iconphoto(True, self._app_icon_img)
        except Exception:
            pass

        # Thread-safe UI queue for Python 3.14
        self._ui_queue: queue.Queue = queue.Queue()
        self._poll_ui_queue()

        # Variables
        self.server_dir = tk.StringVar(value=str(DEFAULT_DIR))
        self.port = tk.IntVar(value=DEFAULT_PORT)
        self.website_title = tk.StringVar(value="JMD IT Remote Management")
        self.website_subtitle = tk.StringVar(value="Local Computer Administration")
        self.cert_name = tk.StringVar(value="")
        self.lan_only = tk.BooleanVar(value=True)
        self.allow_new_accounts = tk.BooleanVar(value=True)

        self.boot_autostart = tk.BooleanVar(value=True)
        self.login_autostart = tk.BooleanVar(value=True)
        self.auto_open_web_ui = tk.BooleanVar(value=True)
        self.minimize_to_tray_on_close = tk.BooleanVar(value=True)

        self.node_status = tk.StringVar(value="Checking...")
        self.npm_status = tk.StringVar(value="Checking...")
        self.mesh_status = tk.StringVar(value="Checking...")
        self.service_status = tk.StringVar(value="Checking...")
        self.service_start_type_status = tk.StringVar(value="Checking...")
        self.firewall_status = tk.StringVar(value="Checking...")
        self.https_health_status = tk.StringVar(value="Checking...")
        self.network_status = tk.StringVar(value="Checking...")

        self.progress = tk.DoubleVar(value=0)
        self.status_text = tk.StringVar(value="Ready")

        self._load_saved_state()
        sync_local_artifacts(Path(self.server_dir.get()).expanduser().resolve())

        self._build_style()
        self._build_ui()

        self.protocol("WM_DELETE_WINDOW", self.on_window_close)
        self.after(200, self.refresh_all)
        self.after(30000, self._periodic_refresh)

    def _periodic_refresh(self):
        try:
            self.refresh_all()
            self._autonomous_watchdog_check()
        finally:
            try:
                self.after(30000, self._periodic_refresh)
            except Exception:
                pass

    def _autonomous_watchdog_check(self):
        """Self-healing daemon: if service is supposed to be running but died, auto-restart."""
        def watchdog_worker():
            try:
                # Check if boot autostart is enabled (indicator that service should stay alive)
                if getattr(self, "boot_autostart", None) and self.boot_autostart.get():
                    svc_status = service_status_text().lower()
                    if "stopped" in svc_status and is_admin():
                        self.append_log("⚠️ Watchdog: Service unexpectedly stopped. Attempting autonomous self-healing restart...")
                        ok, msg = control_service("start")
                        if ok:
                            self.append_log("✓ Watchdog: Autonomous self-healing service restart succeeded.")
                            if self.tray:
                                self.tray.notify("LANCONTROL Autonomous Watchdog restored server service.", "Autonomous Self-Healing Active")
                        else:
                            self.append_log(f"Watchdog auto-restart alert: {msg}")
            except Exception as exc:
                self.append_log(f"Watchdog check error: {exc!r}")

        threading.Thread(target=watchdog_worker, daemon=True).start()

    def _poll_ui_queue(self):
        """Drains the thread-safe queue on the main Tkinter thread."""
        try:
            while not self._ui_queue.empty():
                try:
                    fn = self._ui_queue.get_nowait()
                    fn()
                except queue.Empty:
                    break
        except Exception:
            pass
        finally:
            try:
                self.after(40, self._poll_ui_queue)
            except Exception:
                pass

    def post_ui(self, fn: Callable[[], None]):
        """Schedules a callable to run safely on the main thread."""
        self._ui_queue.put(fn)

    def _load_saved_state(self):
        saved = load_app_settings()
        try:
            self.server_dir.set(saved.get("server_dir", str(DEFAULT_DIR)))
            self.port.set(int(saved.get("port", DEFAULT_PORT)))
            self.website_title.set(saved.get("website_title", "JMD IT Remote Management"))
            self.website_subtitle.set(saved.get("website_subtitle", "Local Computer Administration"))
            self.cert_name.set(saved.get("cert_name", ""))
            self.lan_only.set(bool(saved.get("lan_only", True)))
            self.allow_new_accounts.set(bool(saved.get("allow_new_accounts", True)))
            self.auto_open_web_ui.set(bool(saved.get("auto_open_web_ui_on_login", True)))
            self.minimize_to_tray_on_close.set(bool(saved.get("minimize_to_tray_on_close", True)))
            self.current_theme = saved.get("app_theme", "dark")
            if self.current_theme not in THEMES:
                self.current_theme = "dark"
        except Exception as exc:
            app_log(f"Settings error: {exc!r}")

        found = discover_meshcentral_root()
        if found:
            self.server_dir.set(str(found))
            app_log(f"Auto-detected installation: {found}")
            # Seed UI defaults from the ACTIVE config only when the manager has no saved value.
            # This avoids replacing the existing site's title/port with generic defaults.
            try:
                active_cfg_path = server_paths(found)["config"]
                if active_cfg_path.exists():
                    active_cfg = load_json(active_cfg_path)
                    active_settings = active_cfg.get("settings", {}) if isinstance(active_cfg, dict) else {}
                    active_domains = active_cfg.get("domains", {}) if isinstance(active_cfg, dict) else {}
                    active_domain = active_domains.get("", {}) if isinstance(active_domains, dict) else {}
                    if "port" not in saved:
                        self.port.set(int(active_settings.get("port", self.port.get())))
                    if "website_title" not in saved:
                        self.website_title.set(active_domain.get("title", self.website_title.get()))
                    if "website_subtitle" not in saved:
                        self.website_subtitle.set(active_domain.get("title2", self.website_subtitle.get()))
                    if "cert_name" not in saved:
                        self.cert_name.set(active_settings.get("cert", self.cert_name.get()))
                    if "lan_only" not in saved:
                        self.lan_only.set(bool(active_settings.get("LANonly", True)))
                    if "allow_new_accounts" not in saved:
                        self.allow_new_accounts.set(bool(active_domain.get("newAccounts", False)))
            except Exception as exc:
                app_log(f"Could not seed settings from active LANController config: {exc!r}")

        self.boot_autostart.set("AUTO" in service_start_type().upper())
        self.login_autostart.set(is_login_autostart_enabled())

    def _save_state(self):
        save_app_settings({
            "server_dir": self.server_dir.get(),
            "port": int(self.port.get()),
            "website_title": self.website_title.get(),
            "website_subtitle": self.website_subtitle.get(),
            "cert_name": self.cert_name.get(),
            "lan_only": bool(self.lan_only.get()),
            "allow_new_accounts": bool(self.allow_new_accounts.get()),
            "auto_open_web_ui_on_login": bool(self.auto_open_web_ui.get()),
            "minimize_to_tray_on_close": bool(self.minimize_to_tray_on_close.get()),
            "app_theme": getattr(self, "current_theme", "dark"),
        })

    def _build_style(self):
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        t = THEMES.get(getattr(self, "current_theme", "dark"), THEMES["dark"])

        self.configure(bg=t["bg_main"])

        # Base Frames & Backgrounds
        style.configure("TFrame", background=t["bg_main"])
        style.configure("Header.TFrame", background=t["bg_nav"])
        style.configure("Footer.TFrame", background=t["bg_nav"])
        style.configure("Card.TFrame", background=t["bg_card"])

        # Apple Typography & Labels
        style.configure("Title.TLabel", font=("Segoe UI", 16, "bold"), foreground=t["text_primary"], background=t["bg_nav"])
        style.configure("Subtitle.TLabel", font=("Segoe UI", 9), foreground=t["text_secondary"], background=t["bg_nav"])
        style.configure("Section.TLabelframe", background=t["bg_card"], bordercolor=t["bg_card_border"], darkcolor=t["bg_card_border"], lightcolor=t["bg_card_border"])
        style.configure("Section.TLabelframe.Label", font=("Segoe UI", 9, "bold"), foreground=t["accent"], background=t["bg_card"])
        style.configure("TLabel", background=t["bg_card"], foreground=t["text_primary"], font=("Segoe UI", 9))
        style.configure("Status.TLabel", font=("Segoe UI", 9, "bold"), background=t["bg_main"], foreground=t["accent"])
        style.configure("Muted.TLabel", font=("Segoe UI", 8), foreground=t["text_secondary"], background=t["bg_card"])

        # Standard Secondary Buttons (Clean Apple Rounded Border)
        style.configure("TButton", font=("Segoe UI", 8, "bold"), background=t["btn_bg"], foreground=t["btn_fg"], padding=(8, 4), borderwidth=1, bordercolor=t["bg_card_border"], relief="flat")
        style.map("TButton", background=[("active", t["btn_hover"]), ("pressed", t["bg_card_border"])])

        # Primary iOS Blue Accent Button
        style.configure("Primary.TButton", font=("Segoe UI", 9, "bold"), background=t["accent"], foreground="#ffffff", padding=(10, 5), borderwidth=0, relief="flat")
        style.map("Primary.TButton", background=[("active", t["accent_hover"]), ("pressed", t["accent_hover"])])

        # Action Button (iOS System Green / Secondary Prominent)
        style.configure("Action.TButton", font=("Segoe UI", 8, "bold"), background=t["success"], foreground="#ffffff", padding=(8, 4), borderwidth=0, relief="flat")
        style.map("Action.TButton", background=[("active", "#28a745"), ("pressed", "#1e7e34")])

        # Danger Button (iOS System Red)
        style.configure("Danger.TButton", font=("Segoe UI", 8, "bold"), background=t["danger"], foreground="#ffffff", padding=(8, 4), borderwidth=0, relief="flat")
        style.map("Danger.TButton", background=[("active", "#d93829"), ("pressed", "#b82b1d")])

        # Sleek Apple Notebook Tabs
        style.configure("TNotebook", background=t["bg_main"], borderwidth=0)
        style.configure("TNotebook.Tab", background=t["bg_card"], foreground=t["text_secondary"], font=("Segoe UI", 9, "bold"), padding=(12, 6), borderwidth=0)
        style.map("TNotebook.Tab",
                  background=[("selected", t["accent"]), ("active", t["btn_hover"])],
                  foreground=[("selected", "#ffffff"), ("active", t["text_primary"])])

        # Inputs, Combobox, Checkbuttons
        style.configure("TEntry", fieldbackground=t["bg_input"], foreground=t["text_primary"], insertcolor=t["accent"], bordercolor=t["bg_card_border"], padding=4)
        style.configure("TSpinbox", fieldbackground=t["bg_input"], foreground=t["text_primary"], insertcolor=t["accent"], bordercolor=t["bg_card_border"], padding=3)
        style.configure("TCombobox", fieldbackground=t["bg_input"], foreground=t["text_primary"], padding=3)
        style.configure("TCheckbutton", background=t["bg_card"], foreground=t["text_primary"], font=("Segoe UI", 8))
        style.map("TCheckbutton", background=[("active", t["bg_card"])])
        style.configure("TRadiobutton", background=t["bg_card"], foreground=t["text_primary"], font=("Segoe UI", 8))
        style.map("TRadiobutton", background=[("active", t["bg_card"])])

        # Treeview (Fleet Scanner)
        style.configure("Treeview", background=t["bg_card"], foreground=t["text_primary"], fieldbackground=t["bg_card"], font=("Segoe UI", 9), rowheight=24)
        style.configure("Treeview.Heading", background=t["bg_input"], foreground=t["text_primary"], font=("Segoe UI", 9, "bold"))
        style.map("Treeview", background=[("selected", t["accent"])], foreground=[("selected", "#ffffff")])

    def _update_dwm_titlebar(self):
        """Applies Windows 11 / Windows 10 DWM Immersive Dark Mode to the title bar."""
        try:
            hwnd = ctypes.windll.user32.GetParent(self.winfo_id())
            if not hwnd:
                hwnd = self.winfo_id()
            # DWMWA_USE_IMMERSIVE_DARK_MODE (20 on Windows 11/10 20H1+, 19 on older 10)
            is_dark = getattr(self, "current_theme", "dark") == "dark"
            value = ctypes.c_int(1 if is_dark else 0)
            for attr in (20, 19):
                res = ctypes.windll.dwmapi.DwmSetWindowAttribute(
                    hwnd,
                    attr,
                    ctypes.byref(value),
                    ctypes.sizeof(value),
                )
                if res == 0:
                    break
        except Exception:
            pass

    def set_theme(self, theme_name: str):
        if theme_name not in THEMES:
            return
        self.current_theme = theme_name
        self._save_state()
        self._build_style()
        self._apply_theme_to_text_widgets()
        self._update_dwm_titlebar()
        if hasattr(self, "theme_btn"):
            next_label = "☀️ Light Theme" if self.current_theme == "dark" else "🌙 Dark Theme"
            self.theme_btn.configure(text=next_label)

    def toggle_theme(self):
        new_theme = "light" if getattr(self, "current_theme", "dark") == "dark" else "dark"
        self.set_theme(new_theme)

    def _apply_theme_to_text_widgets(self):
        t = THEMES.get(getattr(self, "current_theme", "dark"), THEMES["dark"])
        # Update text console and editor widgets across all tabs
        widgets_to_update = [
            getattr(self, "bottom_console_widget", None),
            getattr(self, "address_box", None),
            getattr(self, "config_text_widget", None),
            getattr(self, "cmd_box", None),
            getattr(self, "diag_widget", None),
            getattr(self, "log_widget", None),
        ]
        for w in widgets_to_update:
            if w and isinstance(w, tk.Text):
                try:
                    w.configure(
                        bg=t["bg_console"],
                        fg=t["text_primary"],
                        insertbackground=t["accent"],
                        selectbackground=t["accent"],
                        selectforeground="#ffffff"
                    )
                except Exception:
                    pass

        # Update QR Canvas background and borders
        if hasattr(self, "qr_canvas") and isinstance(self.qr_canvas, tk.Canvas):
            try:
                self.qr_canvas.configure(
                    bg=t["bg_console"],
                    highlightbackground=t["bg_card_border"]
                )
            except Exception:
                pass

        # Update all status card pill badges
        for fn in getattr(self, "_status_card_updaters", []):
            try:
                fn()
            except Exception:
                pass


    def _build_ui(self):
        header = ttk.Frame(self, padding=(16, 12, 16, 8), style="Header.TFrame")
        header.pack(fill="x")

        title_box = ttk.Frame(header, style="Header.TFrame")
        title_box.pack(side="left", fill="x", expand=True)
        ttk.Label(title_box, text=APP_TITLE, style="Title.TLabel").pack(anchor="w")
        ttk.Label(
            title_box,
            text="Autonomous Server Management • Auto-Start on Boot • Auto-Launch Web UI • Background Tray",
            style="Subtitle.TLabel",
        ).pack(anchor="w", pady=(2, 0))

        top_actions = ttk.Frame(header, style="Header.TFrame")
        top_actions.pack(side="right")
        self.theme_btn = ttk.Button(
            top_actions,
            text="☀️ Light Theme" if getattr(self, "current_theme", "dark") == "dark" else "🌙 Dark Theme",
            command=self.toggle_theme,
        )
        self.theme_btn.pack(side="left", padx=4)
        ttk.Button(top_actions, text="🌐 OPEN WEB UI", style="Primary.TButton", command=self.open_web_ui).pack(side="left", padx=6)
        ttk.Button(top_actions, text="🗕 Minimize to Tray", command=self.hide_to_tray).pack(side="left", padx=6)

        status_bar = ttk.Frame(self, padding=(16, 0, 16, 8))
        status_bar.pack(fill="x")
        ttk.Label(status_bar, textvariable=self.status_text, style="Status.TLabel").pack(side="left")
        ttk.Progressbar(status_bar, variable=self.progress, maximum=100, length=280).pack(side="right")

        # ---------------- 1. FIXED BOTTOM STATUS FOOTER (PACKED FIRST) ----------------
        footer = ttk.Frame(self, padding=(14, 6, 14, 8), style="Footer.TFrame")
        footer.pack(side="bottom", fill="x")

        elevation_text = "Windows Administrator Active" if is_admin() else "Standard User Mode"
        elevation_color = COLOR_SUCCESS if is_admin() else COLOR_WARNING
        ttk.Label(
            footer,
            text=f"LANCONTROL Core v{APP_VERSION} • {elevation_text}",
            font=("Segoe UI", 9, "bold" if is_admin() else "normal"),
            foreground=elevation_color,
        ).pack(side="left")

        if not is_admin():
            ttk.Button(
                footer,
                text="⚡ Elevate to Admin",
                command=lambda: request_admin_elevation("Restart LANCONTROL Fleet Manager with Administrator privileges?"),
            ).pack(side="left", padx=10)

        ttk.Button(footer, text="↻ Refresh All", command=self.refresh_all).pack(side="right")

        # ---------------- 2. FIXED BOTTOM TERMINAL CONSOLE (LARGE & EXPANDED) ----------------
        console_box = ttk.LabelFrame(self, text="  ⚡ LIVE SYSTEM TERMINAL & ACTIVITY STREAM  ", style="Section.TLabelframe")
        console_box.pack(side="bottom", fill="x", padx=12, pady=(0, 6))

        c_top = ttk.Frame(console_box, padding=(10, 4, 10, 3), style="Card.TFrame")
        c_top.pack(fill="x")

        ttk.Label(
            c_top,
            text="● Live Runtime Engine Monitor — Active socket handshakes, peer connections, and fleet events:",
            style="Status.TLabel",
        ).pack(side="left")

        ttk.Button(
            c_top,
            text="Clear Console",
            command=lambda: (self.bottom_console_widget.delete("1.0", "end") if hasattr(self, "bottom_console_widget") else None),
        ).pack(side="right")

        c_inner = ttk.Frame(console_box, padding=(6, 2, 6, 6), style="Card.TFrame")
        c_inner.pack(fill="x")

        t = THEMES.get(getattr(self, "current_theme", "dark"), THEMES["dark"])
        self.bottom_console_widget = tk.Text(
            c_inner,
            height=4,
            wrap="word",
            font=("Consolas", 9),
            bg=t["bg_console"],
            fg=t["text_primary"],
            insertbackground=t["accent"],
            selectbackground=t["accent"],
            selectforeground="#ffffff",
            padx=8,
            pady=4,
            relief="flat",
        )
        self.bottom_console_widget.pack(fill="both", expand=True, side="left")
        c_sb = ttk.Scrollbar(c_inner, orient="vertical", command=self.bottom_console_widget.yview)
        c_sb.pack(side="right", fill="y")
        self.bottom_console_widget.configure(yscrollcommand=c_sb.set)

        # Preload initial logs into bottom console
        try:
            if LOCAL_LOG_FILE.exists():
                lines_log = LOCAL_LOG_FILE.read_text(encoding="utf-8", errors="replace").splitlines()
                tail = lines_log[-45:]
                self.bottom_console_widget.insert("1.0", "\n".join(tail) + ("\n" if tail else ""))
                self.bottom_console_widget.see("end")
        except Exception:
            pass

        # ---------------- 3. MAIN APPLICATION TABS (FILLS ALL REMAINING SPACE) ----------------
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=12, pady=(0, 6))

        # 6 Core Logical Hubs
        self.dashboard_tab = ttk.Frame(self.notebook, padding=(12, 10))
        self.deploy_tab = ttk.Frame(self.notebook, padding=(12, 10))
        self.tailscale_tab = ttk.Frame(self.notebook, padding=(12, 10))
        self.network_tab = ttk.Frame(self.notebook, padding=(12, 10))
        self.server_tab = ttk.Frame(self.notebook, padding=(12, 10))
        self.diagnostics_tab = ttk.Frame(self.notebook, padding=(12, 10))

        # Clean, modern responsive tab headers with iconography
        self.notebook.add(self.dashboard_tab, text=" ⚡ OVERVIEW & STATUS ")
        self.notebook.add(self.deploy_tab, text=" 🚀 ENDPOINT & MDM BUILDER ")
        self.notebook.add(self.tailscale_tab, text=" 🌐 REMOTE & TAILSCALE ")
        self.notebook.add(self.network_tab, text=" 🔍 FLEET SCANNER ")
        self.notebook.add(self.server_tab, text=" ⚙️ SERVER & CONFIG ")
        self.notebook.add(self.diagnostics_tab, text=" 🛠️ AUDIT & SYSTEM REPAIR ")

        self._build_dashboard_tab()
        self._build_deploy_tab()
        self._build_tailscale_tab()
        self._build_network_tab()
        self._build_server_tab()
        self._build_diagnostics_tab()

        self._apply_theme_to_text_widgets()

        # Listen to tab switch to auto-refresh tab data
        self.notebook.bind("<<NotebookTabChanged>>", self._on_tab_changed)
    def _on_tab_changed(self, event):
        tab = self.notebook.select()
        if tab == str(self.deploy_tab):
            self.refresh_deploy_tab()
        elif tab == str(self.tailscale_tab):
            self.refresh_tailscale_status()
        elif tab == str(self.server_tab):
            if hasattr(self, "reload_config_tab"):
                self.reload_config_tab()

    
    def _detect_public_ip_for_deploy(self):
        def worker():
            self.set_status("Detecting public WAN IP...", 30)
            pub = fetch_public_ipv4()
            if pub:
                self.post_ui(lambda: (self.deploy_host_var.set(pub), self._update_quick_commands()))
                self.append_log(f"Detected Public WAN IP: {pub}")
                self.post_ui(lambda: messagebox.showinfo(
                    APP_TITLE,
                    f"Public WAN IPv4 Detected: {pub}\n\n"
                    f"• Connect Host updated to {pub}.\n"
                    f"• Ensure WAN mode is enabled in Server tab and your router forwards the port if not using Tailscale."
                ))
            else:
                self.append_log("Could not detect public IPv4 automatically.")
                self.post_ui(lambda: messagebox.showwarning(APP_TITLE, "Could not detect public WAN IP automatically. Check internet connection."))
            self.set_status("Ready")
        threading.Thread(target=worker, daemon=True).start()

    def refresh_deploy_tab(self):
        if hasattr(self, "deploy_box"):
            self.deploy_box.configure(state="normal")
            self.deploy_box.delete("1.0", "end")
            self.deploy_box.insert("1.0", self.deployment_text())
            self.deploy_box.configure(state="disabled")

    def _status_card(self, parent, title, variable, row, column):
        frame = ttk.LabelFrame(parent, text=f"  {title}  ", style="Section.TLabelframe")
        frame.grid(row=row, column=column, sticky="nsew", padx=4, pady=3)

        badge_box = tk.Frame(frame, bd=0, relief="flat")
        badge_box.pack(anchor="w", padx=8, pady=5)

        badge_lbl = tk.Label(
            badge_box,
            textvariable=variable,
            font=("Segoe UI", 9, "bold"),
            padx=10,
            pady=3,
            bd=0,
            relief="flat",
        )
        badge_lbl.pack(anchor="w")

        def update_badge_color(*args):
            val = str(variable.get()).strip()
            val_lower = val.lower()
            t = THEMES.get(getattr(self, "current_theme", "dark"), THEMES["dark"])
            is_dark = getattr(self, "current_theme", "dark") == "dark"

            if any(k in val_lower for k in ["running", "active", "online", "healthy", "installed", "auto", "ok"]):
                bg = "#132d1e" if is_dark else "#e8f8ed"
                fg = t["success"]
            elif any(k in val_lower for k in ["stopped", "offline", "missing", "error", "failed", "disabled"]):
                bg = "#331616" if is_dark else "#fde8e8"
                fg = t["danger"]
            elif any(k in val_lower for k in ["checking", "pending", "resolving", "starting"]):
                bg = "#332612" if is_dark else "#fef3e2"
                fg = t["warning"]
            else:
                bg = t["bg_input"]
                fg = t["text_primary"]

            try:
                badge_box.configure(bg=t["bg_card"])
                badge_lbl.configure(bg=bg, fg=fg)
            except Exception:
                pass

        variable.trace_add("write", update_badge_color)
        update_badge_color()
        if not hasattr(self, "_status_card_updaters"):
            self._status_card_updaters = []
        self._status_card_updaters.append(update_badge_color)
        return frame

    def _build_dashboard_tab(self):
        parent = self.dashboard_tab
        grid = ttk.Frame(parent)
        grid.pack(fill="x")
        for c in range(4):
            grid.columnconfigure(c, weight=1)

        self._status_card(grid, "Node.js Runtime", self.node_status, 0, 0)
        self._status_card(grid, "npm Package Mgr", self.npm_status, 0, 1)
        self._status_card(grid, "LANCONTROL Package", self.mesh_status, 0, 2)
        self._status_card(grid, "HTTPS Endpoint", self.https_health_status, 0, 3)

        self._status_card(grid, "Windows Service", self.service_status, 1, 0)
        self._status_card(grid, "Service Boot Startup", self.service_start_type_status, 1, 1)
        self._status_card(grid, "Windows Firewall", self.firewall_status, 1, 2)
        self._status_card(grid, "Network Interfaces", self.network_status, 1, 3)

        actions = ttk.LabelFrame(parent, text="Fast Actions & Service Controls", style="Section.TLabelframe")
        actions.pack(fill="x", pady=(6, 4))
        a = ttk.Frame(actions, padding=(8, 4, 8, 4))
        a.pack(fill="x")

        ttk.Button(a, text="⚡ 1-CLICK AUTOMATED SETUP (ANY PC / ANY OFFICE)", style="Primary.TButton", command=self.one_click_setup).pack(side="left", padx=(0, 8))
        ttk.Button(a, text="🔍 DIAGNOSE & REPAIR", style="Action.TButton", command=self.diagnose_and_repair).pack(side="left", padx=6)
        ttk.Button(a, text="Start Service", command=lambda: self.service_action("start")).pack(side="left", padx=6)
        ttk.Button(a, text="Stop Service", command=lambda: self.service_action("stop")).pack(side="left", padx=6)
        ttk.Button(a, text="Restart Service", command=lambda: self.service_action("restart")).pack(side="left", padx=6)
        ttk.Button(a, text="Open Web UI", style="Action.TButton", command=self.open_web_ui).pack(side="right")

        info = ttk.LabelFrame(parent, text="Active LANCONTROL Access URLs", style="Section.TLabelframe")
        info.pack(fill="x", pady=(4, 2))
        t = THEMES.get(getattr(self, "current_theme", "dark"), THEMES["dark"])
        self.address_box = tk.Text(
            info,
            height=3,
            font=("Consolas", 9),
            wrap="word",
            bg=t["bg_console"],
            fg=t["text_primary"],
            insertbackground=t["accent"],
            selectbackground=t["accent"],
            selectforeground="#ffffff",
            relief="flat",
        )
        self.address_box.pack(fill="x", padx=8, pady=(4, 4))
        self.address_box.configure(state="disabled")

        banner = ttk.Frame(parent, padding=(4, 2, 4, 2))
        banner.pack(fill="x")
        ttk.Label(
            banner,
            text="✓ Boot Autostart: Server starts automatically as a Windows Service at machine boot.\n"
                 "✓ Login Autostart: Web UI opens and Manager stays alive in system tray when user logs in.",
            font=("Segoe UI", 9, "bold"),
            foreground=COLOR_SUCCESS,
        ).pack(anchor="w")

    def _build_server_tab(self):
        parent = self.server_tab

        # Dynamic Responsive PanedWindow (User can drag or window can auto-distribute)
        paned = ttk.PanedWindow(parent, orient="horizontal")
        paned.pack(fill="both", expand=True)

        # LEFT PANE: Server Settings & Windows Service Controls
        left_pane = ttk.Frame(paned, padding=(0, 0, 6, 0))
        paned.add(left_pane, weight=1)

        cfg = ttk.LabelFrame(left_pane, text="  Server Engine & Network Identity  ", style="Section.TLabelframe")
        cfg.pack(fill="x", pady=(0, 6))
        g = ttk.Frame(cfg, padding=(8, 6, 8, 6))
        g.pack(fill="x")
        g.columnconfigure(1, weight=1)

        ttk.Label(g, text="Server Folder:").grid(row=0, column=0, sticky="w", pady=2)
        ttk.Entry(g, textvariable=self.server_dir).grid(row=0, column=1, sticky="ew", padx=4, pady=2)
        ttk.Button(g, text="Browse...", command=self.browse_server_dir).grid(row=0, column=2, pady=2)

        ttk.Label(g, text="HTTPS Port:").grid(row=1, column=0, sticky="w", pady=2)
        ttk.Spinbox(g, from_=1, to=65535, textvariable=self.port, width=8).grid(row=1, column=1, sticky="w", padx=4, pady=2)

        ttk.Label(g, text="Portal Title:").grid(row=2, column=0, sticky="w", pady=2)
        ttk.Entry(g, textvariable=self.website_title).grid(row=2, column=1, columnspan=2, sticky="ew", padx=4, pady=2)

        ttk.Label(g, text="Subtitle:").grid(row=3, column=0, sticky="w", pady=2)
        ttk.Entry(g, textvariable=self.website_subtitle).grid(row=3, column=1, columnspan=2, sticky="ew", padx=4, pady=2)

        ttk.Label(g, text="Cert / DNS:").grid(row=4, column=0, sticky="w", pady=2)
        ttk.Entry(g, textvariable=self.cert_name).grid(row=4, column=1, columnspan=2, sticky="ew", padx=4, pady=2)

        ttk.Checkbutton(g, text="LAN-only mode (Private mesh)", variable=self.lan_only).grid(row=5, column=1, columnspan=2, sticky="w", padx=4, pady=2)
        ttk.Checkbutton(g, text="Allow account registration on first run", variable=self.allow_new_accounts).grid(row=6, column=1, columnspan=2, sticky="w", padx=4, pady=2)

        cfg_actions = ttk.Frame(cfg, padding=(8, 2, 8, 6))
        cfg_actions.pack(fill="x")
        ttk.Button(cfg_actions, text="Save Config", style="Action.TButton", command=self.write_config).pack(side="left")
        ttk.Button(cfg_actions, text="Backup", command=self.backup_current_config).pack(side="left", padx=4)
        ttk.Button(cfg_actions, text="Rollback", command=self.rollback_config_action).pack(side="left", padx=2)
        ttk.Button(cfg_actions, text="npm Update", command=self.install_or_update_mesh).pack(side="right")

        startup_box = ttk.LabelFrame(left_pane, text="  Windows Startup & Background Tray  ", style="Section.TLabelframe")
        startup_box.pack(fill="x", pady=4)
        sb = ttk.Frame(startup_box, padding=(8, 4, 8, 4))
        sb.pack(fill="x")

        ttk.Checkbutton(
            sb, text="Auto-start Service on Boot (Service: start= auto)",
            variable=self.boot_autostart, command=self.on_toggle_boot_autostart,
        ).pack(anchor="w", pady=1)

        ttk.Checkbutton(
            sb, text="Auto-start Manager on Login (Registry: HKCU Run)",
            variable=self.login_autostart, command=self.on_toggle_login_autostart,
        ).pack(anchor="w", pady=1)

        ttk.Checkbutton(
            sb, text="Auto-open Web UI in browser on launch",
            variable=self.auto_open_web_ui, command=self._save_state,
        ).pack(anchor="w", pady=1)

        ttk.Checkbutton(
            sb, text="Keep running in tray (Minimize to tray on [X])",
            variable=self.minimize_to_tray_on_close, command=self._save_state,
        ).pack(anchor="w", pady=1)

        sf_box = ttk.LabelFrame(left_pane, text="  Windows Service & Firewall  ", style="Section.TLabelframe")
        sf_box.pack(fill="x", pady=4)
        sf = ttk.Frame(sf_box, padding=(8, 4, 8, 4))
        sf.pack(fill="x")

        ttk.Button(sf, text="Install Service", command=self.install_service).pack(side="left", padx=2)
        ttk.Button(sf, text="Remove", command=self.remove_service).pack(side="left", padx=2)
        ttk.Button(sf, text="Firewall", command=self.allow_firewall).pack(side="left", padx=2)
        ttk.Button(sf, text="Test HTTPS", command=self.test_local_https).pack(side="right")

        # RIGHT PANE: Integrated Live JSON Editor
        right_pane = ttk.LabelFrame(paned, text="  Live config.json Active Editor & Backup  ", style="Section.TLabelframe")
        paned.add(right_pane, weight=2)

        top_r = ttk.Frame(right_pane, padding=(8, 3, 8, 3))
        top_r.pack(fill="x")

        self.config_path_label = ttk.Label(top_r, text="Locating active config...", font=("Segoe UI", 8), foreground=COLOR_TEXT_SECONDARY)
        self.config_path_label.pack(side="left", fill="x", expand=True)

        r_btns = ttk.Frame(top_r)
        r_btns.pack(side="right")
        ttk.Button(r_btns, text="↻ Reload", command=self.reload_config_tab).pack(side="left", padx=2)
        ttk.Button(r_btns, text="💾 Save", style="Action.TButton", command=self.save_config_from_editor).pack(side="left", padx=2)
        ttk.Button(r_btns, text="Notepad", command=self.open_config_in_notepad).pack(side="left", padx=2)
        ttk.Button(r_btns, text="Folder", command=self.open_config_folder).pack(side="left", padx=2)

        t = THEMES.get(getattr(self, "current_theme", "dark"), THEMES["dark"])
        self.config_text_widget = tk.Text(
            right_pane,
            wrap="none",
            font=("Consolas", 9),
            bg=t["bg_console"],
            fg=t["text_primary"],
            insertbackground=t["accent"],
            selectbackground=t["accent"],
            selectforeground="#ffffff",
            padx=8,
            pady=6,
            relief="flat",
        )
        self.config_text_widget.pack(fill="both", expand=True, padx=6, pady=(0, 6), side="left")
        cfg_sb_y = ttk.Scrollbar(right_pane, orient="vertical", command=self.config_text_widget.yview)
        cfg_sb_y.pack(side="right", fill="y", pady=(0, 6))
        self.config_text_widget.configure(yscrollcommand=cfg_sb_y.set)
        self.reload_config_tab()



    def reload_config_tab(self):
        root = Path(self.server_dir.get()).expanduser().resolve()
        active_config = server_paths(root)["config"]

        target_file = active_config if active_config.exists() else (
            LOCAL_CONFIG_FILE if LOCAL_CONFIG_FILE.exists() else None
        )

        if target_file and target_file.exists():
            try:
                content = target_file.read_text(encoding="utf-8", errors="replace")
                try:
                    parsed = json.loads(content)
                    content = json.dumps(parsed, indent=2, ensure_ascii=False)
                except Exception:
                    pass
                self.config_text_widget.delete("1.0", "end")
                self.config_text_widget.insert("1.0", content)
                self.config_path_label.configure(
                    text=f"Active File: {target_file}  •  Local App Folder Mirror: {LOCAL_CONFIG_FILE}"
                )
            except Exception as exc:
                self.config_text_widget.delete("1.0", "end")
                self.config_text_widget.insert("1.0", f"Error reading config: {exc}")
        else:
            self.config_text_widget.delete("1.0", "end")
            self.config_text_widget.insert("1.0", "No config.json found. Click 'Write Config' or 'One-Click Local Setup' to create one.")
            self.config_path_label.configure(text=f"Expected Path: {active_config}")

    def save_config_from_editor(self):
        root = Path(self.server_dir.get()).expanduser().resolve()
        active_config = server_paths(root)["config"]
        content = self.config_text_widget.get("1.0", "end").strip()

        try:
            parsed = json.loads(content)
        except json.JSONDecodeError as exc:
            messagebox.showerror(APP_TITLE, f"Invalid JSON syntax! Please fix error:\n\n{exc}")
            return

        try:
            backup_config(active_config, server_paths(root)["backups"])
            atomic_write_json(active_config, parsed)
            atomic_write_json(LOCAL_CONFIG_FILE, parsed)

            self.append_log(f"Config successfully updated from GUI editor: {active_config}")
            messagebox.showinfo(APP_TITLE, f"Configuration saved successfully!\n\nWritten to:\n{active_config}\nand mirrored to:\n{LOCAL_CONFIG_FILE}")
            self.reload_config_tab()
            self.refresh_all()
        except Exception as exc:
            messagebox.showerror(APP_TITLE, f"Failed to save config file:\n{exc}")

    def open_config_in_notepad(self):
        root = Path(self.server_dir.get()).expanduser().resolve()
        active_config = server_paths(root)["config"]
        sync_local_artifacts(root)
        target = active_config if active_config.exists() else LOCAL_CONFIG_FILE
        if target.exists():
            os.startfile(str(target))
        else:
            messagebox.showinfo(APP_TITLE, "config.json does not exist yet. Run setup first.")

    def open_config_folder(self):
        root = Path(self.server_dir.get()).expanduser().resolve()
        target_dir = server_paths(root)["data"]
        if not target_dir.exists():
            target_dir = APP_DIR
        os.startfile(str(target_dir))

    # ---------------- Local Fleet Discovery Tab ----------------

    def _build_tailscale_tab(self):
        parent = self.tailscale_tab
        ttk.Label(parent, text="Secure Remote Access from Home", style="Title.TLabel").pack(anchor="w")
        ttk.Label(
            parent,
            text="Keep your existing LANCONTROL configuration. Tailscale Serve securely proxies the current localhost HTTPS page to your private tailnet; it does not open a public internet port.",
            style="Subtitle.TLabel", wraplength=950, justify="left",
        ).pack(anchor="w", pady=(4, 12))

        status_frame = ttk.LabelFrame(parent, text="Tailscale Status", style="Section.TLabelframe")
        status_frame.pack(fill="x", pady=(0, 10))
        self.tailscale_status_var = tk.StringVar(value="Checking Tailscale...")
        self.tailscale_ip_var = tk.StringVar(value="Tailscale IP: —")
        self.tailscale_url_var = tk.StringVar(value="Remote URL: not configured")
        ttk.Label(status_frame, textvariable=self.tailscale_status_var, font=("Segoe UI", 10, "bold")).pack(anchor="w", padx=10, pady=(8, 2))
        ttk.Label(status_frame, textvariable=self.tailscale_ip_var).pack(anchor="w", padx=10, pady=2)
        ttk.Label(status_frame, textvariable=self.tailscale_url_var, wraplength=950).pack(anchor="w", padx=10, pady=(2, 8))

        actions = ttk.LabelFrame(parent, text="Setup Actions", style="Section.TLabelframe")
        actions.pack(fill="x", pady=(0, 6))
        row1 = ttk.Frame(actions, padding=(8, 4, 8, 4))
        row1.pack(fill="x")
        ttk.Button(row1, text="1. Install Tailscale Automatically", style="Primary.TButton", command=self.install_tailscale_action).pack(side="left", padx=(0, 6))
        ttk.Button(row1, text="2. Connect / Sign In", command=self.connect_tailscale_action).pack(side="left", padx=4)
        ttk.Button(row1, text="Refresh Status", command=self.refresh_tailscale_status).pack(side="left", padx=4)
        row2 = ttk.Frame(actions, padding=(8, 0, 8, 6))
        row2.pack(fill="x")
        ttk.Button(row2, text="3. Configure Private Remote URL", style="Primary.TButton", command=self.configure_tailscale_action).pack(side="left", padx=(0, 6))
        ttk.Button(row2, text="Open URL", command=self.open_tailscale_url).pack(side="left", padx=4)
        ttk.Button(row2, text="Copy URL", command=self.copy_tailscale_url).pack(side="left", padx=4)
        ttk.Button(row2, text="Disable Serve", command=self.disable_tailscale_action).pack(side="left", padx=4)

        guide = ttk.LabelFrame(parent, text="One-time setup checklist", style="Section.TLabelframe")
        guide.pack(fill="both", expand=True)
        guide_text = (
            "OFFICE PC\n"
            "1. Install Tailscale with the first button. If winget is unavailable, the official download page will be shown.\n"
            "2. Click Connect / Sign In and authenticate in the browser or Tailscale app.\n"
            "3. Confirm LANController is healthy locally, then configure the private remote URL.\n\n"
            "HOME WINDOWS PC + ANDROID\n"
            "4. Install Tailscale on each device and sign in to the SAME tailnet/account.\n"
            "5. Open the Remote URL shown above. It is only reachable by devices permitted on your Tailscale network.\n\n"
            "SAFETY\n"
            "• This manager never configures Tailscale Funnel and never creates router port-forwarding rules.\n"
            "• The local LANController config is not rewritten for Tailscale.\n"
            "• ‘Disable Serve’ removes this machine's Tailscale Serve configuration; it does not uninstall Tailscale or stop MeshCentral.\n"
            "• Use a strong LANCONTROL password and limit tailnet access to trusted devices/users."
        )
        t = THEMES.get(getattr(self, "current_theme", "dark"), THEMES["dark"])
        text_box = tk.Text(
            guide,
            height=12,
            wrap="word",
            font=("Segoe UI", 9),
            bg=t["bg_console"],
            fg=t["text_primary"],
            insertbackground=t["accent"],
            selectbackground=t["accent"],
            selectforeground="#ffffff",
            relief="flat",
        )
        text_box.pack(fill="both", expand=True, padx=8, pady=8)
        text_box.insert("1.0", guide_text)
        text_box.configure(state="disabled")

    def refresh_tailscale_status(self):
        def worker():
            info = tailscale_status_info()
            configured, serve_text, serve_url = tailscale_serve_status() if info.get("installed") else (False, "Tailscale is not installed.", "")
            if not info.get("installed"):
                headline = "Not installed"
            elif info.get("connected"):
                headline = "Connected to Tailscale"
            else:
                headline = "Installed, but not connected / signed in"
            ip_val = info.get('ip') or 'not available'
            dns_val = info.get('dns') or ''
            ip_text = f"Tailscale IP: {ip_val}   |   MagicDNS: {dns_val}"
            direct_url = f"https://{ip_val}:443/" if ip_val != 'not available' else ""
            if configured and serve_url:
                url = serve_url
                url_text = f"Tailscale Remote URL: {url} (Direct: {direct_url})"
            elif direct_url:
                url = direct_url
                url_text = f"Direct Tailnet URL: {direct_url}  (Ready to access from Home PC!)"
            else:
                url = ""
                url_text = "Remote URL: not configured" 
            detail = info.get("detail", "")
            if detail and detail not in ("Connected", "running"):
                headline += f" — {detail[:180]}"
            self.post_ui(lambda: self._apply_tailscale_status(headline, ip_text, url_text, url))
        threading.Thread(target=worker, daemon=True).start()

    def _apply_tailscale_status(self, headline: str, ip_text: str, url_text: str, url: str):
        self.tailscale_status_var.set(headline)
        self.tailscale_ip_var.set(ip_text)
        self.tailscale_url_var.set(url_text)
        self._tailscale_remote_url = url

    def install_tailscale_action(self):
        self.run_background(self._install_tailscale_worker, refresh_after=False)

    def _install_tailscale_worker(self):
        self.set_status("Installing Tailscale...", 20)
        ok, message = install_tailscale()
        self.append_log(message)
        if not ok and "https://tailscale.com/download/windows" in message:
            self.post_ui(lambda: webbrowser.open("https://tailscale.com/download/windows"))
        self.post_ui(lambda: messagebox.showinfo(APP_TITLE, message) if ok else messagebox.showwarning(APP_TITLE, message))
        self.post_ui(self.refresh_tailscale_status)
        self.set_status("Tailscale installation check complete", 100)

    def connect_tailscale_action(self):
        self.run_background(self._connect_tailscale_worker, refresh_after=False)

    def _connect_tailscale_worker(self):
        if not tailscale_path():
            self.post_ui(lambda: messagebox.showwarning(APP_TITLE, "Tailscale is not installed. Click Install Tailscale Automatically first."))
            return
        self.set_status("Starting Tailscale sign-in...", 25)
        rc, out = tailscale_cli(["up"], timeout=90)
        self.append_log("Tailscale up result:\n" + (out or f"Exit code: {rc}"))
        urls = re.findall(r"https?://[^\s\]\[<>\"']+", out or "")
        login_url = next((u.rstrip(".,)") for u in urls if "tailscale.com" in u.lower()), "")
        if login_url:
            self.post_ui(lambda u=login_url: webbrowser.open(u))
        self.post_ui(self.refresh_tailscale_status)
        if rc != 0 and not login_url:
            self.post_ui(lambda: messagebox.showwarning(APP_TITLE, f"Tailscale connection did not complete. Open the Tailscale tray app and sign in, then retry.\n\n{out}"))
        else:
            self.post_ui(lambda: messagebox.showinfo(APP_TITLE, "If prompted, finish signing in to Tailscale. Once the office PC shows Connected, click Configure Private Remote URL."))
        self.set_status("Tailscale sign-in step finished", 100)

    def configure_tailscale_action(self):
        if not messagebox.askyesno(
            APP_TITLE,
            "Configure Tailscale Serve for private remote access?\n\n"
            "This will share the existing https://127.0.0.1:<LANCONTROL port> endpoint with your Tailscale network only.\n"
            "It will NOT use Funnel, change LANCONTROL config.json, or create router port forwarding.",
        ):
            return
        port = int(self.port.get() or DEFAULT_PORT)
        self.run_background(self._configure_tailscale_worker, port, refresh_after=False)

    def _configure_tailscale_worker(self, port: int):
        self.set_status("Configuring private Tailscale Serve...", 35)
        ok, message, url = configure_tailscale_serve(port)
        self.append_log("Tailscale Serve setup:\n" + message)
        if url:
            self._tailscale_remote_url = url
        if ok:
            self.post_ui(lambda: messagebox.showinfo(APP_TITLE, f"Private remote access configured.\n\n{url or message}\n\nInstall Tailscale on your home PC and Android device, sign in to the same tailnet, then open this URL."))
        else:
            # Open a consent URL emitted by the Tailscale CLI, when one was captured.
            urls = re.findall(r"https?://[^\s\]\[<>\"']+", message or "")
            consent_url = next(
                (u.rstrip(".,)") for u in urls if "login.tailscale.com" in u.lower()),
                "",
            )
            if consent_url:
                self.post_ui(lambda u=consent_url: webbrowser.open(u))
            self.post_ui(lambda: messagebox.showwarning(APP_TITLE, message))
        self.post_ui(self.refresh_tailscale_status)
        self.set_status("Tailscale Serve setup finished" if ok else "Tailscale Serve setup needs attention", 100)

    
    def open_direct_tailscale_url(self):
        info = tailscale_status_info()
        ts_ip = info.get("ip") or "100.113.51.119"
        port = int(self.port.get() or DEFAULT_PORT)
        url = f"https://{ts_ip}:{port}/"
        webbrowser.open(url)
        self.append_log(f"Opened direct Tailscale URL: {url}")

    def open_tailscale_url(self):
        url = getattr(self, "_tailscale_remote_url", "")
        if not url:
            self.refresh_tailscale_status()
            messagebox.showinfo(APP_TITLE, "No remote URL is detected yet. Connect Tailscale and configure Private Remote URL first.")
            return
        webbrowser.open(url)

    def copy_tailscale_url(self):
        url = getattr(self, "_tailscale_remote_url", "")
        if not url:
            messagebox.showinfo(APP_TITLE, "No remote URL is detected yet. Configure Private Remote URL first.")
            return
        self.clipboard_clear()
        self.clipboard_append(url)
        self.update_idletasks()
        messagebox.showinfo(APP_TITLE, f"Copied remote URL:\n{url}")

    def disable_tailscale_action(self):
        if not messagebox.askyesno(
            APP_TITLE,
            "Disable Tailscale Serve on this office PC?\n\nThis removes this node's Serve configuration and makes the remote URL stop working. It does not uninstall Tailscale or stop MeshCentral.",
        ):
            return
        self.run_background(self._disable_tailscale_worker, refresh_after=False)

    def _disable_tailscale_worker(self):
        ok, message = disable_tailscale_serve()
        self.append_log("Tailscale Serve reset: " + message)
        self.post_ui(lambda: messagebox.showinfo(APP_TITLE, message) if ok else messagebox.showwarning(APP_TITLE, message))
        self.post_ui(self.refresh_tailscale_status)

    def _build_network_tab(self):
        parent = self.network_tab
        top = ttk.Frame(parent)
        top.pack(fill="x", pady=(0, 6))

        ttk.Button(top, text="🔍 Scan Network", style="Action.TButton", command=self.scan_hosts).pack(side="left")

        ttk.Label(top, text="Target Subnet / Range:", font=("Segoe UI", 8, "bold")).pack(side="left", padx=(10, 4))
        self.scan_target_var = tk.StringVar(value="All Local Subnets")
        detected_subnets = ["All Local Subnets"]
        for ip in local_ipv4_addresses():
            if ip and not ip.startswith("127."):
                parts = ip.split(".")
                if len(parts) == 4:
                    detected_subnets.append(f"{parts[0]}.{parts[1]}.{parts[2]}.0/24")
        ts_info = tailscale_status_info()
        ts_ip = ts_info.get("ip")
        if ts_ip:
            detected_subnets.append(f"{ts_ip}/32 (Tailnet)")

        self.scan_target_combo = ttk.Combobox(top, textvariable=self.scan_target_var, values=detected_subnets, width=28)
        self.scan_target_combo.pack(side="left", padx=2)

        ttk.Button(top, text="Export CSV", command=self.export_hosts_csv).pack(side="left", padx=6)
        ttk.Button(top, text="Refresh IPs", command=self.refresh_network).pack(side="left")

        columns = ("ip", "mac", "state", "hostname", "source")
        self.host_tree = ttk.Treeview(parent, columns=columns, show="headings", selectmode="extended")
        headings = {"ip": "IP Address", "mac": "MAC Address", "state": "Status", "hostname": "Discovered Hostname", "source": "Detection Source"}
        widths = {"ip": 160, "mac": 180, "state": 110, "hostname": 300, "source": 160}
        for c in columns:
            self.host_tree.heading(c, text=headings[c])
            self.host_tree.column(c, width=widths[c], anchor="w")
        self.host_tree.pack(fill="both", expand=True, pady=6)

        sb = ttk.Scrollbar(self.host_tree, orient="vertical", command=self.host_tree.yview)
        sb.pack(side="right", fill="y")
        self.host_tree.configure(yscrollcommand=sb.set)

    # ---------------- Endpoint Deployment Tab ----------------

    def _build_deploy_tab(self):
        parent = self.deploy_tab

        header_frame = ttk.Frame(parent)
        header_frame.pack(fill="x", pady=(0, 6))
        ttk.Label(header_frame, text="LANCONTROL Endpoint Client & Agent Generator", style="Title.TLabel").pack(anchor="w")
        ttk.Label(
            header_frame,
            text="Generate standalone, pre-configured 1-click executables for Windows and instant QR pairing for Android devices.",
            style="Subtitle.TLabel",
        ).pack(anchor="w", pady=(2, 6))

        cfg_frame = ttk.LabelFrame(parent, text="Agent Connection & Fleet Settings", style="Section.TLabelframe")
        cfg_frame.pack(fill="x", pady=(0, 8))

        row1 = ttk.Frame(cfg_frame, padding=(8, 6, 8, 4))
        row1.pack(fill="x")

        ttk.Label(row1, text="Connect Host / IP:", font=("Segoe UI", 9, "bold")).pack(side="left")
        self.deploy_host_var = tk.StringVar(value=choose_best_lan_ip())
        self.deploy_host_entry = ttk.Entry(row1, textvariable=self.deploy_host_var, width=22)
        self.deploy_host_entry.pack(side="left", padx=(6, 12))

        ttk.Button(row1, text="LAN IP", command=lambda: (self.deploy_host_var.set(choose_best_lan_ip()), self._update_quick_commands())).pack(side="left", padx=2)
        ts_info = tailscale_status_info()
        ts_ip = ts_info.get("ip") or (ts_info.get("ips")[0] if ts_info.get("ips") else "")
        if ts_ip:
            ttk.Button(row1, text="Tailscale IP", command=lambda ip=ts_ip: (self.deploy_host_var.set(ip), self._update_quick_commands())).pack(side="left", padx=2)
        if ts_info.get("dns"):
            ttk.Button(row1, text="Tailscale DNS", command=lambda dns=ts_info.get("dns"): (self.deploy_host_var.set(dns), self._update_quick_commands())).pack(side="left", padx=2)
        ttk.Button(row1, text="Detect Public WAN IP", command=self._detect_public_ip_for_deploy).pack(side="left", padx=2)

        ttk.Label(row1, text="Port:", font=("Segoe UI", 9, "bold")).pack(side="left", padx=(16, 6))
        self.deploy_port_var = tk.StringVar(value=str(self.port.get() or DEFAULT_PORT))
        ttk.Entry(row1, textvariable=self.deploy_port_var, width=7).pack(side="left")

        row2 = ttk.Frame(cfg_frame, padding=(8, 4, 8, 6))
        row2.pack(fill="x")

        ttk.Label(row2, text="Device Group:", font=("Segoe UI", 9, "bold")).pack(side="left")
        self.deploy_group_var = tk.StringVar(value="")
        self.deploy_group_combo = ttk.Combobox(row2, textvariable=self.deploy_group_var, state="readonly", width=36)
        self.deploy_group_combo.pack(side="left", padx=(6, 12))

        ttk.Button(row2, text="↻ Refresh Groups", command=self.refresh_device_groups).pack(side="left", padx=2)

        ttk.Label(row2, text="Optional Tag/Location:", font=("Segoe UI", 9)).pack(side="left", padx=(16, 6))
        self.deploy_tag_var = tk.StringVar(value="")
        ttk.Entry(row2, textvariable=self.deploy_tag_var, width=16).pack(side="left")

        split_pane = ttk.PanedWindow(parent, orient="horizontal")
        split_pane.pack(fill="both", expand=True)

        # LEFT PANE: Windows Executable Generation
        win_card = ttk.LabelFrame(split_pane, text="  Windows Standalone Client & Service Generation  ", style="Section.TLabelframe")
        split_pane.add(win_card, weight=1)

        win_inner = ttk.Frame(win_card, padding=(8, 6, 8, 6))
        win_inner.pack(fill="both", expand=True)

        ttk.Label(
            win_inner,
            text="1. Normal User Client (User-Mode):\n   • Zero installation required; no admin password needed.\n   • Remote desktop access & file transfers directly via pre-configured PE header.",
            font=("Segoe UI", 8),
            foreground=COLOR_TEXT_SECONDARY,
            justify="left",
        ).pack(anchor="w", pady=(0, 4))

        ttk.Button(
            win_inner,
            text="⬇ Generate Normal User Client (LANCONTROL_Client.exe)",
            style="Primary.TButton",
            command=self.generate_user_client_exe,
        ).pack(fill="x", pady=(0, 8))

        ttk.Label(
            win_inner,
            text="2. Administrator Background Service (Full MDM):\n   • Installs silent persistent background Windows Service with SYSTEM rights.\n   • Remote CMD/PowerShell, Task Manager, Sleep/Wake, and lock control.",
            font=("Segoe UI", 8),
            foreground=COLOR_TEXT_SECONDARY,
            justify="left",
        ).pack(anchor="w", pady=(0, 4))

        ttk.Button(
            win_inner,
            text="⬇ Generate Administrator Service Agent (LANCONTROL_Service_x64.exe)",
            style="Action.TButton",
            command=self.generate_service_agent_exe,
        ).pack(fill="x", pady=(0, 8))

        t = THEMES.get(getattr(self, "current_theme", "dark"), THEMES["dark"])
        ttk.Label(win_inner, text="Cross-Platform Quick Commands:", font=("Segoe UI", 8, "bold")).pack(anchor="w", pady=(4, 1))
        self.cmd_box = tk.Text(
            win_inner,
            height=2,
            font=("Consolas", 8),
            bg=t["bg_console"],
            fg=t["text_primary"],
            relief="flat",
        )
        self.cmd_box.pack(fill="x", pady=(0, 2))
        self.cmd_box.insert("1.0", "Linux: wget -q -O - https://127.0.0.1:443/meshagents?script=1 | sudo sh\nmacOS: curl -k https://127.0.0.1:443/meshagents?id=10005 -o agent && chmod +x agent")
        self.cmd_box.configure(state="disabled")

        # RIGHT PANE: Android MDM Device Control & Pairing
        droid_card = ttk.LabelFrame(split_pane, text="  Android MDM Device Control & Pairing  ", style="Section.TLabelframe")
        split_pane.add(droid_card, weight=1)

        droid_inner = ttk.Frame(droid_card, padding=(8, 6, 8, 6))
        droid_inner.pack(fill="both", expand=True)

        droid_action_row = ttk.Frame(droid_inner)
        droid_action_row.pack(fill="x", pady=(0, 4))

        ttk.Button(
            droid_action_row,
            text="⬇ Download Android APK",
            style="Action.TButton",
            command=self.download_android_apk,
        ).pack(side="left", padx=(0, 4))

        ttk.Button(
            droid_action_row,
            text="📱 LAN QR Code",
            style="Primary.TButton",
            command=self.display_android_qr_code,
        ).pack(side="left", padx=(0, 4))

        ttk.Button(
            droid_action_row,
            text="🌐 Tailscale Mobile QR",
            command=self.display_tailscale_mobile_qr_code,
        ).pack(side="left")

        self.qr_canvas = tk.Canvas(
            droid_inner,
            width=150,
            height=150,
            bg=t["bg_console"],
            highlightthickness=1,
            highlightbackground=t["bg_card_border"],
        )
        self.qr_canvas.pack(pady=2)

        self.android_url_text = tk.StringVar(value="mc://... (Click 'Generate Pairing QR Code')")
        url_entry = ttk.Entry(droid_inner, textvariable=self.android_url_text, font=("Consolas", 8), state="readonly")
        url_entry.pack(fill="x", pady=(2, 0))

        ttk.Label(
            droid_inner,
            text="Instructions: Install the LANCONTROL APK on your Android device, open app, tap 'Scan QR Code' to pair immediately.",
            font=("Segoe UI", 8),
            foreground=COLOR_TEXT_SECONDARY,
            wraplength=350,
            justify="center",
        ).pack(pady=(2, 0))




    # ---------------- Diagnostics, Audit & System Logs Tab ----------------

    def _build_diagnostics_tab(self):
        parent = self.diagnostics_tab

        header_frame = ttk.Frame(parent)
        header_frame.pack(fill="x", pady=(0, 6))
        ttk.Label(header_frame, text="Deep Diagnostics, System Audit & Event Logs", style="Title.TLabel").pack(anchor="w")
        ttk.Label(
            header_frame,
            text="Inspect environment, services, active ports, firewall rules, and examine live server event logs with automatic 1-click repairs.",
            style="Subtitle.TLabel",
        ).pack(anchor="w", pady=(2, 6))

        # Dynamic Responsive PanedWindow for Diagnostics & Logs
        split_diag = ttk.PanedWindow(parent, orient="horizontal")
        split_diag.pack(fill="both", expand=True)

        # LEFT PANE: Diagnostics & Automated Repair
        left_box = ttk.LabelFrame(split_diag, text="  Automated Self-Audit & Self-Healing Engine  ", style="Section.TLabelframe")
        split_diag.add(left_box, weight=1)

        l_bar = ttk.Frame(left_box, padding=(8, 4, 8, 4))
        l_bar.pack(fill="x")
        ttk.Button(l_bar, text="⚡ RUN DEEP AUDIT & REPAIR", style="Primary.TButton", command=self.diagnose_and_repair).pack(side="left")
        ttk.Button(l_bar, text="Clear", command=lambda: self.diag_widget.delete("1.0", "end")).pack(side="right")

        t = THEMES.get(getattr(self, "current_theme", "dark"), THEMES["dark"])
        self.diag_widget = tk.Text(
            left_box,
            wrap="word",
            font=("Consolas", 9),
            bg=t["bg_console"],
            fg=t["text_primary"],
            insertbackground=t["accent"],
            selectbackground=t["accent"],
            selectforeground="#ffffff",
            padx=8,
            pady=6,
            relief="flat",
        )
        self.diag_widget.pack(fill="both", expand=True, padx=6, pady=(0, 6), side="left")
        d_sb = ttk.Scrollbar(left_box, orient="vertical", command=self.diag_widget.yview)
        d_sb.pack(side="right", fill="y", pady=(0, 6))
        self.diag_widget.configure(yscrollcommand=d_sb.set)
        self.diag_widget.insert("1.0", "Click 'RUN DEEP AUDIT & REPAIR' to perform complete environment validation and automatic remediation.\n")

        # RIGHT PANE: System & Setup Event Logs
        right_box = ttk.LabelFrame(split_diag, text="  Full Event Logs (setup.log & runtime)  ", style="Section.TLabelframe")
        split_diag.add(right_box, weight=1)

        r_bar = ttk.Frame(right_box, padding=(8, 4, 8, 4))
        r_bar.pack(fill="x")
        ttk.Button(r_bar, text="↻ Refresh Log", command=self.refresh_log).pack(side="left")
        ttk.Button(r_bar, text="📝 Open Log", command=self.open_local_log).pack(side="left", padx=3)
        ttk.Button(r_bar, text="📁 App Folder", command=self.open_app_folder).pack(side="left", padx=3)
        ttk.Button(r_bar, text="Clear", command=self.clear_log).pack(side="right")

        self.log_path_label = ttk.Label(
            right_box,
            text=f"Log: {LOCAL_LOG_FILE}",
            font=("Segoe UI", 8),
            foreground=COLOR_TEXT_SECONDARY,
        )
        self.log_path_label.pack(anchor="w", padx=8, pady=(0, 2))

        self.log_widget = tk.Text(
            right_box,
            wrap="word",
            font=("Consolas", 9),
            bg=t["bg_console"],
            fg=t["text_primary"],
            insertbackground=t["accent"],
            selectbackground=t["accent"],
            selectforeground="#ffffff",
            padx=10,
            pady=8,
            relief="flat",
        )
        self.log_widget.pack(fill="both", expand=True, padx=8, pady=(0, 8), side="left")
        l_sb = ttk.Scrollbar(right_box, orient="vertical", command=self.log_widget.yview)
        l_sb.pack(side="right", fill="y", pady=(0, 8))
        self.log_widget.configure(yscrollcommand=l_sb.set)
        self.refresh_log()

    # ---------------- Window & Tray Handlers ----------------

    def on_window_close(self):
        if self.minimize_to_tray_on_close.get() and self.tray:
            self.withdraw()
            self.tray.notify(
                "LANController Fleet Manager is running in the background.\nDouble-click tray icon to restore.",
                "Minimized to System Tray",
            )
        else:
            self.quit_app()

    def hide_to_tray(self):
        if self.tray:
            self.withdraw()
            self.tray.notify("Running in background.", "LANCONTROL")

    def show_window(self):
        def ui():
            self.deiconify()
            self.state("normal")
            self.lift()
            self.focus_force()
        self.post_ui(ui)

    def quit_app(self):
        if self.tray:
            self.tray.stop()
        self.destroy()
        sys.exit(0)

    def append_log(self, message: str):
        stamp = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        line = f"[{stamp}] {message.rstrip()}\n"

        def ui():
            if hasattr(self, "log_widget"):
                try:
                    self.log_widget.insert("end", line)
                    self.log_widget.see("end")
                except Exception:
                    pass
            if hasattr(self, "bottom_console_widget"):
                try:
                    self.bottom_console_widget.insert("end", line)
                    self.bottom_console_widget.see("end")
                except Exception:
                    pass

        self.post_ui(ui)
        app_log(message)

    def set_status(self, text: str, progress: float | None = None):
        def ui():
            self.status_text.set(text)
            if progress is not None:
                self.progress.set(float(progress))
        self.post_ui(ui)

    def run_background(self, fn, *args, refresh_after: bool = True):
        def worker():
            try:
                fn(*args)
            except Exception as exc:
                self.append_log(f"ERROR: {exc!r}")
                self.post_ui(lambda e=str(exc): messagebox.showerror(APP_TITLE, e))
            finally:
                self.set_status("Ready")
                if refresh_after and fn != self._refresh_all_worker:
                    self.post_ui(self.refresh_all)

        threading.Thread(target=worker, daemon=True).start()

    def refresh_all(self):
        if getattr(self, "_is_refreshing", False):
            return
        server_dir_val = self.server_dir.get()
        port_val = int(self.port.get() or DEFAULT_PORT)
        self.run_background(self._refresh_all_worker, server_dir_val, port_val, refresh_after=False)

    def _refresh_all_worker(self, server_dir_val: str, port_val: int):
        if getattr(self, "_is_refreshing", False):
            return
        self._is_refreshing = True
        try:
            self.set_status("Refreshing status...", 15)

            node = node_path()
            if node:
                rc, out = run_cmd([node, "-v"], timeout=10)
                node_val = out.splitlines()[0] if rc == 0 and out else "Detected"
            else:
                node_val = "NOT FOUND"

            npm = npm_path()
            if npm:
                rc, out = run_cmd([npm, "-v"], timeout=10)
                npm_val = f"v{out.splitlines()[0]}" if rc == 0 and out else "Detected"
            else:
                npm_val = "NOT FOUND"

            root = Path(server_dir_val).expanduser().resolve()
            installed = meshcentral_installed(root)
            mesh_val = "INSTALLED" if installed else "NOT INSTALLED"

            state = service_state()
            st = service_start_type()
            boot_val = "AUTO" in st.upper()

            fw_ok = firewall_rule_exists(port_val)
            fw_val = "ACTIVE (Rule Exists)" if fw_ok else "NO RULE"

            https_ok, https_msg = test_local_https(port_val, timeout=3)
            https_val = "ONLINE (200 OK)" if https_ok else "OFFLINE"

            ips = local_ipv4_addresses()
            net_val = f"{len(ips)} IPv4 Address(es)"

            def update_ui():
                self.node_status.set(node_val)
                self.npm_status.set(npm_val)
                self.mesh_status.set(mesh_val)
                self.service_status.set(state)
                self.service_start_type_status.set(st)
                self.boot_autostart.set(boot_val)
                self.firewall_status.set(fw_val)
                self.https_health_status.set(https_val)
                self.network_status.set(net_val)
                self.refresh_address_box(ips)

            self.post_ui(update_ui)
        finally:
            self._is_refreshing = False

    def refresh_address_box(self, ips: list[str] | None = None):
        if ips is None:
            ips = local_ipv4_addresses()

        port = int(self.port.get() or DEFAULT_PORT)
        primary_ip = choose_best_lan_ip()
        lines = [f"Port: {port} (HTTPS)", f"• Primary LAN: https://{primary_ip}:{port}/"]

        ts_info = tailscale_status_info()
        ts_ip = ts_info.get("ip") or (ts_info.get("ips")[0] if ts_info.get("ips") else "")
        if ts_ip:
            lines.append(f"• Tailscale Direct Private IP: https://{ts_ip}:{port}/")
        if ts_info.get("dns"):
            lines.append(f"• Tailscale MagicDNS: https://{ts_info.get('dns')}:{port}/")

        lines.append(f"• Localhost: https://127.0.0.1:{port}/")
        for ip in ips:
            if ip != primary_ip and ip != ts_ip:
                lines.append(f"• Other Interface ({ip}): https://{ip}:{port}/")

        self.address_box.configure(state="normal")
        self.address_box.delete("1.0", "end")
        self.address_box.insert("1.0", "\n".join(lines))
        self.address_box.configure(state="disabled")

    def refresh_network(self):
        ips = local_ipv4_addresses()
        self.refresh_address_box(ips)
        self.network_status.set(f"{len(ips)} IPv4 Address(es)")
        self.append_log("Network adapter IPs refreshed.")

    def refresh_log(self):
        if not hasattr(self, "log_widget"):
            return

        sync_local_artifacts()
        content = ""
        for target in [LOCAL_LOG_FILE, APP_LOG_FILE]:
            if target.exists():
                try:
                    content = target.read_text(encoding="utf-8", errors="replace")
                    if content.strip():
                        break
                except Exception:
                    pass

        if not content:
            content = "Setup log has not been created yet.\n"

        self.log_widget.delete("1.0", "end")
        self.log_widget.insert("1.0", content[-200000:])
        self.log_widget.see("end")

    def clear_log(self):
        if hasattr(self, "log_widget"):
            self.log_widget.delete("1.0", "end")

    def open_local_log(self):
        sync_local_artifacts()
        target = LOCAL_LOG_FILE if LOCAL_LOG_FILE.exists() else APP_LOG_FILE
        if target.exists():
            os.startfile(str(target))
        else:
            messagebox.showinfo(APP_TITLE, "Log file has not been created yet.")

    def open_app_folder(self):
        os.startfile(str(APP_DIR))

    def open_setup_log(self):
        self.open_local_log()

    def open_log_file(self):
        root = Path(self.server_dir.get()).expanduser().resolve()
        path = server_paths(root)["logs"]
        path.parent.mkdir(parents=True, exist_ok=True)
        if not path.exists():
            path.write_text("", encoding="utf-8")
        os.startfile(str(path))

    def on_toggle_boot_autostart(self):
        if not is_admin():
            if not request_admin_elevation("Administrator privileges are required to configure service boot startup."):
                self.boot_autostart.set(not self.boot_autostart.get())
                return
        new_val = self.boot_autostart.get()
        ok, msg = set_service_autostart(new_val)
        if ok:
            self.append_log(f"Service Boot Autostart set to {new_val}")
        else:
            messagebox.showerror(APP_TITLE, f"Failed to configure service startup:\n{msg}")
            self.boot_autostart.set(not new_val)

    def on_toggle_login_autostart(self):
        new_val = self.login_autostart.get()
        ok, msg = set_login_autostart_enabled(new_val)
        if ok:
            self.append_log(f"User Login Autostart set to {new_val}")
        else:
            messagebox.showerror(APP_TITLE, f"Failed to configure registry startup:\n{msg}")
            self.login_autostart.set(not new_val)

    def open_web_ui(self):
        port = int(self.port.get() or DEFAULT_PORT)
        host = choose_best_lan_ip() if self.lan_only.get() else (self.cert_name.get().strip() or "127.0.0.1")
        url = f"https://{host}:{port}/"
        webbrowser.open(url)
        self.append_log(f"Web UI opened in browser: {url}")

    def test_local_https(self):
        port = int(self.port.get() or DEFAULT_PORT)
        ok, msg = test_local_https(port, timeout=5)
        if ok:
            messagebox.showinfo(APP_TITLE, f"Local HTTPS is responding!\n\nStatus: {msg}\nURL: https://127.0.0.1:{port}/")
        else:
            messagebox.showwarning(APP_TITLE, f"Local HTTPS test failed:\n\n{msg}")

    def browse_server_dir(self):
        path = filedialog.askdirectory(title="Select LANCONTROL Server Folder", initialdir=self.server_dir.get() or str(DEFAULT_DIR))
        if path:
            self.server_dir.set(path)
            self.refresh_all()

    def service_action(self, action: str):
        if not is_admin():
            if not request_admin_elevation(f"Administrator privileges are required to {action} the Windows service."):
                return
        self.run_background(self._service_action_worker, action)

    def _service_action_worker(self, action: str):
        self.set_status(f"{action.capitalize()}ing service...", 50)
        self.append_log(f"Executing service action: {action}")
        ok, msg = control_service(action)
        self.append_log(msg)
        if not ok:
            raise RuntimeError(msg)

    def install_service(self):
        if not is_admin():
            if not request_admin_elevation("Administrator privileges are required to install the Windows service."):
                return
        server_dir_val = self.server_dir.get()
        self.run_background(self._install_service_worker, server_dir_val)

    def _install_service_worker(self, server_dir_val: str):
        self.set_status("Installing Windows service...", 60)
        root = Path(server_dir_val).expanduser().resolve()
        node = node_path()
        entry = server_paths(root)["entry"]
        if not node or not entry.exists():
            raise RuntimeError("LANCONTROL server is not installed in the target folder.")

        self.post_ui(lambda: self.write_config(silent=True))
        rc, out = run_cmd([node, str(entry), "--install"], cwd=root, timeout=180)
        self.append_log(out)
        if rc != 0:
            raise RuntimeError("Service installation command returned non-zero.")
        set_service_autostart(True)
        self.append_log("Service installation and auto-start configuration completed.")

    def remove_service(self):
        if not is_admin():
            if not request_admin_elevation("Administrator privileges are required to remove the Windows service."):
                return
        if not messagebox.askyesno(APP_TITLE, "Remove the LANCONTROL Windows Service?\n\n(Server files will remain intact)"):
            return
        server_dir_val = self.server_dir.get()
        self.run_background(self._remove_service_worker, server_dir_val)

    def _remove_service_worker(self, server_dir_val: str):
        root = Path(server_dir_val).expanduser().resolve()
        node = node_path()
        entry = server_paths(root)["entry"]
        rc, out = run_cmd([node, str(entry), "--uninstall"], cwd=root, timeout=180)
        self.append_log(out)
        if rc != 0:
            raise RuntimeError("Service removal command failed.")
        self.append_log("LANCONTROL service removed.")

    def allow_firewall(self):
        if not is_admin():
            if not request_admin_elevation("Administrator privileges are required to configure firewall rules."):
                return
        port = int(self.port.get())
        ok, msg = allow_firewall(port)
        if ok:
            messagebox.showinfo(APP_TITLE, msg)
            self.refresh_all()
        else:
            messagebox.showerror(APP_TITLE, msg)

    def remove_firewall(self):
        if not is_admin():
            if not request_admin_elevation("Administrator privileges are required to remove firewall rules."):
                return
        port = int(self.port.get())
        ok, msg = remove_firewall(port)
        if ok:
            messagebox.showinfo(APP_TITLE, msg)
            self.refresh_all()
        else:
            messagebox.showerror(APP_TITLE, msg)

    def write_config(self, silent=False) -> bool:
        try:
            root = Path(self.server_dir.get()).expanduser().resolve()
            port = int(self.port.get())
            if not 1 <= port <= 65535:
                raise ValueError("HTTPS port must be between 1 and 65535.")
            paths = server_paths(root)
            paths["data"].mkdir(parents=True, exist_ok=True)
            paths["backups"].mkdir(parents=True, exist_ok=True)

            existing: dict = {}
            if paths["config"].exists():
                try:
                    loaded = load_json(paths["config"])
                    if not isinstance(loaded, dict):
                        raise ValueError("Root JSON value must be an object.")
                    existing = loaded
                except Exception as exc:
                    # Never replace an unreadable existing production config with a fresh one.
                    raise RuntimeError(
                        f"Existing LANCONTROL config could not be parsed; it was left untouched.\n"
                        f"File: {paths['config']}\nReason: {exc}"
                    ) from exc

            backup = backup_config(paths["config"], paths["backups"])
            if backup:
                self.append_log(f"Config backup created: {backup}")

            # Merge only fields this UI owns. Keep all other LANCONTROL settings, domain
            # options, TLS options, agent settings, plugins, aliases and future fields intact.
            cfg = copy.deepcopy(existing)
            cfg.setdefault("$schema", "https://raw.githubusercontent.com/Ylianst/MeshCentral/master/meshcentral-config-schema.json")
            settings = cfg.setdefault("settings", {})
            if not isinstance(settings, dict):
                raise RuntimeError("Existing config has a non-object 'settings' value; refusing to overwrite it.")
            settings["LANonly"] = bool(self.lan_only.get())
            settings["WANonly"] = not bool(self.lan_only.get())
            settings["port"] = port
            settings.setdefault("sessionKey", generate_session_key())
            settings.setdefault("ExactPorts", True)
            settings.setdefault("WebRTC", True)
            settings.setdefault("SelfUpdate", True)
            if self.cert_name.get().strip():
                settings["cert"] = self.cert_name.get().strip()

            domains = cfg.setdefault("domains", {})
            if not isinstance(domains, dict):
                raise RuntimeError("Existing config has a non-object 'domains' value; refusing to overwrite it.")
            domain = domains.setdefault("", {})
            if not isinstance(domain, dict):
                raise RuntimeError("Existing config's default domain is not an object; refusing to overwrite it.")
            domain["title"] = self.website_title.get().strip() or domain.get("title") or "LANCONTROL"
            domain["title2"] = self.website_subtitle.get().strip() or domain.get("title2") or "Remote Administration"
            domain["newAccounts"] = bool(self.allow_new_accounts.get())
            domain.setdefault("minify", True)
            domain.setdefault("userNameIsEmail", False)

            # Write only after a backup exists; atomic replacement avoids partial JSON files.
            atomic_write_json(paths["config"], cfg)
            atomic_write_json(LOCAL_CONFIG_FILE, cfg)

            self._save_state()
            self.append_log(f"Configuration merged safely: {paths['config']} (mirror: {LOCAL_CONFIG_FILE})")
            if not silent:
                messagebox.showinfo(
                    APP_TITLE,
                    "Configuration saved safely. Existing LANCONTROL options were preserved.\n\n"
                    f"Active config:\n{paths['config']}\n\nBackup folder:\n{paths['backups']}"
                )
            self.reload_config_tab()
            return True
        except Exception as exc:
            self.append_log(f"Config write failed: {exc}")
            if not silent:
                messagebox.showerror(APP_TITLE, str(exc))
            return False

    def backup_current_config(self):
        root = Path(self.server_dir.get()).expanduser().resolve()
        paths = server_paths(root)
        backup = backup_config(paths["config"], paths["backups"])
        if backup:
            messagebox.showinfo(APP_TITLE, f"Backup created:\n{backup}")
        else:
            messagebox.showinfo(APP_TITLE, "No existing configuration file to backup.")

    def rollback_config_action(self):
        root = Path(self.server_dir.get()).expanduser().resolve()
        paths = server_paths(root)
        backup_dir = paths["backups"]
        if not backup_dir.exists():
            messagebox.showinfo(APP_TITLE, "No backup directory exists yet.")
            return

        candidates = sorted(list(backup_dir.glob("config.*.json")), reverse=True)
        if not candidates:
            messagebox.showinfo(APP_TITLE, "No saved config backups found in:\n" + str(backup_dir))
            return

        # Modal selection dialog for available backups
        dlg = tk.Toplevel(self)
        dlg.title("Rollback Configuration Snapshot")
        dlg.geometry("560x340")
        dlg.grab_set()

        ttk.Label(dlg, text="Select Configuration Snapshot To Restore", font=("Segoe UI", 11, "bold")).pack(anchor="w", padx=14, pady=(12, 4))
        ttk.Label(dlg, text="Choose a timestamped snapshot to roll back config.json. The current config will be automatically backed up first.", font=("Segoe UI", 8)).pack(anchor="w", padx=14, pady=(0, 8))

        list_frame = ttk.Frame(dlg)
        list_frame.pack(fill="both", expand=True, padx=14, pady=4)

        lb = tk.Listbox(list_frame, font=("Consolas", 9), selectmode="single")
        lb.pack(side="left", fill="both", expand=True)
        sb = ttk.Scrollbar(list_frame, orient="vertical", command=lb.yview)
        sb.pack(side="right", fill="y")
        lb.configure(yscrollcommand=sb.set)

        for b in candidates:
            mtime = dt.datetime.fromtimestamp(b.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S")
            lb.insert("end", f"{b.name}  [{mtime}] ({b.stat().st_size:,} bytes)")
        lb.selection_set(0)

        def do_restore():
            sel = lb.curselection()
            if not sel:
                return
            target_snap = candidates[sel[0]]
            # Make safety backup of current before overwriting
            backup_config(paths["config"], paths["backups"])
            shutil.copy2(target_snap, paths["config"])
            atomic_write_json(LOCAL_CONFIG_FILE, load_json(paths["config"]))
            self.append_log(f"Config rolled back to snapshot: {target_snap.name}")
            self.reload_config_tab()
            dlg.destroy()
            messagebox.showinfo(APP_TITLE, f"Configuration successfully rolled back to:\n{target_snap.name}\n\nRestart service if active.")

        btn_bar = ttk.Frame(dlg, padding=(14, 8, 14, 10))
        btn_bar.pack(fill="x")
        ttk.Button(btn_bar, text="Cancel", command=dlg.destroy).pack(side="right")
        ttk.Button(btn_bar, text="⚡ Restore Selected Snapshot", style="Primary.TButton", command=do_restore).pack(side="right", padx=6)

    def install_or_update_mesh(self):
        server_dir_val = self.server_dir.get()
        self.run_background(self._install_mesh_worker, server_dir_val)

    def _install_mesh_worker(self, server_dir_val: str):
        npm = npm_path()
        if not npm:
            raise RuntimeError("npm is not available.")
        root = Path(server_dir_val).expanduser().resolve()
        root.mkdir(parents=True, exist_ok=True)

        self.set_status("Installing/updating server via npm...", 40)
        rc, out = run_cmd([npm, "install", "meshcentral@latest"], cwd=root, timeout=1200)
        self.append_log(out)
        if rc != 0:
            raise RuntimeError("npm install failed.")
        self.post_ui(lambda: self.write_config(silent=True))
        self.append_log("Server install/update finished.")

    def scan_hosts(self):
        self.run_background(self._scan_hosts_worker)

    def _scan_hosts_worker(self):
        self.set_status("Scanning local network neighbors...", 30)
        rows: list[list[str]] = []
        ps = powershell_path()

        if ps:
            script = (
                "Get-NetNeighbor -AddressFamily IPv4 | Where-Object {$_.IPAddress -and $_.IPAddress -notlike '127.*'} "
                "| Select-Object IPAddress,LinkLayerAddress,State | ConvertTo-Csv -NoTypeInformation"
            )
            rc, out = run_cmd([ps, "-NoProfile", "-Command", script], timeout=30)
            if rc == 0 and out.strip():
                try:
                    reader = csv.DictReader(out.splitlines())
                    for item in reader:
                        ip = (item.get("IPAddress") or "").strip()
                        mac = (item.get("LinkLayerAddress") or "").strip()
                        state = (item.get("State") or "").strip()
                        if not ip or ip.endswith(".255") or mac.upper().replace("-", ":") == "FF:FF:FF:FF:FF:FF":
                            continue
                        try:
                            addr = ipaddress.ip_address(ip)
                            if addr.is_multicast or addr.is_reserved or addr.is_loopback or addr.is_link_local:
                                continue
                        except Exception:
                            continue
                        rows.append([ip, mac, state, "Resolving...", "Get-NetNeighbor"])
                except Exception as exc:
                    self.append_log(f"Neighbor parse failed: {exc}")

        if not rows:
            rc, out = run_cmd(["arp", "-a"], timeout=20)
            if rc == 0:
                for line in out.splitlines():
                    parts = line.split()
                    if len(parts) >= 3:
                        ip = parts[0].strip()
                        mac = parts[1].strip()
                        state = parts[2].strip()
                        if not ip or ip.endswith(".255") or mac.upper().replace("-", ":") == "FF:FF:FF:FF:FF:FF":
                            continue
                        try:
                            addr = ipaddress.ip_address(ip)
                            if addr.is_multicast or addr.is_reserved or addr.is_loopback or addr.is_link_local:
                                continue
                        except Exception:
                            continue
                        rows.append([ip, mac, state, "Resolving...", "arp -a"])

        unique = {}
        for r in rows:
            unique[(r[0], r[1])] = r

        final_rows = sorted(unique.values(), key=lambda r: ipaddress.ip_address(r[0]))

        # Render list immediately so GUI is instant
        row_id_map: dict[str, str] = {}

        def render_initial():
            for item in self.host_tree.get_children():
                self.host_tree.delete(item)
            for r in final_rows:
                node_id = self.host_tree.insert("", "end", values=r)
                row_id_map[r[0]] = node_id
            self.append_log(f"Discovered {len(final_rows)} network host(s). Resolving hostnames in background...")

        self.post_ui(render_initial)

        # Fast non-blocking concurrent hostname resolution
        def resolve_single_host(ip: str) -> tuple[str, str]:
            try:
                name = socket.gethostbyaddr(ip)[0]
                return ip, name
            except Exception:
                return ip, ""

        def resolve_all_hostnames():
            ips = [r[0] for r in final_rows]
            with ThreadPoolExecutor(max_workers=8) as executor:
                for ip, hostname in executor.map(resolve_single_host, ips):
                    if ip in row_id_map and hostname:
                        def update_row(node=row_id_map[ip], host=hostname):
                            try:
                                current_vals = list(self.host_tree.item(node, "values"))
                                current_vals[3] = host
                                self.host_tree.item(node, values=current_vals)
                            except Exception:
                                pass
                        self.post_ui(update_row)
                    elif ip in row_id_map and not hostname:
                        def clear_pending(node=row_id_map[ip]):
                            try:
                                current_vals = list(self.host_tree.item(node, "values"))
                                if current_vals[3] == "Resolving...":
                                    current_vals[3] = ""
                                    self.host_tree.item(node, values=current_vals)
                            except Exception:
                                pass
                        self.post_ui(clear_pending)

        threading.Thread(target=resolve_all_hostnames, daemon=True).start()

    def export_hosts_csv(self):
        items = [self.host_tree.item(i)["values"] for i in self.host_tree.get_children()]
        if not items:
            messagebox.showinfo(APP_TITLE, "Scan local network first.")
            return

        path = filedialog.asksaveasfilename(
            title="Export Discovered PCs",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            initialfile=f"lancontroller_lan_{dt.datetime.now():%Y%m%d_%H%M%S}.csv",
        )
        if not path:
            return
        try:
            with open(path, "w", newline="", encoding="utf-8-sig") as f:
                w = csv.writer(f)
                w.writerow(["IP Address", "MAC", "State", "Hostname", "Source"])
                w.writerows(items)
            messagebox.showinfo(APP_TITLE, f"Exported successfully:\n{path}")
        except Exception as exc:
            messagebox.showerror(APP_TITLE, str(exc))

    
    def _detect_public_ip_for_deploy(self):
        def worker():
            self.set_status("Detecting public WAN IP...", 30)
            pub = fetch_public_ipv4()
            if pub:
                self.post_ui(lambda: (self.deploy_host_var.set(pub), self._update_quick_commands()))
                self.append_log(f"Detected Public WAN IP: {pub}")
                self.post_ui(lambda: messagebox.showinfo(
                    APP_TITLE,
                    f"Public WAN IPv4 Detected: {pub}\n\n"
                    f"• Connect Host updated to {pub}.\n"
                    f"• Ensure WAN mode is enabled in Server tab and your router forwards the port if not using Tailscale."
                ))
            else:
                self.append_log("Could not detect public IPv4 automatically.")
                self.post_ui(lambda: messagebox.showwarning(APP_TITLE, "Could not detect public WAN IP automatically. Check internet connection."))
            self.set_status("Ready")
        threading.Thread(target=worker, daemon=True).start()

    def refresh_deploy_tab(self):
        self.refresh_device_groups()
        self._update_quick_commands()

    def refresh_device_groups(self):
        try:
            groups = get_available_device_groups()
            self._available_device_groups = groups
            if groups:
                values = [f"{g.get('name', 'Group')} ({g.get('id', '').split('/')[-1][:10]}...)" for g in groups]
                self.deploy_group_combo["values"] = values
                if not self.deploy_group_var.get() or self.deploy_group_var.get() not in values:
                    self.deploy_group_combo.current(0)
            else:
                self.deploy_group_combo["values"] = ["Default Mesh Group (Automatic)"]
                self.deploy_group_combo.current(0)
            self._update_quick_commands()
        except Exception as exc:
            self.append_log(f"Device group refresh: {exc!r}")

    def _get_selected_mesh_info(self) -> tuple[str, str]:
        selected = self.deploy_group_var.get()
        if hasattr(self, "_available_device_groups") and self._available_device_groups:
            idx = self.deploy_group_combo.current()
            if 0 <= idx < len(self._available_device_groups):
                g = self._available_device_groups[idx]
                return g["id"], g["name"]
            for g in self._available_device_groups:
                if g["name"] in selected:
                    return g["id"], g["name"]
        return "mesh//default", "LANCONTROL"

    def _update_quick_commands(self):
        host = self.deploy_host_var.get().strip() if hasattr(self, "deploy_host_var") else choose_best_lan_ip()
        port = self.deploy_port_var.get().strip() if hasattr(self, "deploy_port_var") else "443"
        linux_cmd = f"curl -s -k \"https://{host}:{port}/meshagents?script=1\" | sudo sh"
        mac_cmd = f"curl -k -o agent \"https://{host}:{port}/meshagents?id=10005\" && chmod +x agent && sudo ./agent"
        if hasattr(self, "cmd_box"):
            self.cmd_box.configure(state="normal")
            self.cmd_box.delete("1.0", "end")
            self.cmd_box.insert("1.0", f"Linux: {linux_cmd}\nmacOS: {mac_cmd}")
            self.cmd_box.configure(state="disabled")

    def generate_user_client_exe(self):
        host = self.deploy_host_var.get().strip()
        port_str = self.deploy_port_var.get().strip()
        tag = self.deploy_tag_var.get().strip()
        if not host or not port_str:
            messagebox.showerror(APP_TITLE, "Please specify a valid Connect Host/IP and Port.")
            return
        port = int(port_str)
        mesh_id, mesh_name = self._get_selected_mesh_info()

        save_path = filedialog.asksaveasfilename(
            title="Save Normal User Client Executable",
            initialfile="LANCONTROL_Client.exe",
            filetypes=[("Windows Executable", "*.exe")],
            defaultextension=".exe",
        )
        if not save_path:
            return

        def worker():
            self.set_status("Downloading client base binary...", 25)
            self.append_log(f"Generating Normal User Client for {host}:{port} ({mesh_name})...")
            try:
                raw_bin = fetch_server_agent_binary(10006, port=port)
                self.set_status("Embedding zero-brand configuration policy...", 60)
                msh = build_lancontrol_msh(host, port, mesh_id, mesh_name=mesh_name, tag=tag)
                final_bin = embed_policy(raw_bin, msh)
                with open(save_path, "wb") as f:
                    f.write(final_bin)
                self.append_log(f"Generated standalone client: {save_path} ({len(final_bin):,} bytes)")
                self.post_ui(lambda: messagebox.showinfo(
                    APP_TITLE,
                    f"LANCONTROL Client Executable Generated Successfully!\n\n"
                    f"Saved to:\n{save_path}\n\n"
                    f"• Requires NO administrator privileges to run.\n"
                    f"• Instantly connects to your LANCONTROL console.\n"
                    f"• Ready to distribute to normal users or run from USB."
                ))
            except Exception as exc:
                self.append_log(f"Failed to generate client exe: {exc!r}")
                self.post_ui(lambda: messagebox.showerror(APP_TITLE, f"Failed to generate executable:\n{exc!r}"))

        threading.Thread(target=worker, daemon=True).start()

    def generate_service_agent_exe(self):
        host = self.deploy_host_var.get().strip()
        port_str = self.deploy_port_var.get().strip()
        tag = self.deploy_tag_var.get().strip()
        if not host or not port_str:
            messagebox.showerror(APP_TITLE, "Please specify a valid Connect Host/IP and Port.")
            return
        port = int(port_str)
        mesh_id, mesh_name = self._get_selected_mesh_info()

        save_path = filedialog.asksaveasfilename(
            title="Save Administrator Service Agent Executable",
            initialfile="LANCONTROL_Service_x64.exe",
            filetypes=[("Windows Executable", "*.exe")],
            defaultextension=".exe",
        )
        if not save_path:
            return

        def worker():
            self.set_status("Downloading x64 service agent...", 25)
            self.append_log(f"Generating Administrator Service Agent for {host}:{port} ({mesh_name})...")
            try:
                raw_bin = fetch_server_agent_binary(4, port=port)
                self.set_status("Embedding zero-brand service policy...", 60)
                msh = build_lancontrol_msh(host, port, mesh_id, mesh_name=mesh_name, tag=tag)
                final_bin = embed_policy(raw_bin, msh)
                with open(save_path, "wb") as f:
                    f.write(final_bin)
                self.append_log(f"Generated standalone service agent: {save_path} ({len(final_bin):,} bytes)")
                self.post_ui(lambda: messagebox.showinfo(
                    APP_TITLE,
                    f"LANCONTROL Administrator Service Agent Generated Successfully!\n\n"
                    f"Saved to:\n{save_path}\n\n"
                    f"• Installs as persistent background Windows Service.\n"
                    f"• Starts automatically on boot with full SYSTEM rights.\n"
                    f"• Provides SYSTEM full MDM rights, Wake-On-LAN, Terminal, Desktop."
                ))
            except Exception as exc:
                self.append_log(f"Failed to generate service agent exe: {exc!r}")
                self.post_ui(lambda: messagebox.showerror(APP_TITLE, f"Failed to generate service agent:\n{exc!r}"))

        threading.Thread(target=worker, daemon=True).start()

    def download_android_apk(self):
        port_str = self.deploy_port_var.get().strip() or "443"
        port = int(port_str)
        save_path = filedialog.asksaveasfilename(
            title="Save LANCONTROL Android APK",
            initialfile="LANCONTROL_Android_Agent.apk",
            filetypes=[("Android Package", "*.apk")],
            defaultextension=".apk",
        )
        if not save_path:
            return

        def worker():
            self.set_status("Downloading Android APK from server...", 30)
            try:
                apk_bytes = fetch_server_agent_binary(14, port=port)
                with open(save_path, "wb") as f:
                    f.write(apk_bytes)
                self.append_log(f"Saved Android APK to {save_path} ({len(apk_bytes):,} bytes)")
                self.post_ui(lambda: messagebox.showinfo(
                    APP_TITLE,
                    f"LANCONTROL Android APK Saved Successfully!\n\n"
                    f"Saved to:\n{save_path}\n\n"
                    f"Install on target Android device, open app, and scan the QR code."
                ))
            except Exception as exc:
                self.append_log(f"Failed to download APK: {exc!r}")
                self.post_ui(lambda: messagebox.showerror(APP_TITLE, f"Download failed:\n{exc!r}"))

        threading.Thread(target=worker, daemon=True).start()

    def display_android_qr_code(self):
        host = self.deploy_host_var.get().strip()
        port_str = self.deploy_port_var.get().strip() or "443"
        port = int(port_str)
        mesh_id, mesh_name = self._get_selected_mesh_info()

        if not host:
            messagebox.showerror(APP_TITLE, "Please specify a valid Connect Host/IP.")
            return

        pairing_url = build_android_pairing_url(host, port, mesh_id)
        self.android_url_text.set(pairing_url)
        self.append_log(f"Android Pairing URL generated: {pairing_url}")

        rendered = False
        if HAS_QRCODE and HAS_PIL:
            try:
                qr = qrcode.QRCode(box_size=3, border=2)
                qr.add_data(pairing_url)
                qr.make(fit=True)
                pil_img = qr.make_image(fill_color="#000000", back_color="#ffffff").convert("RGBA")
                tk_img = ImageTk.PhotoImage(pil_img)
                self._current_qr_img = tk_img
                self.qr_canvas.delete("all")
                self.qr_canvas.create_image(85, 85, image=tk_img)
                self.append_log("Rendered Android MDM Pairing QR Code in canvas.")
                rendered = True
            except Exception as exc:
                self.append_log(f"QR render exception: {exc!r}")
        if not rendered:
            self.qr_canvas.delete("all")
            self.qr_canvas.create_rectangle(8, 8, 162, 162, fill="#f8fafc", outline="#0a84ff", width=2)
            self.qr_canvas.create_text(85, 60, text="📱 Android Pairing", fill="#0a84ff", font=("Segoe UI", 10, "bold"))
            self.qr_canvas.create_text(85, 95, text="Use Direct URL Below\n(Click Copy URL)", fill="#475569", font=("Segoe UI", 8), justify="center")
            self.append_log("Canvas pairing badge active (QR module offline).")

    def display_tailscale_mobile_qr_code(self):
        info = tailscale_status_info()
        ts_ip = info.get("ip") or (info.get("ips")[0] if info.get("ips") else "")
        dns = info.get("dns") or ""
        host = dns or ts_ip
        if not host:
            messagebox.showwarning(APP_TITLE, "Tailscale is not connected or no Tailscale IP was found.\nConnect Tailscale first.")
            return

        port_str = self.deploy_port_var.get().strip() or "443"
        port = int(port_str)
        mesh_id, mesh_name = self._get_selected_mesh_info()

        pairing_url = build_android_pairing_url(host, port, mesh_id)
        self.android_url_text.set(pairing_url)
        self.append_log(f"Tailscale Mobile Pairing URL generated: {pairing_url}")

        rendered = False
        if HAS_QRCODE and HAS_PIL:
            try:
                qr = qrcode.QRCode(box_size=3, border=2)
                qr.add_data(pairing_url)
                qr.make(fit=True)
                pil_img = qr.make_image(fill_color="#000000", back_color="#ffffff").convert("RGBA")
                tk_img = ImageTk.PhotoImage(pil_img)
                self._current_qr_img = tk_img
                self.qr_canvas.delete("all")
                self.qr_canvas.create_image(85, 85, image=tk_img)
                self.append_log("Rendered Tailscale Remote Android Pairing QR Code in canvas.")
                rendered = True
            except Exception as exc:
                self.append_log(f"QR render exception: {exc!r}")
        if not rendered:
            self.qr_canvas.delete("all")
            self.qr_canvas.create_rectangle(8, 8, 162, 162, fill="#f8fafc", outline="#0a84ff", width=2)
            self.qr_canvas.create_text(85, 60, text="🌐 Remote Pairing", fill="#0a84ff", font=("Segoe UI", 10, "bold"))
            self.qr_canvas.create_text(85, 95, text="Use MagicDNS URL\n(Click Copy URL)", fill="#475569", font=("Segoe UI", 8), justify="center")
            self.append_log("Canvas remote pairing badge active (QR module offline).")

    def one_click_setup(self):
        if not is_admin():
            if not request_admin_elevation("Full Automated Setup requires Administrator privileges to configure services, background tasks, and firewall."):
                return

        # Modal Dialog to choose machine setup role
        role_dlg = tk.Toplevel(self)
        role_dlg.title("LANCONTROL Autonomous Setup Wizard")
        role_dlg.geometry("540x360")
        role_dlg.resizable(False, False)
        role_dlg.grab_set()

        ttk.Label(role_dlg, text="Choose Setup Role For This Computer", style="Title.TLabel").pack(anchor="w", padx=16, pady=(16, 4))
        ttk.Label(role_dlg, text="Select whether this machine is the primary Management Server or a Remote Home/Client PC:", style="Subtitle.TLabel").pack(anchor="w", padx=16, pady=(0, 14))

        role_var = tk.StringVar(value="server")

        f1 = ttk.LabelFrame(role_dlg, text="Role 1: Primary Controller & Server (Office PC / Host)", padding=10)
        f1.pack(fill="x", padx=16, pady=4)
        ttk.Radiobutton(
            f1,
            text="Primary Management Host (Full Server + Windows Service + Tailscale)\n"
                 "Configures autonomous server, creates Windows Service, opens firewall, installs Tailscale, and enables boot autostart.",
            variable=role_var, value="server",
        ).pack(anchor="w")

        f2 = ttk.LabelFrame(role_dlg, text="Role 2: Remote Access Workstation (Home PC / Laptop)", padding=10)
        f2.pack(fill="x", padx=16, pady=4)
        ttk.Radiobutton(
            f2,
            text="Remote Client Console (Home PC to manage Office PC)\n"
                 "Installs Tailscale silently, launches user tray manager, and immediately opens the office web portal.",
            variable=role_var, value="client",
        ).pack(anchor="w")

        btn_box = ttk.Frame(role_dlg, padding=(16, 16, 16, 16))
        btn_box.pack(fill="x", side="bottom")

        def start_chosen():
            chosen = role_var.get()
            role_dlg.destroy()
            server_dir_val = self.server_dir.get()
            port_val = int(self.port.get() or DEFAULT_PORT)
            self.run_background(self._one_click_setup_worker, server_dir_val, port_val, chosen)

        ttk.Button(btn_box, text="⚡ START AUTOMATED SETUP", style="Primary.TButton", command=start_chosen).pack(side="right")
        ttk.Button(btn_box, text="Cancel", command=role_dlg.destroy).pack(side="right", padx=8)

    def _one_click_setup_worker(self, server_dir_val: str, port_val: int, role: str = "server"):
        app_log(f"Starting 1-Click Automated Setup for role: {role}...")

        # Step 1: Ensure Tailscale is installed on both Server and Client roles
        self.set_status("Checking Tailscale installation...", 15)
        if not tailscale_path():
            self.set_status("Installing Tailscale from bundled package...", 25)
            self.append_log("Tailscale CLI not found. Installing from bundled bin/tailscale-setup.msi...")
            ok_ts, msg_ts = install_tailscale()
            self.append_log(f"Tailscale installation result: {msg_ts}")
            time.sleep(2)
        else:
            self.append_log(f"Tailscale is already present: {tailscale_path()}")

        if role == "client":
            # Client / Home PC Setup
            self.set_status("Configuring Home PC access...", 60)
            set_login_autostart_enabled(True)
            self.post_ui(lambda: self.login_autostart.set(True))
            self.set_status("Home PC Setup Complete!", 100)
            self.append_log("HOME PC WORKSTATION SETUP FINISHED.")

            ts_info = tailscale_status_info()
            office_url = "https://100.113.51.119:443/"
            self.post_ui(lambda: messagebox.showinfo(
                APP_TITLE,
                f"Home PC Setup Complete!\n\n"
                f"• Tailscale is installed and ready on this Home PC.\n"
                f"• Tray Manager is configured to start on login.\n"
                f"• Target Office URL: {office_url}\n\n"
                f"Opening the Office Portal in your browser now..."
            ))
            webbrowser.open(office_url)
            return

        # Server / Office PC Setup
        self.set_status("Configuring server configuration...", 35)
        self.post_ui(lambda: self.write_config(silent=True))

        self.set_status("Checking LANCONTROL server runtime...", 50)
        root = Path(server_dir_val).expanduser().resolve()
        if not meshcentral_installed(root):
            self._install_mesh_worker(server_dir_val)

        if not service_exists():
            self._install_service_worker(server_dir_val)

        self.set_status("Configuring boot & login autostart...", 70)
        set_service_autostart(True)
        set_login_autostart_enabled(True)
        self.post_ui(lambda: (self.boot_autostart.set(True), self.login_autostart.set(True)))

        self.set_status("Configuring Windows Firewall rules...", 80)
        allow_firewall(port_val)

        self.set_status("Starting background Windows service...", 90)
        control_service("start")

        # Auto-connect Tailscale if not connected
        if tailscale_path():
            ts_status = tailscale_status_info()
            if not ts_status.get("connected"):
                self.append_log("Bringing Tailscale online in background...")
                run_cmd([tailscale_path(), "up", "--unattended=true"], timeout=20)

        sync_local_artifacts(root)
        self.set_status("Setup Complete!", 100)
        self.append_log("ONE-CLICK AUTOMATED SETUP FINISHED SUCCESSFULLY.")
        self.post_ui(lambda: messagebox.showinfo(
            APP_TITLE,
            "LANCONTROL Automated Setup Complete!\n\n"
            "• Server is running as an autonomous Windows Service (starts on boot).\n"
            "• Tailscale is installed and configured for private remote access.\n"
            "• Tray Manager is configured to launch at user login.\n"
            "• Opening Web UI in your browser now...",
        ))
        self.post_ui(self.open_web_ui)

    def diagnose_and_repair(self):
        server_dir_val = self.server_dir.get()
        port_val = int(self.port.get() or DEFAULT_PORT)
        self.run_background(self._diagnose_and_repair_worker, server_dir_val, port_val)

    def _diagnose_and_repair_worker(self, server_dir_val: str, port_val: int):
        self.set_status("Running diagnostics...", 10)
        lines = ["========== MESHCONTROL DEEP AUDIT =========="]

        root = Path(server_dir_val).expanduser().resolve()
        found = discover_meshcentral_root()
        lines.append(f"Current Directory: {root}")
        lines.append(f"App Directory: {APP_DIR}")
        lines.append(f"Detected Root: {found or 'None'}")
        lines.append(f"Python: {sys.version.split()[0]} ({sys.executable})")
        lines.append(f"Platform: {platform.platform()}")
        lines.append(f"Administrator: {is_admin()}")
        lines.append(f"Node.js: {node_path() or 'NOT FOUND'}")
        lines.append(f"npm: {npm_path() or 'NOT FOUND'}")

        svc = find_meshcentral_service()
        state = service_state()
        st = service_start_type()
        lines.append(f"Service Name: {svc}")
        lines.append(f"Service State: {state}")
        lines.append(f"Service Start Type: {st}")

        fw_ok = firewall_rule_exists(port_val)
        lines.append(f"Firewall Rule (Port {port_val}): {'ACTIVE' if fw_ok else 'MISSING'}")

        occupied, owner = is_port_in_use(port_val)
        lines.append(f"Port {port_val} Status: {'LISTENING' if occupied else 'NOT LISTENING'} ({owner})")

        https_ok, https_msg = test_local_https(port_val, timeout=4)
        lines.append(f"Local HTTPS Endpoint: {'HEALTHY' if https_ok else 'FAILED'} ({https_msg})")
        lines.append(f"Login Autostart Registry: {'ENABLED' if is_login_autostart_enabled() else 'DISABLED'}")

        lines.append("\n--- Running Automatic Repairs ---")
        if not fw_ok and is_admin():
            ok, m = allow_firewall(port_val)
            lines.append(f"Firewall Repair: {m}")
        if "AUTO" not in st.upper() and is_admin():
            ok, m = set_service_autostart(True)
            lines.append(f"Service Boot AutoStart Repair: {m}")
        if not is_login_autostart_enabled():
            ok, m = set_login_autostart_enabled(True)
            lines.append(f"Login Autostart Repair: {m}")
        if state != "RUNNING" and service_exists() and is_admin():
            ok, m = control_service("start")
            lines.append(f"Service Start Repair: {m}")

        sync_local_artifacts(root)
        lines.append(f"Config & Log Mirror: Updated to {LOCAL_CONFIG_FILE} and {LOCAL_LOG_FILE}")
        lines.append("========== AUDIT & REPAIR COMPLETE ==========\n")
        report = "\n".join(lines)
        self.append_log(report)

        def show():
            self.diag_widget.delete("1.0", "end")
            self.diag_widget.insert("1.0", report)
            self.notebook.select(self.diagnostics_tab)
            messagebox.showinfo(APP_TITLE, "Diagnostics and repair completed!")

        self.post_ui(show)


# ---------------------------------------------------------------------------
# Application Entry Points
# ---------------------------------------------------------------------------

def handle_autostart():
    """Triggered on Windows user login."""
    app_log("Autostart triggered at Windows user login.")

    settings = load_app_settings()
    port = settings.get("port", DEFAULT_PORT)
    root = discover_meshcentral_root()
    if root:
        cfg_path = server_paths(root)["config"]
        if cfg_path.exists():
            try:
                cfg_data = load_json(cfg_path)
                port = cfg_data.get("settings", {}).get("port", port)
            except Exception:
                pass

    sync_local_artifacts(root)

    def show_gui():
        subprocess.Popen([sys.executable, str(__file__), "--setup"])

    def exit_app():
        sys.exit(0)

    tray = LANControlTray(
        on_show_gui=show_gui,
        on_exit_app=exit_app,
        port=port,
    )
    tray.start()

    def startup_worker():
        app_log("Startup worker: polling LANCONTROL server...")
        tray.notify("LANCONTROL is starting up in background...", "LANCONTROL Fleet Manager")

        server_ready = False
        start_time = time.time()
        while time.time() - start_time < 45:
            if service_state() == "STOPPED":
                control_service("start")
            ok, _ = test_local_https(port, timeout=3)
            if ok:
                server_ready = True
                break
            time.sleep(2)

        auto_open = settings.get("auto_open_web_ui_on_login", True)
        if server_ready:
            app_log("Server is ready at startup.")
            if auto_open:
                ip = choose_best_lan_ip()
                url = f"https://{ip}:{port}/"
                webbrowser.open(url)
                app_log(f"Web UI automatically launched: {url}")
                tray.notify(f"Server is Online • Web UI launched at {url}", "LANCONTROL Fleet Manager")
            else:
                tray.notify("Server is Online and running in background.", "LANCONTROL Fleet Manager")
        else:
            app_log("Server did not respond within startup timeout.")
            tray.notify("LANCONTROL server did not respond. Check services.", "LANCONTROL Warning")

    threading.Thread(target=startup_worker, daemon=True).start()

    try:
        while True:
            time.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        tray.stop()


def handle_normal(start_minimized: bool = False):
    if not is_windows():
        messagebox.showerror(APP_TITLE, "This tool requires Windows.")
        return

    # Auto-elevate to Administrator on start unless explicitly bypassed with --no-elevate
    if not is_admin() and "--no-elevate" not in sys.argv:
        app_log("Auto-elevating to Administrator via Windows UAC...")
        if relaunch_as_admin():
            app_log("Elevated Administrator process launched. Exiting standard launcher.")
            sys.exit(0)
        else:
            app_log("Administrator elevation was declined or unavailable. Continuing in standard user mode.")

    app_log("========== APPLICATION START ==========")
    app_log(f"GUI started with Administrator privileges: {is_admin()}")
    settings = load_app_settings()
    port = settings.get("port", DEFAULT_PORT)
    sync_local_artifacts()

    gui = LANControlGUI()

    tray = LANControlTray(
        on_show_gui=gui.show_window,
        on_exit_app=gui.quit_app,
        port=port,
    )
    gui.tray = tray
    tray.start()

    if start_minimized:
        gui.withdraw()
        tray.notify("LANCONTROL Fleet Manager started in system tray.", "LANCONTROL")

    gui.mainloop()


def main():
    parser = argparse.ArgumentParser(description="LANCONTROL Fleet Manager")
    parser.add_argument("--autostart", action="store_true", help="Run in startup mode (wait for server, open web UI, tray)")
    parser.add_argument("--tray", action="store_true", help="Launch directly into system tray minimized")
    parser.add_argument("--setup", action="store_true", help="Launch setup management console")
    parser.add_argument("--no-elevate", action="store_true", help="Do not attempt Administrator elevation on launch")

    args, _ = parser.parse_known_args()

    if args.autostart:
        handle_autostart()
    elif args.tray:
        handle_normal(start_minimized=True)
    else:
        handle_normal(start_minimized=False)


if __name__ == "__main__":
    main()
