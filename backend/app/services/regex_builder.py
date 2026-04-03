"""
regex_builder.py
----------------
Core service responsible for turning a list of selected mod IDs into a
valid PoE stash-search regex string.

PoE stash search rules:
  - Pipe  |  means OR
  - Parentheses group tokens
  - Case-insensitive
  - 69 CHARACTER LIMIT on the search string

Strategy: Minimum Discriminating Token
---------------------------------------
Rather than using a generic keyword like "fire resistance" (which would match
ALL fire resistance tiers), we extract the smallest substring that uniquely
identifies the specific tier selected.

For numeric mods we use the minimum value of the roll range:
  +(16-20)% to Fire Resistance  →  "16"
  +(21-28)% to Fire Resistance  →  "21"
  +(29-35)% to Fire Resistance  →  "29"

If two selected mods share the same min value (collision), we fall back
to the full range string "16-20" which is always unique.

For metamods and mods with no tier_range we use a short keyword token.

For added flat damage mods (min_lo/min_hi format) we use min_lo.

Finally we enforce the 69 char limit by progressively shortening tokens
if the assembled regex exceeds it.
"""

from __future__ import annotations
import re as _re

from app.models.mod import Mod

POE_REGEX_LIMIT = 69


def _numeric_token(mod: Mod) -> str | None:
    """
    Extract the minimum discriminating numeric value from a mod's tier_range.
    Returns None if the mod has no numeric range.
    """
    tr = mod.tier_range
    if tr is None:
        return None

    # Added flat damage format: {"min_lo": 11, "min_hi": 12, "max_lo": 19, ...}
    if tr.min_lo is not None:
        val = tr.min_lo
        return str(int(val)) if val == int(val) else str(val)

    # Standard format: {"min": 16, "max": 20}
    if tr.min is not None:
        val = tr.min
        return str(int(val)) if val == int(val) else str(val)

    return None


def _range_token(mod: Mod) -> str | None:
    """
    Return the full range string e.g. "16-20" as a fallback collision token.
    """
    tr = mod.tier_range
    if tr is None:
        return None

    if tr.min_lo is not None and tr.max_hi is not None:
        lo = int(tr.min_lo) if tr.min_lo == int(tr.min_lo) else tr.min_lo
        hi = int(tr.max_hi) if tr.max_hi == int(tr.max_hi) else tr.max_hi
        return f"{lo}-{hi}"

    if tr.min is not None and tr.max is not None:
        lo = int(tr.min) if tr.min == int(tr.min) else tr.min
        hi = int(tr.max) if tr.max == int(tr.max) else tr.max
        return f"{lo}-{hi}"

    return None


def _keyword_token(mod: Mod) -> str:
    """
    For mods with no numeric range, derive a short keyword from regex_token.
    Strips regex special chars and takes the first meaningful phrase.
    """
    raw = mod.regex_token.strip().lower()
    # Remove regex syntax like .* 
    raw = _re.sub(r'\.\*|\.\+|[\[\](){}^$\\]', '', raw)
    raw = raw.strip()
    # Truncate to first 20 chars at a word boundary
    if len(raw) <= 20:
        return raw
    cut = raw[:20].rsplit(' ', 1)[0]
    return cut or raw[:20]


def build_regex(selected_mods: list[Mod]) -> tuple[str, list[str]]:
    """
    Build a PoE-compatible regex string from a list of selected Mod objects.

    Returns
    -------
    regex : str
        The final regex string, ≤69 characters, ready to paste into PoE.
    tokens_used : list[str]
        The discriminating tokens combined into the regex.
    """
    if not selected_mods:
        return "", []

    # ── Step 1: assign each mod a candidate numeric token ────────────────────
    # { mod_id: candidate_token }
    candidates: dict[str, str] = {}
    for mod in selected_mods:
        tok = _numeric_token(mod)
        candidates[mod.id] = tok if tok is not None else ""

    # ── Step 2: detect collisions among numeric tokens ────────────────────────
    # Two mods collide if they share the same min value token.
    from collections import Counter
    token_counts = Counter(t for t in candidates.values() if t)
    colliding_values = {t for t, c in token_counts.items() if c > 1}

    # ── Step 3: resolve collisions with full range token ─────────────────────
    tokens: list[str] = []
    for mod in selected_mods:
        tok = candidates[mod.id]

        if not tok:
            # No numeric range — use keyword
            tokens.append(_keyword_token(mod))
        elif tok in colliding_values:
            # Collision — use full range string
            fallback = _range_token(mod)
            tokens.append(fallback if fallback else tok)
        else:
            tokens.append(tok)

    # ── Step 4: deduplicate while preserving order ────────────────────────────
    seen: set[str] = set()
    unique_tokens: list[str] = []
    for t in tokens:
        if t not in seen:
            seen.add(t)
            unique_tokens.append(t)

    if not unique_tokens:
        return "", []

    # ── Step 5: assemble and enforce 69-char limit ────────────────────────────
    def assemble(toks: list[str]) -> str:
        if len(toks) == 1:
            return toks[0]
        return "(" + "|".join(toks) + ")"

    regex = assemble(unique_tokens)

    # If within limit, we're done
    if len(regex) <= POE_REGEX_LIMIT:
        return regex, unique_tokens

    # Over limit — progressively drop the longest tokens until we fit.
    # This is a best-effort: we keep as many mods as possible.
    trimmed = list(unique_tokens)
    while len(assemble(trimmed)) > POE_REGEX_LIMIT and len(trimmed) > 1:
        # Remove the longest token first (least likely to be unique anyway)
        trimmed.sort(key=len, reverse=True)
        trimmed.pop(0)
        trimmed.sort(key=lambda t: unique_tokens.index(t))  # restore order

    regex = assemble(trimmed)
    return regex, trimmed
