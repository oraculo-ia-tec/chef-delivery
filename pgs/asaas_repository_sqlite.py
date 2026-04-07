from __future__ import annotations

import json
import sqlite3
from dataclasses import asdict
from pathlib import Path
from typing import Any

from api_asaas import PaymentRecord


class SQLitePaymentRepository:
    def __init__(self, db_path: str = "chef_delivery.db") -> None:
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
                CREATE TABLE IF NOT EXISTS asaas_payments (
                    order_id TEXT PRIMARY KEY,
                    payment_id TEXT,
                    customer_id TEXT,
                    status TEXT,
                    payment_method TEXT NOT NULL,
                    value REAL NOT NULL,
                    description TEXT NOT NULL,
                    external_reference TEXT NOT NULL,
                    invoice_url TEXT,
                    bank_slip_url TEXT,
                    pix_payload TEXT,
                    raw_json TEXT NOT NULL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            conn.execute(
                "CREATE UNIQUE INDEX IF NOT EXISTS idx_asaas_payment_id ON asaas_payments(payment_id)"
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS asaas_webhook_events (
                    event_hash TEXT PRIMARY KEY,
                    event_id TEXT,
                    payment_id TEXT,
                    event_name TEXT,
                    payload_json TEXT NOT NULL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            conn.commit()

    def _row_to_record(self, row: sqlite3.Row | None) -> PaymentRecord | None:
        if row is None:
            return None
        return PaymentRecord(
            order_id=row["order_id"],
            payment_id=row["payment_id"],
            customer_id=row["customer_id"],
            status=row["status"],
            payment_method=row["payment_method"],
            value=row["value"],
            description=row["description"],
            external_reference=row["external_reference"],
            invoice_url=row["invoice_url"],
            bank_slip_url=row["bank_slip_url"],
            pix_payload=row["pix_payload"],
            raw=json.loads(row["raw_json"] or "{}"),
        )

    async def get_by_order_id(self, order_id: str) -> PaymentRecord | None:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM asaas_payments WHERE order_id = ?",
                (order_id,),
            ).fetchone()
        return self._row_to_record(row)

    async def get_by_payment_id(self, payment_id: str) -> PaymentRecord | None:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM asaas_payments WHERE payment_id = ?",
                (payment_id,),
            ).fetchone()
        return self._row_to_record(row)

    async def upsert(self, record: PaymentRecord) -> PaymentRecord:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO asaas_payments (
                    order_id, payment_id, customer_id, status, payment_method, value,
                    description, external_reference, invoice_url, bank_slip_url,
                    pix_payload, raw_json, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(order_id) DO UPDATE SET
                    payment_id = excluded.payment_id,
                    customer_id = excluded.customer_id,
                    status = excluded.status,
                    payment_method = excluded.payment_method,
                    value = excluded.value,
                    description = excluded.description,
                    external_reference = excluded.external_reference,
                    invoice_url = excluded.invoice_url,
                    bank_slip_url = excluded.bank_slip_url,
                    pix_payload = excluded.pix_payload,
                    raw_json = excluded.raw_json,
                    updated_at = CURRENT_TIMESTAMP
                """,
                (
                    record.order_id,
                    record.payment_id,
                    record.customer_id,
                    record.status,
                    record.payment_method,
                    record.value,
                    record.description,
                    record.external_reference,
                    record.invoice_url,
                    record.bank_slip_url,
                    record.pix_payload,
                    json.dumps(record.raw, ensure_ascii=False),
                ),
            )
            conn.commit()
        return record

    async def mark_webhook_processed(self, payload: dict[str, Any]) -> bool:
        event_hash = self._build_event_hash(payload)
        with self._connect() as conn:
            existing = conn.execute(
                "SELECT event_hash FROM asaas_webhook_events WHERE event_hash = ?",
                (event_hash,),
            ).fetchone()
            if existing:
                return False
            payment = payload.get("payment") or {}
            conn.execute(
                """
                INSERT INTO asaas_webhook_events (event_hash, event_id, payment_id, event_name, payload_json)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    event_hash,
                    payload.get("id"),
                    payment.get("id"),
                    payload.get("event"),
                    json.dumps(payload, ensure_ascii=False),
                ),
            )
            conn.commit()
            return True

    async def list_payments(self, limit: int = 50) -> list[dict[str, Any]]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT * FROM asaas_payments ORDER BY updated_at DESC LIMIT ?",
                (limit,),
            ).fetchall()
        return [asdict(self._row_to_record(row)) for row in rows if row]

    async def list_webhooks(self, limit: int = 50) -> list[dict[str, Any]]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT * FROM asaas_webhook_events ORDER BY created_at DESC LIMIT ?",
                (limit,),
            ).fetchall()
        return [dict(row) for row in rows]

    @staticmethod
    def _build_event_hash(payload: dict[str, Any]) -> str:
        import hashlib

        serialized = json.dumps(payload, sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()
