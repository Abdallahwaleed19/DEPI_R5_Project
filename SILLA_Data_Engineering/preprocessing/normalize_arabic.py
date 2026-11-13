"""
preprocessing/normalize_arabic.py
==================================
Pure-regex Arabic text normalisation — no external Arabic NLP dependency.

Functions
---------
normalize_arabic_text(text)       → str
clean_ingredient_name_ar(name)    → str
"""

import re
import unicodedata

# ---------------------------------------------------------------------------
# Character-level replacements
# ---------------------------------------------------------------------------

# Alef variants → plain alef (ا)
_ALEF_VARIANTS = re.compile(r"[أإآٱ]")

# Hamza on waw / ya → standalone
_WAW_HAMZA  = re.compile(r"ؤ")
_YA_HAMZA   = re.compile(r"ئ")

# Teh marbuta → heh (at word boundary, common normalisation)
_TEH_MARBUTA = re.compile(r"ة\b")

# Remove Arabic diacritics (tashkeel / harakat)
_DIACRITICS = re.compile(
    r"[\u0610-\u061A"   # Quranic annotation signs
    r"\u064B-\u065F"    # Fathah .. Sukun and beyond
    r"\u0670"           # Superscript alef
    r"\u06D6-\u06DC"    # Quranic small high ligatures
    r"\u06DF-\u06E4"    # More Quranic signs
    r"\u06E7-\u06E8"    # Quranic small high yeh
    r"\u06EA-\u06ED]"   # Quranic small low signs
)

# Kashida (tatweel) — decorative elongation
_TATWEEL = re.compile(r"\u0640")

# Zero-width characters
_ZERO_WIDTH = re.compile(
    r"[\u200B\u200C\u200D\u200E\u200F\uFEFF]"
)

# Presentation forms (ﻋ etc.) → compatibility equivalents
def _decompose_presentation_forms(text: str) -> str:
    """NFKC normalisation collapses Arabic presentation forms."""
    return unicodedata.normalize("NFKC", text)


# ---------------------------------------------------------------------------
# Public functions
# ---------------------------------------------------------------------------

def normalize_arabic_text(text: str) -> str:
    """
    Normalise an Arabic string:
    1. NFKC decomposition (removes presentation forms).
    2. Remove zero-width characters.
    3. Remove diacritics (tashkeel).
    4. Remove kashida.
    5. Normalise alef variants to plain alef.
    6. Normalise waw-hamza and ya-hamza.
    7. Collapse multiple whitespace.

    Parameters
    ----------
    text : str
        Raw Arabic (or mixed) text.

    Returns
    -------
    str
        Normalised text.
    """
    if not isinstance(text, str):
        return ""

    text = _decompose_presentation_forms(text)
    text = _ZERO_WIDTH.sub("", text)
    text = _DIACRITICS.sub("", text)
    text = _TATWEEL.sub("", text)
    text = _ALEF_VARIANTS.sub("ا", text)
    text = _WAW_HAMZA.sub("و", text)
    text = _YA_HAMZA.sub("ي", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def clean_ingredient_name_ar(name: str) -> str:
    """
    Clean an Arabic ingredient name:
    * Apply normalize_arabic_text().
    * Strip leading/trailing punctuation.
    * Title-case is not applied (not standard for Arabic).

    Parameters
    ----------
    name : str
        Raw ingredient name in Arabic.

    Returns
    -------
    str
        Cleaned Arabic ingredient name.
    """
    text = normalize_arabic_text(name)
    # Strip leading/trailing non-Arabic/non-space chars
    text = re.sub(r"^[^\u0600-\u06FF\s]+", "", text)
    text = re.sub(r"[^\u0600-\u06FF\s]+$", "", text)
    return text.strip()
