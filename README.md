# LIHKG Hot Topic Word Cloud

[![CI](https://github.com/Steven-YCH/wordcloud-from-lihkg-hot-topic/actions/workflows/ci.yml/badge.svg)](https://github.com/Steven-YCH/wordcloud-from-lihkg-hot-topic/actions/workflows/ci.yml)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)

Scrape LIHKG daily hot threads and turn the titles into a Chinese/Cantonese word cloud.

![Sample word cloud](https://user-images.githubusercontent.com/85422707/137614391-d0610115-c884-404b-9562-30cae9115b24.png)

## Pipeline

1. Pull hot-thread JSON from LIHKG (`/api_v2/thread/hot`)
2. Store results in **SQLite** and **JSONL**
3. Tokenize titles with **jieba** plus a small custom user dictionary / stopword list
4. Render a masked word cloud (auto-detects a CJK font)

```text
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

CLI: `lihkg-hot`

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
```

### Fonts

Word clouds need a font that covers CJK glyphs. Common fonts are detected automatically:

| OS | Tried first |
|----|-------------|
| Windows | `msjh.ttc`, `msyh.ttc`, `mingliu.ttc`, `kaiu.ttf`, … |
| macOS | PingFang, STHeiti, Hiragino Sans GB, … |
| Linux | Noto Sans CJK, WenQuanYi, AR PL UMing, … |

Override if needed:

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

### Dictionary helpers

```bash
lihkg-hot add-user-word 難頂
lihkg-hot add-stopword 的
```

### Tests

```bash
pytest
```

Live scrape may fail if Cloudflare challenges the request. Fixture tests still cover parsing and storage. You can also seed SQLite from `tests/fixtures/sample_hot_response.json` for a local word-cloud dry run. Optional helper:

```bash
pip install -e ".[cloudflare]"
lihkg-hot scrape --pages 1 --count 10 -v
```

## Limitations

- LIHKG may sit behind **Cloudflare**; plain `requests` can get blocked. `cloudscraper` is a best-effort fallback.
- Tokenization is title-only, so slang / multi-character Cantonese terms may need `add-user-word`.
- Mask quality depends on `assets/mask.png` contrast; dark silhouettes work best.
- Missing CJK fonts produce boxes or empty glyphs.

## Project layout

```text
src/lihkg_hot/     # installable package
assets/            # mask, stopwords, user_dict
data/              # SQLite / JSONL (gitignored contents)
outputs/           # generated images (gitignored)
tests/             # fixture-based tests
archive/legacy/    # original scripts
```
