"""
API endpointlar — Chat, TODO, AI (stub), REST API
"""

import json
from datetime import datetime

from flask import request, session, redirect, abort, jsonify

from app.config import app, CFG
from app.database import db_exec, q1
from app.auth import user_req, write_req, api_key_req
from app.utils import get_ip, gtok, audit


# ╔══════════════════════════════════════════════════════════════════════════╗
# ║              REST API (Bearer token)                                      ║
# ╚══════════════════════════════════════════════════════════════════════════╝
@app.route("/api/v1/links", methods=["GET", "POST"])
@api_key_req
def api_links():
    uid = request.api_user_id
    if request.method == "GET":
        rows = db_exec("SELECT id,token,mode,label,is_active,visit_count,created_at FROM links WHERE owner_id=? ORDER BY created_at DESC", (uid,)) or []
        return jsonify({"links": rows})
    d = request.get_json(silent=True) or {}
    mode = d.get("mode", "private")
    if mode not in ("private", "lan", "global"):
        return jsonify({"error": "noto'g'ri mode"}), 400
    tok = gtok()
    db_exec("INSERT INTO links (token,mode,label,target_path,owner_id) VALUES (?,?,?,?,?)",
            (tok, mode, d.get("label", ""), d.get("target_path", ""), uid), fetch=False)
    return jsonify({"ok": True, "token": tok})


@app.route("/api/v1/files", methods=["GET"])
@api_key_req
def api_files():
    uid = request.api_user_id
    rows = db_exec("SELECT uuid,original_name,file_size_bytes,is_public,download_count,created_at FROM files WHERE owner_id=? ORDER BY created_at DESC", (uid,)) or []
    return jsonify({"files": rows})


@app.route("/api/v1/projects", methods=["GET"])
@api_key_req
def api_projects():
    uid = request.api_user_id
    rows = db_exec("SELECT uuid,name,current_version,is_public,updated_at FROM projects WHERE owner_id=? ORDER BY updated_at DESC", (uid,)) or []
    return jsonify({"projects": rows})


# ╔══════════════════════════════════════════════════════════════════════════╗
# ║              CHAT                                                          ║
# ╚══════════════════════════════════════════════════════════════════════════╝
@app.route("/api/chat/<puuid>/messages")
@user_req
def chat_messages(puuid):
    proj = q1("SELECT id FROM projects WHERE uuid=?", (puuid,))
    if not proj:
        return jsonify({"messages": []})
    msgs = db_exec("SELECT * FROM chat_messages WHERE project_id=? ORDER BY id DESC LIMIT 50", (proj["id"],)) or []
    msgs.reverse()
    return jsonify({"messages": [{"id": m["id"], "username": m["username"],
                                   "message": m["message"],
                                   "created_at": str(m["created_at"])[:19]} for m in msgs]})


@app.route("/api/chat/<puuid>/send", methods=["POST"])
@user_req
def chat_send(puuid):
    proj = q1("SELECT id FROM projects WHERE uuid=?", (puuid,))
    if not proj:
        return jsonify({"ok": False}), 404
    d = request.get_json() or {}
    msg = (d.get("message") or "").strip()[:500]
    if not msg:
        return jsonify({"ok": False})
    db_exec("INSERT INTO chat_messages (project_id,user_id,username,message) VALUES (?,?,?,?)",
            (proj["id"], session["user_id"], session.get("username", ""), msg), fetch=False)
    return jsonify({"ok": True})


# ╔══════════════════════════════════════════════════════════════════════════╗
# ║              TODO                                                          ║
# ╚══════════════════════════════════════════════════════════════════════════╝
@app.route("/api/todos/<puuid>", methods=["GET", "POST"])
@user_req
def api_todos(puuid):
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
        return jsonify({"ok": False})
    new_id = db_exec("INSERT INTO project_todos (project_id,user_id,title,priority) VALUES (?,?,?,?)",
                     (proj["id"], session["user_id"], title, priority), fetch=False)
    return jsonify({"ok": True, "id": new_id})


