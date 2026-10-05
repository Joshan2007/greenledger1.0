"""
GreenLedger - Local optimization trial memory.
Stores verified before/after optimization outcomes so future recommendations can
adapt to this device instead of relying only on generic heuristics.
"""

import json
import sqlite3
import time
from pathlib import Path
from typing import Any, Dict, List

DB_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "optimization_trials.sqlite3"


class OptimizationTrialStore:
    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _connect(self):
        return sqlite3.connect(self.db_path)

    def _init_db(self):
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS optimization_trials (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    created_at REAL NOT NULL,
                    user_id TEXT NOT NULL,
                    device_hash TEXT NOT NULL,
                    action_id TEXT NOT NULL,
                    predicted_watts_saved REAL,
                    actual_watts_saved REAL NOT NULL,
                    actual_reduction_pct REAL NOT NULL,
                    before_power_w REAL NOT NULL,
                    after_power_w REAL NOT NULL,
                    before_telemetry_json TEXT NOT NULL,
                    after_telemetry_json TEXT NOT NULL
                )
                """
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_trials_action_device ON optimization_trials(action_id, device_hash)"
            )

    def record_trial(
        self,
        *,
        user_id: str,
        device_hash: str,
        action_id: str,
        predicted_watts_saved: float | None,
        actual_watts_saved: float,
        actual_reduction_pct: float,
        before_power_w: float,
        after_power_w: float,
        before_telemetry: Dict[str, Any],
        after_telemetry: Dict[str, Any],
    ) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO optimization_trials (
                    created_at, user_id, device_hash, action_id, predicted_watts_saved,
                    actual_watts_saved, actual_reduction_pct, before_power_w, after_power_w,
                    before_telemetry_json, after_telemetry_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    time.time(),
                    user_id,
                    device_hash,
                    action_id,
                    predicted_watts_saved,
                    actual_watts_saved,
                    actual_reduction_pct,
                    before_power_w,
                    after_power_w,
                    json.dumps(before_telemetry, sort_keys=True),
                    json.dumps(after_telemetry, sort_keys=True),
                ),
            )

    def summarize_action(self, action_id: str, device_hash: str) -> Dict[str, Any]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT actual_watts_saved, actual_reduction_pct
                FROM optimization_trials
                WHERE action_id = ? AND device_hash = ?
                ORDER BY created_at DESC
                LIMIT 20
                """,
                (action_id, device_hash),
            ).fetchall()

        if not rows:
            return {"trial_count": 0, "avg_watts_saved": None, "avg_reduction_pct": None}

        watts = [max(0.0, float(row[0])) for row in rows]
        pct = [max(0.0, float(row[1])) for row in rows]
        return {
            "trial_count": len(rows),
            "avg_watts_saved": round(sum(watts) / len(watts), 2),
            "avg_reduction_pct": round(sum(pct) / len(pct), 2),
        }

    def recent_trials(self, limit: int = 25) -> List[Dict[str, Any]]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT created_at, user_id, device_hash, action_id, predicted_watts_saved,
                       actual_watts_saved, actual_reduction_pct
                FROM optimization_trials
                ORDER BY created_at DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()

        return [
            {
                "created_at": row[0],
                "user_id": row[1],
                "device_hash": row[2],
                "action_id": row[3],
                "predicted_watts_saved": row[4],
                "actual_watts_saved": row[5],
                "actual_reduction_pct": row[6],
            }
            for row in rows
        ]


trial_store = OptimizationTrialStore()
