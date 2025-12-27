import { useState, useEffect } from 'react'
import { getApiUrl } from '../config'

export default function DiagnosisModal({ patient, selectedRecord, onClose }) {
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [diagnosis, setDiagnosis] = useState(null)

  useEffect(() => {
    if (patient) {
      generateDiagnosis()
    }
  }, [patient, selectedRecord])

  const generateDiagnosis = async () => {
    setLoading(true)
    setError(null)

    try {
      const body = selectedRecord 
        ? { fiscal_code: patient.codice_fiscale, clinical_record: selectedRecord }
        : { fiscal_code: patient.codice_fiscale }

      const res = await fetch(getApiUrl('/api/diagnostics/generate'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify(body)
      })

      const data = await res.json()

      if (!res.ok) {
        throw new Error(data.error || 'Errore nella generazione della diagnosi')
      }

      setDiagnosis(data)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const downloadDiagnosis = () => {
    if (!diagnosis) return

    const content = `
DIAGNOSI MEDICA AI
================================================================================

Paziente: ${patient.nome} ${patient.cognome}
Codice Fiscale: ${patient.codice_fiscale}
Data Analisi: ${new Date(diagnosis.timestamp).toLocaleString('it-IT')}
Modello AI: ${diagnosis.metadata?.model || 'gemini-3-flash-preview'}
Punti Dati Analizzati: ${diagnosis.metadata?.data_points_analyzed || 'N/A'}

================================================================================

${diagnosis.diagnosis}

================================================================================

NOTA IMPORTANTE:
Questa è una valutazione generata da intelligenza artificiale a scopo di 
supporto decisionale. La diagnosi finale e le decisioni terapeutiche devono 
sempre essere effettuate da un medico qualificato.

Generato da EarlyCare Gateway - ${new Date().toISOString()}
`

    const blob = new Blob([content], { type: 'text/plain;charset=utf-8' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `diagnosi_${patient.codice_fiscale}_${new Date().toISOString().split('T')[0]}.txt`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()} style={{ maxWidth: '900px', maxHeight: '90vh', overflowY: 'auto' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', marginBottom: '1.5rem' }}>
          <div>
            <h3 style={{ margin: 0, display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              Diagnosi Medica AI
            </h3>
            {selectedRecord && (
              <p style={{ margin: '0.5rem 0 0 0', fontSize: '0.9rem', color: '#1e3a8a', fontWeight: '600' }}>
                📋 Analisi della scheda: {selectedRecord.motivo_tipo} - {selectedRecord.motivo || selectedRecord.chief_complaint}
              </p>
            )}
          </div>
          <button onClick={onClose} style={{ background: 'none', border: 'none', fontSize: '1.5rem', cursor: 'pointer', color: '#6b7280' }}>×</button>
        </div>

        {loading && (
          <div style={{ textAlign: 'center', padding: '3rem' }}>
            <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>
              <span style={{ display: 'inline-block', animation: 'spin 1s linear infinite' }}>⌛</span>
            </div>
            <p style={{ color: '#6b7280', fontSize: '1.1rem' }}>Analisi in corso con AI Gemini...</p>
            <p style={{ color: '#9ca3af', fontSize: '0.9rem' }}>L'analisi potrebbe richiedere alcuni secondi</p>
          </div>
        )}

        {error && (
          <div style={{ textAlign: 'center', padding: '3rem' }}>
            <h4 style={{ color: '#ef4444', marginBottom: '0.5rem' }}>Errore nella generazione della diagnosi</h4>
            <p style={{ color: '#6b7280' }}>{error}</p>
            <button onClick={generateDiagnosis} className="btn btn-primary" style={{ marginTop: '1rem' }}>
              Riprova
            </button>
          </div>
        )}

        {diagnosis && !loading && !error && (
          <>
            <div style={{ 
              background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', 
              color: 'white', 
              padding: '1.5rem', 
              borderRadius: '8px', 
              marginBottom: '1.5rem' 
            }}>
              <h4 style={{ margin: '0 0 0.5rem 0', fontSize: '1.2rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                👤 Paziente: {patient.nome} {patient.cognome}
              </h4>
              <p style={{ margin: 0, opacity: 0.9, fontSize: '0.9rem' }}>
                {new Date(diagnosis.timestamp).toLocaleString('it-IT', {
                  year: 'numeric',
                  month: 'long',
                  day: 'numeric',
                  hour: '2-digit',
                  minute: '2-digit'
                })}
              </p>
            </div>

            <div style={{ 
              background: 'white', 
              padding: '1.5rem', 
              borderRadius: '8px', 
              border: '1px solid #e5e7eb',
              marginBottom: '1.5rem'
            }}>
              <div style={{ 
                whiteSpace: 'pre-wrap', 
                lineHeight: '1.8', 
                color: '#374151',
                fontSize: '1rem'
              }}>
                {diagnosis.diagnosis}
              </div>
            </div>

            {diagnosis.warning && (
              <div className="alert" style={{ 
                background: '#fee2e2', 
                border: '1px solid #ef4444', 
                borderRadius: '8px',
                padding: '1rem',
                marginBottom: '1.5rem',
                color: '#991b1b'
              }}>
                <strong>Attenzione:</strong> {diagnosis.warning}
              </div>
            )}

            <div style={{ 
              padding: '1rem', 
              background: '#f9fafb', 
              borderRadius: '8px', 
              fontSize: '0.9rem',
              marginBottom: '1.5rem'
            }}>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem' }}>
                <div>
                  <strong>Modello AI:</strong>{' '}
                  <span>{diagnosis.metadata?.model || 'gemini-3-flash-preview'}</span>
                </div>
                <div>
                  <strong>Punti dati analizzati:</strong>{' '}
                  <span>{diagnosis.metadata?.data_points_analyzed || 'N/A'}</span>
                </div>
                {diagnosis.metadata?.finish_reason && diagnosis.metadata.finish_reason !== 'COMPLETE' && (
                  <div style={{ gridColumn: '1 / -1', color: '#6b7280' }}>
                    <strong>Status:</strong> {diagnosis.metadata.finish_reason}
                  </div>
                )}
              </div>
            </div>

            <div className="alert" style={{ 
              background: '#fef3c7', 
              border: '1px solid #fbbf24', 
              borderRadius: '8px',
              padding: '1rem',
              marginBottom: '1.5rem'
            }}>
              <strong>Nota Importante:</strong> Questa è una valutazione generata da intelligenza artificiale a scopo di supporto decisionale. La diagnosi finale e le decisioni terapeutiche devono sempre essere effettuate da un medico qualificato.
            </div>

            <div className="modal-buttons">
              <button onClick={downloadDiagnosis} className="btn btn-secondary">
                Scarica PDF
              </button>
              <button onClick={onClose} className="btn btn-primary">
                Chiudi
              </button>
            </div>
          </>
        )}

        <style>{`
          @keyframes spin {
            from { transform: rotate(0deg); }
            to { transform: rotate(360deg); }
          }
        `}</style>
      </div>
    </div>
  )
}
