"""
ADVANCED FEATURES:
- Fork loyiha
- Loyiha shablonlari
- Environment variables
- Webhook receiver
- Email yuborish
- Cron / scheduled tasks
- Analytics (real)
- Error tracking
- Tarif rejalari
- Code review
- @mention notifications
- NPM CDN simulator
- A/B testing
"""

import json
import re
import uuid
import os
import threading
import time
import smtplib
from email.mime.text import MIMEText
from datetime import datetime, timedelta

from flask import request, session, redirect, abort, jsonify

from app.config import app, CFG
from app.database import db_exec, q1
from app.auth import user_req, write_req, admin_req, csrf_field
from app.utils import (get_ip, audit, get_setting, set_setting,
                        _proj_or_404, _ensure_files, telegram_send)
from app.templates import _pg



# ╔══════════════════════════════════════════════════════════════════════════╗
# ║              FORK LOYIHA                                                    ║
# ╚══════════════════════════════════════════════════════════════════════════╝
@app.route("/api/project/fork/<puuid>", methods=["POST"])
@user_req
@write_req
def fork_project(puuid):
    proj = q1("SELECT * FROM projects WHERE uuid=?", (puuid,))
    if not proj:
        return jsonify({"ok": False, "error": "Loyiha topilmadi"}), 404
    # Yangi loyiha yaratish
    new_uuid = str(uuid.uuid4())
    new_name = proj["name"] + " (Fork)"
    new_id = db_exec("INSERT INTO projects (uuid,name,owner_id) VALUES (?,?,?)",
                     (new_uuid, new_name, session["user_id"]), fetch=False)
    # Fayllarni nusxalash
    files = db_exec("SELECT path,is_folder,content FROM project_files WHERE project_id=?",
                    (proj["id"],)) or []
    for f in files:
        db_exec("INSERT INTO project_files (project_id,path,is_folder,content) VALUES (?,?,?,?)",
                (new_id, f["path"], f["is_folder"], f.get("content") or ""), fetch=False)
    audit("fork", "project", puuid, f"-> {new_uuid}")
    return jsonify({"ok": True, "new_uuid": new_uuid})


