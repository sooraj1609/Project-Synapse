const BASE_URL = 'https://project-synapse-backend-215504640371.asia-south1.run.app'

async function request(path, options = {}) {
  const res = await fetch(`${BASE_URL}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  })
  if (!res.ok) {
    const body = await res.json().catch(() => ({}))
    throw new Error(body.detail || `Request failed: ${res.status}`)
  }
  return res.json()
}

export const api = {
  getDashboardSummary: () => request('/api/dashboard/summary'),
  getLocalities: () => request('/api/localities'),
  getLocalityProfile: (id) => request(`/api/localities/${id}`),
  getMetricHistory: (id, metric, days = 30) =>
    request(`/api/localities/${id}/history/${metric}?days=${days}`),
  askAssistant: (locality_id, question) =>
    request('/api/assistant/ask', {
      method: 'POST',
      body: JSON.stringify({ locality_id, question }),
    }),
  getDecisionBrief: (id) => request(`/api/assistant/decision-brief/${id}`),
}
