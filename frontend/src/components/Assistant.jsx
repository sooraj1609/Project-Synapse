import { useEffect, useState } from 'react'
import { api } from '../api.js'
import DecisionBrief from './DecisionBrief.jsx'

const SUGGESTED_QUESTIONS = [
  'Why does this locality need immediate attention?',
  'What factors are contributing to the risk?',
  'What action should be prioritized?',
]

export default function Assistant({ initialLocalityId }) {
  const [localities, setLocalities] = useState([])
  const [localityId, setLocalityId] = useState(initialLocalityId || '')
  const [question, setQuestion] = useState('')
  const [messages, setMessages] = useState([])
  const [loading, setLoading] = useState(false)
  const [brief, setBrief] = useState(null)
  const [briefLoading, setBriefLoading] = useState(false)

  useEffect(() => {
    api.getLocalities().then((data) => {
      setLocalities(data)
      if (!localityId && data.length) setLocalityId(data[0].locality_id)
    })
  }, [])

  useEffect(() => {
    if (initialLocalityId) setLocalityId(initialLocalityId)
  }, [initialLocalityId])

  async function handleAsk(q) {
    const text = q || question
    if (!text.trim() || !localityId) return
    setLoading(true)
    setMessages((m) => [...m, { role: 'user', text }])
    setQuestion('')
    try {
      const res = await api.askAssistant(localityId, text)
      setMessages((m) => [...m, { role: 'assistant', text: res.answer, evidence: res.grounded_evidence }])
    } catch (e) {
      setMessages((m) => [...m, { role: 'assistant', text: `Error: ${e.message}` }])
    } finally {
      setLoading(false)
    }
  }

  async function handleGenerateBrief() {
    setBriefLoading(true)
    try {
      const res = await api.getDecisionBrief(localityId)
      setBrief(res)
    } finally {
      setBriefLoading(false)
    }
  }

  const selectedLocality = localities.find((l) => l.locality_id === localityId)

  return (
    <div className="p-8 max-w-4xl mx-auto">
      <header className="mb-6">
        <h1 className="text-textPrimary text-xl font-semibold">AI Decision Assistant</h1>
        <p className="text-textMuted text-sm mt-1">
          Grounded Q&A — every answer traces back to the same evidence used in the Decision Brief.
        </p>
      </header>

      <div className="flex items-center gap-3 mb-6">
        <label className="text-textMuted text-sm shrink-0">Locality:</label>
        <select
          value={localityId}
          onChange={(e) => { setLocalityId(e.target.value); setBrief(null); setMessages([]) }}
          className="bg-surface border border-border rounded-lg px-3 py-2 text-sm text-textPrimary flex-1"
        >
          {localities.map((l) => (
            <option key={l.locality_id} value={l.locality_id}>
              {l.name} — {l.risk_level} ({l.overall_risk_score})
            </option>
          ))}
        </select>
        <button
          onClick={handleGenerateBrief}
          disabled={briefLoading || !localityId}
          className="bg-ai/10 border border-ai/30 text-ai text-sm px-4 py-2 rounded-lg hover:bg-ai/20 transition-colors whitespace-nowrap disabled:opacity-50"
        >
          {briefLoading ? 'Generating…' : 'Generate Decision Brief'}
        </button>
      </div>

      {/* Chat */}
      <div className="bg-surface border border-border rounded-xl mb-6">
        <div className="p-5 space-y-4 min-h-[120px] max-h-[400px] overflow-y-auto">
          {messages.length === 0 && (
            <p className="text-textMuted text-sm">
              Ask a question about {selectedLocality?.name || 'this locality'}, or try a suggestion below.
            </p>
          )}
          {messages.map((m, i) => (
            <div key={i} className={m.role === 'user' ? 'text-right' : ''}>
              <div
                className={`inline-block max-w-[85%] rounded-lg px-4 py-2.5 text-sm text-left ${
                  m.role === 'user'
                    ? 'bg-surfaceRaised text-textPrimary'
                    : 'bg-ai/10 border border-ai/20 text-textPrimary'
                }`}
              >
                {m.text}
              </div>
            </div>
          ))}
          {loading && <div className="text-textMuted text-sm">Analyzing across domain agents…</div>}
        </div>

        <div className="border-t border-border p-3 flex gap-2 flex-wrap">
          {SUGGESTED_QUESTIONS.map((q) => (
            <button
              key={q}
              onClick={() => handleAsk(q)}
              className="text-xs text-textMuted border border-border rounded-full px-3 py-1.5 hover:text-ai hover:border-ai/30 transition-colors"
            >
              {q}
            </button>
          ))}
        </div>

        <form
          onSubmit={(e) => { e.preventDefault(); handleAsk() }}
          className="border-t border-border p-3 flex gap-2"
        >
          <input
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="Ask about this locality…"
            className="flex-1 bg-surfaceRaised border border-border rounded-lg px-3 py-2 text-sm text-textPrimary placeholder:text-textMuted focus:outline-none focus:border-ai/40"
          />
          <button
            type="submit"
            disabled={loading}
            className="bg-ai text-base font-medium text-sm px-4 py-2 rounded-lg hover:opacity-90 transition-opacity disabled:opacity-50"
          >
            Ask
          </button>
        </form>
      </div>

      {brief && <DecisionBrief brief={brief} />}
    </div>
  )
}
