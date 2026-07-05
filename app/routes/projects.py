"""
Loyihalar, Editor, Preview, Download
"""

import re
import uuid
import io
import zipfile
import html as hm

from flask import request, session, redirect, abort, send_file, jsonify

from app.config import app, CFG, FILES_PATH, _active_mode
from app.database import db_exec, q1
from app.auth import user_req, write_req, csrf_field, get_csrf_token
from app.utils import (get_ip, log_access, gtok, local_ip, audit,
                        _proj_or_404, _ensure_files, _build_page_html)
from app.templates import _pg, CSS


HISTORY_KEEP = 20


def _snapshot_history(project_id, path, content):
    db_exec("INSERT INTO project_file_history (project_id,path,content) VALUES (?,?,?)",
            (project_id, path, content), fetch=False)
    old = db_exec("SELECT id FROM project_file_history WHERE project_id=? AND path=? "
                  "ORDER BY id DESC LIMIT -1 OFFSET ?", (project_id, path, HISTORY_KEEP)) or []
    for r in old:
        db_exec("DELETE FROM project_file_history WHERE id=?", (r["id"],), fetch=False)


@app.route("/projects")
@user_req
def projects_list():
    uid = session["user_id"]
    adm = session.get("admin") or session.get("_guest")
    if adm:
        ps = db_exec("SELECT p.*,u.username FROM projects p LEFT JOIN users u ON p.owner_id=u.id ORDER BY p.updated_at DESC") or []
    else:
        ps = db_exec("SELECT p.*,u.username FROM projects p LEFT JOIN users u ON p.owner_id=u.id WHERE p.owner_id=? ORDER BY p.updated_at DESC", (uid,)) or []
    cards = ""
    for p in ps:
        pub = '<span class="bx xg">Ommaviy</span>' if p["is_public"] else '<span class="bx xm">Shaxsiy</span>'
        cards += f"""
        <div class="card">
          <div class="fl mb"><b style="color:#fff">{p['name']}</b>{pub}
            <span class="bx xp mla">v{p['current_version']}</span></div>
          <p class="tm" style="font-size:.78rem;margin-bottom:12px">
            {p.get('username') or '—'} · {str(p.get('updated_at',''))[:16]}</p>
          <div class="fl">
            <a href="/editor/{p['uuid']}" class="btn bp bsm">✏️ Tahrirlash</a>
            <a href="/preview/{p['uuid']}" class="btn bgh bsm" target="_blank">👁 Ko'rish</a>
            <a href="/projects/download/{p['uuid']}" class="btn bgh bsm">⬇ ZIP</a>
            <form method="POST" action="/projects/delete/{p['uuid']}" onsubmit="return confirm('O'+chr(39)+'chirish?')" style="margin-left:auto">{csrf_field()}
              <button class="btn br bsm">🗑</button></form>
          </div>
        </div>"""
    body = f"""
    <div class="fl mb"><h2 style="color:#fff">Loyihalar</h2>
      <a href="/editor/new" class="btn bp mla">+ Yangi loyiha</a></div>
    <div class="g g3">{cards or '<div class="card"><p class="tm">Hali loyiha yo'+chr(39)+'q. <a href="/editor/new">Yarating!</a></p></div>'}</div>"""
    return _pg("Loyihalar", body, "projects")


@app.route("/projects/delete/<puuid>", methods=["POST"])
@user_req
@write_req
def proj_delete(puuid):
    row = q1("SELECT id FROM projects WHERE uuid=?", (puuid,))
    if row:
        db_exec("DELETE FROM project_versions WHERE project_id=?", (row["id"],), fetch=False)
        db_exec("DELETE FROM project_files WHERE project_id=?", (row["id"],), fetch=False)
        db_exec("DELETE FROM project_file_history WHERE project_id=?", (row["id"],), fetch=False)
        db_exec("DELETE FROM projects WHERE uuid=?", (puuid,), fetch=False)
    return redirect("/projects")


@app.route("/projects/download/<puuid>")
@user_req
def project_download(puuid):
    proj = _proj_or_404(puuid, session["user_id"], session.get("admin") or session.get("_guest"))
    _ensure_files(proj["id"])
    rows = db_exec("SELECT path,is_folder,content FROM project_files WHERE project_id=?", (proj["id"],)) or []
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for r in rows:
            if r["is_folder"]:
                zf.writestr(r["path"].rstrip("/") + "/", "")
            else:
                zf.writestr(r["path"], r.get("content") or "")
    buf.seek(0)
    safe_name = re.sub(r'[^a-zA-Z0-9_-]+', '_', proj["name"]) or "loyiha"
    return send_file(buf, as_attachment=True, download_name=f"{safe_name}.zip", mimetype="application/zip")


