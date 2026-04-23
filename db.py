import sqlite3
import json
import csv
import io
import os
from contextlib import contextmanager
from pathlib import Path

# On Render the persistent disk mounts at /data; fall back to local dir
_db_dir = Path(os.environ.get("DB_DIR", Path(__file__).parent))
DB_PATH = _db_dir / "submissions.db"


@contextmanager
def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db():
    with get_conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS submissions (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                email       TEXT NOT NULL,
                form_data   TEXT NOT NULL DEFAULT '{}',
                form_version TEXT NOT NULL DEFAULT 'unknown',
                is_test     INTEGER NOT NULL DEFAULT 0,
                timestamp   TEXT NOT NULL,
                ip_address  TEXT,
                user_agent  TEXT,
                referrer    TEXT
            )
        """)


def insert_submission(
    email: str,
    form_data: dict,
    form_version: str,
    is_test: bool,
    timestamp: str,
    ip_address: str | None,
    user_agent: str | None,
    referrer: str | None,
) -> int:
    with get_conn() as conn:
        cur = conn.execute(
            """
            INSERT INTO submissions
                (email, form_data, form_version, is_test, timestamp, ip_address, user_agent, referrer)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                email,
                json.dumps(form_data),
                form_version,
                1 if is_test else 0,
                timestamp,
                ip_address,
                user_agent,
                referrer,
            ),
        )
        return cur.lastrowid


def export_leads_csv(include_test: bool = False) -> str:
    with get_conn() as conn:
        query = "SELECT * FROM submissions"
        if not include_test:
            query += " WHERE is_test = 0"
        query += " ORDER BY timestamp ASC"
        rows = conn.execute(query).fetchall()

    if not rows:
        return "id,email,form_version,is_test,timestamp,ip_address,user_agent,referrer,form_data\n"

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["id", "email", "form_version", "is_test", "timestamp", "ip_address", "user_agent", "referrer", "form_data"])
    for row in rows:
        writer.writerow([
            row["id"], row["email"], row["form_version"], row["is_test"],
            row["timestamp"], row["ip_address"], row["user_agent"],
            row["referrer"], row["form_data"],
        ])
    return output.getvalue()
