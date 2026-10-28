"""HTTP client for the LIHKG hot-thread API (requests, optional cloudscraper)."""

from __future__ import annotations

import logging
import time
from typing import Any

import requests

from .config import API_BASE, DEFAULT_BACKOFF, DEFAULT_RETRIES, DEFAULT_TIMEOUT, default_headers

logger = logging.getLogger(__name__)


def _make_session() -> requests.Session:
    """Prefer cloudscraper when installed; otherwise plain requests."""
    try:
        import cloudscraper  # type: ignore

        scraper = cloudscraper.create_scraper()
        logger.debug("Using cloudscraper session")
        return scraper
    except ImportError:
        logger.debug("cloudscraper not installed; using requests")
        return requests.Session()


class LihkgClient:
    """Fetch paginated hot-thread JSON with retries and backoff."""

    def __init__(
        self,
        *,
        timeout: float = DEFAULT_TIMEOUT,
        retries: int = DEFAULT_RETRIES,
        backoff: float = DEFAULT_BACKOFF,
        session: requests.Session | None = None,
    ) -> None:
        self.timeout = timeout
        self.retries = retries
        self.backoff = backoff
        self.session = session or _make_session()
        self.headers = default_headers()

    def fetch_hot_page(
        self,
        *,
        cat_id: int,
        page: int,
        count: int,
        thread_type: str = "daily",
    ) -> dict[str, Any]:
        params = {
            "cat_id": cat_id,
            "page": page,
            "count": count,
            "type": thread_type,
        }
        last_error: Exception | None = None
        for attempt in range(1, self.retries + 1):
            try:
                response = self.session.get(
                    API_BASE,
                    params=params,
                    headers=self.headers,
                    timeout=self.timeout,
                )
                if response.status_code == 200:
                    payload = response.json()
                    if not isinstance(payload, dict):
                        raise ValueError("Unexpected non-object JSON payload")
                    return payload
                last_error = RuntimeError(
                    f"HTTP {response.status_code}: {response.text[:200]}"
                )
                logger.warning(
                    "Attempt %s/%s failed for page %s: %s",
                    attempt,
                    self.retries,
                    page,
                    last_error,
                )
            except (requests.RequestException, ValueError) as exc:
                last_error = exc
                logger.warning(
                    "Attempt %s/%s error for page %s: %s",
                    attempt,
                    self.retries,
                    page,
                    exc,
                )
            if attempt < self.retries:
                sleep_for = self.backoff * (2 ** (attempt - 1))
                time.sleep(sleep_for)

        raise RuntimeError(
            f"Failed to fetch LIHKG hot page {page} after {self.retries} attempts"
        ) from last_error


def parse_items(payload: dict[str, Any]) -> list[dict[str, Any]]:
    """Normalize API items into flat thread records."""
    response = payload.get("response") or {}
    raw_items = response.get("items") or []
    threads: list[dict[str, Any]] = []
    for item in raw_items:
        if not isinstance(item, dict):
            continue
        category = item.get("category") or {}
        category_name = category.get("name") if isinstance(category, dict) else None
        thread_id = item.get("thread_id", item.get("id"))
        title = item.get("title")
        if thread_id is None or not title:
            continue
        threads.append(
            {
                "thread_id": int(thread_id),
                "title": str(title),
                "no_of_reply": int(item.get("no_of_reply") or 0),
                "no_of_uni_user_reply": int(item.get("no_of_uni_user_reply") or 0),
                "like_count": int(item.get("like_count") or 0),
                "dislike_count": int(item.get("dislike_count") or 0),
                "category": str(category_name or ""),
            }
        )
    return threads
