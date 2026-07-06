import { useEffect, useState } from 'react'
import { api } from '../api.js'
import LocalityCard from './LocalityCard.jsx'
import RiskBadge from './RiskBadge.jsx'

function KpiCard({ label, value, mono = true }) {
  return (
    <div className="bg-surface border border-border rounded-xl px-5 py-4">
      <div className="text-textMuted text-xs uppercase tracking-wide mb-2">{label}</div>
      <div className={`text-2xl text-textPrimary ${mono ? 'font-mono' : 'font-medium'}`}>{value}</div>
    </div>
  )
}

export default function Dashboard({ onSelectLocality }) {
  const [data, setData] = useState(null)
  const [error, setError] = useState(null)

  useEffect(() => {
    api.getDashboardSummary().then(setData).catch((e) => setError(e.message))
  }, [])

  if (error) {
    return (
      <div className="p-8 text-risk-critical text-sm">
        Couldn't reach the backend at the configured API URL. Is it running? ({error})
      </div>
    )
  }
  if (!data) {
    return <div className="p-8 text-textMuted text-sm">Loading community overview…</div>
  }

  return (
    <div className="p-8 max-w-6xl mx-auto">
      <header className="mb-8">
        <h1 className="text-textPrimary text-xl font-semibold">Community Overview</h1>
        <p className="text-textMuted text-sm mt-1">Hyderabad — live status across all tracked localities</p>
      </header>

      {/* KPI row */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        <KpiCard label="Community Health Score" value={data.kpis.community_health_score} />
        <KpiCard label="Active Alerts" value={data.kpis.active_alerts} />
        <KpiCard label="High-Risk Localities" value={data.kpis.high_risk_localities} />
        <div className="bg-surface border border-border rounded-xl px-5 py-4">
          <div className="text-textMuted text-xs uppercase tracking-wide mb-2">Community Pulse</div>
          <RiskBadge level={data.kpis.community_pulse} />
        </div>
      </div>

      {/* AI daily summary */}
      <div className="bg-surfaceRaised border border-ai/20 rounded-xl px-5 py-4 mb-8 flex gap-3">
        <div className="w-1.5 h-1.5 rounded-full bg-ai mt-1.5 shrink-0" aria-hidden="true" />
        <div>
          <div className="text-ai text-xs font-medium uppercase tracking-wide mb-1">AI Daily Summary</div>
          <p className="text-textPrimary text-sm leading-relaxed">{data.ai_daily_summary}</p>
        </div>
      </div>

      {/* Locality grid */}
      <h2 className="text-textPrimary text-sm font-medium mb-4">Localities</h2>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {data.localities
          .slice()
          .sort((a, b) => b.overall_risk_score - a.overall_risk_score)
          .map((loc) => (
            <LocalityCard key={loc.locality_id} locality={loc} onSelect={onSelectLocality} />
          ))}
      </div>
    </div>
  )
}
