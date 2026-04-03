/**
 * SearchBar.jsx
 * -------------
 * Real-time search input that filters the mod list.
 */

export default function SearchBar({ value, onChange }) {
  return (
    <div className="px-3 py-2 border-b border-[#1e1810]">
      <input
        type="text"
        className="search-bar"
        placeholder="Search mods..."
        value={value}
        onChange={e => onChange(e.target.value)}
        spellCheck={false}
      />
    </div>
  )
}
