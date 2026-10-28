# LIHKG Hot Topic Word Cloud

[![CI](https://github.com/Steven-YCH/wordcloud-from-lihkg-hot-topic/actions/workflows/ci.yml/badge.svg)](https://github.com/Steven-YCH/wordcloud-from-lihkg-hot-topic/actions/workflows/ci.yml)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)


Portfolio rewrite of a first-project scraper that turns **LIHKG daily hot threads** into a **Chinese/Cantonese word cloud**.

LIHKG is a popular Hong Kong forum. Thread titles are dense with slang, mixed Chinese/English, and reaction culture — a natural corpus for lightweight NLP demos (tokenization, stopwords, visualization) without needing full post bodies.

![Sample word cloud](https://user-images.githubusercontent.com/85422707/137614391-d0610115-c884-404b-9562-30cae9115b24.png)

## Problem statement

Forum “hot” lists change constantly. Manually skimming titles does not show which themes dominate. This project:

1. Pulls the public hot-thread JSON API with polite retries
2. Stores results in **SQLite** (queryable) and **JSONL** (portable)
3. Tokenizes titles with **jieba** + a small custom user dictionary / stopword list
4. Renders a masked word cloud with an auto-detected CJK font

## Architecture

```
lihkg.com API ──► client.py (requests → optional cloudscraper)
                      │
                      ▼
                 scrape.py ──► storage.py (SQLite + JSONL)
                      │
                      ▼
               tokenize.py (jieba + assets/*)
                      │
                      ▼
            wordcloud_gen.py ──► outputs/wordcloud.png
```

CLI entry point: `lihkg-hot` (`src/lihkg_hot/cli.py`).

Legacy flat scripts live under `archive/legacy/` for reference. The huge vendored `jieba/dict.txt` is **removed** — the pip `jieba` package supplies the default dictionary; only `assets/user_dict.txt` and `assets/stopwords.txt` are customized.

## Install

Requires **Python 3.10+**.

```bash
git clone https://github.com/Steven-YCH/wordcloud-from-lihkg-hot-topic.git
cd wordcloud-from-lihkg-hot-topic
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -e ".[dev]"
# Optional Cloudflare helper:
pip install -e ".[cloudflare]"
# Or: pip install -r requirements.txt && pip install -e .
```

### Fonts (important for Chinese glyphs)

Word clouds need a TrueType/OpenType font that covers CJK. The tool auto-detects common fonts:

| OS | Tried first |
|----|-------------|
| Windows | `msjh.ttc`, `msyh.ttc`, `mingliu.ttc`, `kaiu.ttf`, … |
| macOS | PingFang, STHeiti, Hiragino Sans GB, … |
| Linux | Noto Sans CJK, WenQuanYi, AR PL UMing, … |

Overrides:

```bash
lihkg-hot wordcloud --font "C:\Windows\Fonts\msjh.ttc"
# or
set LIHKG_FONT=C:\Windows\Fonts\msjh.ttc   # Windows
export LIHKG_FONT=/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc
```

## Usage

### Scrape hot threads

```bash
lihkg-hot scrape --pages 1 --count 50 --cat-id 1 --type daily
```

Writes:

- `data/lihkg.sqlite`
- `data/threads.jsonl`

### Generate a word cloud

```bash
lihkg-hot wordcloud --db data/lihkg.sqlite --mask assets/mask.png --out outputs/wordcloud.png
```

### Dictionary helpers (non-interactive)

```bash
lihkg-hot add-user-word 難頂
lihkg-hot add-stopword 的
```

### Smoke / offline checks

```bash
pip install -e ".[dev]"
pytest
```

Live scrape (may fail behind Cloudflare or network policy):

```bash
lihkg-hot scrape --pages 1 --count 10 -v
```

If the live endpoint is blocked (e.g. TCP reset / Cloudflare challenge), fixture-based unit tests still validate parsing and storage. You can also seed SQLite from `tests/fixtures/sample_hot_response.json` for a local word-cloud dry run. Re-run scrape when you have network access that can reach `lihkg.com`.

## Ethics & responsible use

- Intended for **personal / educational / portfolio** exploration of public list data.
- Do **not** hammer the API. Default settings fetch a small page count with exponential backoff.
- Respect LIHKG terms of service and local law. Do not republish scraped content at scale or use it for harassment, spam, or commercial redistribution without permission.
- Titles can contain offensive language; treat outputs accordingly.

## Limitations

- LIHKG sits behind **Cloudflare**; plain `requests` may get challenged. Install `cloudscraper` (`pip install -e ".[cloudflare]"`) for a best-effort fallback — it is not guaranteed forever.
- Tokenization is title-only (not full threads), so slang and multi-character Cantonese terms may need `add-user-word`.
- Mask quality depends on `assets/mask.png` contrast; dark silhouettes work best.
- Fonts must be installed locally; missing CJK fonts produce boxes or empty glyphs.

## Project layout

```
src/lihkg_hot/     # installable package
assets/            # mask, stopwords, user_dict
data/              # SQLite / JSONL (gitignored contents)
outputs/           # generated images (gitignored)
tests/             # fixture-based tests
archive/legacy/    # original scripts
```

## License

MIT — see [LICENSE](LICENSE).
