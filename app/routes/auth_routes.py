"""
Auth routes — Login, Register, Logout, Profile, 2FA
"""

from flask import request, session, redirect, abort, jsonify
from werkzeug.security import generate_password_hash, check_password_hash

from app.config import app, CFG
from app.database import db_exec, q1
from app.utils import get_ip, is_blocked, record_fail, clear_fails, telegram_send
from app.auth import (get_csrf_token, csrf_field, user_req, admin_req, write_req,
                      role_rank, new_api_key, send_2fa_code, verify_2fa_code, finalize_login)
from app.config import ROLE_RANK
from app.templates import _pg, _auth_pg, CSS


@app.route("/login", methods=["GET", "POST"])
def login():
    ip = get_ip()
    if is_blocked(ip):
        abort(403)
    err = None
    if request.method == "POST":
        u = request.form.get("username", "").strip()
        p = request.form.get("password", "")
        user = q1("SELECT * FROM users WHERE username=? AND is_active=1", (u,))
        if user and check_password_hash(user["password_hash"], p):
            finalize_login(user, ip)
            return redirect("/dashboard")
        else:
            if record_fail(ip, u):
                return _auth_pg("Kirish", "",
                    f"Juda ko'p xato. {CFG['BAN_MINUTES']} daqiqa bloklandi."), 403
            err = "Noto'g'ri login yoki parol"
    f = """
    <form method="POST">
      <div class="fld"><label>Login</label><input name="username" required placeholder="admin" autocomplete="username"></div>
      <div class="fld"><label>Parol</label><input name="password" type="password" required autocomplete="current-password"></div>
      <button class="btn bp" style="width:100%">Kirish</button>
    </form>
    <p style="text-align:center;margin-top:12px;font-size:.8rem">
      Hisob yo'qmi? <a href="/register">Ro'yxatdan o'tish</a></p>"""
    return _auth_pg("Kirish", f, err)


@app.route("/register", methods=["GET", "POST"])
def register():
    if is_blocked(get_ip()):
        abort(403)
    err = suc = None
    if request.method == "POST":
        u = request.form.get("username", "").strip()
        e = request.form.get("email", "").strip()
        p = request.form.get("password", "")
        c = request.form.get("confirm", "")
        if len(u) < 3:
            err = "Username kamida 3 ta belgi"
        elif len(p) < 6:
            err = "Parol kamida 6 ta belgi"
        elif p != c:
            err = "Parollar mos kelmadi"
        else:
            try:
                db_exec("INSERT INTO users (username,email,password_hash) VALUES (?,?,?)",
                        (u, e, generate_password_hash(p)), fetch=False)
                suc = "Ro'yxatdan o'tildi! Kirishingiz mumkin."
                telegram_send(f"🆕 Yangi foydalanuvchi ro'yxatdan o'tdi: {u} ({e})")
            except:
                err = "Bu username yoki email allaqachon mavjud"
    f = """
    <form method="POST">
      <div class="fld"><label>Username</label><input name="username" required></div>
      <div class="fld"><label>Email</label><input name="email" type="email" required></div>
      <div class="fld"><label>Parol</label><input name="password" type="password" required></div>
      <div class="fld"><label>Tasdiqlash</label><input name="confirm" type="password" required></div>
      <button class="btn bp" style="width:100%">Ro'yxatdan o'tish</button>
    </form>
    <p style="text-align:center;margin-top:12px;font-size:.8rem"><a href="/login">← Kirish</a></p>"""
    return _auth_pg("Ro'yxatdan o'tish", f, suc or err, "ok" if suc else "er")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


@app.route("/login/verify", methods=["GET", "POST"])
def login_verify():
    pending_uid = session.get("_pending_2fa_uid")
    if not pending_uid:
        return redirect("/login")
    err = None
    if request.method == "POST":
        code = request.form.get("code", "").strip()
        if verify_2fa_code(pending_uid, code):
            user = q1("SELECT * FROM users WHERE id=?", (pending_uid,))
            session.pop("_pending_2fa_uid", None)
            finalize_login(user, get_ip())
            return redirect("/dashboard")
        err = "Kod noto'g'ri yoki muddati o'tgan"
    f = f"""
    <form method="POST">{csrf_field()}
      <div class="fld"><label>Telegramga yuborilgan 6 xonali kod</label>
        <input name="code" required maxlength="6" autofocus placeholder="000000"></div>
      <button class="btn bp" style="width:100%">Tasdiqlash</button>
    </form>"""
    return _auth_pg("Ikki bosqichli tasdiqlash", f, err)