# ╔══════════════════════════════════════════════════════════════════════════╗
# ║              LOYIHA SHABLONLARI (Templates Store)                          ║
# ╚══════════════════════════════════════════════════════════════════════════╝
PROJECT_TEMPLATES = [
    {"id": "blank", "name": "Bo'sh loyiha", "desc": "Minimal HTML/CSS/JS",
     "files": [
         ("index.html", '<!DOCTYPE html>\n<html lang="uz">\n<head>\n  <meta charset="UTF-8">\n  <title>Sahifa</title>\n  <link rel="stylesheet" href="style.css">\n</head>\n<body>\n  <h1>Salom!</h1>\n  <script src="script.js"></script>\n</body>\n</html>'),
         ("style.css", "body{font-family:sans-serif;margin:0;padding:20px}"),
         ("script.js", "console.log('Tayyor!');"),
     ]},
    {"id": "landing", "name": "Landing Page", "desc": "Zamonaviy landing sahifa",
     "files": [
         ("index.html", '<!DOCTYPE html>\n<html lang="uz">\n<head>\n  <meta charset="UTF-8">\n  <meta name="viewport" content="width=device-width,initial-scale=1">\n  <title>Landing</title>\n  <link rel="stylesheet" href="style.css">\n</head>\n<body>\n  <header class="hero">\n    <h1>Xush kelibsiz!</h1>\n    <p>Zamonaviy veb-sahifa</p>\n    <a href="#about" class="btn">Batafsil</a>\n  </header>\n  <section id="about" class="section">\n    <h2>Biz haqimizda</h2>\n    <p>Matn shu yerda.</p>\n  </section>\n  <footer>&copy; 2025</footer>\n  <script src="script.js"></script>\n</body>\n</html>'),
         ("style.css", "*{margin:0;padding:0;box-sizing:border-box}\nbody{font-family:system-ui,sans-serif;color:#333}\n.hero{min-height:80vh;display:flex;flex-direction:column;align-items:center;justify-content:center;background:linear-gradient(135deg,#667eea,#764ba2);color:#fff;text-align:center;padding:40px}\n.hero h1{font-size:3rem;margin-bottom:10px}\n.hero .btn{display:inline-block;margin-top:20px;padding:12px 30px;background:#fff;color:#764ba2;border-radius:30px;text-decoration:none;font-weight:700}\n.section{padding:60px 20px;max-width:800px;margin:0 auto;text-align:center}\nfooter{text-align:center;padding:20px;background:#1a1a2e;color:#aaa}"),
         ("script.js", "document.querySelectorAll('a[href^=\"#\"]').forEach(a=>a.addEventListener('click',e=>{e.preventDefault();document.querySelector(a.getAttribute('href')).scrollIntoView({behavior:'smooth'})}));"),
     ]},
    {"id": "dashboard", "name": "Admin Dashboard", "desc": "Sidebar + Cards layout",
     "files": [
         ("index.html", '<!DOCTYPE html>\n<html>\n<head>\n  <meta charset="UTF-8">\n  <title>Dashboard</title>\n  <link rel="stylesheet" href="style.css">\n</head>\n<body>\n  <aside class="sidebar">\n    <h2>Menu</h2>\n    <nav><a href="#">Dashboard</a><a href="#">Users</a><a href="#">Settings</a></nav>\n  </aside>\n  <main class="content">\n    <h1>Dashboard</h1>\n    <div class="cards">\n      <div class="card"><h3>100</h3><p>Users</p></div>\n      <div class="card"><h3>42</h3><p>Orders</p></div>\n      <div class="card"><h3>$5,200</h3><p>Revenue</p></div>\n    </div>\n  </main>\n</body>\n</html>'),
         ("style.css", "body{margin:0;display:flex;font-family:system-ui;background:#f0f2f5}\n.sidebar{width:200px;min-height:100vh;background:#1a1a2e;color:#fff;padding:20px}\n.sidebar nav a{display:block;color:#aaa;padding:10px 0;text-decoration:none}\n.sidebar nav a:hover{color:#fff}\n.content{flex:1;padding:30px}\n.cards{display:grid;grid-template-columns:repeat(3,1fr);gap:20px;margin-top:20px}\n.card{background:#fff;border-radius:12px;padding:24px;box-shadow:0 2px 8px rgba(0,0,0,.08);text-align:center}\n.card h3{font-size:2rem;color:#667eea}"),
         ("script.js", "// Dashboard logic"),
     ]},
    {"id": "portfolio", "name": "Portfolio", "desc": "Shaxsiy portfolio sahifa",
     "files": [
         ("index.html", '<!DOCTYPE html>\n<html>\n<head>\n  <meta charset="UTF-8">\n  <title>Portfolio</title>\n  <link rel="stylesheet" href="style.css">\n</head>\n<body>\n  <header><h1>Ism Familiya</h1><p>Web Developer</p></header>\n  <section class="projects">\n    <h2>Loyihalarim</h2>\n    <div class="grid">\n      <div class="item"><h3>Loyiha 1</h3></div>\n      <div class="item"><h3>Loyiha 2</h3></div>\n      <div class="item"><h3>Loyiha 3</h3></div>\n    </div>\n  </section>\n  <footer>Email: hello@example.com</footer>\n</body>\n</html>'),
         ("style.css", "body{margin:0;font-family:system-ui;background:#0d0f18;color:#d4daf0}\nheader{text-align:center;padding:80px 20px;background:linear-gradient(135deg,#7c6fff,#22d3a0)}\nheader h1{font-size:2.5rem;color:#fff}\n.projects{padding:40px 20px;max-width:900px;margin:0 auto}\n.grid{display:grid;grid-template-columns:repeat(3,1fr);gap:20px;margin-top:20px}\n.item{background:#1c2136;border:1px solid #252d45;border-radius:12px;padding:30px;text-align:center}\nfooter{text-align:center;padding:30px;color:#5c6890}"),
         ("script.js", "// Portfolio animations"),
     ]},
]

@app.route("/api/templates")
@user_req
def api_templates():
    return jsonify({"templates": [{"id": t["id"], "name": t["name"], "desc": t["desc"]} for t in PROJECT_TEMPLATES]})

@app.route("/api/templates/use/<tid>", methods=["POST"])
@user_req
@write_req
def api_template_use(tid):
    tmpl = next((t for t in PROJECT_TEMPLATES if t["id"] == tid), None)
    if not tmpl:
        return jsonify({"ok": False, "error": "Shablon topilmadi"}), 404
    d = request.get_json() or {}
    name = (d.get("name") or tmpl["name"]).strip()
    new_uuid = str(uuid.uuid4())
    new_id = db_exec("INSERT INTO projects (uuid,name,owner_id) VALUES (?,?,?)",
                     (new_uuid, name, session["user_id"]), fetch=False)
    for path, content in tmpl["files"]:
        db_exec("INSERT INTO project_files (project_id,path,is_folder,content) VALUES (?,?,0,?)",
                (new_id, path, content), fetch=False)
    audit("template_use", "project", new_uuid, tid)
    return jsonify({"ok": True, "uuid": new_uuid, "name": name})