@app.route("/editor/new", methods=["GET", "POST"])
@app.route("/editor/<puuid>")
@user_req
def editor(puuid=None):
    from app.auth import role_rank
    from app.config import ROLE_RANK
    if puuid is None:
        if request.method == "POST":
            if role_rank(session.get("role")) < ROLE_RANK["user"]:
                abort(403)
            name = request.form.get("name", "Yangi loyiha")
            uid_s = str(uuid.uuid4())
            new_id = db_exec("INSERT INTO projects (uuid,name,owner_id) VALUES (?,?,?)",
                             (uid_s, name, session["user_id"]), fetch=False)
            db_exec("INSERT INTO project_versions (project_id,version,html_code,css_code,js_code) VALUES (?,1,?,?,?)",
                    (new_id, '<!DOCTYPE html>\n<html>\n<head>\n  <meta charset="UTF-8">\n  <title>Sahifa</title>\n</head>\n<body>\n  <h1>Salom Dunyo!</h1>\n</body>\n</html>',
                     '/* CSS */', '// JS'), fetch=False)
            return redirect(f"/editor/{uid_s}")
        form = f'<div class="card" style="max-width:380px"><h3>Yangi loyiha</h3><form method="POST">{csrf_field()}<div class="fld"><label>Nomi</label><input name="name" required placeholder="Mening loyiham" autofocus></div><button class="btn bp">Yaratish</button><a href="/projects" class="btn bgh" style="margin-left:8px">Bekor</a></form></div>'
        return _pg("Yangi loyiha", form, "editor")
    proj = q1("SELECT * FROM projects WHERE uuid=?", (puuid,))
    if not proj:
        abort(404)
    _ensure_files(proj["id"])
    # Minimal editor sahifasi (to'liq editor kodi original server.py dan kelib chiqadi)
    csrf = get_csrf_token()
    return f"""<!DOCTYPE html><html lang="uz"><head><meta charset="UTF-8">
<title>Muharrir — {hm.escape(proj['name'])}</title>
<style>{CSS} body{{margin:0;padding:20px}}</style></head><body>
<h2 style="color:#fff">✏️ {hm.escape(proj['name'])}</h2>
<p class="tm">Editor yuklanmoqda... <a href="/projects">← Loyihalar</a></p>
<script>
var CSRF_TOKEN="{csrf}";
function authFetch(url,opts){{opts=opts||{{}};opts.headers=Object.assign({{'X-CSRF-Token':CSRF_TOKEN}},opts.headers||{{}});return fetch(url,opts);}}
</script>
</body></html>"""


@app.route("/preview/<puuid>")
def preview(puuid):
    proj = q1("SELECT * FROM projects WHERE uuid=?", (puuid,))
    if not proj:
        abort(404)
    is_owner = session.get("user_id") == proj["owner_id"]
    is_adm = session.get("admin", False)
    if not proj["is_public"] and not is_owner and not is_adm:
        tok = request.args.get("token", "")
        if tok:
            lk = q1("SELECT * FROM links WHERE token=? AND project_id=? AND is_active=1", (tok, proj["id"]))
            if not lk:
                abort(403)
        elif not session.get("user_id"):
            return redirect("/login")
        else:
            abort(403)
    _ensure_files(proj["id"])
    pf_rows = db_exec("SELECT path,content FROM project_files WHERE project_id=? AND is_folder=0", (proj["id"],)) or []
    files_map = {r["path"]: (r.get("content") or "") for r in pf_rows}
    entry = "index.html" if "index.html" in files_map else next(iter(files_map), None)
    built = _build_page_html(files_map, entry) if entry else None
    if built is not None:
        h = built
    else:
        ver = q1("SELECT * FROM project_versions WHERE project_id=? AND version=?", (proj["id"], proj["current_version"]))
        if ver:
            h = ver.get("html_code", "") or ""
            c = ver.get("css_code", "") or ""
            j = ver.get("js_code", "") or ""
            if c:
                h = f"<style>{c}</style>\n" + h
            if j:
                h += f"\n<script>{j}</script>"
        else:
            abort(404)
    log_access("private", path=f"/preview/{puuid}")
    return f"""<!DOCTYPE html><html><head><meta charset=UTF-8>
    <title>Preview — {hm.escape(proj['name'])}</title></head><body>
    <iframe srcdoc="{hm.escape(h)}" sandbox="allow-scripts allow-forms allow-popups allow-same-origin"
      style="width:100%;height:100vh;border:none;display:block"></iframe>
    </body></html>"""


# ── Virtual FS API ────────────────────────────────────────────────────────
@app.route("/editor/fs/all/<puuid>")
@user_req
def fs_all(puuid):
    proj = _proj_or_404(puuid, session["user_id"], session.get("admin") or session.get("_guest"))
    _ensure_files(proj["id"])
    rows = db_exec("SELECT path,is_folder,content FROM project_files WHERE project_id=? ORDER BY path", (proj["id"],)) or []
    return jsonify({"files": [{"path": r["path"], "is_folder": bool(r["is_folder"]), "content": r.get("content") or ""} for r in rows]})


