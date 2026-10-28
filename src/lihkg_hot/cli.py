"""Command-line interface for ``lihkg-hot``."""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

from . import __version__
from .config import (
    DEFAULT_CAT_ID,
    DEFAULT_COUNT,
    DEFAULT_DB_PATH,
    DEFAULT_JSONL_PATH,
    DEFAULT_MASK,
    DEFAULT_PAGES,
    DEFAULT_STOPWORDS,
    DEFAULT_TYPE,
    DEFAULT_USER_DICT,
    DEFAULT_WORDCLOUD_OUT,
)
from .scrape import scrape_hot
from .storage import append_word
from .wordcloud_gen import generate_wordcloud


def _add_verbose(p: argparse.ArgumentParser) -> None:
    p.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable debug logging",
    )


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="lihkg-hot",
        description="Scrape LIHKG hot topics and generate Chinese word clouds.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    _add_verbose(parser)
    sub = parser.add_subparsers(dest="command", required=True)

    scrape_p = sub.add_parser("scrape", help="Fetch hot threads into SQLite + JSONL")
    _add_verbose(scrape_p)
    scrape_p.add_argument("--pages", type=int, default=DEFAULT_PAGES)
    scrape_p.add_argument("--count", type=int, default=DEFAULT_COUNT)
    scrape_p.add_argument("--cat-id", type=int, default=DEFAULT_CAT_ID)
    scrape_p.add_argument("--type", dest="thread_type", default=DEFAULT_TYPE)
    scrape_p.add_argument("--db", type=Path, default=DEFAULT_DB_PATH)
    scrape_p.add_argument("--jsonl", type=Path, default=DEFAULT_JSONL_PATH)

    wc_p = sub.add_parser("wordcloud", help="Generate a word cloud from stored titles")
    _add_verbose(wc_p)
    wc_p.add_argument("--db", type=Path, default=DEFAULT_DB_PATH)
    wc_p.add_argument("--mask", type=Path, default=DEFAULT_MASK)
    wc_p.add_argument("--font", type=Path, default=None, help="Override CJK font path")
    wc_p.add_argument("--out", type=Path, default=DEFAULT_WORDCLOUD_OUT)
    wc_p.add_argument("--stopwords", type=Path, default=DEFAULT_STOPWORDS)
    wc_p.add_argument("--user-dict", type=Path, default=DEFAULT_USER_DICT)

    add_user = sub.add_parser("add-user-word", help="Append a word to the user dictionary")
    _add_verbose(add_user)
    add_user.add_argument("word", help="Word to add")
    add_user.add_argument("--path", type=Path, default=DEFAULT_USER_DICT)

    add_stop = sub.add_parser("add-stopword", help="Append a word to the stopword list")
    _add_verbose(add_stop)
    add_stop.add_argument("word", help="Word to add")
    add_stop.add_argument("--path", type=Path, default=DEFAULT_STOPWORDS)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(levelname)s %(name)s: %(message)s",
    )

    try:
        if args.command == "scrape":
            stats = scrape_hot(
                pages=args.pages,
                count=args.count,
                cat_id=args.cat_id,
                thread_type=args.thread_type,
                db_path=args.db,
                jsonl_path=args.jsonl,
            )
            print(
                f"Scraped pages={stats['pages_fetched']} "
                f"saved={stats['threads_saved']} total_rows={stats['total_rows']}"
            )
            print(f"DB: {args.db}")
            print(f"JSONL: {args.jsonl}")
            return 0

        if args.command == "wordcloud":
            out = generate_wordcloud(
                db_path=args.db,
                mask_path=args.mask,
                font_path=args.font,
                out_path=args.out,
                stopwords_path=args.stopwords,
                user_dict_path=args.user_dict,
            )
            print(f"Wrote {out}")
            return 0

        if args.command == "add-user-word":
            append_word(args.path, args.word)
            print(f"Added user word to {args.path}")
            return 0

        if args.command == "add-stopword":
            append_word(args.path, args.word)
            print(f"Added stopword to {args.path}")
            return 0

        parser.error(f"Unknown command: {args.command}")
        return 2
    except Exception as exc:  # noqa: BLE001 - CLI boundary
        logging.getLogger(__name__).error("%s", exc)
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
