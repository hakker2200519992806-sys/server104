"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                      YORDAMCHI FUNKSIYALAR                                   ║
║  IP, logging, Telegram, token, settings va boshqa umumiy funksiyalar        ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import re
import secrets
import socket
import subprocess
import platform
import threading
import time
import urllib.request
import urllib.parse
from datetime import datetime, timedelta
from pathlib import Path

from flask import request, session

from app.config import CFG, _c, R, _active_mode
from app.database import db_exec, q1


# ── IP va tarmoq ──────────────────────────────────────────────────────────
def get_ip():
    return (request.headers.get("X-Forwarded-For", "").split(",")[0].strip()
            or request.remote_addr or "unknown")


def local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"


def get_ssid():
    try:
        if platform.system() == "Windows":
            out = subprocess.check_output("netsh wlan show interfaces", shell=True,
                stderr=subprocess.DEVNULL).decode("cp1251", errors="ignore")
            for l in out.splitlines():
                if "SSID" in l and "BSSID" not in l:
                    return l.split(":", 1)[-1].strip()
        elif platform.system() == "Linux":
            return subprocess.check_output("iwgetid -r", shell=True,
                stderr=subprocess.DEVNULL).decode().strip()
    except:
        pass
    return "Noma'lum WiFi"


# ── Logging va bandwidth ──────────────────────────────────────────────────
def log_access(mode, token=None, status=200, path=None, nb=0):
    db_exec(
        "INSERT INTO access_logs (link_token,mode,ip_address,user_agent,referer,bytes_served,status_code,path)"
        " VALUES (?,?,?,?,?,?,?,?)",
        (token, mode, get_ip(),
         request.headers.get("User-Agent", "")[:500],
         request.headers.get("Referer", "")[:500],
         nb, status, (path or request.path)[:500]), fetch=False)
    if nb > 0:
        db_exec("INSERT INTO bandwidth_log (ip_address,bytes_used,log_date) VALUES (?,?,date('now'))",
                (get_ip(), nb), fetch=False)


# ── Bloklash va xato login ────────────────────────────────────────────────
def is_blocked(ip):
    r = q1("SELECT id FROM blocked_ips WHERE ip_address=?"
           " AND (unblock_at IS NULL OR unblock_at>datetime('now'))", (ip,))
    return r is not None


def record_fail(ip, username=""):
    db_exec("INSERT INTO failed_logins (ip_address,username) VALUES (?,?)",
            (ip, username), fetch=False)
    cutoff = (datetime.now() - timedelta(minutes=CFG["BAN_MINUTES"])).strftime("%Y-%m-%d %H:%M:%S")
    cnt = q1("SELECT COUNT(*) c FROM failed_logins WHERE ip_address=? AND attempt_at>?",
             (ip, cutoff))
    if cnt and cnt["c"] >= CFG["MAX_LOGIN_FAIL"]:
        unblock = (datetime.now() + timedelta(minutes=CFG["BAN_MINUTES"])).strftime("%Y-%m-%d %H:%M:%S")
        db_exec("INSERT OR IGNORE INTO blocked_ips (ip_address,reason,unblock_at) VALUES (?,?,?)",
                (ip, "Too many failed logins", unblock), fetch=False)
        telegram_send(f"🚫 IP bloklandi: {ip}\nSabab: {CFG['MAX_LOGIN_FAIL']} marta xato login urinishi")
        return True
    return False


def clear_fails(ip):
    db_exec("DELETE FROM failed_logins WHERE ip_address=?", (ip,), fetch=False)


# ── Rejim va havola tekshiruvi ────────────────────────────────────────────
def mode_on(mode):
    r = q1("SELECT is_enabled FROM mode_settings WHERE mode=?", (mode,))
    return bool(r and r["is_enabled"])


def check_link(token, pw=None):
    from werkzeug.security import check_password_hash
    lk = q1("SELECT * FROM links WHERE token=? AND is_active=1", (token,))
    if not lk:
        return None, "Havola topilmadi yoki o'chirilgan"
    if lk.get("expires_at"):
        try:
            if datetime.now() > datetime.strptime(lk["expires_at"], "%Y-%m-%d %H:%M:%S"):
                return None, "Havolaning muddati tugagan"
        except:
            pass
    if not mode_on(lk["mode"]):
        return None, f"Rejim ({lk['mode']}) o'chirilgan"
    if lk.get("password_hash"):
        if pw is None:
            return None, "NEED_PASSWORD"
        if not check_password_hash(lk["password_hash"], pw):
            return None, "Noto'g'ri parol"
    return lk, None


# ── Yordamchi funksiyalar ─────────────────────────────────────────────────
def allowed(fn):
    return Path(fn).suffix.lower() in CFG["ALLOWED_EXT"]


def hsize(b):
    b = b or 0
    for u in ["B", "KB", "MB", "GB"]:
        if b < 1024:
            return f"{b:.1f} {u}"
        b /= 1024
    return f"{b:.1f} TB"


def gtok(n=32):
    return secrets.token_urlsafe(n)


# ── Sozlamalar (key-value) ────────────────────────────────────────────────
def get_setting(key, default=""):
    r = q1("SELECT value FROM app_settings WHERE key=?", (key,))
    return r["value"] if r else default


def set_setting(key, value):
    db_exec("INSERT INTO app_settings (key,value) VALUES (?,?) "
            "ON CONFLICT(key) DO UPDATE SET value=excluded.value", (key, value), fetch=False)


