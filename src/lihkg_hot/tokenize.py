"""Chinese/Cantonese tokenization via jieba + custom stopwords/user dict."""

from __future__ import annotations

from pathlib import Path

import jieba

from .config import DEFAULT_STOPWORDS, DEFAULT_USER_DICT


def load_stopwords(path: Path = DEFAULT_STOPWORDS) -> set[str]:
    if not path.is_file():
        return set()
    return {
        line.strip()
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    }


def configure_jieba(user_dict: Path = DEFAULT_USER_DICT) -> None:
    """Load optional custom user dictionary (jieba's built-in dict is used)."""
    if user_dict.is_file():
        jieba.load_userdict(str(user_dict))


def tokenize_titles(
    titles: list[str],
    *,
    stopwords_path: Path = DEFAULT_STOPWORDS,
    user_dict_path: Path = DEFAULT_USER_DICT,
) -> list[str]:
    """Cut titles into tokens, dropping stopwords and trivial fragments."""
    configure_jieba(user_dict_path)
    stopwords = load_stopwords(stopwords_path)
    tokens: list[str] = []
    for title in titles:
        for token in jieba.cut(str(title)):
            word = token.strip()
            if not word or word in stopwords:
                continue
            if len(word) == 1 and not word.isalpha():
                # Drop lone punctuation / symbols that slipped through.
                continue
            tokens.append(word)
    return tokens


def tokens_to_text(tokens: list[str]) -> str:
    return " ".join(tokens)