@app.route("/profile", methods=["GET", "POST"])
@user_req
def profile():
    uid = session["user_id"]
    err = suc = None
    if uid == 0:
        return redirect("/dashboard")
    if request.method == "POST":
        action = request.form.get("_action", "update")
        if action == "update":
            e = request.form.get("email", "").strip()
            tg_chat_id = request.form.get("tg_chat_id", "").strip()
            req2fa = 1 if request.form.get("require_2fa") else 0
            op = request.form.get("old_password", "")
            np = request.form.get("new_password", "")
            cp = request.form.get("confirm_password", "")
            user = q1("SELECT * FROM users WHERE id=?", (uid,))
            if np:
                if not check_password_hash(user["password_hash"], op):
                    err = "Joriy parol noto'g'ri"
                elif np != cp:
                    err = "Yangi parollar mos kelmadi"
                elif len(np) < 6:
                    err = "Kamida 6 ta belgi"
                else:
                    db_exec("UPDATE users SET email=?,password_hash=?,tg_chat_id=?,require_2fa=? WHERE id=?",
                            (e, generate_password_hash(np), tg_chat_id, req2fa, uid), fetch=False)
                    suc = "Parol va sozlamalar yangilandi"
            else:
                db_exec("UPDATE users SET email=?,tg_chat_id=?,require_2fa=? WHERE id=?",
                        (e, tg_chat_id, req2fa, uid), fetch=False)
                suc = "Sozlamalar yangilandi"
        elif action == "new_api_key" and role_rank(session.get("role")) >= ROLE_RANK["user"]:
            raw = new_api_key(uid, request.form.get("key_name", "API kalit"))
            suc = f"Yangi API kalit (faqat shu safar ko'rsatiladi): {raw}"
    user = q1("SELECT * FROM users WHERE id=?", (uid,))
    my_keys = db_exec("SELECT * FROM api_keys WHERE user_id=? AND revoked=0 ORDER BY created_at DESC",
                      (uid,)) or []
    keys_html = "".join(f"""<tr><td>{k.get('name') or '—'}</td><td><code>{k['key_prefix']}…</code></td>
      <td class="tm" style="font-size:.74rem">{str(k['created_at'])[:16]}</td>
      <td><form method="POST" action="/profile/apikey/revoke/{k['id']}">{csrf_field()}
        <button class="btn br bsm">🗑</button></form></td></tr>""" for k in my_keys)
    form = f"""<form method="POST">{csrf_field()}<input type="hidden" name="_action" value="update">
      <div class="fld"><label>Username</label><input value="{user['username']}" disabled style="opacity:.5"></div>
      <div class="fld"><label>Email</label><input name="email" value="{user.get('email','')}" type="email"></div>
      <div class="fld"><label>Telegram Chat ID</label>
        <input name="tg_chat_id" value="{user.get('tg_chat_id') or ''}" placeholder="@userinfobot orqali oling"></div>
      <label style="display:flex;gap:8px;align-items:center;margin-bottom:12px">
        <input type="checkbox" name="require_2fa" {'checked' if user.get('require_2fa') else ''} style="width:auto">
        Kirishda 2FA talab qilish
      </label>
      <div class="fld"><label>Joriy parol</label><input name="old_password" type="password"></div>
      <div class="g g2">
        <div class="fld"><label>Yangi parol</label><input name="new_password" type="password"></div>
        <div class="fld"><label>Tasdiqlash</label><input name="confirm_password" type="password"></div>
      </div>
      <button class="btn bp">Saqlash</button></form>"""
    api_form = f"""<form method="POST">{csrf_field()}<input type="hidden" name="_action" value="new_api_key">
      <div class="row"><div class="fld" style="flex:1"><label>Yangi API kalit nomi</label>
        <input name="key_name" placeholder="Masalan: CI/CD skripti"></div>
      <button class="btn bp">+ Yaratish</button></div></form>
      <div class="tw mt"><table><thead><tr><th>Nomi</th><th>Prefiks</th><th>Yaratilgan</th><th>Amal</th></tr></thead>
      <tbody>{keys_html or '<tr><td colspan=4 style="text-align:center;color:var(--mt);padding:12px">Hali API kalit yo'+chr(39)+'q</td></tr>'}</tbody></table></div>"""
    body = f"""
    <div class="card" style="max-width:520px"><h3>Profil</h3>{form}</div>
    <div class="card" style="max-width:520px"><h3>🔑 API kalitlarim</h3>{api_form}</div>"""
    return _pg("Profilim", body, "profile", flash=suc or err, ftype="ok" if suc else "er")


@app.route("/profile/apikey/revoke/<int:kid>", methods=["POST"])
@user_req
def profile_apikey_revoke(kid):
    db_exec("UPDATE api_keys SET revoked=1 WHERE id=? AND user_id=?",
            (kid, session["user_id"]), fetch=False)
    return redirect("/profile")
