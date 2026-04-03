"""
mod_loader.py
-------------
Loads the crafting bench mod dataset from disk and provides fast
in-memory lookups. The RegexDeriver is also initialised here once
at startup so uniqueness testing runs against the full corpus.
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

from app.models.mod import Mod, ModsData
from app.services.regex_deriver import RegexDeriver

DATA_PATH = Path(__file__).parent.parent.parent / "data" / "crafting_bench_mods.json"


@lru_cache(maxsize=1)
def load_mods() -> ModsData:
    """Load and parse the mod dataset. Cached after first call."""
    with DATA_PATH.open(encoding="utf-8") as f:
        raw = json.load(f)
    return ModsData(**raw)


@lru_cache(maxsize=1)
def get_deriver() -> RegexDeriver:
    """Initialise the RegexDeriver against the full corpus. Cached."""
    return RegexDeriver(get_all_mods())


def get_all_mods() -> list[Mod]:
    return load_mods().mods


def get_mods_by_slot(slot: str) -> list[Mod]:
    """Return all mods that apply to the given item slot."""
    return [m for m in get_all_mods() if slot in m.slots]


def get_mods_by_tag(tag: str) -> list[Mod]:
    """Return all mods with the given tag."""
    return [m for m in get_all_mods() if m.tag == tag]


def get_mods_by_ids(mod_ids: list[str]) -> list[Mod]:
    """Return mods matching the given list of IDs. Preserves request order."""
    lookup = {m.id: m for m in get_all_mods()}
    return [lookup[mid] for mid in mod_ids if mid in lookup]


def get_all_slots() -> list[str]:
    return load_mods().slots


def get_all_tags() -> list[str]:
    return load_mods().tags
