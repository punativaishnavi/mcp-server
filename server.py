"""MCP server: tools, resources, and prompts for an LLM.

Run over stdio (what MCP clients expect):
    python server.py
"""

import json
import logging
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from mcp.server.mcpserver import MCPServer  # noqa: E402

from tools import calculator, database, filesystem  # noqa: E402

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s")
log = logging.getLogger("mcp-server")

mcp = MCPServer("toolkit")


# ---------- filesystem tools (sandboxed) ----------

@mcp.tool()
def list_dir(path: str = ".") -> list[str]:
    """List files and directories in the sandboxed workspace."""
    return filesystem.list_dir(path)


@mcp.tool()
def read_file(path: str) -> str:
    """Read a text file from the sandboxed workspace."""
    return filesystem.read_file(path)


@mcp.tool()
def write_file(path: str, content: str) -> str:
    """Write (or overwrite) a text file in the sandboxed workspace."""
    return filesystem.write_file(path, content)


@mcp.tool()
def search_files(pattern: str, path: str = ".") -> list[dict]:
    """Search workspace files for a regex pattern. Returns file/line matches."""
    return filesystem.search_files(pattern, path)


# ---------- calculator ----------

@mcp.tool()
def calculate(expression: str) -> float:
    """Safely evaluate a math expression, e.g. 'sqrt(16) + 2**10'."""
    return calculator.calculate(expression)


# ---------- database tools (read-only) ----------

@mcp.tool()
def list_tables() -> list[str]:
    """List all tables in the sample SQLite database."""
    return database.list_tables()


@mcp.tool()
def describe_table(table: str) -> list[dict]:
    """Show a table's schema: column names, types, nullability, primary key."""
    return database.describe_table(table)


@mcp.tool()
def query_database(sql: str, limit: int = 50) -> list[dict]:
    """Run a read-only SELECT query against the sample database."""
    return database.query_database(sql, limit)


# ---------- resources ----------

@mcp.resource("db://schema")
def db_schema() -> str:
    """Full schema of the sample database as JSON."""
    schema = {t: database.describe_table(t) for t in database.list_tables()}
    return json.dumps(schema, indent=2)


# ---------- prompts ----------

@mcp.prompt()
def analyze_table(table: str) -> str:
    """Starter prompt for exploring a database table."""
    return (
        f"Analyze the '{table}' table in the sample database.\n"
        f"1. Call describe_table('{table}') to see its schema.\n"
        f"2. Query row counts and a 5-row sample.\n"
        f"3. Summarize: what the table stores, key columns, and one "
        f"interesting distribution (e.g. counts by category)."
    )


if __name__ == "__main__":
    log.info("Starting MCP server 'toolkit' over stdio")
    log.info("Workspace: %s", filesystem.WORKSPACE_DIR)
    log.info("Database:  %s", database.DB_PATH)
    mcp.run()
