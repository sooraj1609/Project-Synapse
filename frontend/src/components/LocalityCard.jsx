import PulseLine from './PulseLine.jsx'
import RiskBadge from './RiskBadge.jsx'

export default function LocalityCard({ locality, onSelect }) {
  return (
    <button
      onClick={() => onSelect(locality.locality_id)}
      className="text-left w-full bg-surface border border-border rounded-xl p-5 hover:border-ai/40 hover:bg-surfaceRaised transition-colors group"
    >
      <div className="flex items-start justify-between mb-3">
        <div>
          <h3 className="text-textPrimary font-medium text-base">{locality.name}</h3>
          <p className="text-textMuted text-xs font-mono mt-0.5">
            pop. {locality.population.toLocaleString()}
          </p>
        </div>
        <RiskBadge level={locality.risk_level} />
      </div>

      <div className="flex items-center justify-between">
        <PulseLine score={locality.overall_risk_score} riskLevel={locality.risk_level} width={100} height={32} />
        <div className="text-right">
          <div className="font-mono text-2xl text-textPrimary leading-none">
            {locality.overall_risk_score}
          </div>
          <div className="text-textMuted text-[10px] uppercase tracking-wide mt-1">risk / 100</div>
        </div>
      </div>

      <div className="mt-4 pt-3 border-t border-border flex items-center justify-between text-xs text-textMuted group-hover:text-ai transition-colors">
        <span>View risk profile</span>
        <span aria-hidden="true">→</span>
      </div>
    </button>
  )
}
