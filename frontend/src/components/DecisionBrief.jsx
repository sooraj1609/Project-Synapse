import RiskBadge from './RiskBadge.jsx'

export default function DecisionBrief({ brief }) {
  if (brief.error) return <div className="text-risk-critical text-sm">{brief.error}</div>

  return (
    <div className="bg-surface border border-border rounded-xl overflow-hidden">
      <div className="px-5 py-4 border-b border-border flex items-center justify-between">
        <div>
          <div className="text-textMuted text-xs uppercase tracking-wide mb-1">Decision Brief</div>
          <h3 className="text-textPrimary font-medium">{brief.locality}</h3>
        </div>
        <div className="text-right">
          <RiskBadge level={brief.risk_level} />
          <div className="font-mono text-xl text-textPrimary mt-1">{brief.overall_risk_score}</div>
        </div>
      </div>

      <div className="px-5 py-4 border-b border-border">
        <p className="text-textPrimary text-sm leading-relaxed">{brief.summary}</p>
      </div>

      <div className="px-5 py-4 border-b border-border">
        <h4 className="text-textMuted text-xs uppercase tracking-wide mb-2">Contributing Factors</h4>
        <ul className="space-y-1">
          {brief.contributing_factors.map((f, i) => (
            <li key={i} className="text-textPrimary text-sm flex gap-2">
              <span className="text-risk-atrisk" aria-hidden="true">•</span>{f}
            </li>
          ))}
        </ul>
      </div>

      <div className="px-5 py-4 border-b border-border">
        <h4 className="text-textMuted text-xs uppercase tracking-wide mb-2">Evidence</h4>
        <div className="grid grid-cols-2 gap-2">
          {brief.evidence.map((e, i) => (
            <div key={i} className="bg-surfaceRaised rounded-lg px-3 py-2 font-mono text-xs">
              <div className="text-textMuted">{e.metric_name.replace(/_/g, ' ')}</div>
              <div className="text-textPrimary mt-0.5">
                {e.value} <span className="text-textMuted">/ baseline {e.baseline}</span>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="px-5 py-4 border-b border-border">
        <h4 className="text-textMuted text-xs uppercase tracking-wide mb-2">Recommended Actions</h4>
        <ol className="space-y-2">
          {brief.recommended_actions.map((a, i) => (
            <li key={i} className="text-textPrimary text-sm flex gap-2">
              <span className="text-ai font-mono text-xs mt-0.5">{i + 1}</span>{a}
            </li>
          ))}
        </ol>
      </div>

      <div className="px-5 py-4 grid grid-cols-2 gap-4 text-sm">
        <div>
          <div className="text-textMuted text-xs uppercase tracking-wide mb-1">Expected Impact</div>
          <p className="text-textPrimary text-xs leading-relaxed">{brief.expected_impact}</p>
        </div>
        <div>
          <div className="text-textMuted text-xs uppercase tracking-wide mb-1">Confidence</div>
          <p className="text-textPrimary text-xs">{brief.confidence}</p>
        </div>
      </div>

      <div className="px-5 py-3 bg-surfaceRaised/50 text-textMuted text-[11px] leading-relaxed">
        {brief.limitations}
      </div>
    </div>
  )
}
