"""Scrape LIHKG hot threads into SQLite + JSONL."""

from __future__ import annotations

import logging
from pathlib import Path

from .client import LihkgClient, parse_items
from .config import (
    DEFAULT_CAT_ID,
    DEFAULT_COUNT,
    DEFAULT_DB_PATH,
    DEFAULT_JSONL_PATH,
    DEFAULT_PAGES,
    DEFAULT_TYPE,
)
from .storage import ThreadStore

logger = logging.getLogger(__name__)


def scrape_hot(
    *,
    pages: int = DEFAULT_PAGES,
    count: int = DEFAULT_COUNT,
    cat_id: int = DEFAULT_CAT_ID,
    thread_type: str = DEFAULT_TYPE,
    db_path: Path = DEFAULT_DB_PATH,
    jsonl_path: Path = DEFAULT_JSONL_PATH,
    client: LihkgClient | None = None,
) -> dict[str, int]:
    """Paginate the hot API and persist normalized threads.

    Returns a small stats dict: pages_fetched, threads_saved, total_rows.
    """
    if pages < 1:
        raise ValueError("pages must be >= 1")
    if count < 1:
        raise ValueError("count must be >= 1")

    api = client or LihkgClient()
    saved = 0
    with ThreadStore(db_path, jsonl_path) as store:
        for page in range(1, pages + 1):
            logger.info(
                "Fetching cat_id=%s page=%s count=%s type=%s",
                cat_id,
                page,
                count,
                thread_type,
            )
            payload = api.fetch_hot_page(
                cat_id=cat_id,
                page=page,
                count=count,
                thread_type=thread_type,
            )
            threads = parse_items(payload)
            if not threads:
                logger.warning("Page %s returned no items; stopping early", page)
                break
            n = store.upsert_threads(threads)
            saved += n
            logger.info("Saved %s threads from page %s", n, page)
        total = store.count()
    return {"pages_fetched": pages, "threads_saved": saved, "total_rows": total}
