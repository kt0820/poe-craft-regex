"""
family_grouper.py
-----------------
Groups mods into "families" — mods that share the same stat type but
differ only in their numeric values (i.e. different tiers of the same mod).

A family key is derived by replacing all numeric ranges in stat_text with
a placeholder '#', then normalising whitespace and lowercasing.

Example:
    "(71-85) to maximum Life"  →  "# to maximum life"
    "(56-70) to maximum Life"  →  "# to maximum life"   ← same family
    "(20-24)% increased Movement Speed" → "#% increased movement speed"

Within each family, mods are sorted tier descending (highest first).
The frontend shows only the highest tier by default and expands on click.
"""

from __future__ import annotations

import re
from collections import defaultdict

from app.models.mod import Mod, ModFamily


def make_family_key(stat_text: str) -> str:
    """Derive a family key by stripping all numbers from stat_text."""
    t = stat_text.replace('\u2013', '-').replace('\u2014', '-')
    # Remove parenthesised ranges like (71-85) or (0.3-0.5)
    t = re.sub(r'\(\d+(?:\.\d+)?-\d+(?:\.\d+)?\)', '#', t)
    # Remove standalone numbers (with optional leading + or -)
    t = re.sub(r'[+\-]?\d+(?:\.\d+)?\b', '#', t)
    # Collapse whitespace
    t = re.sub(r'\s+', ' ', t).strip().lower()
    return t


def group_into_families(mods: list[Mod]) -> list[ModFamily]:
    """
    Group a list of mods into families, sorted by tag order then family key.
    Within each family, mods are sorted by tier descending.
    """
    TAG_ORDER = ['prefix', 'suffix', 'other']

    buckets: dict[tuple[str, str], list[Mod]] = defaultdict(list)
    for mod in mods:
        key = (mod.tag, make_family_key(mod.stat_text))
        buckets[key].append(mod)

    # Sort within each family: highest tier first
    families: list[ModFamily] = []
    for (tag, key), members in buckets.items():
        members.sort(key=lambda m: m.tier, reverse=True)
        families.append(ModFamily(
            family_key=key,
            tag=tag,
            mods=members,
        ))

    # Sort families: by tag order, then by highest tier descending, then name
    tag_rank = {t: i for i, t in enumerate(TAG_ORDER)}
    families.sort(key=lambda f: (
        tag_rank.get(f.tag, 99),
        -f.mods[0].tier,
        f.mods[0].name,
    ))

    return families
