"""
╔══════════════════════════════════════════════════════════════════════════════╗
║   QOSHIMCHA FUNKSIYALAR:                                                    ║
║   Custom Domain, IP Whitelist, Team, Audit, PWA, README, Markdown,          ║
║   Uptime, Color Picker, Komponentlar, Chat, TODO, Image Upload              ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import json
import re
import uuid
import os
import subprocess
from datetime import datetime, timedelta
from pathlib import Path

from flask import request, session, redirect, abort, jsonify

from app.config import app, CFG, FILES_PATH, ROLE_RANK
from app.database import db_exec, q1
from app.auth import user_req, write_req, admin_req, csrf_field, get_csrf_token
from app.utils import (get_ip, audit, get_setting, set_setting,
                        _proj_or_404, _ensure_files, hsize)
from app.templates import _pg, CSS



# ╔══════════════════════════════════════════════════════════════════════════╗
# ║              CUSTOM DOMAIN / SUBDOMAIN                                     ║
# ╚══════════════════════════════════════════════════════════════════════════╝
@app.route("/admin/domains", methods=["GET", "POST"])
@admin_req
def admin_domains():
    suc = None
    if request.method == "POST":
        action = request.form.get("_action", "add")
        if action == "add":
            puuid = request.form.get("project_uuid", "").strip()
            domain = request.form.get("domain", "").strip().lower()
            proj = q1("SELECT id FROM projects WHERE uuid=?", (puuid,))
            if proj and domain:
                db_exec("INSERT OR IGNORE INTO custom_domains (project_id,domain,created_by) VALUES (?,?,?)",
                        (proj["id"], domain, session["user_id"]), fetch=False)
                audit("domain_add", "domain", domain)
                suc = f"Domain qoshildi: {domain}"
        elif action == "delete":
            did = request.form.get("did")
            db_exec("DELETE FROM custom_domains WHERE id=?", (did,), fetch=False)
            suc = "Domain ochirildi"
        elif action == "toggle":
            did = request.form.get("did")
            db_exec("UPDATE custom_domains SET is_active=1-is_active WHERE id=?", (did,), fetch=False)
            suc = "Domain holati ozgartirildi"
    domains = db_exec("""SELECT d.*,p.name as pname,p.uuid as puuid
        FROM custom_domains d LEFT JOIN projects p ON d.project_id=p.id
        ORDER BY d.created_at DESC""") or []
    projs = db_exec("SELECT uuid,name FROM projects ORDER BY name") or []
    po = "".join(f'<option value="{p["uuid"]}">{p["name"]}</option>' for p in projs)
    rows = "".join(f"""<tr>
      <td><code style="color:var(--ac)">{d['domain']}</code></td>
      <td>{d.get('pname') or '-'}</td>
      <td><span class="bx {'xg' if d['is_active'] else 'xr'}">{'Faol' if d['is_active'] else 'Ochiq'}</span></td>
      <td class="fl">
        <form method="POST">{csrf_field()}<input type="hidden" name="_action" value="toggle"><input type="hidden" name="did" value="{d['id']}">
          <button class="btn bgh bsm">{'⏸' if d['is_active'] else '▶️'}</button></form>
        <form method="POST">{csrf_field()}<input type="hidden" name="_action" value="delete"><input type="hidden" name="did" value="{d['id']}">
          <button class="btn br bsm">🗑</button></form>
      </td></tr>""" for d in domains)
    body = f"""
    <h2 style="color:#fff;margin-bottom:14px">🌐 Custom Domain</h2>
    <div class="card">
      <p class="tm mb" style="font-size:.79rem">Har loyihaga subdomain bering. DNS A yozuvini server IP ga yonaltiring.</p>
      <form method="POST" class="row mb">{csrf_field()}<input type="hidden" name="_action" value="add">
        <select name="project_uuid" required style="flex:1;padding:7px;background:var(--bg);border:1px solid var(--brd);border-radius:6px;color:var(--tx)"><option value="">Loyiha</option>{po}</select>
        <input name="domain" placeholder="mysite.example.com" required style="flex:2;padding:7px 10px;background:var(--bg);border:1px solid var(--brd);border-radius:6px;color:var(--tx);font-size:.82rem">
        <button class="btn bp bsm">+ Qoshish</button>
      </form>
      <div class="tw"><table><thead><tr><th>Domain</th><th>Loyiha</th><th>Holat</th><th>Amal</th></tr></thead>
      <tbody>{rows or '<tr><td colspan=4 class="tm" style="text-align:center;padding:14px">Hali domain yoq</td></tr>'}</tbody></table></div>
    </div>"""
    return _pg("Domenlar", body, "domains", flash=suc, ftype="ok")



# ╔══════════════════════════════════════════════════════════════════════════╗
# ║              IP WHITELIST                                                   ║
# ╚══════════════════════════════════════════════════════════════════════════╝
@app.route("/admin/ip-whitelist", methods=["GET", "POST"])
@admin_req
def admin_ip_whitelist():
    suc = None
    if request.method == "POST":
        action = request.form.get("_action", "add")
        if action == "add":
            ip = request.form.get("ip", "").strip()
            label = request.form.get("label", "").strip()
            if ip:
                db_exec("INSERT OR IGNORE INTO ip_whitelist (ip_address,label,added_by) VALUES (?,?,?)",
                        (ip, label, session["user_id"]), fetch=False)
                audit("ip_whitelist_add", "ip", ip, label)
                suc = f"IP qoshildi: {ip}"
        elif action == "delete":
            wid = request.form.get("wid")
            db_exec("DELETE FROM ip_whitelist WHERE id=?", (wid,), fetch=False)
            suc = "IP ochirildi"
        elif action == "toggle":
            cur = get_setting("ip_whitelist_enabled", "0")
            set_setting("ip_whitelist_enabled", "0" if cur == "1" else "1")
            suc = "IP whitelist holati ozgartirildi"
    wl_on = get_setting("ip_whitelist_enabled", "0") == "1"
    ips = db_exec("SELECT * FROM ip_whitelist ORDER BY created_at DESC") or []
    rows = "".join(f"""<tr><td><code>{ip['ip_address']}</code></td><td>{ip.get('label') or '-'}</td>
      <td class="tm" style="font-size:.74rem">{str(ip['created_at'])[:16]}</td>
      <td><form method="POST">{csrf_field()}<input type="hidden" name="_action" value="delete">
        <input type="hidden" name="wid" value="{ip['id']}">
        <button class="btn br bsm">🗑</button></form></td></tr>""" for ip in ips)
    body = f"""
    <h2 style="color:#fff;margin-bottom:14px">🔒 IP Whitelist</h2>
    <div class="card">
      <div class="fl mb">
        <span class="bx {'xg' if wl_on else 'xm'}">{'Yoqilgan' if wl_on else 'Ochirilgan'}</span>
        <form method="POST" style="margin-left:auto">{csrf_field()}
          <input type="hidden" name="_action" value="toggle">
          <button class="btn {'br' if wl_on else 'bg'} bsm">{'🔴 Ochirish' if wl_on else '🟢 Yoqish'}</button>
        </form>
      </div>
      <p class="tm mb" style="font-size:.79rem">Yoqilganda faqat royxatdagi IP lar saytga kira oladi. Admin har doim kirishi mumkin.</p>
      <form method="POST" class="row mb">{csrf_field()}<input type="hidden" name="_action" value="add">
        <input name="ip" placeholder="192.168.1.10" required style="flex:1;padding:7px 10px;background:var(--bg);border:1px solid var(--brd);border-radius:6px;color:var(--tx);font-size:.82rem">
        <input name="label" placeholder="Izoh" style="flex:1;padding:7px 10px;background:var(--bg);border:1px solid var(--brd);border-radius:6px;color:var(--tx);font-size:.82rem">
        <button class="btn bp bsm">+ Qoshish</button>
      </form>
      <div class="tw"><table><thead><tr><th>IP</th><th>Izoh</th><th>Qoshilgan</th><th>Amal</th></tr></thead>
      <tbody>{rows or '<tr><td colspan=4 class="tm" style="text-align:center;padding:14px">Royxat bosh</td></tr>'}</tbody></table></div>
    </div>"""
    return _pg("IP Whitelist", body, "ipwl", flash=suc, ftype="ok")



# ╔══════════════════════════════════════════════════════════════════════════╗
# ║              JAMOA / TEAM TIZIMI                                            ║
# ╚══════════════════════════════════════════════════════════════════════════╝
@app.route("/projects/<puuid>/team", methods=["GET", "POST"])
@user_req
def project_team(puuid):
    import html as hm
    proj = q1("SELECT * FROM projects WHERE uuid=?", (puuid,))
    if not proj:
        abort(404)
    is_owner = proj["owner_id"] == session["user_id"]
    if not is_owner and not session.get("admin"):
        abort(403)
    suc = err = None
    if request.method == "POST":
        action = request.form.get("_action", "invite")
        if action == "invite":
            username = request.form.get("username", "").strip()
            role = request.form.get("role", "viewer")
            if role not in ("viewer", "editor"):
                role = "viewer"
            user = q1("SELECT id FROM users WHERE username=?", (username,))
            if not user:
                err = "Foydalanuvchi topilmadi"
            elif user["id"] == proj["owner_id"]:
                err = "Loyiha egasini qoshish shart emas"
            else:
                db_exec("INSERT OR REPLACE INTO project_teams (project_id,user_id,role,invited_by) VALUES (?,?,?,?)",
                        (proj["id"], user["id"], role, session["user_id"]), fetch=False)
                audit("team_invite", "project", puuid, f"{username} -> {role}")
                suc = f"{username} jamoga qoshildi ({role})"
        elif action == "remove":
            tid = request.form.get("tid")
            db_exec("DELETE FROM project_teams WHERE id=? AND project_id=?", (tid, proj["id"]), fetch=False)
            suc = "Foydalanuvchi jamoadan chiqarildi"
    members = db_exec("""SELECT t.*,u.username,u.email FROM project_teams t
        JOIN users u ON t.user_id=u.id WHERE t.project_id=? ORDER BY t.created_at""", (proj["id"],)) or []
    rows = "".join(f"""<tr><td>{m['username']}</td><td>{m.get('email','')}</td>
      <td><span class="bx {'xb' if m['role']=='editor' else 'xm'}">{m['role']}</span></td>
      <td><form method="POST">{csrf_field()}<input type="hidden" name="_action" value="remove">
        <input type="hidden" name="tid" value="{m['id']}"><button class="btn br bsm">🗑</button></form></td></tr>""" for m in members)
    body = f"""
    <h2 style="color:#fff;margin-bottom:14px">🧑‍🤝‍🧑 Jamoa — {hm.escape(proj['name'])}</h2>
    <div class="card">
      <form method="POST" class="row mb">{csrf_field()}<input type="hidden" name="_action" value="invite">
        <input name="username" placeholder="Username" required style="flex:1;padding:7px 10px;background:var(--bg);border:1px solid var(--brd);border-radius:6px;color:var(--tx)">
        <select name="role" style="padding:7px;background:var(--bg);border:1px solid var(--brd);border-radius:6px;color:var(--tx)">
          <option value="viewer">Viewer</option><option value="editor">Editor</option></select>
        <button class="btn bp bsm">+ Taklif</button>
      </form>
      <div class="tw"><table><thead><tr><th>User</th><th>Email</th><th>Rol</th><th>Amal</th></tr></thead>
      <tbody>{rows or '<tr><td colspan=4 class="tm" style="text-align:center;padding:14px">Jamoa azosi yoq</td></tr>'}</tbody></table></div>
    </div>
    <a href="/projects" class="btn bgh mt">← Loyihalar</a>"""
    return _pg("Jamoa", body, "projects", flash=suc or err, ftype="ok" if suc else "er")



# ╔══════════════════════════════════════════════════════════════════════════╗
# ║              PWA GENERATOR                                                 ║
# ╚══════════════════════════════════════════════════════════════════════════╝
@app.route("/api/pwa/generate/<puuid>", methods=["POST"])
@user_req
@write_req
def pwa_generate(puuid):
    proj = q1("SELECT * FROM projects WHERE uuid=?", (puuid,))
    if not proj:
        return jsonify({"ok": False}), 404
    name = proj["name"]
    manifest = json.dumps({
        "name": name, "short_name": name[:12], "start_url": ".", "display": "standalone",
        "background_color": "#0d0f18", "theme_color": "#7c6fff",
        "icons": [{"src": "icon-192.png", "sizes": "192x192", "type": "image/png"},
                  {"src": "icon-512.png", "sizes": "512x512", "type": "image/png"}]
    }, indent=2, ensure_ascii=False)
    sw = """const CACHE='pwa-v1';const ASSETS=['/','/index.html'];