# ╔══════════════════════════════════════════════════════════════════════════╗
# ║              ENVIRONMENT VARIABLES (.env)                                   ║
# ╚══════════════════════════════════════════════════════════════════════════╝
@app.route("/api/env/<puuid>", methods=["GET", "POST"])
@user_req
def api_env(puuid):
    proj = _proj_or_404(puuid, session["user_id"], session.get("admin"))
    if request.method == "GET":
        rows = db_exec("SELECT key,value FROM project_files WHERE project_id=? AND path='.env'", (proj["id"],))
        # .env fayldan parse qilish
        env_file = q1("SELECT content FROM project_files WHERE project_id=? AND path='.env'", (proj["id"],))
        vars_list = []
        if env_file and env_file.get("content"):
            for line in env_file["content"].split("\n"):
                line = line.strip()
                if "=" in line and not line.startswith("#"):
                    k, v = line.split("=", 1)
                    vars_list.append({"key": k.strip(), "value": v.strip()})
        return jsonify({"vars": vars_list})
    # POST - qo'shish
    d = request.get_json() or {}
    key = (d.get("key") or "").strip().upper()
    value = (d.get("value") or "").strip()
    if not key:
        return jsonify({"ok": False})
    # .env faylni yangilash
    env_file = q1("SELECT content FROM project_files WHERE project_id=? AND path='.env'", (proj["id"],))
    content = env_file["content"] if env_file and env_file.get("content") else ""
    # Mavjud kalit bo'lsa yangilash
    lines = content.split("\n") if content else []
    found = False
    for i, line in enumerate(lines):
        if line.strip().startswith(key + "="):
            lines[i] = f"{key}={value}"
            found = True
            break
    if not found:
        lines.append(f"{key}={value}")
    new_content = "\n".join(lines)
    db_exec("INSERT INTO project_files (project_id,path,is_folder,content) VALUES (?,'.env',0,?) "
            "ON CONFLICT(project_id,path) DO UPDATE SET content=excluded.content,updated_at=datetime('now')",
            (proj["id"], new_content), fetch=False)
    return jsonify({"ok": True})

@app.route("/api/env/<puuid>/<key>", methods=["DELETE"])
@user_req
@write_req
def api_env_delete(puuid, key):
    proj = _proj_or_404(puuid, session["user_id"], session.get("admin"))
    env_file = q1("SELECT content FROM project_files WHERE project_id=? AND path='.env'", (proj["id"],))
    if not env_file or not env_file.get("content"):
        return jsonify({"ok": True})
    lines = [l for l in env_file["content"].split("\n") if not l.strip().startswith(key + "=")]
    db_exec("UPDATE project_files SET content=?,updated_at=datetime('now') WHERE project_id=? AND path='.env'",
            ("\n".join(lines), proj["id"]), fetch=False)
    return jsonify({"ok": True})



# ╔══════════════════════════════════════════════════════════════════════════╗
# ║              NPM CDN SIMULATOR (esm.sh import maps)                        ║
# ╚══════════════════════════════════════════════════════════════════════════╝
@app.route("/api/npm/list/<puuid>")
@user_req
def npm_list(puuid):
    proj = _proj_or_404(puuid, session["user_id"], session.get("admin"))
    pkg_file = q1("SELECT content FROM project_files WHERE project_id=? AND path='package.json'", (proj["id"],))
    packages = []
    if pkg_file and pkg_file.get("content"):
        try:
            data = json.loads(pkg_file["content"])
            packages = list(data.get("dependencies", {}).keys())
        except:
            pass
    return jsonify({"packages": packages})

