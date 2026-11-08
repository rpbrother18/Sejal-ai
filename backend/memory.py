import re
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "database" / "sejal.db"

BLOCKED = re.compile(
    r"(password|passwd|otp|pin\b|api[_ ]?key|secret|token|cvv|AIza|AQ\.)",
    re.I,
)


def _conn():
    DB_PATH.parent.mkdir(exist_ok=True)
    c = sqlite3.connect(DB_PATH)
    c.row_factory = sqlite3.Row
    c.execute(
        "CREATE TABLE IF NOT EXISTS memories ("
        "id INTEGER PRIMARY KEY AUTOINCREMENT, "
        "category TEXT NOT NULL, text TEXT NOT NULL, created TEXT NOT NULL)"
    )
    c.execute(
        "CREATE TABLE IF NOT EXISTS settings ("
        "key TEXT PRIMARY KEY, value TEXT NOT NULL)"
    )
    return c


def is_enabled():
    with _conn() as c:
        row = c.execute("SELECT value FROM settings WHERE key='enabled'").fetchone()
    return row is None or row["value"] == "1"


def set_enabled(flag):
    with _conn() as c:
        c.execute(
            "INSERT OR REPLACE INTO settings VALUES ('enabled', ?)",
            ("1" if flag else "0",),
        )
    return flag


def add(category, text):
    if not is_enabled():
        return {"ok": False, "error": "memory_disabled"}
    if BLOCKED.search(text):
        return {"ok": False, "error": "looks_like_secret"}
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    with _conn() as c:
        cur = c.execute(
            "INSERT INTO memories (category, text, created) VALUES (?,?,?)",
            (category, text, now),
        )
    return {"ok": True, "id": cur.lastrowid}


def list_all():
    with _conn() as c:
        rows = c.execute("SELECT * FROM memories ORDER BY id").fetchall()
    return [dict(r) for r in rows]


def update(mid, text):
    if BLOCKED.search(text):
        return {"ok": False, "error": "looks_like_secret"}
    with _conn() as c:
        cur = c.execute("UPDATE memories SET text=? WHERE id=?", (text, mid))
    return {"ok": cur.rowcount == 1}


def delete(mid):
    with _conn() as c:
        cur = c.execute("DELETE FROM memories WHERE id=?", (mid,))
    return {"ok": cur.rowcount == 1}
