"""
Admin sahifalari — Foydalanuvchilar, Loglar, Bloklash, Monitoring, Sozlamalar
"""

import os
import time
import shutil
from datetime import datetime, timedelta
from pathlib import Path

from flask import request, session, redirect, abort, jsonify, send_file

from app.config import app, CFG, PSUTIL_OK, PROCESS_START, ROLE_RANK
from app.database import db_exec, q1
from app.auth import admin_req, csrf_field, role_rank
from app.utils import (get_ip, hsize, get_setting, set_setting, audit)
from app.templates import _pg


@app.route("/admin/users")
@admin_req
def admin_users():
    us = db_exec("SELECT * FROM users ORDER BY created_at DESC") or []
    role_opts = ["viewer", "user", "editor", "admin"]
    rows = "".join(f"""<tr>
      <td>{u['id']}</td><td>{u['username']}</td><td>{u.get('email','')}</td>
      <td>
        <form method="POST" action="/admin/users/role/{u['id']}" style="display:inline-flex;gap:4px">{csrf_field()}
          <select name="role" onchange="this.form.submit()" style="padding:3px 6px;background:var(--bg);border:1px solid var(--brd);color:var(--tx);border-radius:5px;font-size:.72rem">
            {''.join(f'<option value="{r}" {"selected" if u["role"]==r else ""}>{r}</option>' for r in role_opts)}
          </select>
        </form>
      </td>
      <td>{'✓' if u['is_active'] else '✗'}</td>
      <td class="tm" style="font-size:.76rem">{str(u.get('last_login','—'))[:16]}</td>
      <td class="fl">
        <form method="POST" action="/admin/users/toggle/{u['id']}">{csrf_field()}
          <button class="btn bgh bsm">{'🔴' if u['is_active'] else '🟢'}</button></form>
        <form method="POST" action="/admin/users/del/{u['id']}" onsubmit="return confirm('O'+chr(39)+'chirish?')">{csrf_field()}
          <button class="btn br bsm">🗑</button></form>
      </td>
    </tr>""" for u in us)
    body = f"""<h2 style="color:#fff;margin-bottom:14px">👥 Foydalanuvchilar</h2>
    <div class="card" style="padding:0"><div class="tw">
      <table><thead><tr><th>#</th><th>Login</th><th>Email</th><th>Rol</th><th>Faol</th><th>Oxirgi kirish</th><th>Amallar</th></tr></thead>
      <tbody>{rows}</tbody></table></div></div>"""
    return _pg("Foydalanuvchilar", body, "users")


@app.route("/admin/users/role/<int:uid>", methods=["POST"])
@admin_req
def admin_usr_role(uid):
    role = request.form.get("role", "user")
    if role not in ROLE_RANK:
        abort(400)
    db_exec("UPDATE users SET role=? WHERE id=?", (role, uid), fetch=False)
    return redirect("/admin/users")


@app.route("/admin/users/toggle/<int:uid>", methods=["POST"])
@admin_req
def admin_usr_toggle(uid):
    db_exec("UPDATE users SET is_active=1-is_active WHERE id=?", (uid,), fetch=False)
    return redirect("/admin/users")


@app.route("/admin/users/del/<int:uid>", methods=["POST"])
@admin_req
def admin_usr_del(uid):
    if uid != session.get("user_id"):
        db_exec("DELETE FROM users WHERE id=?", (uid,), fetch=False)
    return redirect("/admin/users")