# ── Server holati ─────────────────────────────────────────────────────────
def server_enabled():
    return get_setting("server_enabled", "1") == "1"


# ── Telegram bildirishnoma ────────────────────────────────────────────────
def telegram_send(text):
    """Sozlamalarda yoqilgan bo'lsa, Telegram botga xabar yuboradi."""
    if get_setting("tg_enabled", "0") != "1":
        return
    token = get_setting("tg_token", CFG["TELEGRAM_TOKEN"])
    chat = get_setting("tg_chat", CFG["TELEGRAM_CHAT_ID"])
    if not token or not chat:
        return

    def _send():
        try:
            url = f"https://api.telegram.org/bot{token}/sendMessage"
            data = urllib.parse.urlencode({"chat_id": chat, "text": text}).encode()
            urllib.request.urlopen(urllib.request.Request(url, data=data), timeout=6)
        except Exception as e:
            print(_c(f"[Telegram] {e}", R))

    threading.Thread(target=_send, daemon=True).start()


# ── Audit trail ───────────────────────────────────────────────────────────
def audit(action, target_type=None, target_id=None, details=None):
    """Muhim amallarni audit_log jadvaliga yozadi."""
    try:
        uid = session.get("user_id")
        uname = session.get("username", "")
        ip = get_ip()
        db_exec("INSERT INTO audit_log (user_id,username,action,target_type,target_id,details,ip_address) "
                "VALUES (?,?,?,?,?,?,?)",
                (uid, uname, action, target_type, str(target_id) if target_id else None,
                 (details or "")[:500], ip), fetch=False)
    except Exception:
        pass


# ── Loyiha fayl tizimi yordamchilari ─────────────────────────────────────
def _proj_or_404(puuid, uid, adm):
    from flask import abort
    proj = q1("SELECT * FROM projects WHERE uuid=?", (puuid,))
    if not proj:
        abort(404)
    if proj["owner_id"] != uid and not adm:
        abort(403)
    return proj


def _seed_default_files(project_id):
    defaults = [
        ("index.html", 0, '<!DOCTYPE html>\n<html lang="uz">\n<head>\n  <meta charset="UTF-8">\n'
                           '  <title>Sahifa</title>\n  <link rel="stylesheet" href="style.css">\n</head>\n<body>\n'
                           '  <h1>Salom Dunyo!</h1>\n  <script src="script.js"></script>\n</body>\n</html>'),
        ("style.css", 0, "/* CSS kodingiz */\nbody{font-family:sans-serif;background:#fafafa;color:#222;}"),
        ("script.js", 0, "// JS kodingiz\nconsole.log('Loyiha ishga tushdi!');"),
    ]
    for path, is_folder, content in defaults:
        db_exec("INSERT OR IGNORE INTO project_files (project_id,path,is_folder,content) VALUES (?,?,?,?)",
                (project_id, path, is_folder, content), fetch=False)


def _ensure_files(project_id):
    r = q1("SELECT COUNT(*) c FROM project_files WHERE project_id=?", (project_id,))
    if not r or not r["c"]:
        _seed_default_files(project_id)


def _resolve_rel(base, rel):
    rel = rel.lstrip("/")
    base_dir = base.rsplit("/", 1)[0] + "/" if "/" in base else ""
    parts = (base_dir + rel).split("/")
    out = []
    for p in parts:
        if p == "..":
            if out:
                out.pop()
        elif p not in ("", "."):
            out.append(p)
    return "/".join(out)


def _build_page_html(files_map, entry_path):
    html = files_map.get(entry_path)
    if html is None:
        return None

    def repl_css(m):
        href = m.group(1)
        if href.startswith("http"):
            return m.group(0)
        c = files_map.get(_resolve_rel(entry_path, href))
        return f"<style>{c}</style>" if c is not None else m.group(0)

    def repl_js(m):
        src = m.group(1)
        if src.startswith("http"):
            return m.group(0)
        c = files_map.get(_resolve_rel(entry_path, src))
        return f"<script>{c}</script>" if c is not None else m.group(0)

    html = re.sub(r'<link[^>]+href=["\']([^"\'>]+\.css)["\'][^>]*>', repl_css, html, flags=re.I)
    html = re.sub(r'<script[^>]+src=["\']([^"\'>]+\.js)["\'][^>]*></script>', repl_js, html, flags=re.I)
    return html


# ── Fon threadlar ─────────────────────────────────────────────────────────
def expiry_checker():
    """Muddati o'tgan havolalarni avtomatik o'chiradi."""
    while True:
        time.sleep(300)
        try:
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            db_exec("UPDATE links SET is_active=0 WHERE expires_at IS NOT NULL AND expires_at<? AND is_active=1",
                    (now,), fetch=False)
        except:
            pass


def uptime_checker():
    """Har 60 sekundda serverni tekshiradi."""
    while True:
        time.sleep(60)
        try:
            t0 = time.time()
            port = CFG["PORT"]
            try:
                urllib.request.urlopen(f"http://127.0.0.1:{port}/login", timeout=5)
                status = "up"
            except Exception:
                status = "down"
            ms = int((time.time() - t0) * 1000)
            db_exec("INSERT INTO uptime_logs (status,response_ms) VALUES (?,?)",
                    (status, ms), fetch=False)
            db_exec("DELETE FROM uptime_logs WHERE checked_at < datetime('now','-7 days')", fetch=False)
        except Exception:
            pass
