"""Build data/sample.db: a tiny e-commerce SQLite database for the MCP tools."""

import os
import sqlite3
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                       "data", "sample.db")

PRODUCTS = [
    (1, "Trailhead Backpack", "Outdoors", 89.99, 4.7),
    (2, "Summit Tent 2P", "Outdoors", 249.00, 4.8),
    (3, "Ceramic Pour-Over Set", "Kitchen", 42.50, 4.5),
    (4, "Cast Iron Skillet", "Kitchen", 34.99, 4.9),
    (5, "Ergo Wireless Mouse", "Electronics", 59.00, 4.3),
    (6, "Mechanical Keyboard", "Electronics", 129.99, 4.6),
    (7, "Yoga Mat Pro", "Fitness", 68.00, 4.4),
    (8, "Adjustable Dumbbell", "Fitness", 199.99, 4.7),
]

ORDERS = [
    (101, 1, 2, "2026-07-02"),
    (102, 3, 1, "2026-07-05"),
    (103, 5, 1, "2026-07-11"),
    (104, 2, 1, "2026-07-19"),
    (105, 4, 3, "2026-08-01"),
    (106, 6, 1, "2026-08-09"),
    (107, 7, 2, "2026-08-14"),
    (108, 8, 1, "2026-08-22"),
    (109, 1, 1, "2026-09-03"),
    (110, 5, 2, "2026-09-10"),
]


def main() -> None:
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("""CREATE TABLE products (
        id INTEGER PRIMARY KEY, name TEXT NOT NULL, category TEXT NOT NULL,
        price REAL NOT NULL, rating REAL NOT NULL)""")
    cur.execute("""CREATE TABLE orders (
        order_id INTEGER PRIMARY KEY, product_id INTEGER NOT NULL,
        quantity INTEGER NOT NULL, order_date TEXT NOT NULL,
        FOREIGN KEY (product_id) REFERENCES products(id))""")
    cur.executemany("INSERT INTO products VALUES (?,?,?,?,?)", PRODUCTS)
    cur.executemany("INSERT INTO orders VALUES (?,?,?,?)", ORDERS)
    con.commit()
    n_prod = cur.execute("SELECT COUNT(*) FROM products").fetchone()[0]
    n_ord = cur.execute("SELECT COUNT(*) FROM orders").fetchone()[0]
    con.close()
    print(f"Built {DB_PATH}: {n_prod} products, {n_ord} orders")


if __name__ == "__main__":
    main()