@app.route("/admin/logs")
@admin_req
def admin_logs():
    pg = int(request.args.get("p", 1))
    pp = 40
    tot = (q1("SELECT COUNT(*) c FROM access_logs") or {}).get("c", 0)
    logs = db_exec("SELECT * FROM access_logs ORDER BY visited_at DESC LIMIT ? OFFSET ?", (pp, (pg-1)*pp)) or []
    rows = "".join(f"""<tr>
      <td><span class="bx xp">{l['mode']}</span></td>
      <td><code style="font-size:.73rem">{l['ip_address']}</code></td>
      <td style="max-width:200px;overflow:hidden;text-overflow:ellipsis;font-size:.75rem">{l['path']}</td>
      <td><span class="bx {'xg' if l['status_code']==200 else 'xr'}">{l['status_code']}</span></td>
      <td class="tm" style="font-size:.73rem">{hsize(l['bytes_served'] or 0)}</td>
      <td class="tm" style="font-size:.73rem">{str(l['visited_at'])[:16]}</td>
    </tr>""" for l in logs)
    pages = max(1, (tot + pp - 1) // pp)
    pager = "".join(f'<a href="/admin/logs?p={i}" class="btn {"bp" if i==pg else "bgh"} bsm">{i}</a>' for i in range(max(1, pg-3), min(pages+1, pg+4)))
    body = f"""<h2 style="color:#fff;margin-bottom:14px">📋 Kirish loglari</h2>
    <div class="card" style="padding:0"><div class="tw">
      <table><thead><tr><th>Rejim</th><th>IP</th><th>Yo'l</th><th>Status</th><th>Hajm</th><th>Vaqt</th></tr></thead>
      <tbody>{rows}</tbody></table></div></div>
    <div class="fl mt" style="gap:5px">{pager}</div>"""
    return _pg("Kirish loglari", body, "logs")


@app.route("/admin/blocked", methods=["GET", "POST"])
@admin_req
def admin_blocked():
    bls = db_exec("SELECT * FROM blocked_ips ORDER BY blocked_at DESC") or []
    rows = "".join(f"""<tr>
      <td><code>{b['ip_address']}</code></td><td>{b.get('reason','—')}</td>
      <td class="tm" style="font-size:.75rem">{str(b['blocked_at'])[:16]}</td>
      <td><form method="POST" action="/admin/blocked/del/{b['id']}">{csrf_field()}
        <button class="btn bg bsm">✓ Ochish</button></form></td>
    </tr>""" for b in bls)
    body = f"""
    <div class="fl mb"><h2 style="color:#fff">🚫 Bloklangan IP</h2>
      <form method="POST" action="/admin/blocked/add" style="margin-left:auto;display:flex;gap:7px">{csrf_field()}
        <input name="ip" placeholder="IP manzil" style="padding:6px 10px;background:var(--bg);border:1px solid var(--brd);border-radius:6px;color:var(--tx);font-size:.82rem;width:150px">
        <button class="btn br">+ Bloklash</button>
      </form>
    </div>
    <div class="card" style="padding:0"><div class="tw">
      <table><thead><tr><th>IP</th><th>Sabab</th><th>Bloklangan</th><th>Amal</th></tr></thead>
      <tbody>{rows or '<tr><td colspan=4 class="tm" style="text-align:center;padding:16px">Yo'+chr(39)+'q</td></tr>'}</tbody></table>
    </div></div>"""
    return _pg("Bloklangan IPlar", body, "blocked")


@app.route("/admin/blocked/add", methods=["POST"])
@admin_req
def admin_block_add():
    ip = request.form.get("ip", "").strip()
    reason = request.form.get("reason", "Admin tomonidan")
    if ip:
        db_exec("INSERT OR IGNORE INTO blocked_ips (ip_address,reason) VALUES (?,?)", (ip, reason), fetch=False)
    return redirect("/admin/blocked")


@app.route("/admin/blocked/del/<int:bid>", methods=["POST"])
@admin_req
def admin_unblock(bid):
    db_exec("DELETE FROM blocked_ips WHERE id=?", (bid,), fetch=False)
    return redirect("/admin/blocked")


@app.route("/admin/monitor")
@admin_req
def admin_monitor():
    body = f"""
    <h2 style="color:#fff;margin-bottom:14px">📟 Server Monitoring</h2>
    {'<div class="al al-er">psutil o'+chr(39)+'rnatilmagan: pip install psutil</div>' if not PSUTIL_OK else ''}
    <div class="mongrid">
      <div class="stat"><div class="v" id="m-cpu">—</div><div class="l">CPU %</div></div>
      <div class="stat"><div class="v" id="m-mem">—</div><div class="l">RAM</div></div>
      <div class="stat"><div class="v" id="m-disk">—</div><div class="l">Disk</div></div>
      <div class="stat"><div class="v" id="m-uptime">—</div><div class="l">Uptime</div></div>
    </div>
    <script>
    function poll(){{fetch('/api/monitor').then(r=>r.json()).then(d=>{{
      if(d.error) return;
      document.getElementById('m-cpu').textContent=d.cpu.toFixed(1)+'%';
      document.getElementById('m-mem').textContent=d.mem_used+'/'+d.mem_total+' GB';
      document.getElementById('m-disk').textContent=d.disk_used+'/'+d.disk_total+' GB';
      var m=d.uptime_min; document.getElementById('m-uptime').textContent=m<60?m.toFixed(0)+' min':Math.floor(m/60)+'h '+Math.round(m%60)+'m';
    }})}} poll(); setInterval(poll,3000);
    </script>"""
    return _pg("Monitoring", body, "monitor")


@app.route("/api/monitor")
@admin_req
def api_monitor():
    if not PSUTIL_OK:
        return jsonify({"error": "psutil o'rnatilmagan"})
    import psutil
    cpu = psutil.cpu_percent(interval=0.2)
    mem = psutil.virtual_memory()
    disk = psutil.disk_usage(os.getcwd())
    return jsonify({
        "cpu": cpu,
        "mem_percent": mem.percent,
        "mem_used": round(mem.used / 1073741824, 1),
        "mem_total": round(mem.total / 1073741824, 1),
        "disk_percent": disk.percent,
        "disk_used": round(disk.used / 1073741824, 1),
        "disk_total": round(disk.total / 1073741824, 1),
        "uptime_min": round((time.time() - PROCESS_START) / 60, 1)
    })



@app.route("/admin/audit")
@admin_req
def admin_audit():
    logs = db_exec("SELECT * FROM audit_log ORDER BY id DESC LIMIT 200") or []
    rows = "".join(f"""<tr>
      <td>{l.get('username') or '—'}</td>
      <td><span class="bx xb">{l['action']}</span></td>
      <td>{l.get('target_type') or '—'}</td>
      <td style="max-width:180px;overflow:hidden;text-overflow:ellipsis;font-size:.74rem">{(l.get('details') or '—')[:60]}</td>
      <td class="tm" style="font-size:.73rem">{str(l['created_at'])[:19]}</td>
    </tr>""" for l in logs)
    body = f"""<h2 style="color:#fff;margin-bottom:14px">📝 Audit Trail</h2>
    <div class="card" style="padding:0"><div class="tw">
      <table><thead><tr><th>User</th><th>Harakat</th><th>Turi</th><th>Tafsilot</th><th>Vaqt</th></tr></thead>
      <tbody>{rows or '<tr><td colspan=5 class="tm" style="text-align:center;padding:16px">Yozuv yo'+chr(39)+'q</td></tr>'}</tbody></table>
    </div></div>"""
    return _pg("Audit Trail", body, "audit")


@app.route("/admin/settings", methods=["GET", "POST"])
@admin_req
def admin_settings():
    suc = None
    if request.method == "POST":
        set_setting("tg_enabled", "1" if request.form.get("tg_enabled") else "0")
        set_setting("tg_token", request.form.get("tg_token", "").strip())
        set_setting("tg_chat", request.form.get("tg_chat", "").strip())
        set_setting("site_title", request.form.get("site_title", "SrvManager").strip() or "SrvManager")
        suc = "Sozlamalar saqlandi"
    tg_enabled = get_setting("tg_enabled", "0") == "1"
    tg_token = get_setting("tg_token", CFG["TELEGRAM_TOKEN"])
    tg_chat = get_setting("tg_chat", CFG["TELEGRAM_CHAT_ID"])
    site_title = get_setting("site_title", "SrvManager")
    body = f"""
    <h2 style="color:#fff;margin-bottom:14px">⚙️ Sozlamalar</h2>
    <div class="card"><h3>🔔 Telegram</h3>
      <form method="POST">{csrf_field()}
        <label style="display:flex;gap:8px;align-items:center;margin-bottom:12px">
          <input type="checkbox" name="tg_enabled" {'checked' if tg_enabled else ''} style="width:auto">
          Bildirishnomalarni yoqish
        </label>
        <div class="g g2">
          <div class="fld"><label>Bot Token</label><input name="tg_token" value="{tg_token}"></div>
          <div class="fld"><label>Chat ID</label><input name="tg_chat" value="{tg_chat}"></div>
        </div>
        <div class="fld"><label>Sayt nomi</label><input name="site_title" value="{site_title}"></div>
        <button class="btn bp">💾 Saqlash</button>
      </form>
    </div>
    <div class="card"><h3>💾 Backup</h3>
      <a href="/admin/backup/download" class="btn bg">⬇ Backup yuklab olish</a>
    </div>"""
    return _pg("Sozlamalar", body, "settings", flash=suc, ftype="ok")


@app.route("/admin/backup/download")
@admin_req
def admin_backup_download():
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"backup_{ts}.db"
    backup_path = Path(CFG["DB_FILE"]).parent / backup_name
    shutil.copy(CFG["DB_FILE"], backup_path)
    return send_file(str(backup_path), as_attachment=True, download_name=backup_name)


@app.route("/admin/bandwidth")
@admin_req
def admin_bandwidth():
    dy = db_exec("SELECT log_date,SUM(bytes_used) tot FROM bandwidth_log GROUP BY log_date ORDER BY log_date DESC LIMIT 30") or []
    dr = "".join(f"<tr><td>{r['log_date']}</td><td>{hsize(r['tot'] or 0)}</td></tr>" for r in dy)
    body = f"""<h2 style="color:#fff;margin-bottom:14px">📊 Bandwidth</h2>
    <div class="card"><div class="tw"><table><thead><tr><th>Kun</th><th>Trafik</th></tr></thead>
    <tbody>{dr or '<tr><td colspan=2 class="tm" style="text-align:center;padding:14px">Yo'+chr(39)+'q</td></tr>'}</tbody></table></div></div>"""
    return _pg("Bandwidth", body, "bw")


@app.route("/admin/backend/logs")
@admin_req
def backend_admin_logs():
    rows = db_exec("SELECT * FROM backend_exec_logs ORDER BY id DESC LIMIT 100") or []
    tr = "".join(f"""<tr>
      <td>{r['path']}</td><td>{r['duration_ms']} ms</td>
      <td><span class="bx {'xg' if r['ok'] else 'xr'}">{'OK' if r['ok'] else 'Xato'}</span></td>
      <td class="tm" style="font-size:.72rem">{str(r['created_at'])[:19]}</td>
    </tr>""" for r in rows)
    body = f"""<h2 style="color:#fff;margin-bottom:14px">🐍 Backend loglari</h2>
    <div class="card" style="padding:0"><div class="tw">
      <table><thead><tr><th>Yo'l</th><th>Vaqt</th><th>Holat</th><th>Sana</th></tr></thead>
      <tbody>{tr or '<tr><td colspan=4 class="tm" style="text-align:center;padding:16px">Chaqiruv yo'+chr(39)+'q</td></tr>'}</tbody></table>
    </div></div>"""
    return _pg("Backend loglari", body, "backend")
