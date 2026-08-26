"""
Dashboard va Statistika sahifalari
"""

import json

from flask import request

from app.config import app
from app.database import db_exec, q1
from app.auth import user_req
from app.utils import hsize
from app.templates import _pg


@app.route("/")
@app.route("/dashboard")
@user_req
def dashboard():
    def cnt(t):
        return (q1(f"SELECT COUNT(*) c FROM {t}") or {}).get("c", 0)

    s = {
        "links": cnt("links WHERE is_active=1"),
        "files": cnt("files"),
        "projs": cnt("projects"),
        "visits": cnt("access_logs WHERE date(visited_at)=date('now')")
    }
    logs = db_exec("SELECT mode,ip_address,path,status_code,visited_at "
                   "FROM access_logs ORDER BY visited_at DESC LIMIT 10") or []
    lr = "".join(f"""<tr>
      <td><span class="bx xp">{l['mode']}</span></td>
      <td><code style="font-size:.75rem">{l['ip_address']}</code></td>
      <td style="max-width:180px;overflow:hidden;text-overflow:ellipsis;font-size:.77rem">{l['path']}</td>
      <td><span class="bx {'xg' if l['status_code']==200 else 'xr'}">{l['status_code']}</span></td>
      <td class="tm" style="font-size:.75rem">{str(l['visited_at'])[:16]}</td>
    </tr>""" for l in logs)

    from app.utils import mode_on
    modes_html = ""
    for mode, icon, desc in [("private", "🔒", "Maxsus token havolasi"),
                              ("lan", "📡", "WiFi tarmog'i"),
                              ("global", "🌍", "Internet / ngrok")]:
        on = mode_on(mode)
        modes_html += f"""
        <div class="card" style="border-left:3px solid {'var(--gr)' if on else 'var(--rd)'}">
          <div class="fl"><span style="font-size:1.3rem">{icon}</span>
            <b style="color:#fff">{mode.upper()}</b>
            <span class="bx {'xg' if on else 'xr'} mla">{'Faol' if on else "O'chiq"}</span></div>
          <p class="tm mt" style="font-size:.78rem">{desc}</p>
        </div>"""

    body = f"""
    <div class="g g4 mb" style="margin-bottom:18px">
      <div class="stat"><div class="v">{s['links']}</div><div class="l">Havolalar</div></div>
      <div class="stat"><div class="v">{s['files']}</div><div class="l">Fayllar</div></div>
      <div class="stat"><div class="v">{s['projs']}</div><div class="l">Loyihalar</div></div>
      <div class="stat"><div class="v">{s['visits']}</div><div class="l">Bugungi tashriflar</div></div>
    </div>
    <div class="g g3 mb">{modes_html}</div>
    <div class="card"><h3>So'nggi tashriflar</h3>
      <div class="tw"><table><thead><tr>
        <th>Rejim</th><th>IP</th><th>Yo'l</th><th>Status</th><th>Vaqt</th>
      </tr></thead><tbody>{lr or '<tr><td colspan=5 style="text-align:center;color:var(--mt);padding:16px">Hali tashrif yo'+chr(39)+'q</td></tr>'}</tbody></table></div>
    </div>"""
    return _pg("Dashboard", body, "dash")


