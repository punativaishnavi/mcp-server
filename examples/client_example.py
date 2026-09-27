"""Example MCP client: spawns server.py over stdio, lists tools, calls two of them."""

import asyncio
import json
import os
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

SERVER = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                      "server.py")


async def main() -> None:
    params = StdioServerParameters(command=sys.executable, args=[SERVER],
                                   env={**os.environ})
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            tools = await session.list_tools()
            print("Tools exposed by the server:")
            for t in tools.tools:
                print(f"  - {t.name}: {t.description}")

            print("\nResources:")
            for r in (await session.list_resources()).resources:
                print(f"  - {r.uri}: {r.name}")

            print("\nCalling calculate('237 * 41 + 19'):")
            res = await session.call_tool("calculate", {"expression": "237 * 41 + 19"})
            print("  ->", res.content[0].text)

            print("\nCalling query_database (revenue by category):")
            res = await session.call_tool("query_database", {
                "sql": ("SELECT p.category, ROUND(SUM(p.price * o.quantity), 2) AS revenue "
                        "FROM orders o JOIN products p ON p.id = o.product_id "
                        "GROUP BY p.category ORDER BY revenue DESC"),
                "limit": 10,
            })
            for block in res.content:  # one JSON object per content block
                print("  ->", json.loads(block.text))

            print("\nReading resource db://schema (first 200 chars):")
            result = await session.read_resource("db://schema")
            text = result.contents[0].text
            print("  ->", text[:200].replace("\n", " "), "...")


if __name__ == "__main__":
    asyncio.run(main())
