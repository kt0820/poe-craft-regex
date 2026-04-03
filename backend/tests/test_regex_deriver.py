"""
tests/test_regex_deriver.py
---------------------------
Validates that every mod in the dataset produces a regex token that:
  1. TRUE POSITIVE  — matches the mod's own stat_text
  2. TRUE NEGATIVE  — does not match any other mod with a DIFFERENT stat_text

Mods sharing identical stat_text (same mod, different slot groups) are
treated as the same logical mod — matching all of them is correct behaviour.

Run with:
    pytest tests/test_regex_deriver.py -v
    pytest tests/test_regex_deriver.py -v --tb=no -q   (summary only)
"""

import re
import sys
import json
from pathlib import Path
from collections import defaultdict

import pytest

# Ensure backend/ is on path
sys.path.insert(0, str(Path(__file__).parent.parent))

# ---------------------------------------------------------------------------
# Load data and build deriver (without pydantic — load raw JSON)
# ---------------------------------------------------------------------------

DATA_PATH = Path(__file__).parent.parent / "data" / "crafting_bench_mods.json"


def load_raw_mods():
    with DATA_PATH.open(encoding="utf-8") as f:
        return json.load(f)["mods"]


class SimpleMod:
    """Minimal mod object for testing without Pydantic."""
    def __init__(self, data):
        self.id = data["id"]
        self.stat_text = data["stat_text"]
        self.name = data["name"]
        self.tag = data["tag"]
        self.tier = data["tier"]
        self.slots = data["slots"]


# ---------------------------------------------------------------------------
# Build corpus and deriver once at module level
# ---------------------------------------------------------------------------

_raw = load_raw_mods()
ALL_MODS = [SimpleMod(m) for m in _raw]

# Group mods by stat_text — mods sharing stat_text are the same logical mod
STAT_TEXT_GROUPS: dict[str, list[SimpleMod]] = defaultdict(list)
for mod in ALL_MODS:
    STAT_TEXT_GROUPS[mod.stat_text].append(mod)

# All unique stat texts in the corpus (for true-negative testing)
ALL_STAT_TEXTS = list(STAT_TEXT_GROUPS.keys())


def get_deriver():
    """Import and initialise the deriver lazily."""
    from app.services.regex_deriver import RegexDeriver
    return RegexDeriver(ALL_MODS)


DERIVER = get_deriver()


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def check_token(token: str, own_stat_text: str) -> tuple[bool, bool, list[str]]:
    """
    Returns (true_positive, true_negative, false_positive_texts).

    true_positive  : token matches own_stat_text
    true_negative  : token matches NO other stat_text
    false_positives: list of stat_texts incorrectly matched
    """
    try:
        rx = re.compile(token, re.IGNORECASE)
    except re.error:
        return False, False, [f"INVALID REGEX: {token}"]

    true_positive = False
    false_positives = []

    for stat_text in ALL_STAT_TEXTS:
        # Check against each line of the stat_text
        lines = [l.strip() for l in stat_text.split("\n") if l.strip()]
        matched = any(rx.search(line) for line in lines)

        if stat_text == own_stat_text:
            true_positive = matched
        elif matched:
            false_positives.append(stat_text)

    true_negative = len(false_positives) == 0
    return true_positive, true_negative, false_positives


# ---------------------------------------------------------------------------
# Generate one test case per UNIQUE stat_text (not per mod entry)
# ---------------------------------------------------------------------------

def unique_mods():
    """Yield one representative mod per unique stat_text."""
    for stat_text, mods in STAT_TEXT_GROUPS.items():
        yield mods[0]   # first entry represents the whole group


UNIQUE_MODS = list(unique_mods())


# ---------------------------------------------------------------------------
# Parametrized tests
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("mod", UNIQUE_MODS, ids=lambda m: m.id)
def test_token_true_positive(mod):
    """Token must match the mod's own stat_text."""
    result = DERIVER.derive(mod)
    tp, _, _ = check_token(result.token, mod.stat_text)
    assert tp, (
        f"\nMOD : {mod.stat_text!r}\n"
        f"TOKEN: {result.token!r}\n"
        f"ERROR: Token does not match its own stat_text"
    )


@pytest.mark.parametrize("mod", UNIQUE_MODS, ids=lambda m: m.id)
def test_token_true_negative(mod):
    """Token must not match any other mod's stat_text."""
    result = DERIVER.derive(mod)
    _, tn, false_positives = check_token(result.token, mod.stat_text)
    assert tn, (
        f"\nMOD  : {mod.stat_text!r}\n"
        f"TOKEN: {result.token!r}\n"
        f"FALSE POSITIVES ({len(false_positives)}):\n"
        + "\n".join(f"  - {fp!r}" for fp in false_positives[:5])
    )


# ---------------------------------------------------------------------------
# Summary report (run standalone for a full breakdown)
# ---------------------------------------------------------------------------

def run_report():
    """
    Print a full pass/fail report without pytest.
    Usage: python tests/test_regex_deriver.py
    """
    passed = []
    tp_failures = []
    tn_failures = []

    for mod in UNIQUE_MODS:
        result = DERIVER.derive(mod)
        tp, tn, fps = check_token(result.token, mod.stat_text)

        entry = {
            "id": mod.id,
            "stat_text": mod.stat_text,
            "token": result.token,
            "is_unique_derived": result.is_unique,
            "tp": tp,
            "tn": tn,
            "false_positives": fps,
        }

        if tp and tn:
            passed.append(entry)
        elif not tp:
            tp_failures.append(entry)
        else:
            tn_failures.append(entry)

    total = len(UNIQUE_MODS)
    print(f"\n{'='*60}")
    print(f"REGEX DERIVER TEST REPORT")
    print(f"{'='*60}")
    print(f"Total unique mods : {total}")
    print(f"PASS              : {len(passed)} ({100*len(passed)//total}%)")
    print(f"FAIL (no match)   : {len(tp_failures)}")
    print(f"FAIL (collision)  : {len(tn_failures)}")
    print(f"{'='*60}")

    if tp_failures:
        print(f"\n── TOKEN DOESN'T MATCH OWN STAT ({len(tp_failures)}) ──")
        for e in tp_failures:
            print(f"\n  MOD  : {e['stat_text']!r}")
            print(f"  TOKEN: {e['token']!r}")

    if tn_failures:
        print(f"\n── TOKEN MATCHES OTHER MODS (collisions) ({len(tn_failures)}) ──")
        for e in tn_failures:
            print(f"\n  MOD  : {e['stat_text']!r}")
            print(f"  TOKEN: {e['token']!r}")
            for fp in e["false_positives"][:3]:
                print(f"    ✗ {fp!r}")
            if len(e["false_positives"]) > 3:
                print(f"    ... and {len(e['false_positives'])-3} more")

    print(f"\n{'='*60}\n")
    return len(tp_failures) + len(tn_failures)


if __name__ == "__main__":
    failures = run_report()
    sys.exit(1 if failures else 0)
