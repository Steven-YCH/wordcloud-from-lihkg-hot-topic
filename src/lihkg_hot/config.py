"""Paths, defaults, and CJK font discovery."""

from __future__ import annotations

import os
import sys
from pathlib import Path

PACKAGE_ROOT = Path(__file__).resolve().parent
REPO_ROOT = PACKAGE_ROOT.parents[1]

DEFAULT_ASSETS = REPO_ROOT / "assets"
DEFAULT_DATA_DIR = REPO_ROOT / "data"
DEFAULT_OUTPUTS_DIR = REPO_ROOT / "outputs"

DEFAULT_DB_PATH = DEFAULT_DATA_DIR / "lihkg.sqlite"
DEFAULT_JSONL_PATH = DEFAULT_DATA_DIR / "threads.jsonl"
DEFAULT_STOPWORDS = DEFAULT_ASSETS / "stopwords.txt"
DEFAULT_USER_DICT = DEFAULT_ASSETS / "user_dict.txt"
DEFAULT_MASK = DEFAULT_ASSETS / "mask.png"
DEFAULT_WORDCLOUD_OUT = DEFAULT_OUTPUTS_DIR / "wordcloud.png"

API_BASE = "https://lihkg.com/api_v2/thread/hot"
DEFAULT_REFERER = "https://lihkg.com/category/1?order=hot"
DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)

DEFAULT_CAT_ID = 1
DEFAULT_PAGES = 1
DEFAULT_COUNT = 50
DEFAULT_TYPE = "daily"
DEFAULT_RETRIES = 5
DEFAULT_BACKOFF = 1.5
DEFAULT_TIMEOUT = 30.0

# Ordered candidates for common CJK fonts on each platform.
_FONT_CANDIDATES: dict[str, list[str]] = {
    "win32": [
        r"C:\Windows\Fonts\msjh.ttc",
        r"C:\Windows\Fonts\msyh.ttc",
        r"C:\Windows\Fonts\mingliu.ttc",
        r"C:\Windows\Fonts\kaiu.ttf",
        r"C:\Windows\Fonts\simsun.ttc",
        r"C:\Windows\Fonts\simhei.ttf",
    ],
    "darwin": [
        "/System/Library/Fonts/PingFang.ttc",
        "/System/Library/Fonts/STHeiti Light.ttc",
        "/System/Library/Fonts/Hiragino Sans GB.ttc",
        "/Library/Fonts/Arial Unicode.ttf",
    ],
    "linux": [
        "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
        "/usr/share/fonts/truetype/arphic/uming.ttc",
        "/usr/share/fonts/opentype/noto/NotoSerifCJK-Regular.ttc",
    ],
}


def detect_cjk_font(override: str | Path | None = None) -> Path:
    """Return a usable CJK font path, or raise with install guidance."""
    if override:
        path = Path(override).expanduser()
        if path.is_file():
            return path.resolve()
        raise FileNotFoundError(f"Font not found: {path}")

    env = os.environ.get("LIHKG_FONT")
    if env:
        path = Path(env).expanduser()
        if path.is_file():
            return path.resolve()

    platform_key = "win32" if sys.platform.startswith("win") else sys.platform
    candidates = list(_FONT_CANDIDATES.get(platform_key, []))
    # Also try Linux candidates on unknown Unix-likes.
    if platform_key not in _FONT_CANDIDATES:
        candidates.extend(_FONT_CANDIDATES["linux"])

    for candidate in candidates:
        path = Path(candidate)
        if path.is_file():
            return path.resolve()

    raise FileNotFoundError(
        "No CJK font found. Install a Chinese font (e.g. Noto Sans CJK, "
        "Microsoft JhengHei, PingFang) or pass --font / set LIHKG_FONT."
    )


def default_headers() -> dict[str, str]:
    return {
        "referer": DEFAULT_REFERER,
        "User-Agent": DEFAULT_USER_AGENT,
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "zh-HK,zh-TW;q=0.9,zh;q=0.8,en;q=0.7",
    }
