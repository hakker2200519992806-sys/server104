"""
Fayllar yuklash, yuklab olish, o'chirish
"""

import uuid
from datetime import datetime
from pathlib import Path

from flask import request, session, redirect, abort, send_from_directory
from werkzeug.utils import secure_filename

from app.config import app, CFG, FILES_PATH
from app.database import db_exec, q1
from app.auth import user_req, write_req, csrf_field
from app.utils import get_ip, allowed, hsize, log_access, telegram_send
from app.templates import _pg


@app.route("/files")
@user_req
def files_list():
    uid = session["user_id"]
    adm = session.get("admin") or session.get("_guest")
    if adm:
        fs = db_exec("SELECT f.*,u.username FROM files f LEFT JOIN users u ON f.owner_id=u.id ORDER BY f.created_at DESC") or []
    else:
        fs = db_exec("SELECT f.*,u.username FROM files f LEFT JOIN users u ON f.owner_id=u.id WHERE f.owner_id=? ORDER BY f.created_at DESC", (uid,)) or []
    rows = ""
    for f in fs:
        pub = '<span class="bx xg">Ommaviy</span>' if f["is_public"] else '<span class="bx xm">Shaxsiy</span>'
        exp = str(f["expires_at"])[:16] if f.get("expires_at") else "∞"
        rows += f"""<tr>
          <td>{f['original_name']}</td>
          <td><span class="bx xb">{f.get('file_type','?')}</span></td>
          <td>{hsize(f.get('file_size_bytes',0))}</td>
          <td>{pub}</td><td>{f['download_count']}</td><td>{exp}</td>
          <td>{f.get('username') or '—'}</td>
          <td class="fl">
            <a href="/download/{f['uuid']}" class="btn bg bsm">⬇ Olish</a>
            <form method="POST" action="/files/delete/{f['uuid']}" onsubmit="return confirm('O'+chr(39)+'chirish?')">{csrf_field()}
              <button class="btn br bsm">🗑</button></form>
          </td>
        </tr>"""
    body = f"""
    <div class="fl mb"><h2 style="color:#fff">Fayllar</h2></div>
    <div class="card"><h3>Fayl yuklash (max {CFG['MAX_FILE_MB']} MB)</h3>
      <form method="POST" action="/files/upload" enctype="multipart/form-data">{csrf_field()}
        <div class="row">
          <div class="fld" style="flex:1"><label>Fayl</label>
            <input type="file" name="file" required></div>
          <div class="fld"><label>Muddati</label>
            <input type="datetime-local" name="expires"></div>
          <div class="fld"><label>&nbsp;</label>
            <label style="display:flex;align-items:center;gap:6px;color:var(--mt);cursor:pointer">
              <input type="checkbox" name="is_public" style="width:auto">Ommaviy</label></div>
        </div>
        <button class="btn bp">⬆ Yuklash</button>
      </form>
    </div>
    <div class="card" style="padding:0"><div class="tw">
      <table><thead><tr>
        <th>Nomi</th><th>Tur</th><th>Hajm</th><th>Holat</th>
        <th>Yuklab olish</th><th>Muddat</th><th>Egasi</th><th>Amallar</th>
      </tr></thead><tbody>{rows or '<tr><td colspan=8 style="text-align:center;color:var(--mt);padding:20px">Hali fayl yo'+chr(39)+'q</td></tr>'}</tbody></table>
    </div></div>"""
    return _pg("Fayllar", body, "files")


@app.route("/files/upload", methods=["POST"])
@user_req
@write_req
def file_upload():
    f = request.files.get("file")
    if not f or not f.filename:
        return redirect("/files")
    if not allowed(f.filename):
        return _pg("Fayllar", '<div class="al al-er">Ruxsat etilmagan fayl turi!</div>', "files")
    f.seek(0, 2)
    sz = f.tell()
    f.seek(0)
    if sz > CFG["MAX_FILE_MB"] * 1024 * 1024:
        return _pg("Fayllar", f'<div class="al al-er">Fayl {CFG["MAX_FILE_MB"]}MB dan katta!</div>', "files")
    uid_s = str(uuid.uuid4())
    safe = secure_filename(f.filename)
    ext = Path(safe).suffix.lower()
    stored = uid_s + ext
    f.save(str(FILES_PATH / stored))
    edt = None
    exp = request.form.get("expires", "")
    if exp:
        try:
            edt = datetime.strptime(exp, "%Y-%m-%dT%H:%M").strftime("%Y-%m-%d %H:%M:%S")
        except:
            pass
    pub = 1 if request.form.get("is_public") else 0
    db_exec("INSERT INTO files (uuid,original_name,stored_name,file_type,file_size_bytes,owner_id,is_public,expires_at)"
            " VALUES (?,?,?,?,?,?,?,?)",
            (uid_s, safe, stored, ext.lstrip("."), sz, session["user_id"], pub, edt), fetch=False)
    telegram_send(f"📁 Yangi fayl yuklandi: {safe} ({hsize(sz)})\nYuklovchi: {session.get('username')}")
    return redirect("/files")


@app.route("/download/<fuid>")
def file_download(fuid):
    row = q1("SELECT * FROM files WHERE uuid=?", (fuid,))
    if not row:
        abort(404)
    if row.get("expires_at"):
        try:
            if datetime.now() > datetime.strptime(row["expires_at"], "%Y-%m-%d %H:%M:%S"):
                abort(410)
        except:
            pass
    if not row["is_public"] and session.get("user_id") != row["owner_id"] and not session.get("admin"):
        return redirect("/login")
    dest = FILES_PATH / row["stored_name"]
    if not dest.exists():
        abort(404)
    db_exec("UPDATE files SET download_count=download_count+1 WHERE uuid=?", (fuid,), fetch=False)
    nb = dest.stat().st_size
    log_access("private", path=f"/download/{fuid}", nb=nb)
    return send_from_directory(str(FILES_PATH), row["stored_name"],
                               as_attachment=True, download_name=row["original_name"])


@app.route("/files/delete/<fuid>", methods=["POST"])
@user_req
@write_req
def file_delete(fuid):
    row = q1("SELECT * FROM files WHERE uuid=?", (fuid,))
    if row:
        d = FILES_PATH / row["stored_name"]
        if d.exists():
            d.unlink()
        db_exec("DELETE FROM files WHERE uuid=?", (fuid,), fetch=False)
    return redirect("/files")


@app.route("/uploads/files/<filename>")
def serve_upload(filename):
    return send_from_directory(str(FILES_PATH), filename)
