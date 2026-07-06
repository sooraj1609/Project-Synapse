import { useEffect, useState } from 'react'
import { api } from '../api.js'
import RiskBadge from './RiskBadge.jsx'
import PulseLine from './PulseLine.jsx'

const DOMAIN_LABELS = {
  mobility: 'Mobility',
  environment: 'Environment',
  health: 'Health',
  citizen_services: 'Citizen Services',
}

function DomainBar({ domain, score }) {
  const pct = Math.min(100, score)
  const color =
    score >= 85 ? 'bg-risk-critical' : score >= 65 ? 'bg-risk-atrisk' : score >= 50 ? 'bg-risk-warning' : score >= 30 ? 'bg-risk-improving' : 'bg-risk-stable'
  return (
    <div>
      <div className="flex justify-between text-sm mb-1.5">
        <span className="text-textPrimary">{DOMAIN_LABELS[domain] || domain}</span>
        <span className="font-mono text-textMuted">{score}</span>
      </div>
      <div className="h-2 bg-surfaceRaised rounded-full overflow-hidden">
        <div className={`h-full ${color} rounded-full transition-all`} style={{ width: `${pct}%` }} />
      </div>
    </div>
  )
}

function MetricRow({ metric }) {
  const delta = metric.value - metric.baseline
  const worse = delta > 0
  return (
    <div className="flex items-center justify-between py-2.5 border-b border-border last:border-0">
      <span className="text-textMuted text-sm">{metric.metric_name.replace(/_/g, ' ')}</span>
      <div className="flex items-center gap-3 font-mono text-sm">
        <span className="text-textPrimary">{metric.value}</span>
        <span className="text-textMuted text-xs">baseline {metric.baseline}</span>
        <span className={worse ? 'text-risk-atrisk' : 'text-risk-stable'}>
          {worse ? '↑' : '↓'} {Math.abs(delta).toFixed(1)}
        </span>
      </div>
    </div>
  )
}

export default function LocalityDetail({ localityId, onBack, onAskAssistant }) {
  const [profile, setProfile] = useState(null)
  const [error, setError] = useState(null)

  useEffect(() => {
    setProfile(null)
    api.getLocalityProfile(localityId).then(setProfile).catch((e) => setError(e.message))
  }, [localityId])

  if (error) return <div className="p-8 text-risk-critical text-sm">{error}</div>
  if (!profile) return <div className="p-8 text-textMuted text-sm">Loading locality profile…</div>

  const domainsByGroup = {}
  profile.metrics.forEach((m) => {
    domainsByGroup[m.domain] = domainsByGroup[m.domain] || []
    domainsByGroup[m.domain].push(m)
  })

  return (
    <div className="p-8 max-w-4xl mx-auto">
      <button onClick={onBack} className="text-textMuted text-sm hover:text-textPrimary mb-6 inline-flex items-center gap-1">
        ← Back to overview
      </button>

      <div className="flex items-start justify-between mb-8">
        <div>
          <h1 className="text-textPrimary text-2xl font-semibold">{profile.name}</h1>
          <p className="text-textMuted text-sm mt-1">Population {profile.population.toLocaleString()}</p>
        </div>
        <div className="text-right">
          <RiskBadge level={profile.risk_level} />
          <div className="font-mono text-3xl text-textPrimary mt-2">{profile.overall_risk_score}</div>
        </div>
      </div>

      <div className="bg-surface border border-border rounded-xl p-5 mb-6 flex items-center justify-between">
        <PulseLine score={profile.overall_risk_score} riskLevel={profile.risk_level} width={200} height={48} />
        <button
          onClick={() => onAskAssistant(localityId)}
          className="bg-ai/10 border border-ai/30 text-ai text-sm px-4 py-2 rounded-lg hover:bg-ai/20 transition-colors whitespace-nowrap"
        >
          Ask AI about this locality →
        </button>
      </div>

      <div className="bg-surface border border-border rounded-xl p-5 mb-6">
        <h2 className="text-textPrimary text-sm font-medium mb-4">Domain Risk Scores</h2>
        <div className="space-y-4">
          {Object.entries(profile.domain_scores).map(([domain, score]) => (
            <DomainBar key={domain} domain={domain} score={score} />
          ))}
        </div>
        <p className="text-textMuted text-[11px] mt-4 pt-3 border-t border-border">
          Weighted equally at 25% each. Overall score = weighted sum of domain scores.
        </p>
      </div>

      <div className="bg-surface border border-border rounded-xl p-5">
        <h2 className="text-textPrimary text-sm font-medium mb-2">Latest Metrics by Domain</h2>
        {Object.entries(domainsByGroup).map(([domain, rows]) => (
          <div key={domain} className="mt-4 first:mt-0">
            <h3 className="text-textMuted text-xs uppercase tracking-wide mb-1">{DOMAIN_LABELS[domain] || domain}</h3>
            {rows.map((m) => (
              <MetricRow key={m.metric_name} metric={m} />
            ))}
          </div>
        ))}
      </div>
    </div>
  )
}
