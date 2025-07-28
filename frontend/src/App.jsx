import { useState, useEffect } from 'react'
import './App.css'

function App() {
  const [anomalies, setAnomalies] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    fetchAnomalies()
  }, [])

  const fetchAnomalies = async () => {
    try {
      const response = await fetch('/api/anomalies')
      if (!response.ok) {
        throw new Error('Failed to fetch anomalies')
      }
      const data = await response.json()
      setAnomalies(data)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  if (loading) return <div className="loading">Loading anomalies...</div>
  if (error) return <div className="error">Error: {error}</div>

  return (
    <div className="app">
      <header className="header">
        <h1>Billing Anomaly Explanations</h1>
        <p>AI-powered analysis of billing discrepancies</p>
      </header>

      <main className="main">
        {anomalies.length === 0 ? (
          <div className="no-data">No anomalies found</div>
        ) : (
          <div className="anomalies-grid">
            {anomalies.map((anomaly, index) => (
              <div key={index} className="anomaly-card">
                <div className="anomaly-header">
                  <h3>Customer {anomaly.account_number}</h3>
                  <span className={`issue-badge ${anomaly.issue.toLowerCase().replace(/\s+/g, '-')}`}>
                    {anomaly.issue}
                  </span>
                </div>
                
                <div className="anomaly-content">
                  <div className="section">
                    <h4>Issue Description</h4>
                    <p>{anomaly.reason || anomaly.explanation}</p>
                  </div>
                  
                  <div className="section">
                    <h4>Recommended Fix</h4>
                    <p className="fix-text">{anomaly.fix}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </main>
    </div>
  )
}

export default App