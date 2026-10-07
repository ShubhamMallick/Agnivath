"""SQLite-backed persistence for processed lead records."""
import json
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator, Optional


class LeadStore:
    """Persist lead records locally without changing their API shape."""

    def __init__(self, database_path: Path):
        self.database_path = Path(database_path)
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        return connection

    @contextmanager
    def _connection(self) -> Iterator[sqlite3.Connection]:
        connection = self._connect()
        try:
            yield connection
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def _initialize(self) -> None:
        with self._connection() as connection:
            connection.execute(
                """CREATE TABLE IF NOT EXISTS leads (
                    lead_id TEXT PRIMARY KEY,
                    original_data TEXT NOT NULL,
                    extracted_info TEXT NOT NULL,
                    qualification TEXT NOT NULL,
                    notification_sent INTEGER NOT NULL,
                    created_at TEXT NOT NULL
                )"""
            )
            connection.execute(
                """CREATE TABLE IF NOT EXISTS notifications (
                    notification_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    lead_id TEXT NOT NULL,
                    priority TEXT NOT NULL,
                    score INTEGER NOT NULL,
                    lead_name TEXT,
                    company TEXT,
                    next_action TEXT,
                    message TEXT NOT NULL
                )"""
            )

    def save(self, lead: dict[str, Any]) -> None:
        with self._connection() as connection:
            connection.execute(
                """INSERT INTO leads (
                    lead_id, original_data, extracted_info, qualification,
                    notification_sent, created_at
                ) VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(lead_id) DO UPDATE SET
                    original_data = excluded.original_data,
                    extracted_info = excluded.extracted_info,
                    qualification = excluded.qualification,
                    notification_sent = excluded.notification_sent,
                    created_at = excluded.created_at""",
                (
                    lead["lead_id"],
                    json.dumps(lead.get("original_data") or {}),
                    json.dumps(lead.get("extracted_info") or {}),
                    json.dumps(lead.get("qualification") or {}),
                    int(bool(lead.get("notification_sent"))),
                    lead["created_at"],
                ),
            )

    def list_leads(self) -> list[dict[str, Any]]:
        with self._connection() as connection:
            rows = connection.execute(
                "SELECT * FROM leads ORDER BY created_at DESC, rowid DESC"
            ).fetchall()
        return [self._deserialize(row) for row in rows]

    def get_lead(self, lead_id: str) -> Optional[dict[str, Any]]:
        with self._connection() as connection:
            row = connection.execute(
                "SELECT * FROM leads WHERE lead_id = ?", (lead_id,)
            ).fetchone()
        return self._deserialize(row) if row else None

    def save_notification(self, notification: dict[str, Any]) -> None:
        with self._connection() as connection:
            connection.execute(
                """INSERT INTO notifications (
                    timestamp, lead_id, priority, score, lead_name, company,
                    next_action, message
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    notification["timestamp"],
                    notification["lead_id"],
                    notification["priority"],
                    int(notification["score"]),
                    notification.get("lead_name"),
                    notification.get("company"),
                    notification.get("next_action"),
                    notification["message"],
                ),
            )

    def list_notifications(self, min_priority: str = "MEDIUM") -> list[dict[str, Any]]:
        priority_order = {"HIGH": 3, "MEDIUM": 2, "LOW": 1}
        minimum = priority_order.get(min_priority.upper())
        if minimum is None:
            raise ValueError("min_priority must be HIGH, MEDIUM, or LOW")

        allowed_priorities = [
            priority for priority, level in priority_order.items() if level >= minimum
        ]
        placeholders = ", ".join("?" for _ in allowed_priorities)
        with self._connection() as connection:
            rows = connection.execute(
                f"""SELECT timestamp, lead_id, priority, score, lead_name, company,
                           next_action, message
                    FROM notifications
                    WHERE priority IN ({placeholders})
                    ORDER BY timestamp DESC, notification_id DESC""",
                allowed_priorities,
            ).fetchall()
        return [dict(row) for row in rows]

    def clear_notifications(self) -> int:
        with self._connection() as connection:
            cursor = connection.execute("DELETE FROM notifications")
            return cursor.rowcount

    @staticmethod
    def _deserialize(row: sqlite3.Row) -> dict[str, Any]:
        return {
            "lead_id": row["lead_id"],
            "original_data": json.loads(row["original_data"]),
            "extracted_info": json.loads(row["extracted_info"]),
            "qualification": json.loads(row["qualification"]),
            "notification_sent": bool(row["notification_sent"]),
            "created_at": row["created_at"],
        }