/**
 * SlotFilter.jsx
 * --------------
 * Slot filter buttons using local PNG/SVG assets from /public/icons/.
 *
 * To add your icons:
 *   1. Put your image files in frontend/public/icons/
 *   2. Name them to match the slot id, e.g. helmet.png, body_armour.png
 *   3. The src is already wired — just drop the files in and they'll show up
 *
 * Supported formats: .png, .svg (just change the extension in ICON_EXT below)
 */

const ICON_EXT = '.png'   // change to '.svg' if you use SVGs
const ICON_PATH = '/icons' // relative to frontend/public/

const SLOTS = [
  { id: null,               label: '∞',  title: 'All slots',   icon: false },
  { id: 'helmet',           title: 'Helmet' },
  { id: 'body_armour',      title: 'Body Armour' },
  { id: 'gloves',           title: 'Gloves' },
  { id: 'boots',            title: 'Boots' },
  { id: 'belt',             title: 'Belt' },
  { id: 'shield',           title: 'Shield' },
  { id: 'ring',             title: 'Ring' },
  { id: 'amulet',           title: 'Amulet' },
  { id: 'quiver',           title: 'Quiver' },
  { id: 'flask',            title: 'Flask' },
  { id: 'weapon_1h_melee',  title: '1H Melee',  badge: '1H' },
  { id: 'weapon_2h_melee',  title: '2H Melee',  badge: '2H' },
  { id: 'weapon_1h_ranged', title: '1H Ranged',  badge: '1HR' },
  { id: 'weapon_2h_ranged', title: '2H Ranged',  badge: '2HR' },
]

function SlotIcon({ slot, isActive }) {
  // ∞ All button
  if (slot.icon === false) {
    return <span className="all-label">∞</span>
  }

  const src = `${ICON_PATH}/${slot.id}${ICON_EXT}`

  return (
    <div className="relative flex items-center justify-center w-full h-full">
      <img
        src={src}
        alt={slot.title}
        width={22}
        height={22}
        className="slot-icon-img"
        style={{ opacity: isActive ? 1 : 0.5 }}
        onError={e => {
          // If image missing, show short text fallback
          e.target.style.display = 'none'
          e.target.nextSibling.style.display = 'flex'
        }}
      />
      {/* Text fallback — hidden by default, shown if img 404s */}
      <span
        className="slot-icon-fallback"
        style={{ display: 'none' }}
      >
        {slot.badge || slot.title.slice(0, 3).toUpperCase()}
      </span>
      {/* 1H / 2H badge for weapon slots */}
      {slot.badge && (
        <span className="slot-badge">{slot.badge}</span>
      )}
    </div>
  )
}

export default function SlotFilter({ selectedSlot, onSelectSlot }) {
  return (
    <div className="flex flex-wrap gap-1 px-3 py-2 border-b border-[#1e1810] bg-[#0a0804]">
      {SLOTS.map(slot => {
        const isActive = selectedSlot === slot.id
        return (
          <button
            key={slot.id ?? 'all'}
            className={`slot-btn ${isActive ? 'active' : ''}`}
            onClick={() => onSelectSlot(slot.id)}
            title={slot.title}
          >
            <SlotIcon slot={slot} isActive={isActive} />
          </button>
        )
      })}
    </div>
  )
}
