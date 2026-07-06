// A small ECG-style line whose jaggedness scales with risk.
// Stable localities show a calm, near-flat line; critical ones show a sharp spike.
// This is the visual metaphor for the "Living Community Twin" concept.

const RISK_COLORS = {
  Stable: '#2DD4BF',
  Improving: '#60A5FA',
  Warning: '#FBBF24',
  'At Risk': '#FB923C',
  Critical: '#F43F5E',
}

function buildPath(score) {
  // score 0-100 -> amplitude of the spike in the middle of the line
  const amplitude = 2 + (score / 100) * 16
  const midY = 20
  return `M0,${midY} L28,${midY} L34,${midY - amplitude} L40,${midY + amplitude * 0.6} L46,${midY} L120,${midY}`
}

export default function PulseLine({ score, riskLevel, width = 120, height = 40, animate = true }) {
  const color = RISK_COLORS[riskLevel] || '#8B93A7'
  return (
    <svg
      viewBox={`0 0 120 40`}
      width={width}
      height={height}
      className={animate ? 'pulse-animate' : ''}
      aria-label={`Pulse: ${riskLevel}, score ${score}`}
    >
      <path
        d={buildPath(score)}
        fill="none"
        stroke={color}
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeDasharray={animate ? '6 4' : '0'}
      />
    </svg>
  )
}