self.addEventListener('install',e=>e.waitUntil(caches.open(CACHE).then(c=>c.addAll(ASSETS))));
self.addEventListener('fetch',e=>e.respondWith(caches.match(e.request).then(r=>r||fetch(e.request))));"""
    db_exec("INSERT INTO project_files (project_id,path,is_folder,content) VALUES (?,?,0,?) "
            "ON CONFLICT(project_id,path) DO UPDATE SET content=excluded.content,updated_at=datetime('now')",
            (proj["id"], "manifest.json", manifest), fetch=False)
    db_exec("INSERT INTO project_files (project_id,path,is_folder,content) VALUES (?,?,0,?) "
            "ON CONFLICT(project_id,path) DO UPDATE SET content=excluded.content,updated_at=datetime('now')",
            (proj["id"], "sw.js", sw), fetch=False)
    idx = q1("SELECT content FROM project_files WHERE project_id=? AND path='index.html'", (proj["id"],))
    if idx and idx.get("content"):
        html_content = idx["content"]
        if "manifest.json" not in html_content and "</head>" in html_content:
            pwa_tags = '  <link rel="manifest" href="manifest.json">\n  <meta name="theme-color" content="#7c6fff">\n'
            html_content = html_content.replace("</head>", pwa_tags + "</head>")
        if "sw.js" not in html_content and "</body>" in html_content:
            sw_reg = "  <script>if('serviceWorker' in navigator)navigator.serviceWorker.register('sw.js');</script>\n"
            html_content = html_content.replace("</body>", sw_reg + "</body>")
        db_exec("UPDATE project_files SET content=?,updated_at=datetime('now') WHERE project_id=? AND path='index.html'",
                (html_content, proj["id"]), fetch=False)
    audit("pwa_generate", "project", puuid)
    return jsonify({"ok": True, "files": ["manifest.json", "sw.js"]})



# ╔══════════════════════════════════════════════════════════════════════════╗
# ║              README GENERATOR                                              ║
# ╚══════════════════════════════════════════════════════════════════════════╝
@app.route("/api/readme/generate/<puuid>", methods=["POST"])
@user_req
@write_req
def readme_generate(puuid):
    proj = q1("SELECT * FROM projects WHERE uuid=?", (puuid,))
    if not proj:
        return jsonify({"ok": False}), 404
    files = db_exec("SELECT path,is_folder FROM project_files WHERE project_id=? ORDER BY path", (proj["id"],)) or []
    tree_lines = []
    for f in files:
        depth = f["path"].count("/")
        prefix = "  " * depth + ("📁 " if f["is_folder"] else "📄 ")
        tree_lines.append(prefix + f["path"].split("/")[-1])
    tree = "\n".join(tree_lines) or "Fayl yoq"
    readme = f"""# {proj['name']}

