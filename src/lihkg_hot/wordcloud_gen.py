"""Generate a masked word cloud from scraped thread titles."""

from __future__ import annotations

import logging
from pathlib import Path

import numpy as np
from PIL import Image
from wordcloud import WordCloud

from .config import (
    DEFAULT_DB_PATH,
    DEFAULT_MASK,
    DEFAULT_STOPWORDS,
    DEFAULT_USER_DICT,
    DEFAULT_WORDCLOUD_OUT,
    detect_cjk_font,
)
from .storage import ThreadStore
from .tokenize import tokens_to_text, tokenize_titles

logger = logging.getLogger(__name__)


def _load_mask(mask_path: Path) -> np.ndarray:
    mask_color = np.array(Image.open(mask_path).convert("RGB"))
    # Downsample slightly for speed / softer edges (same idea as legacy code).
    mask_color = mask_color[::2, ::2]
    mask_image = mask_color.copy()
    mask_image[mask_image.sum(axis=2) == 0] = 255
    return mask_image


def generate_wordcloud(
    *,
    db_path: Path = DEFAULT_DB_PATH,
    mask_path: Path = DEFAULT_MASK,
    font_path: Path | str | None = None,
    out_path: Path = DEFAULT_WORDCLOUD_OUT,
    stopwords_path: Path = DEFAULT_STOPWORDS,
    user_dict_path: Path = DEFAULT_USER_DICT,
    background_color: str = "white",
) -> Path:
    """Build a word cloud PNG from titles stored in SQLite."""
    with ThreadStore(db_path) as store:
        titles = store.fetch_titles()
    if not titles:
        raise ValueError(f"No titles found in database: {db_path}")

    tokens = tokenize_titles(
        titles,
        stopwords_path=stopwords_path,
        user_dict_path=user_dict_path,
    )
    if not tokens:
        raise ValueError("Tokenization produced no tokens; check stopwords / titles")

    font = detect_cjk_font(font_path)
    mask = _load_mask(Path(mask_path)) if Path(mask_path).is_file() else None
    text = tokens_to_text(tokens)

    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)

    wc = WordCloud(
        font_path=str(font),
        mask=mask,
        background_color=background_color,
        width=1200 if mask is None else None,
        height=800 if mask is None else None,
        margin=2,
        collocations=False,
    ).generate(text)
    wc.to_file(str(out))
    logger.info("Wrote word cloud to %s (font=%s, tokens=%s)", out, font, len(tokens))
    return out.resolve()
