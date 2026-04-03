"""
routers/mods.py
---------------
API route handlers for mod data and regex generation.

Endpoints
---------
GET  /mods                  — mods grouped into families (?slot= ?q= filters)
GET  /mods/slots            — list of valid item slot identifiers
GET  /mods/tags             — list of valid tag identifiers
GET  /mods/{mod_id}         — single mod by ID
POST /mods/regex            — generate regex from a list of mod IDs
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query

from app.models.mod import Mod, ModFamily, RegexRequest, RegexResponse
from app.services.family_grouper import group_into_families
from app.services.mod_loader import (
    get_all_mods,
    get_all_slots,
    get_all_tags,
    get_deriver,
    get_mods_by_ids,
    get_mods_by_slot,
)

router = APIRouter(prefix="/mods", tags=["mods"])


@router.get("/slots", response_model=list[str])
def list_slots() -> list[str]:
    return get_all_slots()


@router.get("/tags", response_model=list[str])
def list_tags() -> list[str]:
    return get_all_tags()


@router.get("", response_model=list[ModFamily])
def list_mods(
    slot: str | None = Query(default=None, description="Filter by item slot"),
    q: str | None    = Query(default=None, description="Search mod names"),
) -> list[ModFamily]:
    """
    Return mods grouped into families, optionally filtered by slot and search.
    Each family contains mods of the same type across different tiers,
    sorted highest tier first. The frontend shows only the top tier by default.
    """
    mods = get_mods_by_slot(slot) if slot else get_all_mods()

    if q:
        q_lower = q.lower()
        mods = [m for m in mods if q_lower in m.name.lower()]

    return group_into_families(mods)


@router.get("/{mod_id}", response_model=Mod)
def get_mod(mod_id: str) -> Mod:
    results = get_mods_by_ids([mod_id])
    if not results:
        raise HTTPException(status_code=404, detail=f"Mod '{mod_id}' not found")
    return results[0]


@router.post("/regex", response_model=RegexResponse)
def generate_regex(request: RegexRequest) -> RegexResponse:
    """
    Generate a PoE stash-search regex from a list of selected mod IDs.
    Uses RegexDeriver to find the shortest unique token per mod.
    """
    if not request.mod_ids:
        raise HTTPException(status_code=422, detail="mod_ids must not be empty")

    mods = get_mods_by_ids(request.mod_ids)
    if not mods:
        raise HTTPException(
            status_code=404,
            detail="None of the provided mod_ids were found",
        )

    deriver = get_deriver()
    derived = [deriver.derive(mod) for mod in mods]
    regex, tokens = deriver.derive_multi(mods)
    has_non_unique = any(not d.is_unique for d in derived)

    return RegexResponse(
        regex=regex,
        mod_count=len(mods),
        tokens_used=tokens,
        has_non_unique=has_non_unique,
    )
