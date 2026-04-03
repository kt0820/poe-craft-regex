export default function Header() {
  return (
    <header className="border-b border-[#1e1810] bg-[#0a0804]">
      <div className="px-4 py-3 flex items-center gap-3">
        <span className="text-xl opacity-50 text-[#c8a850]">⚒</span>
        <div>
          <h1 className="font-heading text-[#c8a850] text-base tracking-wider leading-none">
            PoE Craft Regex
          </h1>
          <p className="text-[#3a3020] text-xs mt-0.5 tracking-wide font-body">
            Crafting Bench · Stash Search Builder
          </p>
        </div>
      </div>
    </header>
  )
}
