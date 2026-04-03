/**
 * App.jsx — Regex bar on top, mod list below.
 *
 *   Header
 *   ┌──────────────────────────────┐
 *   │  regex output  [Clear][Copy] │  ← RegexBar (top, always visible)
 *   │──────────────────────────────│
 *   │  [∞][HLM][BA]...             │  ← SlotFilter
 *   │  [ Search here...          ] │  ← SearchBar
 *   │──────────────────────────────│
 *   │  - Prefix -                  │
 *   │  [5] (71-85) to max Life [▶] │  ← collapsed family
 *   │      (56-70) to max Life     │  ← expanded tiers (when open)
 *   │  [3] (20-24)% Move Speed     │
 *   │  - Suffix -                  │
 *   │  ...                         │
 *   └──────────────────────────────┘
 */

import { useState } from 'react'
import Header      from './components/Header'
import RegexBar    from './components/RegexBar'
import SlotFilter  from './components/SlotFilter'
import SearchBar   from './components/SearchBar'
import ModList     from './components/ModList'
import { useMods } from './hooks/useMods'

export default function App() {
  const [selectedSlot, setSelectedSlot] = useState(null)

  const {
    groupedFamilies,
    selectedIds,
    isExpanded,
    regex,
    hasNonUnique,
    loading,
    error,
    copied,
    search,
    setSearch,
    toggleMod,
    toggleFamily,
    clearSelection,
    copyToClipboard,
  } = useMods(selectedSlot)

  return (
    <div className="min-h-screen flex flex-col bg-[#0d0b08]" style={{ maxWidth: '760px', margin: '0 auto' }}>
      <Header />

      {/* Regex bar — pinned below header, always visible */}
      <RegexBar
        regex={regex}
        selectedCount={selectedIds.size}
        hasNonUnique={hasNonUnique}
        copied={copied}
        onCopy={copyToClipboard}
        onClear={clearSelection}
      />

      <SlotFilter selectedSlot={selectedSlot} onSelectSlot={setSelectedSlot} />
      <SearchBar value={search} onChange={setSearch} />

      {/* Scrollable mod list */}
      <div className="flex-1 overflow-y-auto">
        <ModList
          groupedFamilies={groupedFamilies}
          selectedIds={selectedIds}
          isExpanded={isExpanded}
          onToggleMod={toggleMod}
          onToggleFamily={toggleFamily}
          loading={loading}
          error={error}
          selectedSlot={selectedSlot}
          search={search}
        />
      </div>
    </div>
  )
}
