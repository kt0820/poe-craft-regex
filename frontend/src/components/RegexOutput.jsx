/**
 * RegexOutput.jsx
 * ---------------
 * Displays the generated regex string and provides a copy-to-clipboard button.
 * Also shows a summary of how many mods are selected.
 */

export default function RegexOutput({ regex, modCount, selectedCount, copied, onCopy, onClear }) {
  return (
    <div className="flex flex-col gap-4">

      {/* Header */}
      <div>
        <h2 className="font-heading text-xs tracking-widest uppercase text-poe-gold opacity-80 mb-1">
          Regex Output
        </h2>
        <hr className="poe-divider" />
      </div>

      {/* Regex display box */}
      <div className="regex-output">
        {regex
          ? regex
          : <span className="text-poe-text-dim italic text-sm">
              Select mods to generate a regex...
            </span>
        }
      </div>

      {/* Stats */}
      <div className="text-xs text-poe-text-dim font-body">
        {selectedCount > 0
          ? <>{selectedCount} mod{selectedCount !== 1 ? 's' : ''} selected</>
          : <span className="opacity-50">No mods selected</span>
        }
      </div>

      {/* Actions */}
      <div className="flex gap-2">
        <button
          className={`copy-btn flex-1 ${copied ? 'copied' : ''}`}
          onClick={onCopy}
          disabled={!regex}
        >
          {copied ? '✓ Copied' : 'Copy to Clipboard'}
        </button>
        {selectedCount > 0 && (
          <button className="clear-btn" onClick={onClear}>
            Clear
          </button>
        )}
      </div>

      {/* Usage hint */}
      {regex && (
        <p className="text-xs text-poe-text-dim leading-relaxed border-t border-poe-border pt-3 mt-1">
          Paste this into your PoE stash search box to highlight matching items.
        </p>
      )}
    </div>
  )
}