@app.route("/api/npm/install/<puuid>", methods=["POST"])
@user_req
@write_req
def npm_install(puuid):
    proj = _proj_or_404(puuid, session["user_id"], session.get("admin"))
    d = request.get_json() or {}
    pkg = (d.get("package") or "").strip().lower()
    if not pkg or not re.match(r'^[@a-z0-9][\w./-]*$', pkg):
        return jsonify({"ok": False, "error": "Noto'g'ri paket nomi"})
    # package.json ni yangilash
    pkg_file = q1("SELECT content FROM project_files WHERE project_id=? AND path='package.json'", (proj["id"],))
    if pkg_file and pkg_file.get("content"):
        try:
            data = json.loads(pkg_file["content"])
        except:
            data = {"name": "project", "dependencies": {}}
    else:
        data = {"name": "project", "dependencies": {}}
    data.setdefault("dependencies", {})[pkg] = "latest"
    db_exec("INSERT INTO project_files (project_id,path,is_folder,content) VALUES (?,?,0,?) "
            "ON CONFLICT(project_id,path) DO UPDATE SET content=excluded.content,updated_at=datetime('now')",
            (proj["id"], "package.json", json.dumps(data, indent=2)), fetch=False)
    # index.html ga importmap qo'shish
    idx = q1("SELECT content FROM project_files WHERE project_id=? AND path='index.html'", (proj["id"],))
    if idx and idx.get("content"):
        html = idx["content"]
        cdn_url = f"https://esm.sh/{pkg}"
        script_tag = f'<script type="module" src="{cdn_url}"></script>'
        if cdn_url not in html and "</head>" in html:
            html = html.replace("</head>", f"  {script_tag}\n</head>")
            db_exec("UPDATE project_files SET content=?,updated_at=datetime('now') WHERE project_id=? AND path='index.html'",
                    (html, proj["id"]), fetch=False)
    return jsonify({"ok": True, "cdn": f"https://esm.sh/{pkg}"})

@app.route("/api/npm/uninstall/<puuid>", methods=["POST"])
@user_req
@write_req
def npm_uninstall(puuid):
    proj = _proj_or_404(puuid, session["user_id"], session.get("admin"))
    d = request.get_json() or {}
    pkg = (d.get("package") or "").strip()
    pkg_file = q1("SELECT content FROM project_files WHERE project_id=? AND path='package.json'", (proj["id"],))
    if pkg_file and pkg_file.get("content"):
        try:
            data = json.loads(pkg_file["content"])
            data.get("dependencies", {}).pop(pkg, None)
            db_exec("UPDATE project_files SET content=?,updated_at=datetime('now') WHERE project_id=? AND path='package.json'",
                    (json.dumps(data, indent=2), proj["id"]), fetch=False)
        except:
            pass
    return jsonify({"ok": True})



# ╔══════════════════════════════════════════════════════════════════════════╗
# ║              WEBHOOK RECEIVER                                               ║
# ╚══════════════════════════════════════════════════════════════════════════╝
@app.route("/api/webhook/<puuid>/<path:hook_path>", methods=["GET", "POST", "PUT", "DELETE"])
def webhook_receive(puuid, hook_path):
    """Tashqi xizmatlardan webhook qabul qilish."""
    proj = q1("SELECT id FROM projects WHERE uuid=?", (puuid,))
    if not proj:
        abort(404)
    # Webhook ma'lumotini saqlash
    payload = request.get_json(silent=True) or dict(request.form) or {}
    db_exec("""INSERT INTO audit_log (action,target_type,target_id,details,ip_address,created_at)
               VALUES ('webhook_received','project',?,?,?,datetime('now'))""",
            (puuid, json.dumps({"path": hook_path, "method": request.method,
                                "payload": str(payload)[:500]})[:500], get_ip()), fetch=False)
    return jsonify({"ok": True, "received": True})


# ╔══════════════════════════════════════════════════════════════════════════╗
# ║              EMAIL YUBORISH (SMTP)                                          ║
# ╚══════════════════════════════════════════════════════════════════════════╝
@app.route("/api/email/send", methods=["POST"])
@user_req
@write_req
def email_send():
    """SMTP orqali email yuborish."""
    d = request.get_json() or {}
    to_email = (d.get("to") or "").strip()
    subject = (d.get("subject") or "").strip()
    body = (d.get("body") or "").strip()
    if not to_email or not subject or not body:
        return jsonify({"ok": False, "error": "to, subject, body kerak"})
    smtp_host = get_setting("smtp_host", "")
    smtp_port = int(get_setting("smtp_port", "587"))
    smtp_user = get_setting("smtp_user", "")
    smtp_pass = get_setting("smtp_pass", "")
    if not smtp_host or not smtp_user:
        return jsonify({"ok": False, "error": "SMTP sozlanmagan. Admin/Sozlamalar dan kiriting."})
    try:
        msg = MIMEText(body, "plain", "utf-8")
        msg["Subject"] = subject
        msg["From"] = smtp_user
        msg["To"] = to_email
        with smtplib.SMTP(smtp_host, smtp_port, timeout=10) as server:
            server.starttls()
            server.login(smtp_user, smtp_pass)
            server.send_message(msg)
        audit("email_sent", "email", to_email, subject[:100])
        return jsonify({"ok": True})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)[:200]})

