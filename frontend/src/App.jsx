import { useState } from 'react'
import Sidebar from './components/Sidebar.jsx'
import Dashboard from './components/Dashboard.jsx'
import LocalityDetail from './components/LocalityDetail.jsx'
import Assistant from './components/Assistant.jsx'

export default function App() {
  const [view, setView] = useState('overview') // overview | locality | assistant
  const [selectedLocalityId, setSelectedLocalityId] = useState(null)

  function handleSelectLocality(id) {
    setSelectedLocalityId(id)
    setView('locality')
  }

  function handleAskAssistant(id) {
    setSelectedLocalityId(id)
    setView('assistant')
  }

  function handleNavigate(id) {
    setView(id === 'overview' ? 'overview' : 'assistant')
  }

  return (
    <div className="flex min-h-screen bg-base">
      <Sidebar active={view === 'locality' ? 'overview' : view} onNavigate={handleNavigate} />
      <main className="flex-1">
        {view === 'overview' && <Dashboard onSelectLocality={handleSelectLocality} />}
        {view === 'locality' && (
          <LocalityDetail
            localityId={selectedLocalityId}
            onBack={() => setView('overview')}
            onAskAssistant={handleAskAssistant}
          />
        )}
        {view === 'assistant' && <Assistant initialLocalityId={selectedLocalityId} />}
      </main>
    </div>
  )
}
