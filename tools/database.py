"""Read-only SQLite interface for the sample database.

Only SELECT / WITH statements are executed; anything else is refused
before it reaches the database.
"""

import os
import re
import sqlite3

DB_PATH = os.environ.get("MCP_DB_PATH",
                         os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                      "data", "sample.db"))

_READ_ONLY = re.compile(r"^\s*(select|with)\b", re.IGNORECASE | re.DOTALL)
_FORBIDDEN = re.compile(r"\b(insert|update|delete|drop|alter|create|replace|attach|pragma)\b",
                        re.IGNORECASE)


def _connect() -> sqlite3.Connection:
    if not os.path.isfile(DB_PATH):
        raise ValueError(f"Database not found at {DB_PATH}. Run scripts/build_sample_db.py first.")
    con = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
    con.row_factory = sqlite3.Row
    return con


def _guard(sql: str) -> None:
    if not _READ_ONLY.match(sql):
        raise ValueError("Only SELECT / WITH queries are allowed.")
    if _FORBIDDEN.search(sql):
        raise ValueError("Query contains a forbidden keyword; read-only access only.")


def list_tables() -> list[str]:
    """List all tables in the sample database."""
    with _connect() as con:
        rows = con.execute(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name").fetchall()
    return [r["name"] for r in rows]


def describe_table(table: str) -> list[dict]:
    """Show a table's columns (name, type, nullable, primary key)."""
    if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", table):
        raise ValueError(f"Invalid table name: {table!r}")
    with _connect() as con:
        rows = con.execute(f"PRAGMA table_info({table})").fetchall()
    if not rows:
        raise ValueError(f"Table not found: {table!r}")
    return [{"name": r["name"], "type": r["type"],
             "nullable": not r["notnull"], "pk": bool(r["pk"])} for r in rows]


def query_database(sql: str, limit: int = 50) -> list[dict]:
    """Run a read-only SELECT query; returns rows as dicts (capped at `limit`)."""
    _guard(sql)
    limit = max(1, min(int(limit), 200))
    with _connect() as con:
        rows = con.execute(sql).fetchmany(limit)
    return [dict(r) for r in rows]