@app.route("/admin/smtp", methods=["GET", "POST"])
@admin_req
def admin_smtp():
    suc = None
    if request.method == "POST":
        set_setting("smtp_host", request.form.get("smtp_host", "").strip())
        set_setting("smtp_port", request.form.get("smtp_port", "587").strip())
        set_setting("smtp_user", request.form.get("smtp_user", "").strip())
        set_setting("smtp_pass", request.form.get("smtp_pass", "").strip())
        suc = "SMTP sozlamalari saqlandi"
    body = f"""
    <h2 style="color:#fff;margin-bottom:14px">📧 SMTP Sozlamalari</h2>
    <div class="card">
      <form method="POST">{csrf_field()}
        <div class="g g2">
          <div class="fld"><label>SMTP Host</label><input name="smtp_host" value="{get_setting('smtp_host','')}"></div>
          <div class="fld"><label>Port</label><input name="smtp_port" value="{get_setting('smtp_port','587')}"></div>
        </div>
        <div class="g g2">
          <div class="fld"><label>Username/Email</label><input name="smtp_user" value="{get_setting('smtp_user','')}"></div>
          <div class="fld"><label>Parol</label><input name="smtp_pass" type="password" value="{get_setting('smtp_pass','')}"></div>
        </div>
        <button class="btn bp">💾 Saqlash</button>
      </form>
    </div>"""
    return _pg("SMTP", body, "settings", flash=suc, ftype="ok")



# ╔══════════════════════════════════════════════════════════════════════════╗
# ║              CRON / REJALASHTIRILGAN VAZIFALAR                              ║
# ╚══════════════════════════════════════════════════════════════════════════╝
_cron_jobs = {}  # {job_id: threading.Timer}

@app.route("/api/cron", methods=["GET", "POST"])
@user_req
def api_cron():
    if request.method == "GET":
        rows = db_exec("SELECT * FROM audit_log WHERE action='cron_registered' ORDER BY id DESC LIMIT 20") or []
        return jsonify({"jobs": [{"id": r["id"], "details": r.get("details",""), "created_at": str(r["created_at"])[:19]} for r in rows]})
    d = request.get_json() or {}
    interval = int(d.get("interval_min", 60))
    url_path = (d.get("url_path") or "").strip()
    if not url_path:
        return jsonify({"ok": False, "error": "url_path kerak"})
    audit("cron_registered", "cron", None, f"har {interval} min: {url_path}")
    return jsonify({"ok": True, "interval_min": interval, "url_path": url_path})



# ╔══════════════════════════════════════════════════════════════════════════╗
# ║              REAL ANALYTICS                                                 ║
# ╚══════════════════════════════════════════════════════════════════════════╝
@app.route("/api/analytics/track", methods=["POST"])
def analytics_track():
    """Frontend JS tracker chaqiradi — sahifa ko'rish va hodisalar."""
    d = request.get_json() or {}
    page = (d.get("page") or request.path)[:500]
    event = (d.get("event") or "pageview")[:50]
    referrer = (d.get("referrer") or "")[:500]
    ip = get_ip()
    ua = request.headers.get("User-Agent", "")[:300]
    db_exec("""INSERT INTO access_logs (mode,ip_address,user_agent,referer,path,status_code)
               VALUES ('analytics',?,?,?,?,200)""",
            (ip, ua, referrer, f"[{event}] {page}"), fetch=False)
    return jsonify({"ok": True})

@app.route("/api/analytics/stats/<puuid>")
@user_req
def analytics_stats(puuid):
    """Loyiha uchun analytics statistika."""
    proj = q1("SELECT id FROM projects WHERE uuid=?", (puuid,))
    if not proj:
        return jsonify({})
    # Preview sahifasiga tashriflar
    views = q1("SELECT COUNT(*) c FROM access_logs WHERE path LIKE ?",
               (f"%/preview/{puuid}%",))
    unique = q1("SELECT COUNT(DISTINCT ip_address) c FROM access_logs WHERE path LIKE ?",
                (f"%/preview/{puuid}%",))
    daily = db_exec("""SELECT date(visited_at) d, COUNT(*) cnt FROM access_logs
        WHERE path LIKE ? AND visited_at > datetime('now','-14 days')
        GROUP BY date(visited_at) ORDER BY d""", (f"%/preview/{puuid}%",)) or []
    return jsonify({
        "total_views": views["c"] if views else 0,
        "unique_visitors": unique["c"] if unique else 0,
        "daily": [{"date": r["d"], "count": r["cnt"]} for r in daily]
    })



