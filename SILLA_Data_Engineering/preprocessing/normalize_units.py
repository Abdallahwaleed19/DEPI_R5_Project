"""
preprocessing/normalize_units.py
=================================
Unit and quantity normalisation helpers for SILLA.

Functions
---------
normalize_unit(unit_str)        → canonical unit string or ''
normalize_quantity(qty_str)     → float or None
convert_to_base_unit(qty, unit) → (float, str) in grams or ml
"""

import re
import logging
from fractions import Fraction

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config.settings import UNIT_ALIASES, MASS_TO_G, VOLUME_TO_ML

logger = logging.getLogger(__name__)

# Unicode vulgar fractions → decimal
UNICODE_FRACTIONS: dict[str, float] = {
    "¼": 0.25,  "½": 0.5,   "¾": 0.75,
    "⅓": 1/3,   "⅔": 2/3,
    "⅛": 0.125, "⅜": 0.375, "⅝": 0.625, "⅞": 0.875,
    "⅙": 1/6,   "⅚": 5/6,
}

_FRAC_RE  = re.compile(r"(\d+)\s*/\s*(\d+)")   # e.g. "1/2"
_MIXED_RE = re.compile(r"(\d+)\s+(\d+)\s*/\s*(\d+)")  # e.g. "1 1/2"


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def normalize_unit(unit_str: str) -> str:
    """
    Map *unit_str* to a canonical unit symbol using UNIT_ALIASES.

    Returns the canonical symbol, or an empty string if unrecognised.
    """
    if not unit_str:
        return ""
    cleaned = unit_str.strip().lower()
    result  = UNIT_ALIASES.get(cleaned, "")
    if not result:
        # Try stripping trailing punctuation / digits
        cleaned2 = re.sub(r"[^a-zء-ي]+$", "", cleaned)
        result   = UNIT_ALIASES.get(cleaned2, "")
    if not result:
        logger.debug("Unknown unit: '%s'", unit_str)
    return result


def normalize_quantity(qty_str: str) -> float | None:
    """
    Parse a quantity string such as "1/2", "1 ½", "2.5", "¼" into a float.

    Returns None if the string cannot be parsed.
    """
    if qty_str is None:
        return None
    text = str(qty_str).strip()

    # Replace unicode fractions
    for char, val in UNICODE_FRACTIONS.items():
        text = text.replace(char, f" {val} ")

    text = text.strip()

    # Mixed number: "1 1/2"
    m = _MIXED_RE.search(text)
    if m:
        whole = int(m.group(1))
        frac  = Fraction(int(m.group(2)), int(m.group(3)))
        return float(whole + frac)

    # Simple fraction: "1/2"
    m = _FRAC_RE.search(text)
    if m:
        return float(Fraction(int(m.group(1)), int(m.group(2))))

    # Plain float/int
    # Strip non-numeric trailing chars (e.g. "2 pieces" → "2")
    num_text = re.sub(r"[^\d.\-].*$", "", text).strip()
    try:
        return float(num_text)
    except (ValueError, TypeError):
        logger.debug("Cannot parse quantity: '%s'", qty_str)
        return None


def convert_to_base_unit(
    quantity: float,
    unit: str,
    ingredient: str | None = None,  # reserved for density lookup
) -> tuple[float, str]:
    """
    Convert *quantity* + *unit* to a base unit (grams for mass, ml for volume).

    Rules
    -----
    * g/kg  → grams
    * ml/L  → millilitres
    * Volume-to-mass conversion is NOT performed (density unknown).
    * cup/tbsp/tsp are kept as-is unless mapping to ml is explicitly
      desired — currently we convert them to ml.

    Returns
    -------
    (converted_quantity, base_unit_symbol)
    If unit is not convertible, returns (quantity, unit) unchanged.
    """
    canonical = normalize_unit(unit)

    if canonical in MASS_TO_G:
        return quantity * MASS_TO_G[canonical], "g"

    if canonical in VOLUME_TO_ML:
        return quantity * VOLUME_TO_ML[canonical], "ml"

    # Non-convertible (piece, can, bunch, pinch, …)
    return quantity, canonical or unit
