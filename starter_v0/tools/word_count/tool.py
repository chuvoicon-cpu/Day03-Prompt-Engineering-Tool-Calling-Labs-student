from __future__ import annotations

from typing import Any


def count_words(text: str = "") -> dict[str, Any]:
    if not isinstance(text, str):
        return {"tool": "word_count", "error": "TypeError", "message": "text must be a string"}
    if not text.strip():
        return {"tool": "word_count", "error": "ValueError", "message": "text must not be empty"}
    return {
        "tool": "word_count",
        "word_count": len(text.split()),
        "character_count": len(text),
    }