# ╔══════════════════════════════════════════════════════════════════════════╗
# ║              ERROR TRACKING (frontend JS xatolar)                           ║
# ╚══════════════════════════════════════════════════════════════════════════╝
@app.route("/api/errors/report", methods=["POST"])
def error_report():
    """Frontend JS xatolarni yig'ish (Sentry uslubida)."""
    d = request.get_json() or {}
    message = (d.get("message") or "")[:500]
    stack = (d.get("stack") or "")[:2000]
    url = (d.get("url") or "")[:500]
    ip = get_ip()
    ua = request.headers.get("User-Agent", "")[:200]
    if message:
        db_exec("""INSERT INTO audit_log (action,target_type,details,ip_address)
                   VALUES ('js_error','frontend',?,?)""",
                (json.dumps({"msg": message, "stack": stack[:500], "url": url, "ua": ua[:100]}, ensure_ascii=False)[:500], ip), fetch=False)
    return jsonify({"ok": True})

@app.route("/admin/errors")
@admin_req
def admin_errors():
    errors = db_exec("SELECT * FROM audit_log WHERE action='js_error' ORDER BY id DESC LIMIT 100") or []
    rows = ""
    for e in errors:
        details = {}
        try:
            details = json.loads(e.get("details") or "{}")
        except:
            pass
        rows += f"""<tr>
          <td style="max-width:300px;overflow:hidden;text-overflow:ellipsis;font-size:.75rem">{details.get('msg','')[:80]}</td>
          <td style="font-size:.72rem">{details.get('url','')[:40]}</td>
          <td><code style="font-size:.7rem">{e.get('ip_address','')}</code></td>
          <td class="tm" style="font-size:.72rem">{str(e['created_at'])[:19]}</td>
        </tr>"""
    body = f"""<h2 style="color:#fff;margin-bottom:14px">🐛 Frontend Xatolar</h2>
    <div class="card" style="padding:0"><div class="tw">
      <table><thead><tr><th>Xabar</th><th>URL</th><th>IP</th><th>Vaqt</th></tr></thead>
      <tbody>{rows or '<tr><td colspan=4 class="tm" style="text-align:center;padding:16px">Xato yoq</td></tr>'}</tbody></table>
    </div></div>"""
    return _pg("Xatolar", body, "errors")



# ╔══════════════════════════════════════════════════════════════════════════╗
# ║              TARIF REJALARI (Plans + Quotas)                                ║
# ╚══════════════════════════════════════════════════════════════════════════╝
PLANS = {
    "free":  {"name": "Bepul",  "max_projects": 3,  "max_files": 50,  "max_mb": 100},
    "pro":   {"name": "Pro",    "max_projects": 20, "max_files": 500, "max_mb": 2048},
    "business": {"name": "Business", "max_projects": 100, "max_files": 5000, "max_mb": 10240},
}

@app.route("/api/plan/current")
@user_req
def plan_current():
    uid = session["user_id"]
    user = q1("SELECT * FROM users WHERE id=?", (uid,))
    plan_id = get_setting(f"user_plan_{uid}", "free")
    plan = PLANS.get(plan_id, PLANS["free"])
    # Hozirgi foydalanish
    proj_count = (q1("SELECT COUNT(*) c FROM projects WHERE owner_id=?", (uid,)) or {}).get("c", 0)
    file_count = (q1("SELECT COUNT(*) c FROM files WHERE owner_id=?", (uid,)) or {}).get("c", 0)
    return jsonify({
        "plan": plan_id,
        "plan_info": plan,
        "usage": {"projects": proj_count, "files": file_count}
    })

@app.route("/api/plan/upgrade", methods=["POST"])
@user_req
def plan_upgrade():
    d = request.get_json() or {}
    new_plan = d.get("plan", "free")
    if new_plan not in PLANS:
        return jsonify({"ok": False, "error": "Noto'g'ri tarif"})
    uid = session["user_id"]
    set_setting(f"user_plan_{uid}", new_plan)
    audit("plan_upgrade", "user", str(uid), new_plan)
    return jsonify({"ok": True, "plan": new_plan, "info": PLANS[new_plan]})

@app.route("/admin/plans")
@admin_req
def admin_plans():
    users = db_exec("SELECT id,username,email FROM users ORDER BY id") or []
    rows = ""
    for u in users:
        plan_id = get_setting(f"user_plan_{u['id']}", "free")
        plan = PLANS.get(plan_id, PLANS["free"])
        rows += f"<tr><td>{u['username']}</td><td>{u.get('email','')}</td><td><span class='bx xp'>{plan['name']}</span></td></tr>"
    body = f"""<h2 style="color:#fff;margin-bottom:14px">💰 Tarif Rejalari</h2>
    <div class="card"><div class="tw"><table><thead><tr><th>User</th><th>Email</th><th>Tarif</th></tr></thead>
    <tbody>{rows or '<tr><td colspan=3 class="tm" style="text-align:center;padding:14px">Foydalanuvchilar yoq</td></tr>'}</tbody></table></div></div>"""
    return _pg("Tariflar", body, "settings")



