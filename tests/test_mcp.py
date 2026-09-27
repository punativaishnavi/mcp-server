"""Tests for the MCP server tool implementations (no running server needed)."""

import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

os.environ.setdefault("MCP_WORKSPACE", os.path.join(os.path.dirname(__file__), "sandbox"))

from tools import calculator, database, filesystem  # noqa: E402


# ---------- calculator ----------

def test_calculate_basic():
    assert calculator.calculate("2 + 3 * 4") == 14
    assert calculator.calculate("(2 + 3) * 4") == 20
    assert calculator.calculate("2**10") == 1024


def test_calculate_functions_and_consts():
    assert calculator.calculate("sqrt(16) + pi") == pytest.approx(4 + 3.14159265)
    assert calculator.calculate("round(2.675, 2)") == pytest.approx(2.67, abs=0.01)


def test_calculate_rejects_code_injection():
    with pytest.raises(ValueError):
        calculator.calculate("__import__('os').system('echo pwned')")
    with pytest.raises(ValueError):
        calculator.calculate("open('/etc/passwd').read()")
    with pytest.raises(ValueError):
        calculator.calculate("[x for x in range(3)]")


def test_calculate_rejects_garbage():
    with pytest.raises(ValueError):
        calculator.calculate("2 +")


# ---------- filesystem (sandboxed) ----------

def test_filesystem_write_read_roundtrip(tmp_path, monkeypatch):
    monkeypatch.setenv("MCP_WORKSPACE", str(tmp_path))
    import importlib
    importlib.reload(filesystem)
    assert filesystem.write_file("sub/note.txt", "hello mcp").startswith("Wrote")
    assert filesystem.read_file("sub/note.txt") == "hello mcp"
    assert "note.txt" in filesystem.list_dir("sub")


def test_filesystem_blocks_path_traversal(tmp_path, monkeypatch):
    monkeypatch.setenv("MCP_WORKSPACE", str(tmp_path))
    import importlib
    importlib.reload(filesystem)
    with pytest.raises(ValueError):
        filesystem.read_file("../outside.txt")
    with pytest.raises(ValueError):
        filesystem.write_file("../../evil.txt", "x")


def test_filesystem_search(tmp_path, monkeypatch):
    monkeypatch.setenv("MCP_WORKSPACE", str(tmp_path))
    import importlib
    importlib.reload(filesystem)
    filesystem.write_file("a.txt", "the quick brown fox\nsecond line")
    hits = filesystem.search_files("brown fox")
    assert len(hits) == 1 and hits[0]["file"] == "a.txt" and hits[0]["line_no"] == 1


# ---------- database (read-only) ----------

def _db_ok():
    return os.path.isfile(database.DB_PATH)


def test_list_tables():
    if not _db_ok():
        pytest.skip("sample.db not built yet")
    assert set(database.list_tables()) == {"products", "orders"}


def test_describe_table():
    if not _db_ok():
        pytest.skip("sample.db not built yet")
    cols = database.describe_table("products")
    assert [c["name"] for c in cols] == ["id", "name", "category", "price", "rating"]
    assert cols[0]["pk"] is True


def test_query_database_select():
    if not _db_ok():
        pytest.skip("sample.db not built yet")
    rows = database.query_database("SELECT COUNT(*) AS n FROM products")
    assert rows[0]["n"] == 8


def test_query_database_blocks_writes():
    with pytest.raises(ValueError):
        database.query_database("DROP TABLE products")
    with pytest.raises(ValueError):
        database.query_database("DELETE FROM orders")
    with pytest.raises(ValueError):
        database.query_database("INSERT INTO products VALUES (9,'x','y',1,5)")


def test_describe_table_rejects_injection():
    with pytest.raises(ValueError):
        database.describe_table("products; DROP TABLE orders --")
