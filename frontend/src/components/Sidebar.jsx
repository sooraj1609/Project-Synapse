const NAV_ITEMS = [
  { id: 'overview', label: 'Overview' },
  { id: 'assistant', label: 'Decision Intelligence' },
]

export default function Sidebar({ active, onNavigate }) {
  return (
    <aside className="w-56 shrink-0 border-r border-border bg-surface h-screen sticky top-0 flex flex-col">
      <div className="px-5 py-6 border-b border-border">
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 rounded-full bg-ai animate-pulse" aria-hidden="true" />
          <span className="text-textPrimary font-semibold text-sm tracking-tight">PROJECT SYNAPSE</span>
        </div>
        <p className="text-textMuted text-[11px] mt-1">The Living Intelligence Layer</p>
      </div>

      <nav className="flex-1 px-3 py-4 space-y-1">
        {NAV_ITEMS.map((item) => (
          <button
            key={item.id}
            onClick={() => onNavigate(item.id)}
            className={`w-full text-left px-3 py-2 rounded-lg text-sm transition-colors ${
              active === item.id
                ? 'bg-ai/10 text-ai border border-ai/20'
                : 'text-textMuted hover:text-textPrimary hover:bg-surfaceRaised border border-transparent'
            }`}
          >
            {item.label}
          </button>
        ))}
      </nav>

      <div className="px-5 py-4 border-t border-border text-[10px] text-textMuted font-mono">
        Hyderabad · 5 localities · 4 domains
      </div>
    </aside>
  )
}
