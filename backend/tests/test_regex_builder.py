"""
tests/test_regex_builder.py
---------------------------
Unit tests for the regex builder service and mod loader.

Run with:
    pytest
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from app.models.mod import Mod
from app.services.regex_builder import build_regex, POE_REGEX_LIMIT
from app.services.mod_loader import (
    get_all_mods,
    get_mods_by_slot,
    get_mods_by_ids,
    get_all_slots,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_mod(**kwargs) -> Mod:
    defaults = dict(
        id="test_mod",
        name="Test Mod",
        stat_text="Test stat",
        regex_token="test token",
        type="prefix",
        tier=1,
        tier_range={"min": 10, "max": 20},
        item_level_required=1,
        applies_to=["helmet"],
        category="life_and_mana",
        tags=["test"],
        unlock="Default",
    )
    defaults.update(kwargs)
    return Mod(**defaults)


# ---------------------------------------------------------------------------
# regex_builder — core behaviour
# ---------------------------------------------------------------------------

class TestBuildRegex:
    def test_empty_list_returns_empty_string(self):
        regex, tokens = build_regex([])
        assert regex == ""
        assert tokens == []

    def test_single_mod_uses_min_value(self):
        """Single mod should produce just its minimum value, no parentheses."""
        mod = make_mod(tier_range={"min": 16, "max": 20})
        regex, tokens = build_regex([mod])
        assert regex == "16"

    def test_different_tiers_produce_distinct_tokens(self):
        """Three tiers of fire resistance should each get their own min value."""
        mods = [
            make_mod(id="t1", tier_range={"min": 16, "max": 20}),
            make_mod(id="t2", tier_range={"min": 21, "max": 28}),
            make_mod(id="t3", tier_range={"min": 29, "max": 35}),
        ]
        regex, tokens = build_regex(mods)
        assert "16" in tokens
        assert "21" in tokens
        assert "29" in tokens
        assert regex == "(16|21|29)"

    def test_collision_falls_back_to_full_range(self):
        """
        If two mods share the same min value (unlikely but possible),
        fall back to the full range string to disambiguate.
        """
        mods = [
            make_mod(id="a", tier_range={"min": 10, "max": 20}),
            make_mod(id="b", tier_range={"min": 10, "max": 30}),
        ]
        regex, tokens = build_regex(mods)
        assert "10-20" in tokens
        assert "10-30" in tokens

    def test_metamod_uses_keyword_token(self):
        """Metamods have no tier_range — should use regex_token keyword."""
        mod = make_mod(
            id="meta",
            type="metamod",
            tier=None,
            tier_range=None,
            regex_token="prefixes cannot",
        )
        regex, tokens = build_regex([mod])
        assert regex == "prefixes cannot"

    def test_mixed_numeric_and_metamod(self):
        mods = [
            make_mod(id="a", tier_range={"min": 16, "max": 20}),
            make_mod(id="b", type="metamod", tier=None, tier_range=None,
                     regex_token="prefixes cannot"),
        ]
        regex, tokens = build_regex(mods)
        assert "16" in tokens
        assert "prefixes cannot" in tokens

    def test_added_flat_damage_uses_min_lo(self):
        """Flat added damage mods use the min_lo field."""
        mod = make_mod(
            id="flat",
            tier_range={"min_lo": 11, "min_hi": 12, "max_lo": 19, "max_hi": 23},
        )
        regex, tokens = build_regex([mod])
        assert regex == "11"

    def test_duplicate_tokens_deduplicated(self):
        """
        If two selected mods resolve to the same discriminating token
        (e.g. same mod selected twice), include the token only once.
        """
        mods = [
            make_mod(id="a", tier_range={"min": 16, "max": 20}),
            make_mod(id="b", tier_range={"min": 16, "max": 20}),
        ]
        regex, tokens = build_regex(mods)
        # Both mods have min=16 → collision → both become "16-20" → deduplicated to one
        assert len(tokens) == 1

    def test_regex_within_69_char_limit(self):
        """Assembled regex must never exceed PoE's 69 character limit."""
        mods = [make_mod(id=str(i), tier_range={"min": i * 10, "max": i * 10 + 9})
                for i in range(1, 20)]
        regex, _ = build_regex(mods)
        assert len(regex) <= POE_REGEX_LIMIT

    def test_single_mod_no_parentheses(self):
        """A single token should never be wrapped in parentheses."""
        mod = make_mod(tier_range={"min": 40, "max": 55})
        regex, _ = build_regex([mod])
        assert not regex.startswith("(")


# ---------------------------------------------------------------------------
# mod_loader tests
# ---------------------------------------------------------------------------

class TestModLoader:
    def test_loads_mods_successfully(self):
        mods = get_all_mods()
        assert len(mods) > 0

    def test_all_mods_have_required_fields(self):
        for mod in get_all_mods():
            assert mod.id
            assert mod.name
            assert mod.regex_token
            assert mod.type in ("prefix", "suffix", "metamod", "utility")
            assert isinstance(mod.applies_to, list)
            assert len(mod.applies_to) > 0

    def test_no_duplicate_ids(self):
        ids = [m.id for m in get_all_mods()]
        assert len(ids) == len(set(ids)), "Duplicate mod IDs found"

    def test_get_mods_by_slot_returns_subset(self):
        helmet_mods = get_mods_by_slot("helmet")
        assert len(helmet_mods) > 0
        for mod in helmet_mods:
            assert "helmet" in mod.applies_to

    def test_get_mods_by_slot_unknown_slot_returns_empty(self):
        result = get_mods_by_slot("banana")
        assert result == []

    def test_get_mods_by_ids_returns_correct_mods(self):
        all_mods = get_all_mods()
        sample_ids = [m.id for m in all_mods[:3]]
        result = get_mods_by_ids(sample_ids)
        assert [m.id for m in result] == sample_ids

    def test_get_mods_by_ids_skips_unknown_ids(self):
        result = get_mods_by_ids(["does_not_exist"])
        assert result == []

    def test_get_all_slots_returns_list(self):
        slots = get_all_slots()
        assert isinstance(slots, list)
        assert "helmet" in slots
        assert "ring" in slots
        assert "weapon_1h_melee" in slots

    def test_metamods_have_null_tier(self):
        metamods = [m for m in get_all_mods() if m.type == "metamod"]
        assert len(metamods) > 0
        for mod in metamods:
            assert mod.tier is None

    def test_fire_resistance_tiers_produce_unique_tokens(self):
        """
        The three fire resistance tiers should each produce a distinct
        discriminating token — the core requirement that prompted this redesign.
        """
        from app.services.mod_loader import get_mods_by_ids
        fire_ids = ["craft_fire_res_t1", "craft_fire_res_t2", "craft_fire_res_t3"]
        mods = get_mods_by_ids(fire_ids)
        assert len(mods) == 3, "All three fire resistance tiers must exist in dataset"
        regex, tokens = build_regex(mods)
        assert len(tokens) == 3, "Each tier must produce a unique token"
        assert len(set(tokens)) == 3, "No two tiers should share a token"
        assert regex == "(16|21|29)"
