import { useState } from 'react'

const API_URL = 'http://127.0.0.1:8000/pred_high'

export default function App() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  async function fetchPrediction() {
    setLoading(true)
    setError(null)
    try {
      const res = await fetch(API_URL)
      if (!res.ok) throw new Error(`Server error: ${res.status}`)
      const json = await res.json()
      setData(json)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={styles.page}>
      <div style={styles.card}>
        <h1 style={styles.title}>NIFTY Next-Day High Predictor</h1>

        <button style={styles.button} onClick={fetchPrediction} disabled={loading}>
          {loading ? 'Loading...' : 'Get Prediction'}
        </button>

        {error && <p style={styles.error}>{error}</p>}

        {data && (
          <div style={styles.fields}>
            <Field label="Based on Date"  value={data.based_on_date} />
            <Field label="Last Close"     value={data.last_close} />
            <Field label="High % (pred)"  value={`${data.high_perc}%`} />
            <Field label="Predicted High" value={data.predicted_high} highlight />
          </div>
        )}
      </div>
    </div>
  )
}

function Field({ label, value, highlight }) {
  return (
    <div style={styles.fieldRow}>
      <label style={styles.label}>{label}</label>
      <input
        style={{ ...styles.input, ...(highlight ? styles.inputHighlight : {}) }}
        value={value ?? ''}
        readOnly
      />
    </div>
  )
}

const styles = {
  page: {
    minHeight: '100vh',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#f0f2f5',
    fontFamily: 'sans-serif',
  },
  card: {
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: '40px 48px',
    boxShadow: '0 4px 20px rgba(0,0,0,0.1)',
    width: 380,
  },
  title: {
    margin: '0 0 28px',
    fontSize: 20,
    fontWeight: 700,
    color: '#1a1a2e',
    textAlign: 'center',
  },
  button: {
    width: '100%',
    padding: '12px 0',
    backgroundColor: '#4f46e5',
    color: '#fff',
    border: 'none',
    borderRadius: 8,
    fontSize: 15,
    fontWeight: 600,
    cursor: 'pointer',
    marginBottom: 24,
  },
  fields: {
    display: 'flex',
    flexDirection: 'column',
    gap: 14,
  },
  fieldRow: {
    display: 'flex',
    flexDirection: 'column',
    gap: 4,
  },
  label: {
    fontSize: 12,
    fontWeight: 600,
    color: '#6b7280',
    textTransform: 'uppercase',
    letterSpacing: '0.05em',
  },
  input: {
    padding: '10px 12px',
    border: '1px solid #e5e7eb',
    borderRadius: 6,
    fontSize: 15,
    color: '#111827',
    backgroundColor: '#f9fafb',
    outline: 'none',
  },
  inputHighlight: {
    backgroundColor: '#eff6ff',
    border: '1px solid #93c5fd',
    color: '#1d4ed8',
    fontWeight: 700,
    fontSize: 17,
  },
  error: {
    color: '#dc2626',
    fontSize: 13,
    marginBottom: 12,
    textAlign: 'center',
  },
}
