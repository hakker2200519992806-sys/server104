"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                          HTML / CSS SHABLONLAR                               ║
║  Barcha sahifa shablonlari va CSS shu yerda                                 ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from flask import session

from app.auth import get_csrf_token
from app.utils import get_setting

# ── Asosiy CSS ─────────────────────────────────────────────────────────────
CSS = """
:root{--bg:#0d0f18;--surf:#161929;--card:#1c2136;--brd:#252d45;
  --ac:#7c6fff;--ac2:#5548e0;--gr:#22d3a0;--rd:#f05d5d;
  --yl:#f5c518;--tx:#d4daf0;--mt:#5c6890;--r:10px}
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:'Segoe UI',system-ui,sans-serif;background:var(--bg);color:var(--tx);min-height:100vh;font-size:14px}
a{color:var(--ac);text-decoration:none} a:hover{color:#a89fff}
.layout{display:flex;min-height:100vh}
.sb{width:220px;background:var(--surf);border-right:1px solid var(--brd);
  flex-shrink:0;position:sticky;top:0;height:100vh;overflow-y:auto;display:flex;flex-direction:column}
.sb .logo{padding:18px;font-size:1.05rem;font-weight:700;color:#fff;
  border-bottom:1px solid var(--brd)}
.sb .logo span{color:var(--ac)}
.sb nav a{display:flex;align-items:center;gap:9px;padding:9px 18px;
  color:var(--mt);font-size:.85rem;transition:.15s;border-left:3px solid transparent}
.sb nav a:hover,.sb nav a.act{color:var(--tx);background:rgba(124,111,255,.08);border-left-color:var(--ac)}
.sb nav .sep{padding:12px 18px 4px;font-size:.68rem;letter-spacing:.1em;color:var(--mt);text-transform:uppercase}
.main{flex:1;display:flex;flex-direction:column;overflow-x:hidden}
.top{background:var(--surf);border-bottom:1px solid var(--brd);
  padding:11px 24px;display:flex;align-items:center;justify-content:space-between;gap:12px}
.top h1{font-size:.95rem;font-weight:600;color:#fff;white-space:nowrap}
.srch input{width:100%;padding:7px 14px;background:var(--bg);border:1px solid var(--brd);
  border-radius:20px;color:var(--tx);font-size:.8rem;outline:none;transition:.15s}
.srch input:focus{border-color:var(--ac)}
.cnt{padding:22px;flex:1}
.card{background:var(--card);border:1px solid var(--brd);border-radius:var(--r);padding:18px;margin-bottom:14px}
.card h3{font-size:.87rem;color:#fff;margin-bottom:12px;font-weight:600}
.g{display:grid;gap:14px} .g2{grid-template-columns:1fr 1fr}
.g3{grid-template-columns:1fr 1fr 1fr} .g4{grid-template-columns:repeat(4,1fr)}
.stat{background:var(--card);border:1px solid var(--brd);border-radius:var(--r);padding:16px;text-align:center}
.stat .v{font-size:1.7rem;font-weight:800;color:var(--ac)} .stat .l{font-size:.73rem;color:var(--mt);margin-top:3px}
.btn{display:inline-flex;align-items:center;gap:5px;padding:7px 14px;border-radius:7px;
  font-size:.8rem;font-weight:600;cursor:pointer;border:none;transition:.15s;white-space:nowrap}
.bp{background:var(--ac);color:#fff} .bp:hover{background:var(--ac2);color:#fff}
.bg{background:#0d6b51;color:var(--gr)} .bg:hover{background:#0a8464;color:#fff}
.br{background:#5c1a1a;color:var(--rd)} .br:hover{background:#7a1e1e;color:#fff}
.bgh{background:transparent;border:1px solid var(--brd);color:var(--mt)}
.bgh:hover{border-color:var(--ac);color:var(--ac)}
.bsm{padding:5px 10px;font-size:.76rem}
.fld{margin-bottom:12px}
.fld label{display:block;margin-bottom:4px;color:var(--mt);font-size:.78rem;font-weight:600}
.fld input,.fld select,.fld textarea{width:100%;padding:8px 11px;background:var(--bg);
  border:1px solid var(--brd);border-radius:7px;color:var(--tx);font-size:.85rem;outline:none;transition:.15s}
.fld input:focus,.fld select:focus,.fld textarea:focus{border-color:var(--ac)}
.fld textarea{min-height:90px;resize:vertical}
.row{display:flex;gap:10px;align-items:flex-end;flex-wrap:wrap}
.tw{overflow-x:auto;border-radius:var(--r);border:1px solid var(--brd)}
table{width:100%;border-collapse:collapse}
th,td{padding:10px 13px;text-align:left;font-size:.8rem;border-bottom:1px solid var(--brd)}
th{color:var(--mt);font-weight:600;background:rgba(255,255,255,.02)} td{color:var(--tx)}
tr:last-child td{border-bottom:none} tr:hover td{background:rgba(124,111,255,.04)}
.bx{display:inline-flex;align-items:center;gap:4px;padding:2px 8px;border-radius:20px;font-size:.7rem;font-weight:600}
.xg{background:#0a3d2e;color:var(--gr)} .xr{background:#3b1010;color:var(--rd)}
.xy{background:#3b2e05;color:var(--yl)} .xb{background:#0d1f40;color:#60a5fa}
.xp{background:#1e1040;color:#c4b5fd} .xm{background:#1a1f30;color:var(--mt)}
.al{padding:11px 15px;border-radius:var(--r);margin-bottom:14px;font-size:.83rem}
.al-ok{background:#0a3d2e;color:var(--gr);border:1px solid #0d5a40}
.al-er{background:#3b1010;color:var(--rd);border:1px solid #5c1a1a}
.fl{display:flex;align-items:center;gap:9px;flex-wrap:wrap}
.mla{margin-left:auto} .mt{margin-top:14px} .mb{margin-bottom:14px}
.tm{color:var(--mt)} .tg{color:var(--gr)} .tr{color:var(--rd)}
.cpb{background:transparent;border:1px solid var(--brd);color:var(--mt);
  border-radius:5px;padding:2px 7px;font-size:.7rem;cursor:pointer;transition:.15s}
.cpb:hover{border-color:var(--ac);color:var(--ac)}
.mcard{border:2px solid var(--brd);border-radius:12px;padding:18px;transition:.2s}
.mcard.on{border-color:var(--gr);background:rgba(34,211,160,.03)}
.urlbox{background:var(--bg);border:1px solid var(--brd);border-radius:6px;
  padding:7px 11px;font-family:monospace;font-size:.75rem;color:var(--ac);
  margin-top:10px;word-break:break-all}
.mongrid{display:grid;grid-template-columns:repeat(4,1fr);gap:14px}
.monbar{background:var(--bg);border-radius:6px;height:9px;overflow:hidden;margin-top:8px}
.monfill{height:100%;border-radius:6px;transition:width .4s}
@media(max-width:768px){.layout{flex-direction:column}.sb{width:100%;height:auto;position:static}
  .g2,.g3,.g4,.mongrid{grid-template-columns:1fr} .srch{display:none}}
"""