@app.route("/api/todos/<puuid>/<int:tid>", methods=["PUT", "DELETE"])
@user_req
def api_todo_item(puuid, tid):
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
# ║              AI YORDAMCHI (stub)                                           ║
# ╚══════════════════════════════════════════════════════════════════════════╝
@app.route("/api/ai/ask", methods=["POST"])
@user_req
def api_ai_ask():
    d = request.get_json() or {}
    question = (d.get("question") or "").strip()
    if not question:
        return jsonify({"answer": "Savol bo'sh"})
    # Oddiy javob
    username = session.get("username", "foydalanuvchi")
    return jsonify({"answer": f"Salom, {username}! Savolingiz qabul qilindi: '{question}'. AI moduli keyinroq kengaytiriladi."})


@app.route("/api/ai/history")
@user_req
def api_ai_history():
    return jsonify({"history": []})


@app.route("/api/ai/history/clear", methods=["POST"])
@user_req
def api_ai_history_clear():
    return jsonify({"ok": True})


@app.route("/api/ai/train", methods=["POST"])
@user_req
def api_ai_train():
    return jsonify({"ok": True})


@app.route("/api/ai/knowledge")
@user_req
def api_ai_knowledge():
    return jsonify({"items": [], "topics": [], "words": [], "badwords": []})


@app.route("/api/ai/knowledge/<int:kid>", methods=["DELETE"])
@user_req
def api_ai_knowledge_delete(kid):
    return jsonify({"ok": True})


# ╔══════════════════════════════════════════════════════════════════════════╗
# ║              KOMPONENTLAR, RANGLAR                                         ║
# ╚══════════════════════════════════════════════════════════════════════════╝
@app.route("/api/components")
@user_req
def api_components():
    components = [
        {"id": "nav-bootstrap", "name": "Navbar", "category": "Bootstrap",
         "code": '<nav class="navbar navbar-dark bg-dark"><div class="container"><a class="navbar-brand" href="#">Logo</a></div></nav>'},
        {"id": "card-bootstrap", "name": "Card", "category": "Bootstrap",
         "code": '<div class="card" style="width:18rem"><div class="card-body"><h5 class="card-title">Sarlavha</h5><p class="card-text">Matn.</p></div></div>'},
    ]
    return jsonify({"components": components})


@app.route("/api/color/palette")
@user_req
def color_palette():
    palettes = {
        "Material": ["#F44336", "#E91E63", "#9C27B0", "#3F51B5", "#2196F3", "#4CAF50", "#FFC107", "#FF5722"],
        "Dark": ["#0d0f18", "#161929", "#1c2136", "#252d45", "#7c6fff", "#22d3a0", "#f05d5d", "#f5c518"],
    }
    return jsonify({"palettes": palettes})



# ╔══════════════════════════════════════════════════════════════════════════╗
# ║              TERMINAL (faqat admin uchun)                                  ║
# ╚══════════════════════════════════════════════════════════════════════════╝
@app.route("/api/terminal/exec", methods=["POST"])
@user_req
def terminal_exec():
    """Admin uchun server terminalida buyruq bajarish."""
    import subprocess, os
    # Faqat admin
    if not session.get("admin"):
        return jsonify({"ok": False, "error": "Faqat admin ishlatishi mumkin"}), 403
    d = request.get_json() or {}
    cmd = (d.get("command") or "").strip()
    if not cmd:
        return jsonify({"ok": False, "error": "Buyruq bo'sh"})
    # Xavfli buyruqlarni bloklash
    dangerous = ["rm -rf /", "mkfs", "dd if=", ":(){", "fork bomb", "shutdown", "reboot", "halt",
                 "format c:", "del /f /s /q"]
    for dng in dangerous:
        if dng in cmd.lower():
            return jsonify({"ok": False, "error": "Bu buyruq taqiqlangan"})
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10, cwd=os.getcwd())
        output = result.stdout + result.stderr
        audit("terminal_exec", "command", None, cmd[:200])
        return jsonify({"ok": True, "output": output[:5000], "returncode": result.returncode})
    except subprocess.TimeoutExpired:
        return jsonify({"ok": False, "error": "Buyruq 10 sekundda yakunlanmadi (timeout)"})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)[:300]})
