from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any


class ChefOrderFlowRepository:
    def __init__(self, db_path: str = "output/chef_delivery_asaas.db") -> None:
        self.db_path = db_path
        self._ensure_schema()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _ensure_schema(self) -> None:
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS chef_orders (
                    order_id TEXT PRIMARY KEY,
                    customer_name TEXT,
                    customer_address TEXT,
                    customer_whatsapp TEXT,
                    status TEXT NOT NULL DEFAULT 'draft',
                    total_value REAL NOT NULL DEFAULT 0,
                    summary_json TEXT NOT NULL DEFAULT '[]',
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS chef_order_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    order_id TEXT NOT NULL,
                    category TEXT NOT NULL,
                    product_name TEXT NOT NULL,
                    unit_type TEXT NOT NULL,
                    quantity REAL NOT NULL,
                    unit_price REAL NOT NULL,
                    subtotal REAL NOT NULL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(order_id) REFERENCES chef_orders(order_id)
                )
                """
            )
            conn.commit()

    def create_order_if_missing(self, order_id: str) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO chef_orders (order_id, summary_json)
                VALUES (?, '[]')
                ON CONFLICT(order_id) DO NOTHING
                """,
                (order_id,),
            )
            conn.commit()

    def add_item(
        self,
        order_id: str,
        category: str,
        product_name: str,
        unit_type: str,
        quantity: float,
        unit_price: float,
    ) -> dict[str, Any]:
        subtotal = round(quantity * unit_price, 2)
        self.create_order_if_missing(order_id)
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO chef_order_items (
                    order_id, category, product_name, unit_type, quantity, unit_price, subtotal
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (order_id, category, product_name,
                 unit_type, quantity, unit_price, subtotal),
            )
            total = conn.execute(
                "SELECT COALESCE(SUM(subtotal), 0) AS total FROM chef_order_items WHERE order_id = ?",
                (order_id,),
            ).fetchone()["total"]
            summary_rows = conn.execute(
                """
                SELECT category, product_name, unit_type, quantity, unit_price, subtotal
                FROM chef_order_items
                WHERE order_id = ?
                ORDER BY id ASC
                """,
                (order_id,),
            ).fetchall()
            summary = [dict(row) for row in summary_rows]
            conn.execute(
                """
                UPDATE chef_orders
                SET total_value = ?, summary_json = ?, updated_at = CURRENT_TIMESTAMP
                WHERE order_id = ?
                """,
                (round(total, 2), json.dumps(summary, ensure_ascii=False), order_id),
            )
            conn.commit()
        return {"order_id": order_id, "subtotal": subtotal, "total_value": round(total, 2), "items": summary}

    def get_order(self, order_id: str) -> dict[str, Any] | None:
        with self._connect() as conn:
            order = conn.execute(
                "SELECT * FROM chef_orders WHERE order_id = ?",
                (order_id,),
            ).fetchone()
            if not order:
                return None
            items = conn.execute(
                "SELECT category, product_name, unit_type, quantity, unit_price, subtotal FROM chef_order_items WHERE order_id = ? ORDER BY id ASC",
                (order_id,),
            ).fetchall()
        result = dict(order)
        result["items"] = [dict(row) for row in items]
        return result
