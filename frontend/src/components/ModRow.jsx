/**
 * ModRow.jsx
 * ----------
 * A single mod row — no checkbox, selection shown by highlight only.
 * Used for lower tiers within an expanded family.
 */

export default function ModRow({ mod, isSelected, onToggle }) {
  return (
    <div
      className={`mod-row ${isSelected ? 'selected' : ''}`}
      onClick={() => onToggle(mod.id)}
    >
      <div className="tier-badge">{mod.tier}</div>
      <div className="mod-name">{mod.name}</div>
    </div>
  )
}
