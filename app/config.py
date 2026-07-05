"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                          KONFIGURATSIYA                                      ║
║  Barcha asosiy sozlamalar va Flask app obyekti shu yerda                     ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import os
import secrets
import time
import threading
from datetime import timedelta
from pathlib import Path

from flask import Flask

# ── Uchinchi tomon kutubxonalar mavjudligini tekshirish ─────────────────────
try:
    from pyngrok import ngrok as _ngrok
    NGROK_OK = True
except ImportError:
    NGROK_OK = False

try:
    from colorama import Fore, Style, init as _cinit
    _cinit(autoreset=True)
    R = Fore.RED; G = Fore.GREEN; Y = Fore.YELLOW
    C = Fore.CYAN; M = Fore.MAGENTA; W = Fore.WHITE
    def _c(t, col=""): return col + Style.BRIGHT + str(t) + Style.RESET_ALL
except ImportError:
    R = G = Y = C = M = W = ""
    def _c(t, col=""): return str(t)

try:
    import psutil
    PSUTIL_OK = True
except ImportError:
    PSUTIL_OK = False

try:
    import qrcode
    QRCODE_OK = True
except ImportError:
    QRCODE_OK = False

try:
    from RestrictedPython import compile_restricted, safe_globals
    from RestrictedPython.Guards import (
        safe_builtins, guarded_iter_unpack_sequence, full_write_guard,
    )
    from RestrictedPython.Eval import default_guarded_getiter
    RESTRICTED_OK = True
except ImportError:
    RESTRICTED_OK = False

# ╔══════════════════════════════════════════════════════════════════════════╗
# ║                 BACKEND ENGINE SOZLAMALARI                               ║
# ╚══════════════════════════════════════════════════════════════════════════╝
EXEC_TIMEOUT_SEC   = 3
MEM_LIMIT_MB       = 128
RATE_LIMIT_PER_MIN = 30
HISTORY_LOG_KEEP   = 500

PROJECT_DB_DIR = Path("project_dbs")
PROJECT_DB_DIR.mkdir(exist_ok=True)

ALLOWED_IMPORTS = {"json", "math", "random", "re", "datetime", "string", "statistics"}

import re as _re
_SQL_FORBIDDEN = _re.compile(
    r"\b(ATTACH|DETACH|PRAGMA|VACUUM|DROP\s+DATABASE|LOAD_EXTENSION)\b", _re.I)

# ╔══════════════════════════════════════════════════════════════════════════╗
# ║                    ASOSIY KONFIGURATSIYA                                  ║
# ╚══════════════════════════════════════════════════════════════════════════╝
CFG = {
    "DB_FILE":        "server_data.db",
    "PORT":           5000,
    "SECRET":         secrets.token_hex(32),
    "ADMIN_USER":     "admin",
    "ADMIN_PASS":     "Admin123!",
    "NGROK_TOKEN":    "",
    "TELEGRAM_TOKEN": "",
    "TELEGRAM_CHAT_ID": "",
    "UPLOAD_DIR":     "uploads",
    "MAX_FILE_MB":    50,
    "ALLOWED_EXT":    {".html", ".css", ".js", ".txt", ".json", ".png", ".jpg",
                       ".jpeg", ".gif", ".svg", ".ico", ".woff", ".woff2", ".ttf",
                       ".mp3", ".mp4", ".py", ".php"},
    "MAX_LOGIN_FAIL": 5,
    "BAN_MINUTES":    30,
    "SESSION_HOURS":  8,
}

# ── Papkalar ───────────────────────────────────────────────────────────────
UPLOAD_PATH = Path(CFG["UPLOAD_DIR"])
FILES_PATH  = UPLOAD_PATH / "files"
for _p in [UPLOAD_PATH, FILES_PATH]:
    _p.mkdir(exist_ok=True)

# ── Flask App yaratish ─────────────────────────────────────────────────────
app = Flask(__name__)
app.secret_key = CFG["SECRET"]
app.permanent_session_lifetime = timedelta(hours=CFG["SESSION_HOURS"])
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

# ── Global holatlar ───────────────────────────────────────────────────────
_active_mode  = {"mode": None, "url": None}
_ngrok_tunnel = None
_db_lock      = threading.Lock()
PROCESS_START = time.time()

# ── RBAC rollar ────────────────────────────────────────────────────────────
ROLE_RANK = {"viewer": 0, "user": 1, "editor": 2, "admin": 3}
