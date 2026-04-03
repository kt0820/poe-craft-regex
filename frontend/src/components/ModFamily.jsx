/**
 * ModFamily.jsx
 * -------------
 * Clicking the top-tier row:
 *   - If single tier: selects/deselects it
 *   - If multi-tier: expands the family to show ALL tiers (including T-top),
 *     and does NOT auto-select — user selects individual tiers after expanding
 *
 * Expanded state shows all tiers from highest to lowest, all individually selectable.
 */

import ModRow from './ModRow'

export default function ModFamily({ family, selectedIds, isExpanded, onToggleFamily, onToggleMod }) {
  const { family_key, mods } = family
  const topMod = mods[0]
  const hasMultiple = mods.length > 1

  const handleTopClick = () => {
    if (hasMultiple) {
      onToggleFamily(family_key)   // expand/collapse — don't select
    } else {
      onToggleMod(topMod.id)       // single tier — just select
    }
  }

  return (
    <div>
      {/* Top tier row — always visible */}
      <div
        className={`mod-row ${hasMultiple ? 'expandable' : ''} ${!isExpanded && selectedIds.has(topMod.id) ? 'selected' : ''}`}
        onClick={handleTopClick}
      >
        <div className="tier-badge">{topMod.tier}</div>
        <div className="mod-name">{topMod.name}</div>
        {hasMultiple && (
          <span className={`expand-arrow ${isExpanded ? 'open' : ''}`}>▶</span>
        )}
      </div>

      {/* ALL tiers (including top) shown when expanded */}
      {isExpanded && (
        <div className="tier-indent">
          {mods.map(mod => (
            <ModRow
              key={mod.id}
              mod={mod}
              isSelected={selectedIds.has(mod.id)}
              onToggle={onToggleMod}
            />
          ))}
        </div>
      )}
    </div>
  )
}