@app.route("/stats")
@user_req
def stats():
    def cnt(q, a=None):
        return (q1(q, a) or {}).get("c", 0)

    tv = cnt("SELECT COUNT(*) c FROM access_logs")
    td = cnt("SELECT COUNT(*) c FROM access_logs WHERE date(visited_at)=date('now')")
    tw = cnt("SELECT COUNT(*) c FROM access_logs WHERE visited_at>datetime('now','-7 days')")
    bm = db_exec("SELECT mode,COUNT(*) cnt FROM access_logs GROUP BY mode ORDER BY cnt DESC") or []
    dy = db_exec("SELECT date(visited_at) d,COUNT(*) cnt FROM access_logs "
                 "WHERE visited_at>datetime('now','-14 days') GROUP BY date(visited_at) ORDER BY d") or []
    bw = db_exec("SELECT log_date,SUM(bytes_used)/1048576.0 mb FROM bandwidth_log "
                 "GROUP BY log_date ORDER BY log_date DESC LIMIT 14") or []
    tp = db_exec("SELECT ip_address,COUNT(*) cnt FROM access_logs "
                 "GROUP BY ip_address ORDER BY cnt DESC LIMIT 10") or []

    mr = "".join(f"""<tr><td><span class="bx xp">{r['mode']}</span></td><td><b>{r['cnt']}</b></td>
      <td><div style="background:var(--brd);border-radius:4px;height:7px;overflow:hidden">
        <div style="background:var(--ac);height:100%;width:{min(100,int(r['cnt']/(tv or 1)*100))}%"></div>
      </div></td></tr>""" for r in bm)
    ir = "".join(f"<tr><td><code>{r['ip_address']}</code></td><td>{r['cnt']}</td></tr>" for r in tp)
    dl = json.dumps([str(d["d"]) for d in dy])
    dd = json.dumps([int(d["cnt"]) for d in dy])
    bl = json.dumps([str(b["log_date"]) for b in bw])
    bd = json.dumps([round(float(b["mb"] or 0), 2) for b in bw])

    body = f"""
    <h2 style="color:#fff;margin-bottom:14px">📈 Statistika</h2>
    <div class="g g4 mb">
      <div class="stat"><div class="v">{tv}</div><div class="l">Jami tashriflar</div></div>
      <div class="stat"><div class="v">{td}</div><div class="l">Bugungi</div></div>
      <div class="stat"><div class="v">{tw}</div><div class="l">7 kunlik</div></div>
      <div class="stat"><div class="v">{len(bm)}</div><div class="l">Rejimlar</div></div>
    </div>
    <div class="g g2">
      <div class="card"><h3>Kunlik tashriflar (14 kun)</h3><canvas id="cd" height="200"></canvas></div>
      <div class="card"><h3>Bandwidth MB (14 kun)</h3><canvas id="cb" height="200"></canvas></div>
    </div>
    <div class="g g3 mt">
      <div class="card"><h3>Rejimlar bo'yicha</h3>
        <div class="tw"><table><thead><tr><th>Rejim</th><th>Soni</th><th>Ulush</th></tr></thead>
        <tbody>{mr}</tbody></table></div></div>
      <div class="card"><h3>Top IP manzillar</h3>
        <div class="tw"><table><thead><tr><th>IP</th><th>Soni</th></tr></thead>
        <tbody>{ir}</tbody></table></div></div>
    </div>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    <script>
    const cd={{borderColor:'#7c6fff',backgroundColor:'rgba(124,111,255,.15)',fill:true,tension:.35,pointRadius:3}};
    new Chart(document.getElementById('cd'),{{type:'line',
      data:{{labels:{dl},datasets:[{{...cd,label:'Tashriflar',data:{dd}}}]}},
      options:{{plugins:{{legend:{{display:false}}}},scales:{{
        x:{{ticks:{{color:'#5c6890'}},grid:{{color:'#252d45'}}}},
        y:{{ticks:{{color:'#5c6890'}},grid:{{color:'#252d45'}},beginAtZero:true}}}}}}
    }});
    new Chart(document.getElementById('cb'),{{type:'bar',
      data:{{labels:{bl},datasets:[{{...cd,label:'MB',type:'bar',backgroundColor:'rgba(34,211,160,.2)',borderColor:'#22d3a0',data:{bd}}}]}},
      options:{{plugins:{{legend:{{display:false}}}},scales:{{
        x:{{ticks:{{color:'#5c6890'}},grid:{{color:'#252d45'}}}},
        y:{{ticks:{{color:'#5c6890'}},grid:{{color:'#252d45'}},beginAtZero:true}}}}}}
    }});
    </script>"""
    return _pg("Statistika", body, "stats")


@app.route("/search")
@user_req
def search():
    q = request.args.get("q", "").strip()
    uid = session.get("user_id")
    adm = session.get("admin") or session.get("_guest")
    links = files = projs = []
    if q:
        like = f"%{q}%"
        if adm:
            links = db_exec("SELECT * FROM links WHERE label LIKE ? OR token LIKE ? ORDER BY created_at DESC LIMIT 25",
                            (like, like)) or []
            files = db_exec("SELECT * FROM files WHERE original_name LIKE ? ORDER BY created_at DESC LIMIT 25",
                            (like,)) or []
            projs = db_exec("SELECT * FROM projects WHERE name LIKE ? ORDER BY updated_at DESC LIMIT 25",
                            (like,)) or []
        else:
            links = db_exec("SELECT * FROM links WHERE owner_id=? AND (label LIKE ? OR token LIKE ?) LIMIT 25",
                            (uid, like, like)) or []
            files = db_exec("SELECT * FROM files WHERE owner_id=? AND original_name LIKE ? LIMIT 25",
                            (uid, like)) or []
            projs = db_exec("SELECT * FROM projects WHERE owner_id=? AND name LIKE ? LIMIT 25",
                            (uid, like)) or []

    lr = "".join(f"""<tr><td><span class="bx xp">{l['mode']}</span></td>
        <td>{l.get('label') or '—'}</td><td><code style="font-size:.72rem">{l['token'][:16]}...</code></td>
        <td><a href="/links/edit/{l['id']}" class="btn bgh bsm">Ochish</a></td></tr>""" for l in links)
    fr = "".join(f"""<tr><td>{f['original_name']}</td><td>{hsize(f.get('file_size_bytes',0))}</td>
        <td><a href="/download/{f['uuid']}" class="btn bg bsm">⬇</a></td></tr>""" for f in files)
    pr = "".join(f"""<tr><td>{p['name']}</td><td>v{p['current_version']}</td>
        <td><a href="/editor/{p['uuid']}" class="btn bp bsm">Tahrirlash</a></td></tr>""" for p in projs)

    body = f"""
    <h2 style="color:#fff;margin-bottom:14px">🔍 Qidiruv: "{q}"</h2>
    <div class="g g2">
      <div class="card"><h3>🔗 Havolalar</h3><div class="tw"><table><tbody>{lr or '<tr><td>Topilmadi</td></tr>'}</tbody></table></div></div>
      <div class="card"><h3>📁 Fayllar</h3><div class="tw"><table><tbody>{fr or '<tr><td>Topilmadi</td></tr>'}</tbody></table></div></div>
      <div class="card"><h3>💻 Loyihalar</h3><div class="tw"><table><tbody>{pr or '<tr><td>Topilmadi</td></tr>'}</tbody></table></div></div>
    </div>""" if q else '<div class="card"><p class="tm">Qidirish uchun so\'z kiriting.</p></div>'
    return _pg("Qidiruv", body, "search")