@app.route("/editor/fs/write", methods=["POST"])
@user_req
@write_req
def fs_write_route():
    d = request.get_json() or {}
    proj = _proj_or_404(d.get("uuid", ""), session["user_id"], session.get("admin"))
    path = (d.get("path") or "").strip().strip("/")
    if not path:
        return jsonify({"ok": False, "error": "Yo'l bo'sh"})
    content = d.get("content", "")
    prev = q1("SELECT content FROM project_files WHERE project_id=? AND path=?", (proj["id"], path))
    if prev is not None and prev.get("content") is not None and prev["content"] != content:
        _snapshot_history(proj["id"], path, prev["content"])
    db_exec("INSERT INTO project_files (project_id,path,is_folder,content,updated_at) VALUES (?,?,0,?,datetime('now')) "
            "ON CONFLICT(project_id,path) DO UPDATE SET content=excluded.content, updated_at=datetime('now')",
            (proj["id"], path, content), fetch=False)
    db_exec("UPDATE projects SET updated_at=datetime('now') WHERE id=?", (proj["id"],), fetch=False)
    return jsonify({"ok": True})


@app.route("/editor/fs/history")
@user_req
def fs_history():
    puuid = request.args.get("uuid", "")
    path = request.args.get("path", "")
    proj = _proj_or_404(puuid, session["user_id"], session.get("admin") or session.get("_guest"))
    rows = db_exec("SELECT id,content,saved_at FROM project_file_history WHERE project_id=? AND path=? ORDER BY id DESC LIMIT ?",
                   (proj["id"], path, HISTORY_KEEP)) or []
    return jsonify({"history": [{"id": r["id"], "content": r["content"], "saved_at": str(r["saved_at"])[:19]} for r in rows]})


@app.route("/editor/fs/mkdir", methods=["POST"])
@user_req
@write_req
def fs_mkdir():
    d = request.get_json() or {}
    proj = _proj_or_404(d.get("uuid", ""), session["user_id"], session.get("admin"))
    path = (d.get("path") or "").strip().strip("/")
    if not path:
        return jsonify({"ok": False})
    ok = db_exec("INSERT OR IGNORE INTO project_files (project_id,path,is_folder,content) VALUES (?,?,1,NULL)",
                 (proj["id"], path), fetch=False)
    return jsonify({"ok": bool(ok)})


@app.route("/editor/fs/mkfile", methods=["POST"])
@user_req
@write_req
def fs_mkfile():
    d = request.get_json() or {}
    proj = _proj_or_404(d.get("uuid", ""), session["user_id"], session.get("admin"))
    path = (d.get("path") or "").strip().strip("/")
    if not path:
        return jsonify({"ok": False})
    ok = db_exec("INSERT OR IGNORE INTO project_files (project_id,path,is_folder,content) VALUES (?,?,0,?)",
                 (proj["id"], path, d.get("content", "")), fetch=False)
    return jsonify({"ok": bool(ok)})


@app.route("/editor/fs/rename", methods=["POST"])
@user_req
@write_req
def fs_rename():
    d = request.get_json() or {}
    proj = _proj_or_404(d.get("uuid", ""), session["user_id"], session.get("admin"))
    old = (d.get("old_path") or "").strip().strip("/")
    new = (d.get("new_path") or "").strip().strip("/")
    if not old or not new:
        return jsonify({"ok": False})
    rows = db_exec("SELECT * FROM project_files WHERE project_id=? AND (path=? OR path LIKE ?)",
                   (proj["id"], old, old + "/%")) or []
    for r in rows:
        np = new + r["path"][len(old):]
        db_exec("UPDATE project_files SET path=? WHERE id=?", (np, r["id"]), fetch=False)
    return jsonify({"ok": True})


@app.route("/editor/fs/delete", methods=["POST"])
@user_req
@write_req
def fs_delete():
    d = request.get_json() or {}
    proj = _proj_or_404(d.get("uuid", ""), session["user_id"], session.get("admin"))
    path = (d.get("path") or "").strip().strip("/")
    if not path:
        return jsonify({"ok": False})
    db_exec("DELETE FROM project_files WHERE project_id=? AND (path=? OR path LIKE ?)",
            (proj["id"], path, path + "/%"), fetch=False)
    return jsonify({"ok": True})


@app.route("/editor/snippets", methods=["GET", "POST"])
@user_req
def editor_snippets():
    if request.method == "GET":
        rows = db_exec("SELECT id,lang,trigger_key,body FROM user_snippets WHERE user_id=? ORDER BY trigger_key",
                       (session["user_id"],)) or []
        return jsonify({"snippets": rows})
    d = request.get_json() or {}
    lang = d.get("lang", "j")
    trig = (d.get("trigger") or "").strip()
    body = d.get("body", "")
    if lang not in ("h", "c", "j") or not trig or not body:
        return jsonify({"ok": False})
    new_id = db_exec("INSERT INTO user_snippets (user_id,lang,trigger_key,body) VALUES (?,?,?,?)",
                     (session["user_id"], lang, trig, body), fetch=False)
    return jsonify({"ok": True, "id": new_id})


@app.route("/editor/snippets/<int:sid>", methods=["DELETE"])
@user_req
@write_req
def editor_snippet_delete(sid):
    db_exec("DELETE FROM user_snippets WHERE id=? AND user_id=?", (sid, session["user_id"]), fetch=False)
    return jsonify({"ok": True})
