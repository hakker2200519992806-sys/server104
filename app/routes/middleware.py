"""
Middleware — CSRF, Guest autologin, Server enabled check, IP Whitelist, Custom domain
"""

from flask import request, session, redirect, abort

from app.config import app
from app.database import q1
from app.utils import get_ip, get_setting, server_enabled
from app.templates import CSS


@app.before_request
def _csrf_protect():
    """CSRF himoyasi."""
    if request.method != "POST":
        return None
    if request.path.startswith("/p/"):
        return None
    tok = request.form.get("_csrf") or request.headers.get("X-CSRF-Token")
    if request.is_json or request.content_type == "application/json":
        tok = request.headers.get("X-CSRF-Token") or tok
    sess_tok = session.get("_csrf")
    if request.path in ("/login", "/register"):
        return None
    if sess_tok and tok != sess_tok:
        abort(403)
    return None


@app.before_request
def _guest_autologin():
    """Guest rejimi — loginsiz kirish."""
    if session.get("user_id"):
        return None
    if get_setting("require_login", "1") == "0":
        session["user_id"] = 0
        session["username"] = "mehmon"
        session["role"] = "viewer"
        session["admin"] = False
        session["_guest"] = True
    return None


@app.before_request
def _check_server_enabled():
    """Server o'chirilgan bo'lsa kirishni to'xtatish."""
    if server_enabled():
        return None
    if request.path in ("/login", "/logout") or request.path.startswith("/static"):
        return None
    if session.get("admin"):
        return None
    return f"""<!DOCTYPE html><html><head><meta charset=UTF-8>
    <style>{CSS} body{{display:flex;align-items:center;justify-content:center;min-height:100vh;text-align:center}}</style>
    </head><body><div>
    <p style="font-size:2.5rem">🛑</p>
    <h1 style="color:var(--rd);margin:10px 0">Server vaqtincha o'chirilgan</h1>
    <a href="/login" class="btn bgh mt">Admin sifatida kirish</a>
    </div></body></html>""", 503


@app.before_request
def _check_custom_domain():
    """Custom domain orqali loyiha preview'ga yo'naltirish."""
    host = request.host.split(":")[0].lower()
    if host in ("127.0.0.1", "localhost", "0.0.0.0"):
        return None
    dom = q1("SELECT d.*,p.uuid FROM custom_domains d JOIN projects p ON d.project_id=p.id WHERE d.domain=? AND d.is_active=1", (host,))
    if dom and request.path == "/":
        return redirect(f"/preview/{dom['uuid']}")
    return None


# ── Error handlerlar ──────────────────────────────────────────────────────
@app.errorhandler(403)
def e403(e):
    return f"""<!DOCTYPE html><html><head><meta charset=UTF-8>
    <style>{CSS} body{{display:flex;align-items:center;justify-content:center;min-height:100vh;text-align:center}}</style>
    </head><body><div><p style="font-size:2.5rem">🚫</p>
    <h1 style="color:var(--rd);margin:10px 0">403 — Kirish taqiqlangan</h1>
    <a href="/" class="btn bgh mt">← Asosiy</a></div></body></html>""", 403


@app.errorhandler(404)
def e404(e):
    return f"""<!DOCTYPE html><html><head><meta charset=UTF-8>
    <style>{CSS} body{{display:flex;align-items:center;justify-content:center;min-height:100vh;text-align:center}}</style>
    </head><body><div><p style="font-size:2.5rem">🔍</p>
    <h1 style="color:var(--mt);margin:10px 0">404 — Topilmadi</h1>
    <a href="/" class="btn bgh mt">← Asosiy</a></div></body></html>""", 404
