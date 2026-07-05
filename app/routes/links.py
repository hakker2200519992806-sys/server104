"""
Havolalar CRUD va public link access
"""

import io
from datetime import datetime
from flask import request, session, redirect, abort, Response

from werkzeug.security import generate_password_hash

from app.config import app, CFG, QRCODE_OK, _active_mode
from app.database import db_exec, q1
from app.auth import user_req, write_req, csrf_field
from app.utils import (get_ip, is_blocked, check_link, log_access, mode_on,
                        gtok, local_ip)
from app.templates import _pg, CSS


@app.route("/links")
@user_req
def links_list():
    uid = session["user_id"]
    adm = session.get("admin") or session.get("_guest")
    if adm:
        lks = db_exec("SELECT l.*,u.username FROM links l LEFT JOIN users u ON l.owner_id=u.id ORDER BY l.created_at DESC") or []
    else:
        lks = db_exec("SELECT l.*,u.username FROM links l LEFT JOIN users u ON l.owner_id=u.id WHERE l.owner_id=? ORDER BY l.created_at DESC", (uid,)) or []
    port = CFG["PORT"]
    rows = ""
    for lk in lks:
        mb = {"private": "xp", "lan": "xb", "global": "xg"}.get(lk["mode"], "xm")
        stat = '<span class="bx xg">Faol</span>' if lk["is_active"] else '<span class="bx xr">O\'chiq</span>'
        exp = str(lk["expires_at"])[:16] if lk.get("expires_at") else "∞"
        url = f"http://127.0.0.1:{port}/p/{lk['token']}"
        pw = "🔐 " if lk.get("password_hash") else ""
        rows += f"""<tr>
          <td><span class="bx {mb}">{lk['mode']}</span></td>
          <td>{pw}{lk.get('label') or '—'}</td>
          <td><code style="font-size:.72rem;color:var(--ac)">{lk['token'][:14]}...</code>
            <button class="cpb" onclick="copyText('{url}')">Nusxa</button></td>
          <td>{stat}</td><td>{lk['visit_count']}</td><td>{exp}</td>
          <td>{lk.get('username') or '—'}</td>
          <td class="fl">
            <a href="/links/edit/{lk['id']}" class="btn bgh bsm">✏️</a>
            <form method="POST" action="/links/toggle/{lk['id']}">{csrf_field()}
              <button class="btn bgh bsm">{'⏸' if lk['is_active'] else '▶️'}</button></form>
            <form method="POST" action="/links/delete/{lk['id']}" onsubmit="return confirm('O'+chr(39)+'chirish?')">{csrf_field()}
              <button class="btn br bsm">🗑</button></form>
          </td>
        </tr>"""
    body = f"""
    <div class="fl mb"><h2 style="color:#fff">Havolalar</h2>
      <a href="/links/new" class="btn bp mla">+ Yangi havola</a></div>
    <div class="card" style="padding:0"><div class="tw">
      <table><thead><tr>
        <th>Rejim</th><th>Nom</th><th>Token</th><th>Holat</th>
        <th>Tashriflar</th><th>Muddat</th><th>Egasi</th><th>Amallar</th>
      </tr></thead><tbody>{rows or '<tr><td colspan=8 style="text-align:center;color:var(--mt);padding:20px">Hali havola yo'+chr(39)+'q</td></tr>'}</tbody></table>
    </div></div>"""
    return _pg("Havolalar", body, "links")