def _nav(href, label, active):
    return f'<a href="{href}" class="{"act" if active else ""}">{label}</a>'


def _pg(title, body, act="dash", flash=None, ftype="ok"):
    """Asosiy sahifa shabloni (sidebar + top bar + content)."""
    adm = session.get("admin", False)
    uname = session.get("username", "")
    role = session.get("role", "user")
    site_title = get_setting("site_title", "SrvManager")
    fl = f'<div class="al al-{ftype}">{flash}</div>' if flash else ""
    adm_nav = ""
    if adm:
        adm_nav = f"""
        <div class="sep">Admin</div>
        {_nav('/admin/users','👥 Foydalanuvchilar','users'==act)}
        {_nav('/admin/logs','📋 Kirish loglari','logs'==act)}
        {_nav('/admin/blocked','🚫 Bloklangan IP','blocked'==act)}
        {_nav('/admin/bandwidth','📊 Bandwidth','bw'==act)}
        {_nav('/admin/monitor','📟 Monitoring','monitor'==act)}
        {_nav('/admin/uptime','📉 Uptime','uptime'==act)}
        {_nav('/admin/backend/logs','🐍 Backend','backend'==act)}
        {_nav('/admin/audit','📝 Audit','audit'==act)}
        {_nav('/admin/ip-whitelist','🔒 IP Whitelist','ipwl'==act)}
        {_nav('/admin/domains','🌐 Domenlar','domains'==act)}
        {_nav('/admin/settings','⚙️ Sozlamalar','settings'==act)}"""
    rb = f'<span class="bx {"xg" if adm else "xb"}">{role}</span>'
    csrf = get_csrf_token()
    return f"""<!DOCTYPE html>
<html lang="uz"><head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title} — {site_title}</title>
<style>{CSS}</style>
</head><body>
<div class="layout">
<aside class="sb">
  <div class="logo">⬡ <span>{site_title}</span></div>
  <nav>
    {_nav('/dashboard','🏠 Dashboard','dash'==act)}
    <div class="sep">Rejimlar</div>
    {_nav('/modes','🔀 Rejimlar','modes'==act)}
    {_nav('/links','🔗 Havolalar','links'==act)}
    <div class="sep">Kontent</div>
    {_nav('/files','📁 Fayllar','files'==act)}
    {_nav('/projects','💻 Loyihalar','projects'==act)}
    {_nav('/editor/new','✏️ Muharrir','editor'==act)}
    <div class="sep">Hisobot</div>
    {_nav('/stats','📈 Statistika','stats'==act)}
    {adm_nav}
    <div class="sep">Hisob</div>
    {_nav('/profile',f'👤 {{uname}}','profile'==act)}
    {_nav('/logout','🚪 Chiqish',False)}
  </nav>
</aside>
<div class="main">
  <div class="top"><h1>{title}</h1>
    <form method="GET" action="/search" class="srch" style="flex:1;max-width:320px">
      <input name="q" placeholder="🔍 Havola, fayl, loyiha qidirish...">
    </form>
    <div class="fl">{rb}<span class="tm" style="font-size:.78rem">{uname}</span>
    <span class="bx xm" style="font-size:.65rem">SQLite</span></div>
  </div>
  <div class="cnt">{fl}{body}</div>
</div>
</div>
<script>
function copyText(t){{navigator.clipboard.writeText(t).then(()=>{{
  const e=event.target;const o=e.textContent;e.textContent='✓ Nusxalandi!';
  setTimeout(()=>e.textContent=o,1500);}});}}
</script>
</body></html>"""


def _auth_pg(title, body, flash=None, ftype="er"):
    """Login/register sahifasi shabloni."""
    fl = f'<div class="al al-{ftype}">{flash}</div>' if flash else ""
    return f"""<!DOCTYPE html>
<html lang="uz"><head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title} — SrvManager</title>
<style>{CSS}
.aw{{display:flex;align-items:center;justify-content:center;min-height:100vh;padding:20px}}
.ab{{background:var(--card);border:1px solid var(--brd);border-radius:14px;
  padding:32px;width:100%;max-width:360px}}
</style></head><body>
<div class="aw"><div class="ab">
  <p style="text-align:center;font-size:2rem;margin-bottom:8px">⬡</p>
  <h2 style="text-align:center;color:#fff;margin-bottom:3px;font-size:1.1rem">SrvManager</h2>
  <p style="text-align:center;color:var(--mt);font-size:.8rem;margin-bottom:20px">{title}</p>
  {fl}{body}
</div></div></body></html>"""
