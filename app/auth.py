"""
╔══════════════════════════════════════════════════════════════════════════════╗
║           XAVFSIZLIK: CSRF, RBAC, API-kalit, 2FA, Dekoratorlar             ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import secrets
import hashlib
import threading
import urllib.request
import urllib.parse
from datetime import datetime, timedelta
from functools import wraps

from flask import session, redirect, abort, request
from werkzeug.security import check_password_hash

from app.config import CFG, ROLE_RANK, _c, R
from app.database import db_exec, q1
from app.utils import get_ip, is_blocked, clear_fails, telegram_send, get_setting


# ── CSRF ──────────────────────────────────────────────────────────────────
def get_csrf_token():
    if "_csrf" not in session:
        session["_csrf"] = secrets.token_hex(24)
    return session["_csrf"]


def csrf_field():
    """HTML <form>lar ichiga qo'yiladigan yashirin CSRF maydoni."""
    return f'<input type="hidden" name="_csrf" value="{get_csrf_token()}">'


# ── Dekoratorlar ──────────────────────────────────────────────────────────
def admin_req(f):
    @wraps(f)
    def d(*a, **k):
        if not session.get("admin"):
            return redirect("/login")
        if is_blocked(get_ip()):
            abort(403)
        return f(*a, **k)
    return d


def user_req(f):
    @wraps(f)
    def d(*a, **k):
        if "user_id" not in session:
            return redirect("/login")
        return f(*a, **k)
    return d


def write_req(f):
    """Faqat 'viewer' bo'lmagan foydalanuvchilar uchun."""
    @wraps(f)
    def d(*a, **k):
        if role_rank(session.get("role")) < ROLE_RANK["user"]:
            abort(403)
        return f(*a, **k)
    return d


def role_rank(role):
    return ROLE_RANK.get(role or "user", 1)


# ── API kalitlari ─────────────────────────────────────────────────────────
def new_api_key(user_id, name=""):
    raw = "sk_" + secrets.token_urlsafe(32)
    prefix = raw[:10]
    h = hashlib.sha256(raw.encode()).hexdigest()
    db_exec("INSERT INTO api_keys (user_id,name,key_prefix,key_hash) VALUES (?,?,?,?)",
            (user_id, name or "API kalit", prefix, h), fetch=False)
    return raw


def api_key_req(f):
    @wraps(f)
    def d(*a, **k):
        auth = request.headers.get("Authorization", "")
        if not auth.startswith("Bearer "):
            from flask import jsonify
            return jsonify({"error": "Authorization: Bearer <API_KEY> talab qilinadi"}), 401
        raw = auth[7:].strip()
        h = hashlib.sha256(raw.encode()).hexdigest()
        row = q1("SELECT * FROM api_keys WHERE key_hash=? AND revoked=0", (h,))
        if not row:
            from flask import jsonify
            return jsonify({"error": "API kalit noto'g'ri yoki bekor qilingan"}), 401
        db_exec("UPDATE api_keys SET last_used_at=datetime('now') WHERE id=?",
                (row["id"],), fetch=False)
        request.api_user_id = row["user_id"]
        return f(*a, **k)
    return d


# ── 2FA (Telegram bir martalik kod) ───────────────────────────────────────
def send_2fa_code(user):
    code = f"{secrets.randbelow(1000000):06d}"
    exp = (datetime.now() + timedelta(minutes=5)).strftime("%Y-%m-%d %H:%M:%S")
    db_exec("INSERT INTO two_fa_codes (user_id,code,expires_at) VALUES (?,?,?)",
            (user["id"], code, exp), fetch=False)
    chat = user.get("tg_chat_id") or get_setting("tg_chat", CFG["TELEGRAM_CHAT_ID"])
    token = get_setting("tg_token", CFG["TELEGRAM_TOKEN"])
    if token and chat:
        def _send():
            try:
                url = f"https://api.telegram.org/bot{token}/sendMessage"
                data = urllib.parse.urlencode({
                    "chat_id": chat,
                    "text": f"🔑 Tasdiqlash kodi: {code} (5 daqiqa amal qiladi)"
                }).encode()
                urllib.request.urlopen(urllib.request.Request(url, data=data), timeout=6)
            except Exception as e:
                print(_c(f"[2FA/Telegram] {e}", R))
        threading.Thread(target=_send, daemon=True).start()
    return code


def verify_2fa_code(user_id, code):
    row = q1("SELECT * FROM two_fa_codes WHERE user_id=? AND code=? AND used=0 "
             "AND expires_at>datetime('now') ORDER BY id DESC LIMIT 1",
             (user_id, code))
    if not row:
        return False
    db_exec("UPDATE two_fa_codes SET used=1 WHERE id=?", (row["id"],), fetch=False)
    return True


def finalize_login(user, ip):
    clear_fails(ip)
    session.permanent = True
    session.update({
        "user_id": user["id"],
        "username": user["username"],
        "role": user["role"],
        "admin": user["role"] == "admin",
        "_guest": False
    })
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    db_exec("UPDATE users SET last_login=? WHERE id=?", (now, user["id"]), fetch=False)
    telegram_send(f"✅ Yangi kirish\nFoydalanuvchi: {user['username']}\nIP: {ip}")