# ╔══════════════════════════════════════════════════════════════════════════╗
# ║              CODE REVIEW (izohlar)                                          ║
# ╚══════════════════════════════════════════════════════════════════════════╝
@app.route("/api/review/<puuid>", methods=["GET", "POST"])
@user_req
def api_review(puuid):
    proj = q1("SELECT id FROM projects WHERE uuid=?", (puuid,))
    if not proj:
        return jsonify({"comments": []})
    if request.method == "GET":
        rows = db_exec("""SELECT r.*,u.username FROM audit_log r
            LEFT JOIN users u ON r.user_id=u.id
            WHERE r.action='code_review' AND r.target_id=?
            ORDER BY r.id DESC LIMIT 50""", (puuid,)) or []
        comments = []
        for r in rows:
            try:
                details = json.loads(r.get("details") or "{}")
            except:
                details = {}
            comments.append({
                "id": r["id"], "username": r.get("username",""),
                "file": details.get("file",""), "line": details.get("line",0),
                "comment": details.get("comment",""),
                "created_at": str(r["created_at"])[:19]
            })
        return jsonify({"comments": comments})
    # POST - yangi izoh
    d = request.get_json() or {}
    file_path = (d.get("file") or "").strip()
    line = int(d.get("line", 0))
    comment = (d.get("comment") or "").strip()[:500]
    if not comment:
        return jsonify({"ok": False, "error": "Izoh bosh"})
    audit("code_review", "project", puuid,
          json.dumps({"file": file_path, "line": line, "comment": comment}, ensure_ascii=False)[:500])
    return jsonify({"ok": True})



# ╔══════════════════════════════════════════════════════════════════════════╗
# ║              @MENTION BILDIRISHNOMALAR                                      ║
# ╚══════════════════════════════════════════════════════════════════════════╝
@app.route("/api/chat/<puuid>/mention", methods=["POST"])
@user_req
def chat_mention(puuid):
    """@mention aniqlanganda Telegram bildirishnoma yuborish."""
    d = request.get_json() or {}
    message = (d.get("message") or "").strip()
    # @username ni topish
    mentions = re.findall(r'@(\w+)', message)
    for username in mentions:
        user = q1("SELECT * FROM users WHERE username=?", (username,))
        if user:
            tg_chat = user.get("tg_chat_id") or ""
            if tg_chat:
                text = f"💬 @{session.get('username','')} sizni eslatdi:\n{message[:200]}"
                telegram_send_to(tg_chat, text)
    return jsonify({"ok": True, "mentions": mentions})


def telegram_send_to(chat_id, text):
    """Ma'lum chat_id ga Telegram xabar yuborish."""
    import urllib.request, urllib.parse
    token = get_setting("tg_token", CFG.get("TELEGRAM_TOKEN", ""))
    if not token or not chat_id:
        return
    def _send():
        try:
            url = f"https://api.telegram.org/bot{token}/sendMessage"
            data = urllib.parse.urlencode({"chat_id": chat_id, "text": text}).encode()
            urllib.request.urlopen(urllib.request.Request(url, data=data), timeout=6)
        except:
            pass
    threading.Thread(target=_send, daemon=True).start()



# ╔══════════════════════════════════════════════════════════════════════════╗
# ║              A/B TESTING                                                    ║
# ╚══════════════════════════════════════════════════════════════════════════╝
@app.route("/api/ab/create", methods=["POST"])
@user_req
@write_req
def ab_create():
    """Yangi A/B test yaratish."""
    d = request.get_json() or {}
    name = (d.get("name") or "").strip()
    variant_a = (d.get("variant_a") or "").strip()
    variant_b = (d.get("variant_b") or "").strip()
    if not name:
        return jsonify({"ok": False, "error": "Nom kerak"})
    test_id = str(uuid.uuid4())[:8]
    set_setting(f"ab_{test_id}", json.dumps({
        "name": name, "variant_a": variant_a, "variant_b": variant_b,
        "views_a": 0, "views_b": 0, "clicks_a": 0, "clicks_b": 0,
        "created_by": session.get("username",""), "active": True
    }))
    audit("ab_test_created", "ab", test_id, name)
    return jsonify({"ok": True, "test_id": test_id})

