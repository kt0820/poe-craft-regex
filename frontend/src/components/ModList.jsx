import ModFamilyRow from './ModFamily'
import { TAG_LABELS, TAG_ORDER } from '../hooks/useMods'

function EmptyState({ selectedSlot, search }) {
  if (!selectedSlot && !search) {
    return (
      <div className="flex flex-col items-center justify-center py-20 text-center">
        <div className="text-5xl mb-4 opacity-20">⚒</div>
        <p className="font-heading text-xs tracking-widest uppercase text-[#3a3020]">
          Select a slot or search to begin
        </p>
      </div>
    )
  }
  return (
    <div className="flex items-center justify-center py-16">
      <p className="text-sm text-[#4a4030] italic">No mods found</p>
    </div>
  )
}

export default function ModList({
  groupedFamilies, selectedIds, isExpanded,
  onToggleMod, onToggleFamily,
  loading, error, selectedSlot, search,
}) {
  if (loading) return (
    <div className="flex items-center justify-center py-16">
      <span className="font-heading text-xs tracking-widest uppercase text-[#4a4030] animate-pulse">Loading...</span>
    </div>
  )

  if (error) return (
    <div className="flex flex-col items-center justify-center py-16 px-6 text-center gap-2">
      <p className="text-red-500 text-sm">Failed to load mods</p>
      <p className="text-[#4a4030] text-xs">{error}</p>
      <p className="text-[#3a3020] text-xs">Is the backend running on port 8000?</p>
    </div>
  )

  const tags = TAG_ORDER.filter(tag => groupedFamilies[tag])
  if (tags.length === 0) return <EmptyState selectedSlot={selectedSlot} search={search} />

  return (
    <div>
      {tags.map(tag => (
        <div key={tag}>
          <div className="section-header">{TAG_LABELS[tag]}</div>
          <hr className="poe-divider" />
          {groupedFamilies[tag].map(family => (
            <ModFamilyRow
              key={family.family_key}
              family={family}
              selectedIds={selectedIds}
              isExpanded={isExpanded(family.family_key)}
              onToggleFamily={onToggleFamily}
              onToggleMod={onToggleMod}
            />
          ))}
        </div>
      ))}
    </div>
  )
}
