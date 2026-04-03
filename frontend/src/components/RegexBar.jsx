/**
 * RegexBar.jsx
 * ------------
 * Sticky bottom bar showing the live regex output, copy button, and clear button.
 * Always visible regardless of scroll position.
 */

export default function RegexBar({ regex, selectedCount, copied, hasNonUnique, onCopy, onClear }) {
  return (
    <div className="regex-bar">
      {/* Regex text or placeholder */}
      {regex
        ? <span className="regex-text">{regex}</span>
        : <span className="regex-placeholder">
            {selectedCount === 0
              ? 'Select mods to generate a regex...'
              : 'Generating...'}
          </span>
      }

      {/* Non-unique warning */}
      {hasNonUnique && regex && (
        <span className="non-unique-warn" title="Some tokens may match similar mods">
          ⚠ broad match
        </span>
      )}

      {/* Selected count */}
      {selectedCount > 0 && (
        <span className="text-xs text-[#5a5040] shrink-0 font-mono">
          {selectedCount} mod{selectedCount !== 1 ? 's' : ''}
        </span>
      )}

      {/* Clear */}
      {selectedCount > 0 && (
        <button className="clear-btn" onClick={onClear}>
          Clear
        </button>
      )}

      {/* Copy */}
      <button
        className={`copy-btn ${copied ? 'copied' : ''}`}
        onClick={onCopy}
        disabled={!regex}
      >
        {copied ? '✓ Copied' : 'Copy'}
      </button>
    </div>
  )
}
