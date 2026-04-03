/**
 * SlotTabs.jsx
 * ------------
 * Renders the row of item slot tabs at the top of the app.
 * The user clicks a tab to load mods for that slot.
 */

// Human-readable labels and display order for each slot
const SLOTS = [
  { id: 'helmet',         label: 'Helmet' },
  { id: 'body_armour',    label: 'Body' },
  { id: 'gloves',         label: 'Gloves' },
  { id: 'boots',          label: 'Boots' },
  { id: 'belt',           label: 'Belt' },
  { id: 'ring',           label: 'Ring' },
  { id: 'amulet',         label: 'Amulet' },
  { id: 'shield',         label: 'Shield' },
  { id: 'quiver',         label: 'Quiver' },
  { id: 'weapon_1h_melee',  label: '1H Melee' },
  { id: 'weapon_2h_melee',  label: '2H Melee' },
  { id: 'weapon_1h_ranged', label: '1H Ranged' },
  { id: 'weapon_2h_ranged', label: '2H Ranged' },
]

export default function SlotTabs({ selectedSlot, onSelectSlot }) {
  return (
    <div className="flex flex-wrap gap-1 p-3 border-b border-poe-border">
      {SLOTS.map(slot => (
        <button
          key={slot.id}
          className={`slot-tab ${selectedSlot === slot.id ? 'active' : ''}`}
          onClick={() => onSelectSlot(slot.id)}
        >
          {slot.label}
        </button>
      ))}
    </div>
  )
}
