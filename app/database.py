"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                          DATABASE — SQLite                                   ║
║  Barcha baza bilan ishlash funksiyalari shu yerda                           ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import sqlite3
from werkzeug.security import generate_password_hash

from app.config import CFG, _db_lock, _c, G, R


def get_conn():
    conn = sqlite3.connect(CFG["DB_FILE"], check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def db_exec(sql, args=None, fetch=True):
    with _db_lock:
        conn = get_conn()
        try:
            cur = conn.execute(sql, args or ())
            if fetch:
                rows = cur.fetchall()
                return [dict(r) for r in rows]
            conn.commit()
            return cur.lastrowid or True
        except Exception as e:
            print(_c(f"[SQL] {e}", R))
            return ([] if fetch else False)
        finally:
            conn.close()


def q1(sql, args=None):
    r = db_exec(sql, args)
    return r[0] if r else None


def _ensure_column(table, col, coldef):
    """Eski bazaga xavfsiz ustun qo'shadi."""
    cols = [r["name"] for r in db_exec(f"PRAGMA table_info({table})")]
    if col not in cols:
        db_exec(f"ALTER TABLE {table} ADD COLUMN {col} {coldef}", fetch=False)


def setup_db():
    """Barcha jadvallarni yaratish va boshlang'ich ma'lumotlarni kiritish."""
    stmts = [
        """CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT DEFAULT 'user',
            is_active INTEGER DEFAULT 1,
            bandwidth_limit_mb INTEGER DEFAULT 0,
            bandwidth_used_mb REAL DEFAULT 0,
            created_at TEXT DEFAULT (datetime('now')),
            last_login TEXT)""",

        """CREATE TABLE IF NOT EXISTS links (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            token TEXT UNIQUE NOT NULL,
            mode TEXT NOT NULL,
            label TEXT,
            target_path TEXT,
            password_hash TEXT,
            expires_at TEXT,
            is_active INTEGER DEFAULT 1,
            owner_id INTEGER,
            project_id INTEGER,
            visit_count INTEGER DEFAULT 0,
            created_at TEXT DEFAULT (datetime('now')))""",

        """CREATE TABLE IF NOT EXISTS access_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            link_token TEXT,
            mode TEXT,
            ip_address TEXT,
            user_agent TEXT,
            referer TEXT,
            bytes_served INTEGER DEFAULT 0,
            status_code INTEGER DEFAULT 200,
            path TEXT,
            visited_at TEXT DEFAULT (datetime('now')))""",

        """CREATE TABLE IF NOT EXISTS failed_logins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ip_address TEXT NOT NULL,
            username TEXT,
            attempt_at TEXT DEFAULT (datetime('now')))""",

        """CREATE TABLE IF NOT EXISTS blocked_ips (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ip_address TEXT UNIQUE NOT NULL,
            reason TEXT,
            blocked_at TEXT DEFAULT (datetime('now')),
            unblock_at TEXT)""",

        """CREATE TABLE IF NOT EXISTS files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            uuid TEXT UNIQUE NOT NULL,
            original_name TEXT NOT NULL,
            stored_name TEXT NOT NULL,
            file_type TEXT,
            file_size_bytes INTEGER DEFAULT 0,
            owner_id INTEGER,
            is_public INTEGER DEFAULT 0,
            download_count INTEGER DEFAULT 0,
            expires_at TEXT,
            created_at TEXT DEFAULT (datetime('now')))""",

        """CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            uuid TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            owner_id INTEGER,
            current_version INTEGER DEFAULT 1,
            is_public INTEGER DEFAULT 0,
            share_token TEXT,
            created_at TEXT DEFAULT (datetime('now')),
            updated_at TEXT DEFAULT (datetime('now')))""",

        """CREATE TABLE IF NOT EXISTS project_versions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            version INTEGER NOT NULL,
            html_code TEXT,
            css_code TEXT,
            js_code TEXT,
            notes TEXT,
            created_at TEXT DEFAULT (datetime('now')),
            UNIQUE(project_id, version))""",

        """CREATE TABLE IF NOT EXISTS mode_settings (
            mode TEXT PRIMARY KEY,
            is_enabled INTEGER DEFAULT 1)""",

        """CREATE TABLE IF NOT EXISTS bandwidth_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ip_address TEXT,
            bytes_used INTEGER DEFAULT 0,
            log_date TEXT DEFAULT (date('now')))""",

        """CREATE TABLE IF NOT EXISTS app_settings (
            key TEXT PRIMARY KEY,
            value TEXT)""",

        """CREATE TABLE IF NOT EXISTS project_files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            path TEXT NOT NULL,
            is_folder INTEGER DEFAULT 0,
            content TEXT,
            created_at TEXT DEFAULT (datetime('now')),
            updated_at TEXT DEFAULT (datetime('now')),
            UNIQUE(project_id, path))""",

        """CREATE TABLE IF NOT EXISTS project_file_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            path TEXT NOT NULL,
            content TEXT,
            saved_at TEXT DEFAULT (datetime('now')))""",

        """CREATE TABLE IF NOT EXISTS user_snippets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            lang TEXT NOT NULL,
            trigger_key TEXT NOT NULL,
            body TEXT NOT NULL,
            created_at TEXT DEFAULT (datetime('now')))""",

        """CREATE TABLE IF NOT EXISTS api_keys (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            name TEXT,
            key_prefix TEXT,
            key_hash TEXT NOT NULL,
            created_at TEXT DEFAULT (datetime('now')),
            last_used_at TEXT,
            revoked INTEGER DEFAULT 0)""",

        """CREATE TABLE IF NOT EXISTS two_fa_codes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            code TEXT NOT NULL,
            expires_at TEXT NOT NULL,
            used INTEGER DEFAULT 0,
            created_at TEXT DEFAULT (datetime('now')))""",

        """CREATE TABLE IF NOT EXISTS project_teams (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            role TEXT DEFAULT 'viewer',
            invited_by INTEGER,
            created_at TEXT DEFAULT (datetime('now')),
            UNIQUE(project_id, user_id))""",

        """CREATE TABLE IF NOT EXISTS audit_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            username TEXT,
            action TEXT NOT NULL,
            target_type TEXT,
            target_id TEXT,
            details TEXT,
            ip_address TEXT,
            created_at TEXT DEFAULT (datetime('now')))""",

        """CREATE TABLE IF NOT EXISTS chat_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            username TEXT,
            message TEXT NOT NULL,
            created_at TEXT DEFAULT (datetime('now')))""",

        """CREATE TABLE IF NOT EXISTS project_todos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            is_done INTEGER DEFAULT 0,
            priority TEXT DEFAULT 'normal',
            created_at TEXT DEFAULT (datetime('now')),
            completed_at TEXT)""",

        """CREATE TABLE IF NOT EXISTS ip_whitelist (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ip_address TEXT NOT NULL UNIQUE,
            label TEXT,
            added_by INTEGER,
            created_at TEXT DEFAULT (datetime('now')))""",

        """CREATE TABLE IF NOT EXISTS custom_domains (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            domain TEXT NOT NULL UNIQUE,
            is_active INTEGER DEFAULT 1,
            created_by INTEGER,
            created_at TEXT DEFAULT (datetime('now')))""",

        """CREATE TABLE IF NOT EXISTS uptime_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            status TEXT DEFAULT 'up',
            response_ms INTEGER,
            checked_at TEXT DEFAULT (datetime('now')))""",

        # Backend engine jadvallari
        """CREATE TABLE IF NOT EXISTS project_backend_routes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            path TEXT NOT NULL,
            method TEXT DEFAULT 'GET',
            code TEXT NOT NULL,
            is_enabled INTEGER DEFAULT 1,
            updated_at TEXT DEFAULT (datetime('now')),
            UNIQUE(project_id, path, method))""",

        """CREATE TABLE IF NOT EXISTS backend_exec_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER,
            user_id INTEGER,
            path TEXT,
            duration_ms INTEGER,
            ok INTEGER,
            error TEXT,
            created_at TEXT DEFAULT (datetime('now')))""",

        """CREATE TABLE IF NOT EXISTS backend_rate_limit (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            called_at TEXT DEFAULT (datetime('now')))""",
    ]

    for s in stmts:
        db_exec(s, fetch=False)

    # Rejimlar
    for mode in ("private", "lan", "global"):
        db_exec("INSERT OR IGNORE INTO mode_settings (mode,is_enabled) VALUES (?,1)",
                (mode,), fetch=False)

    # Yangi ustunlar
    _ensure_column("users", "tg_chat_id", "TEXT")
    _ensure_column("users", "require_2fa", "INTEGER DEFAULT 0")
    _ensure_column("projects", "backend_enabled", "INTEGER DEFAULT 0")

    # Admin foydalanuvchi
    if not q1("SELECT id FROM users WHERE role='admin' LIMIT 1"):
        ph = generate_password_hash(CFG["ADMIN_PASS"])
        db_exec("INSERT OR IGNORE INTO users (username,email,password_hash,role) VALUES (?,?,?,'admin')",
                (CFG["ADMIN_USER"], f"{CFG['ADMIN_USER']}@local.dev", ph), fetch=False)

    print(_c("  ✓ SQLite jadvallar tayyor", G))
