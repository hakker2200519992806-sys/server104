"""
Rejimlar boshqaruvi — Private, LAN, Global, Ngrok
"""

from flask import request, session, redirect

from app.config import app, CFG, NGROK_OK, _active_mode, _ngrok_tunnel
from app.database import db_exec, q1
from app.auth import user_req, admin_req, csrf_field
from app.utils import (get_ip, mode_on, local_ip, get_ssid,
                        get_setting, set_setting, server_enabled)
from app.templates import _pg


@app.route("/modes")
@user_req
def modes_page():
    ip = local_ip()
    ssid = get_ssid()
    port = CFG["PORT"]
    pub = _active_mode.get("url", "") or "(ngrok ishga tushirilmagan)"
    data = [
        ("private", "🔒", "Shaxsiy", "Token — faqat siz", f"http://127.0.0.1:{port}/p/TOKEN"),
        ("lan", "📡", "LAN", "WiFi — " + ssid, f"http://{ip}:{port}"),
        ("global", "🌍", "Global", "Internet orqali", pub)
    ]
    cards = ""
    for mode, icon, label, desc, url in data:
        on = mode_on(mode)
        ngrok_btns = ""
        if mode == "global":
            ngrok_btns = f'<form method="POST" action="/modes/ngrok/start" style="display:inline">{csrf_field()}<button class="btn bgh bsm">🚀 Ngrok start</button></form>'
            if _active_mode.get("url"):
                ngrok_btns += f'<form method="POST" action="/modes/ngrok/stop" style="display:inline;margin-left:6px">{csrf_field()}<button class="btn br bsm">⏹ Stop</button></form>'
        safe_url = url.replace("'", "")
        cards += f"""
        <div class="mcard {'on' if on else ''}">
          <div class="fl mb"><span style="font-size:1.4rem">{icon}</span>
            <b style="color:#fff">{label}</b>
            <span class="bx {'xg' if on else 'xr'} mla">{'Faol' if on else "O'chiq"}</span></div>
          <p class="tm" style="font-size:.79rem;margin-bottom:10px">{desc}</p>
          <div class="urlbox">{url}</div>
          <button class="cpb mt" onclick="copyText('{safe_url}')">Nusxa</button>
          <div class="fl mt">
            <form method="POST" action="/modes/toggle/{mode}">{csrf_field()}
              <button class="btn {'br' if on else 'bg'} bsm">{'🔴 O'+chr(39)+'chir' if on else '🟢 Yoq'}</button>
            </form>
            {ngrok_btns}
          </div>
        </div>"""

    srv_on = server_enabled()
    srv_btn = ""
    if session.get("admin"):
        srv_btn = f"""<form method="POST" action="/admin/server/toggle" class="mt">{csrf_field()}
          <button class="btn {'br' if srv_on else 'bg'} bsm">{"🔴 Serverni o'chirish" if srv_on else "🟢 Serverni yoqish"}</button>
        </form>"""
    srv_card = f"""
    <div class="card mb" style="border-left:3px solid {'var(--gr)' if srv_on else 'var(--rd)'}">
      <div class="fl"><span style="font-size:1.4rem">{'🟢' if srv_on else '🔴'}</span>
        <b style="color:#fff">SERVER (umumiy kirish)</b>
        <span class="bx {'xg' if srv_on else 'xr'} mla">{'Yoqilgan' if srv_on else "O'chirilgan"}</span></div>
      <p class="tm mt" style="font-size:.79rem">Bu tugma butun saytga kirishni yoqadi yoki o'chiradi.</p>
      {srv_btn}
    </div>"""

    guest_on = get_setting("require_login", "1") == "0"
    guest_btn = ""
    if session.get("admin"):
        guest_btn = f"""<form method="POST" action="/admin/guest/toggle" class="mt">{csrf_field()}
          <button class="btn {'br' if guest_on else 'bgh'} bsm">{"🔴 Guest o'chirish" if guest_on else "🟢 Guest yoqish"}</button>
        </form>"""
    guest_card = f"""
    <div class="card mb" style="border-left:3px solid {'var(--yl)' if guest_on else 'var(--brd)'}">
      <div class="fl"><span style="font-size:1.4rem">👤</span>
        <b style="color:#fff">LOGINSIZ KIRISH (Guest)</b>
        <span class="bx {'xy' if guest_on else 'xm'} mla">{'Yoqilgan' if guest_on else "O'chirilgan"}</span></div>
      <p class="tm mt" style="font-size:.79rem">Yoqilsa, login qilmasdan kirish mumkin.</p>
      {guest_btn}
    </div>"""

    ngrok_token = get_setting("ngrok_token", CFG.get("NGROK_TOKEN", ""))
    ngrok_installed = NGROK_OK

    # Global card uchun qo'shimcha ma'lumot
    global_info = ""
    if _active_mode.get("url"):
        global_info = f"""
        <div class="al al-ok mt" style="font-size:.82rem">
          <b>✅ Global rejim faol!</b> Bu linkni boshqalarga yuboring — ular brauzerda ochib saytingizga kiradi:
        </div>
        <div class="urlbox" style="font-size:.9rem;padding:12px;background:#0a3d2e;border-color:#0d5a40;color:#22d3a0">
          {_active_mode['url']}
        </div>
        <button class="cpb mt" onclick="copyText('{_active_mode['url']}')" style="padding:6px 14px;font-size:.8rem">📋 Linkni nusxalash</button>
        """
    elif not ngrok_installed:
        global_info = f"""
        <div class="al al-er mt" style="font-size:.82rem">
          <b>⚠️ pyngrok kutubxonasi o'rnatilmagan!</b><br>
          Terminalda bajaring: <code style="background:#0d0f18;padding:2px 6px;border-radius:4px">pip install pyngrok</code>
        </div>"""
    elif not ngrok_token:
        global_info = f"""
        <div class="al al-er mt" style="font-size:.82rem">
          <b>⚠️ Ngrok token kiritilmagan!</b><br>
          1. <a href="https://dashboard.ngrok.com/get-started/your-authtoken" target="_blank" style="color:#7c6fff">dashboard.ngrok.com</a> dan bepul ro'yxatdan o'ting<br>
          2. "Your Authtoken" ni nusxalang<br>
          3. Pastdagi formaga joylashtiring
        </div>"""

    # Ngrok token kiritish formasi
    ngrok_form = ""
    if session.get("admin"):
        ngrok_form = f"""
        <div class="card mt"><h3>🔑 Ngrok Token</h3>
          <p class="tm mb" style="font-size:.79rem">
            <a href="https://dashboard.ngrok.com/get-started/your-authtoken" target="_blank">dashboard.ngrok.com</a> dan oling (bepul).
            Token kiritilsa, "🚀 Ngrok start" tugmasi ishlaydi va sizga global link beriladi.
          </p>
          <form method="POST" action="/modes/ngrok/token" class="row">{csrf_field()}
            <input name="ngrok_token" value="{ngrok_token}" placeholder="2xxxxxxxxxxxxxxxxxxxxxxx..."
              style="flex:1;padding:8px 12px;background:var(--bg);border:1px solid var(--brd);border-radius:7px;color:var(--tx);font-family:monospace;font-size:.82rem">
            <button class="btn bp bsm">💾 Saqlash</button>
          </form>
          <p class="tm mt" style="font-size:.75rem">Holat: {'✅ pyngrok o'+chr(39)+'rnatilgan' if ngrok_installed else '❌ pyngrok o'+chr(39)+'rnatilmagan (pip install pyngrok)'}</p>
        </div>"""

    body = f"""
    <div class="fl mb"><h2 style="color:#fff">Rejimlar</h2>
      <a href="/links/new" class="btn bp mla">+ Havola yaratish</a></div>
    {global_info}
    {srv_card}
    {guest_card}
    <div class="g g3">{cards}</div>
    {ngrok_form}
    <div class="card mt"><h3>Tarmoq ma'lumotlari</h3>
      <div class="g g3">
        <div><p class="tm mb" style="font-size:.78rem">Lokal IP</p>
          <code style="color:var(--ac)">{ip}:{port}</code></div>
        <div><p class="tm mb" style="font-size:.78rem">WiFi SSID</p>
          <code style="color:var(--ac)">{ssid}</code></div>
        <div><p class="tm mb" style="font-size:.78rem">Ngrok URL</p>
          <code style="color:var(--gr)">{_active_mode.get('url') or 'Ishga tushirilmagan'}</code></div>
      </div>
    </div>
    <div class="card mt"><h3>📖 Global rejim qanday ishlaydi?</h3>
      <ol style="color:var(--mt);font-size:.82rem;line-height:1.8;padding-left:20px">
        <li><b>pip install pyngrok</b> — kutubxonani o'rnatish</li>
        <li><a href="https://dashboard.ngrok.com" target="_blank">ngrok.com</a> da ro'yxatdan o'tish (bepul) va <b>Authtoken</b> olish</li>
        <li>Tokenni yuqoridagi formaga kiritish</li>
        <li><b>🚀 Ngrok start</b> tugmasini bosish</li>
        <li>Paydo bo'lgan linkni (masalan: <code>https://abc123.ngrok-free.app</code>) boshqalarga yuborish</li>
        <li>Ular brauzerda ochib sizning saytingizga kiradi! 🎉</li>
      </ol>
    </div>"""
    return _pg("Rejimlar", body, "modes")


