from __future__ import annotations

from pydantic import BaseModel


class Mod(BaseModel):
    id: str
    name: str
    stat_text: str
    tag: str            # prefix | suffix | other
    tier: int
    slots: list[str]


class ModFamily(BaseModel):
    """A group of mods sharing the same stat type across different tiers."""
    family_key: str     # normalised stat text with numbers replaced by #
    tag: str
    mods: list[Mod]     # sorted highest tier first


class ModsData(BaseModel):
    version: str
    last_updated: str
    slots: list[str]
    tags: list[str]
    mods: list[Mod]


class RegexRequest(BaseModel):
    mod_ids: list[str]


class RegexResponse(BaseModel):
    regex: str
    mod_count: int
    tokens_used: list[str]
    has_non_unique: bool
