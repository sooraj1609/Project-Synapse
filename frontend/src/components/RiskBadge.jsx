const STYLES = {
  Stable: 'bg-risk-stable/15 text-risk-stable border-risk-stable/30',
  Improving: 'bg-risk-improving/15 text-risk-improving border-risk-improving/30',
  Warning: 'bg-risk-warning/15 text-risk-warning border-risk-warning/30',
  'At Risk': 'bg-risk-atrisk/15 text-risk-atrisk border-risk-atrisk/30',
  Critical: 'bg-risk-critical/15 text-risk-critical border-risk-critical/30',
}

export default function RiskBadge({ level }) {
  const style = STYLES[level] || 'bg-textMuted/15 text-textMuted border-textMuted/30'
  return (
    <span className={`inline-flex items-center px-2.5 py-1 rounded-full text-xs font-mono font-medium border ${style}`}>
      {level}
    </span>
  )
}
