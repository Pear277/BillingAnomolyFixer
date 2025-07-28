import { useState, useEffect } from 'react'
import './App.css'

function App() {
  const [anomalies, setAnomalies] = useState([])
  const [autofixes, setAutofixes] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [activeTab, setActiveTab] = useState('anomalies')
  const [deletingItems, setDeletingItems] = useState(new Set())
  const [customerFilter, setCustomerFilter] = useState('')

  useEffect(() => {
    fetchData()
  }, [])

  const fetchData = async () => {
    try {
      const [anomaliesRes, autofixesRes] = await Promise.all([
        fetch('/api/anomalies'),
        fetch('/api/autofixes')
      ])
      
      if (!anomaliesRes.ok || !autofixesRes.ok) {
        throw new Error(`Failed to fetch data`)
      }
      
      const [anomaliesData, autofixesData] = await Promise.all([
        anomaliesRes.json(),
        autofixesRes.json()
      ])
      
      setAnomalies(anomaliesData || [])
      setAutofixes(autofixesData || [])
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const deleteAnomaly = async (index) => {
    const itemKey = `anomaly-${index}`
    setDeletingItems(prev => new Set([...prev, itemKey]))
    
    try {
      const response = await fetch(`/api/anomalies/${index}`, {
        method: 'DELETE'
      })
      
      if (response.ok) {
        // Refresh data to reflect the deletion
        await fetchData()
      } else {
        throw new Error('Failed to delete anomaly')
      }
    } catch (err) {
      setError(err.message)
    } finally {
      setDeletingItems(prev => {
        const newSet = new Set(prev)
        newSet.delete(itemKey)
        return newSet
      })
    }
  }

  const deleteAutofix = async (index) => {
    const itemKey = `autofix-${index}`
    setDeletingItems(prev => new Set([...prev, itemKey]))
    
    try {
      const response = await fetch(`/api/autofixes/${index}`, {
        method: 'DELETE'
      })
      
      if (response.ok) {
        // Refresh data to reflect the deletion
        await fetchData()
      } else {
        throw new Error('Failed to delete autofix')
      }
    } catch (err) {
      setError(err.message)
    } finally {
      setDeletingItems(prev => {
        const newSet = new Set(prev)
        newSet.delete(itemKey)
        return newSet
      })
    }
  }



  if (loading) return <div className="loading">Loading data...</div>
  if (error) return <div className="error">Error: {error}</div>

  return (
    <div className="app">
      <header className="header">
        <h1>Billing Data Analysis</h1>
        <p>AI-powered analysis of billing discrepancies and auto-fixes</p>
      </header>

      <div className="filter-section">
        <input 
          type="text" 
          placeholder="Filter by customer (e.g. CUST0004)" 
          value={customerFilter}
          onChange={(e) => setCustomerFilter(e.target.value)}
          className="customer-filter"
        />
      </div>

      <nav className="tabs">
        <button 
          className={`tab ${activeTab === 'anomalies' ? 'active' : ''}`}
          onClick={() => setActiveTab('anomalies')}
        >
          Anomalies ({anomalies.filter(a => a.account_number.toLowerCase().includes(customerFilter.toLowerCase())).length})
        </button>
        <button 
          className={`tab ${activeTab === 'autofixes' ? 'active' : ''}`}
          onClick={() => setActiveTab('autofixes')}
        >
          Auto-fixes ({autofixes.filter(f => f.account_number.toLowerCase().includes(customerFilter.toLowerCase())).length})
        </button>
      </nav>

      <main className="main">
        {activeTab === 'anomalies' && (
          anomalies.filter(anomaly => 
            anomaly.account_number.toLowerCase().includes(customerFilter.toLowerCase())
          ).length === 0 ? (
            <div className="no-data">{customerFilter ? 'No anomalies found for this customer' : 'No anomalies found'}</div>
          ) : (
            <div className="anomalies-grid">
              {anomalies.filter(anomaly => 
                anomaly.account_number.toLowerCase().includes(customerFilter.toLowerCase())
              ).map((anomaly, index) => {
                const isDeleting = deletingItems.has(`anomaly-${index}`)
                return (
                  <div key={index} className="anomaly-card">
                    <div className="anomaly-header">
                      <h3>Customer {anomaly.account_number}</h3>
                      <div className="header-right">
                        <span className={`issue-badge ${anomaly.issue.toLowerCase().replace(/\s+/g, '-')}`}>
                          {anomaly.issue}
                        </span>
                        <button 
                          className="dismiss-btn" 
                          onClick={() => deleteAnomaly(index)}
                          disabled={isDeleting}
                        >
                          {isDeleting ? 'Dismissing...' : 'Dismiss'}
                        </button>
                      </div>
                    </div>
                  
                  <div className="anomaly-content">
                    <div className="section">
                      <h4>Issue Description</h4>
                      <p>{anomaly.explanation}</p>
                    </div>
                    
                    <div className="section">
                      <h4>Recommended Fix</h4>
                      <p className="fix-text">{anomaly.fix}</p>
                    </div>
                  </div>
                </div>
                )
              })}
            </div>
          )
        )}

        {activeTab === 'autofixes' && (
          autofixes.filter(fix => 
            fix.account_number.toLowerCase().includes(customerFilter.toLowerCase())
          ).length === 0 ? (
            <div className="no-data">{customerFilter ? 'No auto-fixes found for this customer' : 'No auto-fixes found'}</div>
          ) : (
            <div className="autofixes-grid">
              {autofixes.filter(fix => 
                fix.account_number.toLowerCase().includes(customerFilter.toLowerCase())
              ).map((fix, index) => {
                const isDeleting = deletingItems.has(`autofix-${index}`)
                return (
                  <div key={index} className="autofix-card">
                    <div className="autofix-header">
                      <h3>Customer {fix.account_number}</h3>
                      <div className="header-right">
                        <span className={`fix-badge ${fix.change_type.replace(/_/g, '-')}`}>
                          {fix.change_type.replace(/_/g, ' ')}
                        </span>
                        <button 
                          className="dismiss-btn" 
                          onClick={() => deleteAutofix(index)}
                          disabled={isDeleting}
                        >
                          {isDeleting ? 'Dismissing...' : 'Dismiss'}
                        </button>
                      </div>
                    </div>
                  
                  <div className="autofix-content">
                    <div className="section">
                      <h4>Field: {fix.field}</h4>
                      <div className="change-display">
                        <div className="before">
                          <strong>Before:</strong> {fix.original_value}
                        </div>
                        <div className="arrow">→</div>
                        <div className="after">
                          <strong>After:</strong> {fix.fixed_value}
                        </div>
                      </div>
                    </div>
                    
                    <div className="timestamp">
                      Fixed on: {new Date(fix.timestamp).toLocaleString()}
                    </div>
                  </div>
                </div>
                )
              })}
            </div>
          )
        )}
      </main>
    </div>
  )
}

export default App