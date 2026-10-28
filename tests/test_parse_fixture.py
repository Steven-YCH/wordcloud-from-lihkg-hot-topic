"""Fixture-based tests for parse + storage (no live network)."""

from __future__ import annotations

import json
from pathlib import Path

from lihkg_hot.client import parse_items
from lihkg_hot.storage import ThreadStore, append_word
from lihkg_hot.tokenize import tokenize_titles

FIXTURE = Path(__file__).parent / "fixtures" / "sample_hot_response.json"


def test_parse_items_normalizes_fields() -> None:
    payload = json.loads(FIXTURE.read_text(encoding="utf-8"))
    threads = parse_items(payload)
    assert len(threads) == 2  # empty title skipped
    assert threads[0]["thread_id"] == 1001
    assert threads[0]["category"] == "吹水台"
    assert threads[1]["thread_id"] == 1002  # id fallback
    assert threads[1]["no_of_reply"] == 45
    assert threads[1]["like_count"] == 60


def test_storage_roundtrip(tmp_path: Path) -> None:
    payload = json.loads(FIXTURE.read_text(encoding="utf-8"))
    threads = parse_items(payload)
    db = tmp_path / "t.sqlite"
    jsonl = tmp_path / "t.jsonl"
    with ThreadStore(db, jsonl) as store:
        n = store.upsert_threads(threads, scraped_at="2024-01-01T00:00:00+00:00")
        assert n == 2
        titles = store.fetch_titles()
        assert len(titles) == 2
        assert store.count() == 2
    lines = jsonl.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 2
    assert "吹水台" in lines[0]


def test_tokenize_uses_user_dict_and_stopwords(tmp_path: Path) -> None:
    stop = tmp_path / "stop.txt"
    user = tmp_path / "user.txt"
    stop.write_text("的\n", encoding="utf-8")
    user.write_text("難忍\n唔會\n", encoding="utf-8")
    tokens = tokenize_titles(
        ["難忍 唔會再買的公司"],
        stopwords_path=stop,
        user_dict_path=user,
    )
    assert "的" not in tokens
    assert "難忍" in tokens
    assert "唔會" in tokens


def test_append_word_dedupes(tmp_path: Path) -> None:
    path = tmp_path / "words.txt"
    append_word(path, "hello")
    append_word(path, "hello")
    append_word(path, " world ")
    lines = [ln for ln in path.read_text(encoding="utf-8").splitlines() if ln]
    assert lines == ["hello", "world"]