@app.route("/modes/toggle/<mode>", methods=["POST"])
@user_req
def toggle_mode(mode):
    if mode not in ("private", "lan", "global"):
        from flask import abort
        abort(400)
    r = q1("SELECT is_enabled FROM mode_settings WHERE mode=?", (mode,))
    db_exec("UPDATE mode_settings SET is_enabled=? WHERE mode=?",
            (0 if r and r["is_enabled"] else 1, mode), fetch=False)
    return redirect("/modes")


@app.route("/modes/ngrok/start", methods=["POST"])
@user_req
def ngrok_start():
    global _ngrok_tunnel
    import app.config as cfg
    if not NGROK_OK:
        return redirect("/modes")
    try:
        from pyngrok import ngrok as _ngrok_mod
        # Token: avval sozlamadan, keyin CFG dan
        token = get_setting("ngrok_token", CFG.get("NGROK_TOKEN", ""))
        if token:
            _ngrok_mod.set_auth_token(token)
        cfg._ngrok_tunnel = _ngrok_mod.connect(CFG["PORT"], "http")
        cfg._active_mode["url"] = cfg._ngrok_tunnel.public_url
    except Exception as e:
        from app.config import _c, R
        print(_c(f"[ngrok] {e}", R))
    return redirect("/modes")


@app.route("/modes/ngrok/token", methods=["POST"])
@user_req
def ngrok_save_token():
    """Ngrok tokenni saqlash."""
    token = request.form.get("ngrok_token", "").strip()
    set_setting("ngrok_token", token)
    return redirect("/modes")


@app.route("/modes/ngrok/stop", methods=["POST"])
@user_req
def ngrok_stop():
    import app.config as cfg
    if NGROK_OK:
        try:
            from pyngrok import ngrok as _ngrok_mod
            _ngrok_mod.kill()
        except:
            pass
    cfg._ngrok_tunnel = None
    cfg._active_mode["url"] = None
    return redirect("/modes")


@app.route("/admin/guest/toggle", methods=["POST"])
@admin_req
def admin_guest_toggle():
    cur = get_setting("require_login", "1")
    set_setting("require_login", "1" if cur == "0" else "0")
    return redirect(request.referrer or "/modes")


@app.route("/admin/server/toggle", methods=["POST"])
@admin_req
def admin_server_toggle():
    cur = get_setting("server_enabled", "1")
    set_setting("server_enabled", "0" if cur == "1" else "1")
    return redirect(request.referrer or "/modes")