## Loyiha haqida
Bu loyiha SrvManager platformasida yaratilgan.

## Fayl tuzilmasi
```
{tree}
```

## Ishga tushirish
1. Fayllarni yuklab oling (ZIP)
2. `index.html` ni brauzerda oching

## Texnologiyalar
- HTML5
- CSS3
- JavaScript

## Muallif
Yaratilgan: {str(proj.get('created_at',''))[:10]}

---
*SrvManager tomonidan avtomatik yaratilgan*
"""
    db_exec("INSERT INTO project_files (project_id,path,is_folder,content) VALUES (?,?,0,?) "
            "ON CONFLICT(project_id,path) DO UPDATE SET content=excluded.content,updated_at=datetime('now')",
            (proj["id"], "README.md", readme), fetch=False)
    audit("readme_generate", "project", puuid)
    return jsonify({"ok": True, "content": readme})


# ╔══════════════════════════════════════════════════════════════════════════╗
# ║              MARKDOWN PREVIEW                                              ║
# ╚══════════════════════════════════════════════════════════════════════════╝
@app.route("/api/markdown/preview", methods=["POST"])
@user_req
def markdown_preview():
    d = request.get_json() or {}
    md_text = d.get("text", "")
    html_out = _simple_md_to_html(md_text)
    return jsonify({"html": html_out})


def _simple_md_to_html(text):
    """Minimal markdown -> HTML konverter."""
    lines = text.split("\n")
    html_lines = []
    in_code = False
    for line in lines:
        if line.startswith("```"):
            if in_code:
                html_lines.append("</pre></code>")
                in_code = False
            else:
                html_lines.append("<code><pre>")
                in_code = True
            continue
        if in_code:
            html_lines.append(line)
            continue
        if line.startswith("### "):
            html_lines.append(f"<h3>{line[4:]}</h3>")
        elif line.startswith("## "):
            html_lines.append(f"<h2>{line[3:]}</h2>")
        elif line.startswith("# "):
            html_lines.append(f"<h1>{line[2:]}</h1>")
        elif line.startswith("- ") or line.startswith("* "):
            html_lines.append(f"<li>{line[2:]}</li>")
        elif line.startswith("> "):
            html_lines.append(f"<blockquote>{line[2:]}</blockquote>")
        elif line.strip() == "---":
            html_lines.append("<hr>")
        elif line.strip() == "":
            html_lines.append("<br>")
        else:
            l = line
            l = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', l)
            l = re.sub(r'\*(.+?)\*', r'<em>\1</em>', l)
            l = re.sub(r'`(.+?)`', r'<code>\1</code>', l)
            l = re.sub(r'\[(.+?)\]\((.+?)\)', r'<a href="\2">\1</a>', l)
            html_lines.append(f"<p>{l}</p>")
    if in_code:
        html_lines.append("</pre></code>")
    return "\n".join(html_lines)



# ╔══════════════════════════════════════════════════════════════════════════╗
# ║              UPTIME MONITORING (sahifa)                                     ║
# ╚══════════════════════════════════════════════════════════════════════════╝
@app.route("/admin/uptime")
@admin_req
def admin_uptime_page():
    logs = db_exec("SELECT * FROM uptime_logs ORDER BY id DESC LIMIT 1440") or []
    total = len(logs)
    up_count = sum(1 for l in logs if l["status"] == "up")
    uptime_pct = round((up_count / total * 100), 2) if total else 100.0
    avg_ms = round(sum(l["response_ms"] or 0 for l in logs) / total, 1) if total else 0
    last_down = None
    for l in logs:
        if l["status"] == "down":
            last_down = str(l["checked_at"])[:19]
            break
    recent = logs[:60]
    bars = "".join(
        f'<div style="width:2px;height:{min(30, max(3,(l["response_ms"] or 0)//10))}px;'
        f'background:{"var(--gr)" if l["status"]=="up" else "var(--rd)"};border-radius:1px"></div>'
        for l in reversed(recent))
    body = f"""
    <h2 style="color:#fff;margin-bottom:14px">📉 Uptime Monitoring</h2>
    <div class="g g4 mb">
      <div class="stat"><div class="v" style="color:{'var(--gr)' if uptime_pct > 99 else 'var(--yl)'}">{uptime_pct}%</div><div class="l">Uptime (7 kun)</div></div>
      <div class="stat"><div class="v">{avg_ms}</div><div class="l">Ortacha javob (ms)</div></div>
      <div class="stat"><div class="v">{total}</div><div class="l">Tekshiruvlar</div></div>
      <div class="stat"><div class="v" style="font-size:1rem">{last_down or 'Hech qachon'}</div><div class="l">Oxirgi nosozlik</div></div>
    </div>
    <div class="card"><h3>Oxirgi 1 soat (har 1 daqiqa)</h3>
      <div style="display:flex;gap:1px;align-items:end;min-height:34px;padding:8px 0">{bars or '<span class="tm">Malumot yoq</span>'}</div>
    </div>"""
    return _pg("Uptime", body, "uptime")


# ╔══════════════════════════════════════════════════════════════════════════╗
# ║              COLOR PICKER API                                              ║
# ╚══════════════════════════════════════════════════════════════════════════╝
@app.route("/api/color/palettes")
@user_req
def color_palettes():
    palettes = {
        "Material": ["#F44336","#E91E63","#9C27B0","#673AB7","#3F51B5","#2196F3",
                     "#03A9F4","#00BCD4","#009688","#4CAF50","#8BC34A","#CDDC39",
                     "#FFEB3B","#FFC107","#FF9800","#FF5722"],
        "Pastel": ["#FFB3BA","#FFDFBA","#FFFFBA","#BAFFC9","#BAE1FF",
                   "#E8BAFF","#FFC8DD","#BDE0FE","#A2D2FF","#CDB4DB"],
        "Dark Theme": ["#0d0f18","#161929","#1c2136","#252d45","#7c6fff",
                       "#22d3a0","#f05d5d","#f5c518","#5c6890","#d4daf0"],
        "Gradient": ["linear-gradient(135deg,#667eea,#764ba2)",
                     "linear-gradient(135deg,#f093fb,#f5576c)",
                     "linear-gradient(135deg,#4facfe,#00f2fe)",
                     "linear-gradient(135deg,#43e97b,#38f9d7)",
                     "linear-gradient(135deg,#fa709a,#fee140)"],
    }
    return jsonify({"palettes": palettes})



# ╔══════════════════════════════════════════════════════════════════════════╗
# ║              KOMPONENT KUTUBXONASI                                          ║
# ╚══════════════════════════════════════════════════════════════════════════╝
@app.route("/api/components/full")
@user_req
def api_components_full():
    components = [
        {"id": "nav-bs", "name": "Navbar (Bootstrap)", "category": "Bootstrap",
         "code": '<nav class="navbar navbar-expand-lg navbar-dark bg-dark">\n  <div class="container">\n    <a class="navbar-brand" href="#">Logo</a>\n    <button class="navbar-toggler" data-bs-toggle="collapse" data-bs-target="#nav1"><span class="navbar-toggler-icon"></span></button>\n    <div class="collapse navbar-collapse" id="nav1">\n      <ul class="navbar-nav ms-auto"><li class="nav-item"><a class="nav-link" href="#">Bosh sahifa</a></li><li class="nav-item"><a class="nav-link" href="#">Haqida</a></li></ul>\n    </div>\n  </div>\n</nav>'},
        {"id": "card-bs", "name": "Card (Bootstrap)", "category": "Bootstrap",
         "code": '<div class="card" style="width:18rem">\n  <img src="https://via.placeholder.com/300x200" class="card-img-top" alt="...">\n  <div class="card-body">\n    <h5 class="card-title">Sarlavha</h5>\n    <p class="card-text">Qisqa tavsif.</p>\n    <a href="#" class="btn btn-primary">Batafsil</a>\n  </div>\n</div>'},
        {"id": "hero-bs", "name": "Hero Section (Bootstrap)", "category": "Bootstrap",
         "code": '<section class="bg-dark text-white py-5">\n  <div class="container text-center">\n    <h1 class="display-4">Xush kelibsiz!</h1>\n    <p class="lead">Asosiy matn.</p>\n    <a href="#" class="btn btn-primary btn-lg mt-3">Boshlash</a>\n  </div>\n</section>'},
        {"id": "form-bs", "name": "Form (Bootstrap)", "category": "Bootstrap",
         "code": '<form class="p-4">\n  <div class="mb-3"><label class="form-label">Email</label><input type="email" class="form-control" placeholder="email@example.com"></div>\n  <div class="mb-3"><label class="form-label">Parol</label><input type="password" class="form-control"></div>\n  <button type="submit" class="btn btn-primary">Yuborish</button>\n</form>'},
        {"id": "nav-tw", "name": "Navbar (Tailwind)", "category": "Tailwind",
         "code": '<nav class="bg-gray-800 p-4">\n  <div class="max-w-7xl mx-auto flex justify-between items-center">\n    <a href="#" class="text-white font-bold text-xl">Logo</a>\n    <div class="space-x-4"><a href="#" class="text-gray-300 hover:text-white">Bosh sahifa</a><a href="#" class="text-gray-300 hover:text-white">Haqida</a></div>\n  </div>\n</nav>'},
        {"id": "card-tw", "name": "Card (Tailwind)", "category": "Tailwind",
         "code": '<div class="max-w-sm rounded overflow-hidden shadow-lg bg-white">\n  <img class="w-full" src="https://via.placeholder.com/300x200" alt="">\n  <div class="px-6 py-4">\n    <div class="font-bold text-xl mb-2">Sarlavha</div>\n    <p class="text-gray-700 text-base">Tavsif.</p>\n  </div>\n</div>'},
        {"id": "hero-tw", "name": "Hero (Tailwind)", "category": "Tailwind",
         "code": '<section class="bg-gradient-to-r from-purple-600 to-indigo-600 text-white py-20">\n  <div class="max-w-4xl mx-auto text-center">\n    <h1 class="text-5xl font-bold mb-4">Xush kelibsiz!</h1>\n    <p class="text-xl mb-8">Zamonaviy dizayn.</p>\n    <a href="#" class="bg-white text-purple-600 px-8 py-3 rounded-full font-bold">Boshlash</a>\n  </div>\n</section>'},
        {"id": "footer", "name": "Footer", "category": "Umumiy",
         "code": '<footer style="background:#1a1a2e;color:#aaa;padding:30px 20px;text-align:center;margin-top:40px">\n  <p>&copy; 2025 Loyiha nomi. Barcha huquqlar himoyalangan.</p>\n  <div style="margin-top:10px"><a href="#" style="color:#7c6fff;margin:0 8px">GitHub</a><a href="#" style="color:#7c6fff;margin:0 8px">Telegram</a></div>\n</footer>'},
        {"id": "grid-css", "name": "CSS Grid Layout", "category": "Umumiy",
         "code": '<div style="display:grid;grid-template-columns:repeat(3,1fr);gap:16px;padding:20px">\n  <div style="background:#1c2136;border-radius:8px;padding:20px;color:#fff">Block 1</div>\n  <div style="background:#1c2136;border-radius:8px;padding:20px;color:#fff">Block 2</div>\n  <div style="background:#1c2136;border-radius:8px;padding:20px;color:#fff">Block 3</div>\n</div>'},
        {"id": "pricing", "name": "Pricing Table", "category": "Umumiy",
         "code": '<div style="display:flex;gap:20px;justify-content:center;padding:40px;flex-wrap:wrap">\n  <div style="background:#1c2136;border:1px solid #252d45;border-radius:12px;padding:30px;width:250px;text-align:center;color:#fff"><h3>Bepul</h3><p style="font-size:2rem;font-weight:700;color:#7c6fff">$0</p><p style="color:#888">1 loyiha<br>100MB</p><button style="background:#7c6fff;color:#fff;border:none;padding:10px 24px;border-radius:6px;cursor:pointer;margin-top:12px">Tanlash</button></div>\n  <div style="background:#1c2136;border:2px solid #7c6fff;border-radius:12px;padding:30px;width:250px;text-align:center;color:#fff"><h3>Pro</h3><p style="font-size:2rem;font-weight:700;color:#22d3a0">$9</p><p style="color:#888">10 loyiha<br>5GB</p><button style="background:#22d3a0;color:#000;border:none;padding:10px 24px;border-radius:6px;cursor:pointer;margin-top:12px;font-weight:700">Tanlash</button></div>\n</div>'},
        {"id": "login-form", "name": "Login Form (Dark)", "category": "Umumiy",
         "code": '<div style="max-width:360px;margin:40px auto;background:#1c2136;border:1px solid #252d45;border-radius:14px;padding:32px">\n  <h2 style="color:#fff;text-align:center;margin-bottom:20px">Kirish</h2>\n  <input type="text" placeholder="Login" style="width:100%;padding:10px;background:#0d0f18;border:1px solid #252d45;border-radius:7px;color:#d4daf0;margin-bottom:12px">\n  <input type="password" placeholder="Parol" style="width:100%;padding:10px;background:#0d0f18;border:1px solid #252d45;border-radius:7px;color:#d4daf0;margin-bottom:16px">\n  <button style="width:100%;padding:10px;background:#7c6fff;color:#fff;border:none;border-radius:7px;font-weight:600;cursor:pointer">Kirish</button>\n</div>'},
    ]
    return jsonify({"components": components})



# ╔══════════════════════════════════════════════════════════════════════════╗
# ║              TERMINAL (server buyruqlar)                                    ║
# ╚══════════════════════════════════════════════════════════════════════════╝
@app.route("/api/terminal/run", methods=["POST"])
@user_req
def terminal_run():
    """Terminal — faqat admin uchun."""
    if not session.get("admin"):
        return jsonify({"ok": False, "error": "Faqat admin ishlatishi mumkin"}), 403
    d = request.get_json() or {}
    cmd = (d.get("command") or "").strip()
    if not cmd:
        return jsonify({"ok": False, "error": "Buyruq bosh"})
    dangerous = ["rm -rf /", "mkfs", "dd if=", ":(){", "fork bomb",
                 "shutdown", "reboot", "halt", "format c:", "del /f /s /q"]
    for dng in dangerous:
        if dng in cmd.lower():
            return jsonify({"ok": False, "error": "Bu buyruq taqiqlangan"})
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True,
                                timeout=10, cwd=os.getcwd())
        output = result.stdout + result.stderr
        audit("terminal_exec", "command", None, cmd[:200])
        return jsonify({"ok": True, "output": output[:5000], "returncode": result.returncode})
    except subprocess.TimeoutExpired:
        return jsonify({"ok": False, "error": "Buyruq 10 sekundda yakunlanmadi (timeout)"})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)[:300]})


# ╔══════════════════════════════════════════════════════════════════════════╗
# ║              REAL-TIME CHAT                                                 ║
# ╚══════════════════════════════════════════════════════════════════════════╝
@app.route("/api/chat/<puuid>/list")
@user_req
def chat_list(puuid):
    proj = q1("SELECT id FROM projects WHERE uuid=?", (puuid,))
    if not proj:
        return jsonify({"messages": []})
    msgs = db_exec("SELECT * FROM chat_messages WHERE project_id=? ORDER BY id DESC LIMIT 100",
                   (proj["id"],)) or []
    msgs.reverse()
    return jsonify({"messages": [{"id": m["id"], "username": m["username"],
                                   "message": m["message"],
                                   "created_at": str(m["created_at"])[:19]} for m in msgs]})


@app.route("/api/chat/<puuid>/post", methods=["POST"])
@user_req
def chat_post(puuid):
    proj = q1("SELECT id FROM projects WHERE uuid=?", (puuid,))
    if not proj:
        return jsonify({"ok": False}), 404
    d = request.get_json() or {}
    msg = (d.get("message") or "").strip()[:500]
    if not msg:
        return jsonify({"ok": False, "error": "Xabar bosh"})
    db_exec("INSERT INTO chat_messages (project_id,user_id,username,message) VALUES (?,?,?,?)",
            (proj["id"], session["user_id"], session.get("username", ""), msg), fetch=False)
    return jsonify({"ok": True})


# ╔══════════════════════════════════════════════════════════════════════════╗
# ║              TODO / TASK LIST                                               ║
# ╚══════════════════════════════════════════════════════════════════════════╝
@app.route("/api/tasks/<puuid>", methods=["GET", "POST"])
@user_req
def api_tasks(puuid):
    proj = q1("SELECT id FROM projects WHERE uuid=?", (puuid,))
    if not proj:
        return jsonify({"todos": []})
    if request.method == "GET":
        todos = db_exec("SELECT * FROM project_todos WHERE project_id=? ORDER BY is_done, priority DESC, id DESC",
                        (proj["id"],)) or []
        return jsonify({"todos": todos})
    d = request.get_json() or {}
    title = (d.get("title") or "").strip()[:200]
    priority = d.get("priority", "normal")
    if priority not in ("low", "normal", "high"):
        priority = "normal"
    if not title:
        return jsonify({"ok": False, "error": "Sarlavha kerak"})
    new_id = db_exec("INSERT INTO project_todos (project_id,user_id,title,priority) VALUES (?,?,?,?)",
                     (proj["id"], session["user_id"], title, priority), fetch=False)
    return jsonify({"ok": True, "id": new_id})


@app.route("/api/tasks/<puuid>/<int:tid>", methods=["PUT", "DELETE"])
@user_req
def api_task_item(puuid, tid):
    proj = q1("SELECT id FROM projects WHERE uuid=?", (puuid,))
    if not proj:
        abort(404)
    if request.method == "DELETE":
        db_exec("DELETE FROM project_todos WHERE id=? AND project_id=?", (tid, proj["id"]), fetch=False)
        return jsonify({"ok": True})
    d = request.get_json() or {}
    is_done = 1 if d.get("is_done") else 0
    completed_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S") if is_done else None
    db_exec("UPDATE project_todos SET is_done=?,completed_at=? WHERE id=? AND project_id=?",
            (is_done, completed_at, tid, proj["id"]), fetch=False)
    return jsonify({"ok": True})


# ╔══════════════════════════════════════════════════════════════════════════╗
# ║              RASM YUKLASH (drag&drop)                                       ║
# ╚══════════════════════════════════════════════════════════════════════════╝
@app.route("/api/image/upload/<puuid>", methods=["POST"])
@user_req
@write_req
def api_image_upload(puuid):
    from werkzeug.utils import secure_filename
    proj = q1("SELECT * FROM projects WHERE uuid=?", (puuid,))
    if not proj:
        return jsonify({"ok": False}), 404
    f = request.files.get("image")
    if not f or not f.filename:
        return jsonify({"ok": False, "error": "Fayl tanlanmadi"})
    ext = Path(f.filename).suffix.lower()
    if ext not in (".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp", ".ico"):
        return jsonify({"ok": False, "error": "Ruxsat etilmagan format"})
    safe_name = secure_filename(f.filename)
    stored = f"{uuid.uuid4().hex[:8]}_{safe_name}"
    dest = FILES_PATH / stored
    f.save(str(dest))
    url = f"/uploads/files/{stored}"
    audit("image_upload", "project", puuid, safe_name)
    return jsonify({"ok": True, "url": url, "filename": safe_name})
