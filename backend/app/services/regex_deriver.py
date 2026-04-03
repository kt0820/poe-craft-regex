"""
regex_deriver.py  v2
--------------------
Derives the shortest unique PoE stash-search regex token for each mod
algorithmically from its stat_text.

KEY INSIGHT (discovered from testing):
  PoE stash search matches each TOOLTIP LINE independently.
  The .* operator works WITHIN a single line only.
  Therefore all tokens must match on exactly ONE line of the mod's stat_text.
  Cross-line tokens (range from line 1, keyword from line 2) are INVALID.

Strategy — tried in order for EACH LINE of the mod:
  1. Range alone — if the numeric range on this line is globally unique
  2. Range + growing keyword (rightward on SAME line) until unique
  3. Range + growing keyword (leftward, i.e. keyword before range on SAME line)
  4. Substring search — growing substrings of this line until unique
  5. Last resort — extend keyword past 69-char limit (for armour/evasion edge cases)

For multi-line mods: each line is tried independently; first success wins.
Lines are scored first so the most discriminating line is tried first.

Uniqueness is always tested against the full corpus, matching line by line.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

POE_REGEX_LIMIT = 69


@dataclass
class DerivedToken:
    token: str
    is_unique: bool
    source_line: str = ""   # which line of stat_text the token was derived from


class RegexDeriver:
    def __init__(self, all_mods: list) -> None:
        # Build corpus: stat_text → list of lowercase lines
        # Deduplicate by stat_text so identical mods don't inflate match counts
        seen: set[str] = set()
        self._corpus: list[list[str]] = []
        self._corpus_texts: list[str] = []
        for mod in all_mods:
            if mod.stat_text not in seen:
                seen.add(mod.stat_text)
                lines = [l.strip().lower() for l in mod.stat_text.split('\n') if l.strip()]
                self._corpus.append(lines)
                self._corpus_texts.append(mod.stat_text)

    # ── Public API ──────────────────────────────────────────────────────────

    def derive(self, mod) -> DerivedToken:
        lines = [l.strip() for l in mod.stat_text.split('\n') if l.strip()]
        
        # Score lines: prefer lines whose range appears in fewer mods
        scored = sorted(lines, key=lambda l: self._line_score(l))

        for line in scored:
            result = self._derive_from_line(line)
            if result:
                return DerivedToken(token=result, is_unique=True, source_line=line)

        # Nothing unique found — return best-effort from first line
        best = self._best_effort(scored[0])
        return DerivedToken(token=best, is_unique=False, source_line=scored[0])

    def derive_multi(self, mods: list) -> tuple[str, list[str]]:
        """Derive tokens for multiple mods and assemble a PoE regex."""
        if not mods:
            return "", []
        tokens = [self.derive(mod).token for mod in mods]
        # Deduplicate preserving order
        seen: set[str] = set()
        unique: list[str] = []
        for t in tokens:
            if t not in seen:
                seen.add(t)
                unique.append(t)
        regex = self._assemble(unique)
        # Trim to fit limit if necessary
        while len(regex) > POE_REGEX_LIMIT and len(unique) > 1:
            unique.remove(max(unique, key=len))
            regex = self._assemble(unique)
        return regex, unique

    # ── Internal ────────────────────────────────────────────────────────────

    @staticmethod
    def _assemble(tokens: list[str]) -> str:
        if not tokens: return ""
        if len(tokens) == 1: return tokens[0]
        return "(" + "|".join(tokens) + ")"

    def _count_linewise(self, pattern: str) -> int:
        """Count how many unique stat_texts match pattern on any single line."""
        try:
            rx = re.compile(pattern, re.IGNORECASE)
        except re.error:
            return 999
        return sum(1 for lines in self._corpus if any(rx.search(l) for l in lines))

    def _is_unique(self, pattern: str) -> bool:
        return self._count_linewise(pattern) == 1

    def _line_score(self, line: str) -> int:
        """Lower score = more discriminating = try this line first."""
        m = re.search(r'\d+(?:\.\d+)?-\d+(?:\.\d+)?', line)
        if m:
            return self._count_linewise(re.escape(m.group(0)))
        return 999

    def _extract_range(self, line: str) -> str | None:
        """Extract first numeric range from line."""
        m = re.search(r'(\d+(?:\.\d+)?)-(\d+(?:\.\d+)?)', line)
        return m.group(0) if m else None

    def _derive_from_line(self, line: str) -> str | None:
        """
        Try all strategies on a single line. Returns unique token or None.
        All patterns generated here are guaranteed to match on this line.
        """
        line_l = line.lower()
        range_str = self._extract_range(line_l)

        # ── Strategy 1: range alone ─────────────────────────────────────────
        if range_str and self._is_unique(re.escape(range_str)):
            return range_str

        # ── Strategy 2: range + keyword growing rightward ───────────────────
        if range_str:
            token = self._range_plus_keyword_right(range_str, line_l)
            if token:
                return token

        # ── Strategy 3: keyword + range (keyword before range on same line) ─
        if range_str:
            token = self._keyword_plus_range_left(range_str, line_l)
            if token:
                return token

        # ── Strategy 4: pure substring search (no range anchor) ─────────────
        token = self._pure_substring(line_l)
        if token:
            return token

        # ── Strategy 5: range + keyword past the 69-char limit ──────────────
        if range_str:
            token = self._range_plus_keyword_overlimit(range_str, line_l)
            if token:
                return token

        return None

    def _range_plus_keyword_right(self, range_str: str, line: str) -> str | None:
        """
        Try range + growing keyword to the RIGHT of the range on the same line.
        Fragments are re.escape'd so special chars are treated as literals.
        """
        m = re.search(re.escape(range_str), line)
        if not m:
            return None
        after = line[m.end():]

        for length in range(2, len(after) + 1):
            for start in range(len(after) - length + 1):
                frag = after[start:start + length].strip()
                if not frag or frag.isspace():
                    continue
                # Skip fragments that are purely numeric/punctuation
                if re.match(r'^[\d\s\.\-\+%\(\)]+$', frag):
                    continue
                pattern = f"{re.escape(range_str)}.*{re.escape(frag)}"
                if len(pattern) > POE_REGEX_LIMIT:
                    continue
                if self._is_unique(pattern):
                    # Verify this pattern actually matches this line
                    if re.search(pattern, line, re.IGNORECASE):
                        return pattern   # return the escaped pattern as the token
        return None

    def _keyword_plus_range_left(self, range_str: str, line: str) -> str | None:
        """
        Try keyword to the LEFT of the range + range on the same line.
        """
        m = re.search(re.escape(range_str), line)
        if not m:
            return None
        before = line[:m.start()]

        for length in range(2, len(before) + 1):
            for start in range(len(before) - length + 1):
                frag = before[start:start + length].strip()
                if not frag or frag.isspace():
                    continue
                if re.match(r'^[\d\s\.\-\+%\(\)]+$', frag):
                    continue
                pattern = f"{re.escape(frag)}.*{re.escape(range_str)}"
                if len(pattern) > POE_REGEX_LIMIT:
                    continue
                if self._is_unique(pattern):
                    if re.search(pattern, line, re.IGNORECASE):
                        return pattern
        return None

    def _pure_substring(self, line: str) -> str | None:
        """
        Find the shortest substring of this line that is globally unique.
        Returns the re.escape'd pattern so special chars are treated literally.
        """
        for length in range(3, len(line) + 1):
            for start in range(len(line) - length + 1):
                frag = line[start:start + length].strip()
                if not frag:
                    continue
                if re.match(r'^[\d\s\(\)\.\-\+%]+$', frag):
                    continue
                pattern = re.escape(frag)
                if len(pattern) > POE_REGEX_LIMIT:
                    continue
                if self._is_unique(pattern):
                    return pattern
        return None

    def _range_plus_keyword_overlimit(self, range_str: str, line: str) -> str | None:
        """
        Last resort: grow keyword past 69-char limit.
        """
        m = re.search(re.escape(range_str), line)
        if not m:
            return None
        after = line[m.end():]

        for length in range(2, len(after) + 1):
            for start in range(len(after) - length + 1):
                frag = after[start:start + length].strip()
                if not frag or re.match(r'^[\d\s\.\-\+%\(\)]+$', frag):
                    continue
                pattern = f"{re.escape(range_str)}.*{re.escape(frag)}"
                if self._is_unique(pattern):
                    if re.search(pattern, line, re.IGNORECASE):
                        return pattern
        return None

    def _best_effort(self, line: str) -> str:
        """Return a best-effort token when nothing unique was found."""
        line_l = line.lower()
        range_str = self._extract_range(line_l)
        if range_str:
            m = re.search(re.escape(range_str), line_l)
            if m:
                after = line_l[m.end():]
                words = [w for w in re.findall(r'[a-z]+', after) if len(w) >= 2]
                if words:
                    return f"{re.escape(range_str)}.*{re.escape(words[0][:4])}"
            return re.escape(range_str)
        words = re.findall(r'[a-z]+', line_l)
        return re.escape(' '.join(words[:2])[:20]) if words else re.escape(line_l[:10])
