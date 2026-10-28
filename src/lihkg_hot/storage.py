"""SQLite + JSONL persistence for scraped LIHKG threads."""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


SCHEMA = """
CREATE TABLE IF NOT EXISTS threads (
    thread_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    no_of_reply INTEGER,
    no_of_uni_user_reply INTEGER,
    like_count INTEGER,
    dislike_count INTEGER,
    category TEXT,
    scraped_at TEXT NOT NULL,
    PRIMARY KEY (thread_id, scraped_at)
);

CREATE INDEX IF NOT EXISTS idx_threads_title ON threads(title);
"""


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


class ThreadStore:
    def __init__(self, db_path: Path, jsonl_path: Path | None = None) -> None:
        self.db_path = Path(db_path)
        self.jsonl_path = Path(jsonl_path) if jsonl_path else None
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        if self.jsonl_path:
            self.jsonl_path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(self.db_path)
        self._conn.row_factory = sqlite3.Row
        self._conn.executescript(SCHEMA)

    def close(self) -> None:
        self._conn.close()

    def __enter__(self) -> "ThreadStore":
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()

    def upsert_threads(
        self,
        threads: Iterable[dict[str, Any]],
        *,
        scraped_at: str | None = None,
    ) -> int:
        stamp = scraped_at or _utc_now_iso()
        rows = []
        jsonl_lines: list[str] = []
        for thread in threads:
            row = (
                int(thread["thread_id"]),
                str(thread["title"]),
                int(thread.get("no_of_reply") or 0),
                int(thread.get("no_of_uni_user_reply") or 0),
                int(thread.get("like_count") or 0),
                int(thread.get("dislike_count") or 0),
                str(thread.get("category") or ""),
                stamp,
            )
            rows.append(row)
            record = {
                "thread_id": row[0],
                "title": row[1],
                "no_of_reply": row[2],
                "no_of_uni_user_reply": row[3],
                "like_count": row[4],
                "dislike_count": row[5],
                "category": row[6],
                "scraped_at": stamp,
            }
            jsonl_lines.append(json.dumps(record, ensure_ascii=False))

        self._conn.executemany(
            """
            INSERT OR REPLACE INTO threads (
                thread_id, title, no_of_reply, no_of_uni_user_reply,
                like_count, dislike_count, category, scraped_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            rows,
        )
        self._conn.commit()

        if self.jsonl_path and jsonl_lines:
            with self.jsonl_path.open("a", encoding="utf-8") as handle:
                handle.write("\n".join(jsonl_lines) + "\n")
        return len(rows)

    def fetch_titles(self) -> list[str]:
        cur = self._conn.execute(
            "SELECT title FROM threads ORDER BY scraped_at DESC, thread_id DESC"
        )
        return [str(row["title"]) for row in cur.fetchall()]

    def count(self) -> int:
        cur = self._conn.execute("SELECT COUNT(*) AS n FROM threads")
        return int(cur.fetchone()["n"])


def append_word(path: Path, word: str) -> None:
    """Append a unique non-empty word to a dictionary/stopword file."""
    cleaned = word.strip()
    if not cleaned:
        raise ValueError("Empty word")
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    existing: set[str] = set()
    if path.is_file():
        existing = {
            line.strip()
            for line in path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        }
    if cleaned in existing:
        return
    with path.open("a", encoding="utf-8") as handle:
        handle.write(cleaned + "\n")