@app.route("/links/new", methods=["GET", "POST"])
@app.route("/links/edit/<int:lid>", methods=["GET", "POST"])
@user_req
@write_req
def link_form(lid=None):
    lk = {}
    if lid:
        lk = q1("SELECT * FROM links WHERE id=?", (lid,)) or {}
    err = suc = None
    if request.method == "POST":
        mode = request.form.get("mode", "private")
        label = request.form.get("label", "")
        tgt = request.form.get("target_path", "")
        pw = request.form.get("password", "")
        exp = request.form.get("expires", "")
        pid = request.form.get("project_id", "") or None
        ph = generate_password_hash(pw) if pw else None
        edt = None
        if exp:
            try:
                edt = datetime.strptime(exp, "%Y-%m-%dT%H:%M").strftime("%Y-%m-%d %H:%M:%S")
            except:
                err = "Noto'g'ri sana formati"
        if not err:
            if lid:
                if ph:
                    db_exec("UPDATE links SET mode=?,label=?,target_path=?,password_hash=?,expires_at=?,project_id=? WHERE id=?",
                            (mode, label, tgt, ph, edt, pid, lid), fetch=False)
                else:
                    db_exec("UPDATE links SET mode=?,label=?,target_path=?,expires_at=?,project_id=? WHERE id=?",
                            (mode, label, tgt, edt, pid, lid), fetch=False)
                suc = "Havola yangilandi"
            else:
                tok = gtok()
                db_exec("INSERT INTO links (token,mode,label,target_path,password_hash,expires_at,owner_id,project_id)"
                        " VALUES (?,?,?,?,?,?,?,?)",
                        (tok, mode, label, tgt, ph, edt, session["user_id"], pid), fetch=False)
                return redirect("/links")
    projs = db_exec("SELECT id,name FROM projects WHERE owner_id=? ORDER BY name", (session["user_id"],)) or []
    po = "".join(f'<option value="{p["id"]}" {"selected" if lk.get("project_id")==p["id"] else ""}>{p["name"]}</option>' for p in projs)
    mo = "".join(f'<option value="{m}" {"selected" if lk.get("mode",m)==m else ""}>{m.upper()}</option>' for m in ["private", "lan", "global"])
    form = f"""
    {'<div class="al al-er">'+err+'</div>' if err else ''}
    {'<div class="al al-ok">'+suc+'</div>' if suc else ''}
    <form method="POST">{csrf_field()}
      <div class="g g2">
        <div class="fld"><label>Rejim</label><select name="mode">{mo}</select></div>
        <div class="fld"><label>Nom</label><input name="label" value="{lk.get('label','') or ''}"></div>
      </div>
      <div class="fld"><label>Maqsad URL / yo'l</label>
        <input name="target_path" value="{lk.get('target_path','') or ''}" placeholder="/download/uuid yoki https://..."></div>
      <div class="g g2">
        <div class="fld"><label>Parol (bo'sh = yo'q)</label>
          <input name="password" type="password" placeholder="Yangi parol..."></div>
        <div class="fld"><label>Muddati</label>
          <input name="expires" type="datetime-local" value="{str(lk.get('expires_at',''))[:16] if lk.get('expires_at') else ''}"></div>
      </div>
      <div class="fld"><label>Loyiha (ixtiyoriy)</label>
        <select name="project_id"><option value="">— Tanlang —</option>{po}</select></div>
      <button class="btn bp">{'Yangilash' if lid else 'Yaratish'}</button>
      <a href="/links" class="btn bgh" style="margin-left:8px">Bekor</a>
    </form>"""
    return _pg("Havola", f'<div class="card"><h3>{"Havola tahrirlash" if lid else "Yangi havola"}</h3>{form}</div>', "links")


@app.route("/links/toggle/<int:lid>", methods=["POST"])
@user_req
@write_req
def link_toggle(lid):
    db_exec("UPDATE links SET is_active=1-is_active WHERE id=?", (lid,), fetch=False)
    return redirect("/links")


@app.route("/links/delete/<int:lid>", methods=["POST"])
@user_req
@write_req
def link_delete(lid):
    db_exec("DELETE FROM links WHERE id=?", (lid,), fetch=False)
    return redirect("/links")


@app.route("/p/<token>", methods=["GET", "POST"])
def link_access(token):
    ip = get_ip()
    if is_blocked(ip):
        abort(403)
    pw = request.form.get("password") if request.method == "POST" else None
    lk, err = check_link(token, pw)
    if err == "NEED_PASSWORD":
        return f"""<!DOCTYPE html><html><head><meta charset=UTF-8>
        <style>{CSS} body{{display:flex;align-items:center;justify-content:center;min-height:100vh}}</style>
        </head><body>
        <div style="background:var(--card);border:1px solid var(--brd);border-radius:12px;padding:28px;max-width:320px;width:100%">
          <p style="font-size:1.6rem;margin-bottom:10px">🔐</p>
          <form method="POST">
            <div class="fld"><input name="password" type="password" placeholder="Parol..." required autofocus></div>
            <button class="btn bp" style="width:100%">Kirish</button>
          </form>
        </div></body></html>"""
    if err:
        log_access("private", token, 403)
        return f"""<!DOCTYPE html><html><head><meta charset=UTF-8>
        <style>{CSS} body{{display:flex;align-items:center;justify-content:center;min-height:100vh;text-align:center}}</style>
        </head><body><div><p style="font-size:2.5rem">🚫</p>
        <h2 style="color:var(--rd);margin:10px 0">{err}</h2></div></body></html>""", 403
    db_exec("UPDATE links SET visit_count=visit_count+1 WHERE token=?", (token,), fetch=False)
    log_access(lk["mode"], token)
    tgt = lk.get("target_path", "")
    pid = lk.get("project_id")
    if pid:
        pr = q1("SELECT uuid FROM projects WHERE id=?", (pid,))
        if pr:
            return redirect(f"/preview/{pr['uuid']}?token={token}")
    if tgt:
        if tgt.startswith("http"):
            return redirect(tgt)
        return redirect(tgt)
    return f"""<!DOCTYPE html><html><head><meta charset=UTF-8>
    <style>{CSS} body{{display:flex;align-items:center;justify-content:center;min-height:100vh;text-align:center}}</style>
    </head><body><div><p style="font-size:2.5rem">✅</p>
    <h2 style="color:var(--gr);margin:10px 0">Havola faol!</h2></div></body></html>"""


@app.route("/qr/<token>")
def qr_image(token):
    if not QRCODE_OK:
        return "QR-kod uchun kerak: pip install qrcode[pil]", 501
    import qrcode
    port = CFG["PORT"]
    ip = local_ip()
    scope = request.args.get("scope", "lan")
    if scope == "private":
        url = f"http://127.0.0.1:{port}/p/{token}"
    elif scope == "global" and _active_mode.get("url"):
        url = f"{_active_mode['url']}/p/{token}"
    else:
        url = f"http://{ip}:{port}/p/{token}"
    img = qrcode.make(url)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return Response(buf.getvalue(), mimetype="image/png")