@app.route("/api/ab/<test_id>/variant")
def ab_get_variant(test_id):
    """Tasodifiy variant qaytarish (A yoki B)."""
    import random
    data_str = get_setting(f"ab_{test_id}", "")
    if not data_str:
        return jsonify({"variant": "a", "content": ""})
    try:
        data = json.loads(data_str)
    except:
        return jsonify({"variant": "a", "content": ""})
    variant = random.choice(["a", "b"])
    data[f"views_{variant}"] = data.get(f"views_{variant}", 0) + 1
    set_setting(f"ab_{test_id}", json.dumps(data))
    return jsonify({"variant": variant, "content": data.get(f"variant_{variant}", "")})

@app.route("/api/ab/<test_id>/convert", methods=["POST"])
def ab_convert(test_id):
    """Konversiya qayd etish."""
    d = request.get_json() or {}
    variant = d.get("variant", "a")
    data_str = get_setting(f"ab_{test_id}", "")
    if not data_str:
        return jsonify({"ok": False})
    try:
        data = json.loads(data_str)
        data[f"clicks_{variant}"] = data.get(f"clicks_{variant}", 0) + 1
        set_setting(f"ab_{test_id}", json.dumps(data))
    except:
        pass
    return jsonify({"ok": True})

@app.route("/api/ab/<test_id>/stats")
@user_req
def ab_stats(test_id):
    """A/B test statistikasi."""
    data_str = get_setting(f"ab_{test_id}", "")
    if not data_str:
        return jsonify({"error": "Test topilmadi"}), 404
    try:
        data = json.loads(data_str)
    except:
        return jsonify({"error": "Ma'lumot buzilgan"}), 500
    va, vb = data.get("views_a", 0), data.get("views_b", 0)
    ca, cb = data.get("clicks_a", 0), data.get("clicks_b", 0)
    return jsonify({
        "name": data.get("name",""),
        "variant_a": {"views": va, "clicks": ca, "rate": round(ca/va*100, 1) if va else 0},
        "variant_b": {"views": vb, "clicks": cb, "rate": round(cb/vb*100, 1) if vb else 0},
    })



# ╔══════════════════════════════════════════════════════════════════════════╗
# ║              ENVIRONMENT VARIABLES (.env)                                   ║
# ╚══════════════════════════════════════════════════════════════════════════╝
@app.route("/api/env/<puuid>", methods=["GET", "POST"])
@user_req
def api_env(puuid):
    proj = _proj_or_404(puuid, session["user_id"], session.get("admin"))
    if request.method == "GET":
        env_file = q1("SELECT content FROM project_files WHERE project_id=? AND path='.env'", (proj["id"],))
        vars_list = []
        if env_file and env_file.get("content"):
            for line in env_file["content"].split("\n"):
                line = line.strip()
                if "=" in line and not line.startswith("#"):
                    k, v = line.split("=", 1)
                    vars_list.append({"key": k.strip(), "value": v.strip()})
        return jsonify({"vars": vars_list})
    d = request.get_json() or {}
    key = (d.get("key") or "").strip().upper()
    value = (d.get("value") or "").strip()
    if not key:
        return jsonify({"ok": False})
    env_file = q1("SELECT content FROM project_files WHERE project_id=? AND path='.env'", (proj["id"],))
    content = env_file["content"] if env_file and env_file.get("content") else ""
    lines = content.split("\n") if content else []
    found = False
    for i, line in enumerate(lines):
        if line.strip().startswith(key + "="):
            lines[i] = f"{key}={value}"
            found = True
            break
    if not found:
        lines.append(f"{key}={value}")
    new_content = "\n".join(lines)
    db_exec("INSERT INTO project_files (project_id,path,is_folder,content) VALUES (?,'.env',0,?) "
            "ON CONFLICT(project_id,path) DO UPDATE SET content=excluded.content,updated_at=datetime('now')",
            (proj["id"], new_content), fetch=False)
    return jsonify({"ok": True})

@app.route("/api/env/<puuid>/<key>", methods=["DELETE"])
@user_req
@write_req
def api_env_delete(puuid, key):
    proj = _proj_or_404(puuid, session["user_id"], session.get("admin"))
    env_file = q1("SELECT content FROM project_files WHERE project_id=? AND path='.env'", (proj["id"],))
    if not env_file or not env_file.get("content"):
        return jsonify({"ok": True})
    lines = [l for l in env_file["content"].split("\n") if not l.strip().startswith(key + "=")]
    db_exec("UPDATE project_files SET content=?,updated_at=datetime('now') WHERE project_id=? AND path='.env'",
            ("\n".join(lines), proj["id"]), fetch=False)
    return jsonify({"ok": True})
