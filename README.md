# mcp-server

A [Model Context Protocol (MCP)](https://modelcontextprotocol.io) server that
gives an LLM safe, useful tools: sandboxed file operations, a calculator, and
a SQL database interface — plus resources and a prompt template.

Connect it to Claude Desktop, any MCP-compatible client, or talk to it from
the included Python client example.

## Tools

| Tool | Description |
|------|-------------|
| `list_dir` | list files in the sandboxed workspace |
| `read_file` | read a text file from the workspace |
| `write_file` | write/create a text file in the workspace |
| `search_files` | grep for a pattern across workspace files |
| `calculate` | evaluate a math expression safely (no `eval` of arbitrary code) |
| `list_tables` | list tables in the sample SQLite database |
| `describe_table` | show a table's schema |
| `query_database` | run a read-only `SELECT` against the sample database |

## Resources

| URI | Description |
|-----|-------------|
| `db://schema` | full schema of the sample database as JSON |

## Prompts

| Prompt | Description |
|--------|-------------|
| `analyze_table` | starter prompt: "summarize table X — row count, columns, interesting distributions" |

## Quickstart

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Build the sample SQLite database
python3 scripts/build_sample_db.py

# Run the server (stdio transport — what MCP clients expect)
python3 server.py

# Run the tests
pytest -v
```

## Try it with the example client

`examples/client_example.py` spawns the server over stdio, lists its tools,
calls `calculate` and `query_database`, and prints the results:

```bash
python3 examples/client_example.py
```

Expected output (abridged):

```
Tools exposed by the server:
  - list_dir: List files and directories in the sandboxed workspace.
  - read_file: Read a text file from the sandboxed workspace.
  ...
calculate("237 * 41 + 19") -> 9736.0
query_database("SELECT category, COUNT(*) ...") -> [...]
```

## Connect to Claude Desktop

Add this to your Claude Desktop config
(`~/Library/Application Support/Claude/claude_desktop_config.json` on macOS,
`%APPDATA%\Claude\claude_desktop_config.json` on Windows):

```json
{
  "mcpServers": {
    "toolkit": {
      "command": "/absolute/path/to/mcp-server/.venv/bin/python",
      "args": ["/absolute/path/to/mcp-server/server.py"],
      "env": {
        "MCP_WORKSPACE": "/absolute/path/to/mcp-server/workspace"
      }
    }
  }
}
```

A ready-to-edit template is in `examples/claude_desktop_config.json`.
Restart Claude Desktop and the tools appear in the tool picker.

## Safety by design

- **Sandboxed filesystem** — file tools can only touch `MCP_WORKSPACE`
  (defaults to `./workspace`); path traversal (`..`) is rejected.
- **Read-only SQL** — only `SELECT`/`WITH` statements run; anything else
  is refused before it reaches SQLite.
- **Safe calculator** — expressions are parsed with `ast`, not `eval`;
  only arithmetic operators, whitelisted math functions, and numbers are allowed.
- **No secrets in tools** — the server never asks for or handles credentials.

## Project structure

```
mcp-server/
├── server.py                 # MCPServer: tools, resources, prompts
├── tools/
│   ├── filesystem.py         # sandboxed file tools (pure functions)
│   ├── calculator.py         # safe AST-based calculator
│   └── database.py           # read-only SQLite interface
├── scripts/build_sample_db.py# builds data/sample.db (tiny e-commerce data)
├── workspace/                # sandboxed files the tools can touch
├── examples/
│   ├── client_example.py     # stdio client demo
│   └── claude_desktop_config.json
└── tests/test_mcp.py
```

## Why MCP?

MCP is the open standard for connecting LLMs to data and tools — one
protocol instead of a bespoke integration per app. This server shows the
three MCP primitives: **tools** (actions the model can call), **resources**
(data the model can read), and **prompts** (reusable instruction templates).

## License

MIT — see [LICENSE](LICENSE).
