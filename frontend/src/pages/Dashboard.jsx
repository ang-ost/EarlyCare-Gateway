import { useState, useEffect } from 'react'
import Toast from '../components/Toast'
import DiagnosisModal from '../components/DiagnosisModal'

export default function Dashboard({ user, onNavigate, onLogout }) {
  const [showMenu, setShowMenu] = useState(false)
  const [showPatientForm, setShowPatientForm] = useState(false)
  const [showAddRecordForm, setShowAddRecordForm] = useState(false)
  const [showPatientSearch, setShowPatientSearch] = useState(false)
  const [showDiagnosisModal, setShowDiagnosisModal] = useState(false)
  
  const [searchFiscalCode, setSearchFiscalCode] = useState('')
  const [foundPatient, setFoundPatient] = useState(null)
  const [clinicalRecords, setClinicalRecords] = useState([])
  const [expandedRecord, setExpandedRecord] = useState(null)
  const [selectedRecord, setSelectedRecord] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [toast, setToast] = useState(null)
  
  const [createFormData, setCreateFormData] = useState({
    nome: '',
    cognome: '',
    data_nascita: '',
    data_decesso: '',
    comune_nascita: '',
    sesso: 'M',
    codice_fiscale: '',
    allergie: '',
    malattie_permanenti: ''
  })

  const [recordFormData, setRecordFormData] = useState({
    motivo_tipo: 'Visita',
    motivo: '',
    symptoms: '',
    notes: '',
    blood_pressure: '',
    heart_rate: '',
    temperature: '',
    oxygen_saturation: '',
    respiratory_rate: ''
  })

  const [recordFiles, setRecordFiles] = useState([])

  const handleLogout = async () => {
    await fetch('/api/auth/logout', { method: 'POST', credentials: 'include' })
    onLogout()
  }

  const handlePatientSearch = async (e) => {
    e.preventDefault()
    if (!searchFiscalCode.trim()) {
      setError('Inserisci un codice fiscale')
      return
    }

    setLoading(true)
    setError('')
    setFoundPatient(null)
    setClinicalRecords([])

    try {
      const res = await fetch('/api/patient/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ fiscal_code: searchFiscalCode.trim().toUpperCase() })
      })

      const data = await res.json()
      if (!res.ok || !data.success) {
        setError('Paziente non trovato')
        return
      }

      if (data.patient) {
        setFoundPatient(data.patient)
        setShowPatientSearch(false)
        
        // Carica record
        const recordsRes = await fetch(`/api/patient/${searchFiscalCode.trim().toUpperCase()}/records`, {
          credentials: 'include'
        })
        if (recordsRes.ok) {
          const recordsData = await recordsRes.json()
          setClinicalRecords(recordsData.records || [])
        }
      }
    } catch (err) {
      setError('Errore di connessione: ' + err.message)
    } finally {
      setLoading(false)
    }
  }

  const handleCreatePatient = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      const res = await fetch('/api/patient/create', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({
          nome: createFormData.nome,
          cognome: createFormData.cognome,
          codice_fiscale: createFormData.codice_fiscale.toUpperCase(),
          data_nascita: createFormData.data_nascita,
          data_decesso: createFormData.data_decesso || undefined,
          comune_nascita: createFormData.comune_nascita,
          sesso: createFormData.sesso,
          allergie: createFormData.allergie ? createFormData.allergie.split(',').map(s => s.trim()) : [],
          malattie_permanenti: createFormData.malattie_permanenti ? createFormData.malattie_permanenti.split(',').map(s => s.trim()) : []
        })
      })

      const data = await res.json()
      if (!res.ok) {
        setError(data.error || 'Errore nella creazione')
        return
      }

      alert('Paziente creato con successo!')
      setShowPatientForm(false)
      setCreateFormData({
        nome: '',
        cognome: '',
        data_nascita: '',
        data_decesso: '',
        comune_nascita: '',
        sesso: 'M',
        codice_fiscale: '',
        allergie: '',
        malattie_permanenti: ''
      })
    } catch (err) {
      setError('Errore di connessione: ' + err.message)
    } finally {
      setLoading(false)
    }
  }

  const handleAddRecord = async (e) => {
    e.preventDefault()
    if (!foundPatient) {
      setError('Seleziona un paziente')
      return
    }

    setError('')
    setLoading(true)

    try {
      const formData = new FormData()
      formData.append('motivo_tipo', recordFormData.motivo_tipo)
      formData.append('motivo', recordFormData.motivo)
      formData.append('symptoms', recordFormData.symptoms)
      formData.append('notes', recordFormData.notes)
      formData.append('vital_signs', JSON.stringify({
        blood_pressure: recordFormData.blood_pressure,
        heart_rate: recordFormData.heart_rate,
        temperature: recordFormData.temperature,
        oxygen_saturation: recordFormData.oxygen_saturation,
        respiratory_rate: recordFormData.respiratory_rate
      }))
      
      // Aggiungi file
      recordFiles.forEach((file) => {
        formData.append('files', file)
      })

      const res = await fetch(`/api/patient/${foundPatient.codice_fiscale}/add-record`, {
        method: 'POST',
        credentials: 'include',
        body: formData
      })

      const data = await res.json()
      if (!res.ok) {
        setError(data.error || 'Errore nell\'aggiunta della scheda')
        return
      }

      alert('Scheda aggiunta con successo!')
      setShowAddRecordForm(false)
      setRecordFormData({
        motivo_tipo: 'Visita',
        motivo: '',
        symptoms: '',
        notes: '',
        blood_pressure: '',
        heart_rate: '',
        temperature: '',
        oxygen_saturation: '',
        respiratory_rate: ''
      })
      setRecordFiles([])

      // Ricarica record
      const recordsRes = await fetch(`/api/patient/${foundPatient.codice_fiscale}/records`, {
        credentials: 'include'
      })
      if (recordsRes.ok) {
        const recordsData = await recordsRes.json()
        setClinicalRecords(recordsData.records || [])
      }
    } catch (err) {
      setError('Errore di connessione: ' + err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <>
      {toast && <Toast type={toast.type} message={toast.message} icon={toast.icon} onClose={() => setToast(null)} />}
      
      <header className="header">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', width: '100%' }}>
          <div>
            <h1 style={{ margin: 0, fontSize: '1.5rem' }}>🏥 Medical Access & Vision</h1>
          </div>
          <div style={{ display: 'flex', gap: '2rem', alignItems: 'center' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.9rem', color: '#667eea', fontWeight: '500' }}>
              <span style={{ display: 'inline-block', width: '10px', height: '10px', borderRadius: '50%', background: '#10b981' }}></span>
              Database Connesso
            </div>
            <div className="user-menu">
              <button className="menu-button" onClick={() => setShowMenu(!showMenu)}>
                👤 {user?.firstName} {user?.lastName}
              </button>
              {showMenu && (
                <div className="dropdown-menu">
                  <a href="#" onClick={(e) => { e.preventDefault(); setShowMenu(false); onNavigate('profile') }}>
                    👤 Il Mio Profilo
                  </a>
                  <button onClick={() => { handleLogout(); setShowMenu(false) }}>
                    🚪 Esci
                  </button>
                </div>
              )}
            </div>
          </div>
        </div>
      </header>

      {/* Navbar */}
      <nav style={{
        background: 'linear-gradient(90deg, #667eea 0%, #764ba2 100%)',
        padding: '0.5rem 0',
        display: 'flex',
        gap: '0',
        borderBottom: '3px solid rgba(102, 126, 234, 0.3)',
        boxShadow: '0 4px 12px rgba(102, 126, 234, 0.2)'
      }}>
        <a href="#" onClick={(e) => { e.preventDefault() }} style={{
          flex: 1,
          padding: '1rem 1.5rem',
          color: 'white',
          textDecoration: 'none',
          borderRight: '1px solid rgba(255,255,255,0.2)',
          display: 'flex',
          alignItems: 'center',
          gap: '0.75rem',
          fontWeight: '500',
          transition: 'all 0.3s ease',
          cursor: 'pointer',
          fontSize: '0.95rem'
        }} onMouseEnter={(e) => {
          e.currentTarget.style.background = 'rgba(255,255,255,0.15)'
          e.currentTarget.style.transform = 'translateY(-2px)'
        }} onMouseLeave={(e) => {
          e.currentTarget.style.background = 'none'
          e.currentTarget.style.transform = 'translateY(0)'
        }}>
          🏠 Home
        </a>
        <button onClick={() => setShowPatientSearch(true)} style={{
          flex: 1,
          padding: '1rem 1.5rem',
          color: 'white',
          background: 'none',
          border: 'none',
          borderRight: '1px solid rgba(255,255,255,0.2)',
          textDecoration: 'none',
          display: 'flex',
          alignItems: 'center',
          gap: '0.75rem',
          fontWeight: '500',
          cursor: 'pointer',
          transition: 'all 0.3s ease',
          fontSize: '0.95rem'
        }} onMouseEnter={(e) => {
          e.currentTarget.style.background = 'rgba(255,255,255,0.15)'
          e.currentTarget.style.transform = 'translateY(-2px)'
        }} onMouseLeave={(e) => {
          e.currentTarget.style.background = 'none'
          e.currentTarget.style.transform = 'translateY(0)'
        }}>
          🔍 Cerca Paziente
        </button>
        <button onClick={() => setShowPatientForm(true)} style={{
          flex: 1,
          padding: '1rem 1.5rem',
          color: 'white',
          background: 'none',
          border: 'none',
          borderRight: '1px solid rgba(255,255,255,0.2)',
          textDecoration: 'none',
          display: 'flex',
          alignItems: 'center',
          gap: '0.75rem',
          fontWeight: '500',
          cursor: 'pointer',
          transition: 'all 0.3s ease',
          fontSize: '0.95rem'
        }} onMouseEnter={(e) => {
          e.currentTarget.style.background = 'rgba(255,255,255,0.15)'
          e.currentTarget.style.transform = 'translateY(-2px)'
        }} onMouseLeave={(e) => {
          e.currentTarget.style.background = 'none'
          e.currentTarget.style.transform = 'translateY(0)'
        }}>
          👥 Nuovo Paziente
        </button>
        <button onClick={() => {
          if (foundPatient) {
            setShowAddRecordForm(true)
          } else {
            setToast({ type: 'warning', message: 'Seleziona prima un paziente', icon: '⚠️' })
          }
        }} style={{
          flex: 1,
          padding: '1rem 1.5rem',
          color: 'white',
          background: 'none',
          border: 'none',
          borderRight: '1px solid rgba(255,255,255,0.2)',
          textDecoration: 'none',
          display: 'flex',
          alignItems: 'center',
          gap: '0.75rem',
          fontWeight: '500',
          cursor: foundPatient ? 'pointer' : 'not-allowed',
          opacity: foundPatient ? 1 : 0.5,
          transition: 'all 0.3s ease',
          fontSize: '0.95rem'
        }} onMouseEnter={(e) => {
          if (foundPatient) {
            e.currentTarget.style.background = 'rgba(255,255,255,0.15)'
            e.currentTarget.style.transform = 'translateY(-2px)'
          }
        }} onMouseLeave={(e) => {
          e.currentTarget.style.background = 'none'
          e.currentTarget.style.transform = 'translateY(0)'
        }}>
          📋 Aggiungi Scheda
        </button>
      </nav>

      <div className="container">
        {/* Two Panel Layout */}
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '2rem', margin: '2rem 0' }}>
          
          {/* Left Panel */}
          <div className="card">
            <h3 style={{ marginTop: 0, color: '#667eea' }}>📁 Cartella Clinica</h3>

            {/* Patient Info Section */}
            <div style={{ marginBottom: '2rem', paddingBottom: '1.5rem', borderBottom: '1px solid #e5e7eb' }}>
              <h4 style={{ marginBottom: '1rem' }}>👤 Informazioni Paziente</h4>
              {foundPatient ? (
                <div style={{ background: '#f3f4f6', padding: '1rem', borderRadius: '0.5rem' }}>
                  <p><strong>{foundPatient.nome} {foundPatient.cognome}</strong></p>
                  <p style={{ color: '#6b7280', fontSize: '0.9rem', margin: '0.25rem 0' }}>CF: {foundPatient.codice_fiscale}</p>
                  <p style={{ color: '#6b7280', fontSize: '0.9rem', margin: '0.25rem 0' }}>Nato: {new Date(foundPatient.data_nascita).toLocaleDateString('it-IT')}</p>
                  {foundPatient.allergie && foundPatient.allergie.length > 0 && (
                    <p style={{ color: '#ef4444', fontSize: '0.85rem', marginTop: '0.5rem' }}>
                      ⚠️ Allergie: {foundPatient.allergie.join(', ')}
                    </p>
                  )}
                  {foundPatient.malattie_permanenti && foundPatient.malattie_permanenti.length > 0 && (
                    <p style={{ color: '#ef4444', fontSize: '0.85rem' }}>
                      ⚠️ Malattie: {foundPatient.malattie_permanenti.join(', ')}
                    </p>
                  )}
                </div>
              ) : (
                <p style={{ color: '#667eea', fontStyle: 'italic' }}>Nessun paziente selezionato</p>
              )}
            </div>

            {/* Patient List Section - if multiple homonyms */}
            {/* File Upload Section */}
            <div>
              <h4 style={{ marginBottom: '1rem' }}>📤 Carica File Clinici</h4>
              <div style={{
                border: '2px dashed #667eea',
                borderRadius: '0.5rem',
                padding: '2rem',
                textAlign: 'center',
                color: '#667eea',
                cursor: 'pointer',
                transition: 'all 0.3s'
              }} onMouseEnter={(e) => e.currentTarget.style.background = '#f0f4ff'} onMouseLeave={(e) => e.currentTarget.style.background = ''}>
                <div style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>☁️</div>
                <p>Trascina file qui o clicca per selezionare</p>
                <button type="button" className="btn btn-secondary" style={{ marginTop: '0.5rem' }}>
                  📁 Seleziona File
                </button>
              </div>
            </div>
          </div>

          {/* Right Panel */}
          <div className="card">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem', gap: '1rem' }}>
              <h3 style={{ margin: 0, color: '#667eea' }}>📋 Schede Cliniche</h3>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                {selectedRecord !== null && (
                  <button
                    className="btn btn-primary"
                    onClick={() => setShowDiagnosisModal(true)}
                    style={{
                      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                      border: 'none',
                      padding: '0.5rem 1rem',
                      fontSize: '0.9rem',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '0.5rem',
                      boxShadow: '0 4px 6px rgba(102, 126, 234, 0.3)'
                    }}
                  >
                    🧠 Diagnosi AI
                  </button>
                )}
                <span style={{
                  background: '#667eea',
                  color: 'white',
                  padding: '0.25rem 0.75rem',
                  borderRadius: '9999px',
                  fontSize: '0.85rem',
                  fontWeight: '600'
                }}>
                  {clinicalRecords.length}
                </span>
              </div>
            </div>

            {clinicalRecords.length > 0 ? (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                {clinicalRecords.map((record, idx) => (
                  <div
                    key={idx}
                    onClick={(e) => {
                      // Se clicco sul box, seleziono/deseleziono la scheda
                      if (selectedRecord === idx) {
                        setSelectedRecord(null)
                      } else {
                        setSelectedRecord(idx)
                      }
                      // Toggle espansione
                      setExpandedRecord(expandedRecord === idx ? null : idx)
                    }}
                    style={{
                      padding: '1rem',
                      border: selectedRecord === idx ? '3px solid #667eea' : '1px solid #e5e7eb',
                      borderRadius: '0.5rem',
                      background: selectedRecord === idx ? 'linear-gradient(135deg, #f0f4ff 0%, #faf5ff 100%)' : (expandedRecord === idx ? '#f0f4ff' : 'white'),
                      cursor: 'pointer',
                      transition: 'all 0.3s',
                      boxShadow: selectedRecord === idx ? '0 4px 12px rgba(102, 126, 234, 0.2)' : 'none',
                      position: 'relative'
                    }}
                  >
                    {selectedRecord === idx && (
                      <div style={{
                        position: 'absolute',
                        top: '0.5rem',
                        right: '0.5rem',
                        background: '#667eea',
                        color: 'white',
                        padding: '0.25rem 0.5rem',
                        borderRadius: '0.25rem',
                        fontSize: '0.75rem',
                        fontWeight: '600',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '0.25rem'
                      }}>
                        ✓ Selezionata
                      </div>
                    )}
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start' }}>
                      <div style={{ flex: 1 }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.25rem' }}>
                          <span style={{ fontSize: '1.2rem' }}>{record.motivo_tipo === 'Ricovero' ? '🛏️' : '🏥'}</span>
                          <p style={{ fontWeight: '600', margin: 0 }}>{record.motivo_tipo || record.tipo_scheda}</p>
                        </div>
                        {(record.motivo || record.chief_complaint) && (
                          <p style={{ fontSize: '0.9rem', color: '#374151', margin: '0.25rem 0', fontStyle: 'italic' }}>
                            {record.motivo || record.chief_complaint}
                          </p>
                        )}
                        <p style={{ fontSize: '0.85rem', color: '#667eea', margin: '0.25rem 0 0 0' }}>
                          📅 {new Date(record.timestamp).toLocaleDateString('it-IT')} {new Date(record.timestamp).toLocaleTimeString('it-IT', { hour: '2-digit', minute: '2-digit' })}
                        </p>
                        {record.doctor_name && (
                          <p style={{ fontSize: '0.75rem', color: '#667eea', margin: '0.25rem 0 0 0', fontWeight: '500' }}>
                            👨‍⚕️ Dr. {record.doctor_name}
                          </p>
                        )}
                      </div>
                      <span style={{ color: '#667eea', fontSize: '1rem' }}>
                        {expandedRecord === idx ? '▼' : '▶'}
                      </span>
                    </div>

                    {expandedRecord === idx && (
                      <div style={{ marginTop: '1rem', paddingTop: '1rem', borderTop: '1px solid #e5e7eb', fontSize: '0.9rem' }}>
                        {record.symptoms && (
                          <div style={{ marginBottom: '1rem' }}>
                            <p style={{ fontWeight: '600', color: '#667eea', marginBottom: '0.25rem' }}>🩺 Sintomi:</p>
                            <p style={{ margin: 0, lineHeight: '1.6' }}>{record.symptoms}</p>
                          </div>
                        )}
                        
                        {record.vital_signs && Object.keys(record.vital_signs).length > 0 && (
                          <div style={{ marginBottom: '1rem' }}>
                            <p style={{ fontWeight: '600', color: '#667eea', marginBottom: '0.5rem' }}>💓 Parametri Vitali:</p>
                            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.5rem', fontSize: '0.85rem' }}>
                              {record.vital_signs.blood_pressure && <p style={{ margin: 0 }}>🩸 Pressione: {record.vital_signs.blood_pressure}</p>}
                              {record.vital_signs.heart_rate && <p style={{ margin: 0 }}>❤️ FC: {record.vital_signs.heart_rate}</p>}
                              {record.vital_signs.temperature && <p style={{ margin: 0 }}>🌡️ Temp: {record.vital_signs.temperature}</p>}
                              {record.vital_signs.oxygen_saturation && <p style={{ margin: 0 }}>💨 SpO2: {record.vital_signs.oxygen_saturation}</p>}
                              {record.vital_signs.respiratory_rate && <p style={{ margin: 0 }}>🫁 FR: {record.vital_signs.respiratory_rate}</p>}
                            </div>
                          </div>
                        )}

                        {record.attachments && record.attachments.length > 0 && (
                          <div style={{ marginBottom: '1rem' }}>
                            <p style={{ fontWeight: '600', color: '#667eea', marginBottom: '0.5rem' }}>📎 Allegati:</p>
                            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
                              {record.attachments.map((file, fileIdx) => (
                                <div key={fileIdx} style={{
                                  padding: '0.25rem 0.75rem',
                                  background: '#f0f4ff',
                                  borderRadius: '0.25rem',
                                  fontSize: '0.85rem',
                                  display: 'flex',
                                  alignItems: 'center',
                                  gap: '0.25rem'
                                }}>
                                  <span>📄</span>
                                  <span>{file.name || file}</span>
                                </div>
                              ))}
                            </div>
                          </div>
                        )}

                        {record.notes && (
                          <div>
                            <p style={{ fontWeight: '600', color: '#667eea', marginBottom: '0.25rem' }}>📝 Note del Medico:</p>
                            <p style={{ margin: 0, padding: '0.5rem', background: '#f9fafb', borderRadius: '0.25rem', fontFamily: 'monospace', fontSize: '0.85rem', lineHeight: '1.6', whiteSpace: 'pre-wrap' }}>
                              {record.notes}
                            </p>
                          </div>
                        )}

                        {record.diagnosis && (
                          <div style={{ marginTop: '1rem' }}>
                            <p style={{ fontWeight: '600', color: '#667eea', marginBottom: '0.25rem' }}>🔬 Diagnosi:</p>
                            <p style={{ margin: 0 }}>{record.diagnosis}</p>
                          </div>
                        )}
                        
                        {record.treatment && (
                          <div style={{ marginTop: '1rem' }}>
                            <p style={{ fontWeight: '600', color: '#667eea', marginBottom: '0.25rem' }}>💊 Trattamento:</p>
                            <p style={{ margin: 0 }}>{record.treatment}</p>
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            ) : (
              <p style={{ color: '#667eea', fontStyle: 'italic' }}>Nessuna scheda clinica disponibile</p>
            )}
          </div>
        </div>
      </div>

      {/* Search Modal */}
      {showPatientSearch && (
        <div className="modal-overlay" onClick={() => setShowPatientSearch(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <h3>🔍 Ricerca Paziente</h3>
            {error && <div className="alert alert-danger">{error}</div>}
            <form onSubmit={handlePatientSearch}>
              <div className="form-group">
                <label>Codice Fiscale</label>
                <input
                  type="text"
                  value={searchFiscalCode}
                  onChange={(e) => setSearchFiscalCode(e.target.value.toUpperCase())}
                  placeholder="RSSMRA90A01H501Z"
                  required
                />
              </div>
              <div className="modal-buttons">
                <button type="button" className="btn btn-secondary" onClick={() => setShowPatientSearch(false)}>
                  Annulla
                </button>
                <button type="submit" className="btn btn-primary" disabled={loading}>
                  {loading ? 'Ricerca...' : 'Cerca'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Create Patient Modal */}
      {showPatientForm && (
        <div className="modal-overlay" onClick={() => setShowPatientForm(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()} style={{ maxWidth: '700px', maxHeight: '90vh', overflowY: 'auto' }}>
            <h3>👥 Nuovo Paziente</h3>
            {error && <div className="alert alert-danger">{error}</div>}
            
            <form onSubmit={handleCreatePatient}>
              <h4 style={{ color: '#667eea', marginTop: '1.5rem', marginBottom: '1rem' }}>Dati Anagrafici</h4>
              
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                <div className="form-group">
                  <label>Nome *</label>
                  <input type="text" value={createFormData.nome} onChange={(e) => setCreateFormData({...createFormData, nome: e.target.value})} required />
                </div>
                <div className="form-group">
                  <label>Cognome *</label>
                  <input type="text" value={createFormData.cognome} onChange={(e) => setCreateFormData({...createFormData, cognome: e.target.value})} required />
                </div>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                <div className="form-group">
                  <label>Data Nascita *</label>
                  <input type="date" value={createFormData.data_nascita} onChange={(e) => setCreateFormData({...createFormData, data_nascita: e.target.value})} required />
                </div>
                <div className="form-group">
                  <label>Data Decesso</label>
                  <input type="date" value={createFormData.data_decesso} onChange={(e) => setCreateFormData({...createFormData, data_decesso: e.target.value})} />
                </div>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                <div className="form-group">
                  <label>Comune Nascita *</label>
                  <input type="text" value={createFormData.comune_nascita} onChange={(e) => setCreateFormData({...createFormData, comune_nascita: e.target.value})} required />
                </div>
                <div className="form-group">
                  <label>Sesso *</label>
                  <div style={{ display: 'flex', gap: '1.5rem', paddingTop: '0.5rem' }}>
                    <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', cursor: 'pointer', margin: 0 }}>
                      <input type="radio" name="sesso" value="M" checked={createFormData.sesso === 'M'} onChange={(e) => setCreateFormData({...createFormData, sesso: e.target.value})} required />
                      <span>Maschio</span>
                    </label>
                    <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', cursor: 'pointer', margin: 0 }}>
                      <input type="radio" name="sesso" value="F" checked={createFormData.sesso === 'F'} onChange={(e) => setCreateFormData({...createFormData, sesso: e.target.value})} required />
                      <span>Femmina</span>
                    </label>
                  </div>
                </div>
              </div>

              <div className="form-group">
                <label>Codice Fiscale *</label>
                <input type="text" value={createFormData.codice_fiscale} onChange={(e) => setCreateFormData({...createFormData, codice_fiscale: e.target.value.toUpperCase()})} placeholder="RSSMRA90A01H501Z" maxLength="16" required />
              </div>

              <h4 style={{ color: '#667eea', marginTop: '1.5rem', marginBottom: '1rem', borderTop: '1px solid #e5e7eb', paddingTop: '1.5rem' }}>Informazioni Cliniche</h4>

              <div className="form-group">
                <label>Allergie</label>
                <textarea value={createFormData.allergie} onChange={(e) => setCreateFormData({...createFormData, allergie: e.target.value})} placeholder="Separare con virgola o punto e virgola" rows="2"></textarea>
              </div>

              <div className="form-group">
                <label>Malattie Permanenti</label>
                <textarea value={createFormData.malattie_permanenti} onChange={(e) => setCreateFormData({...createFormData, malattie_permanenti: e.target.value})} placeholder="Separare con virgola o punto e virgola" rows="2"></textarea>
              </div>

              <div className="modal-buttons">
                <button type="button" className="btn btn-secondary" onClick={() => setShowPatientForm(false)}>
                  Annulla
                </button>
                <button type="submit" className="btn btn-primary" disabled={loading}>
                  {loading ? 'Salvataggio...' : 'Salva'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Add Record Modal */}
      {showAddRecordForm && foundPatient && (
        <div className="modal-overlay" onClick={() => setShowAddRecordForm(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()} style={{ maxWidth: '700px', maxHeight: '90vh', overflowY: 'auto' }}>
            <h3>📋 Aggiungi Scheda Clinica</h3>
            <p style={{ color: '#6b7280', marginBottom: '1rem' }}>Paziente: <strong>{foundPatient.nome} {foundPatient.cognome}</strong></p>
            {error && <div className="alert alert-danger">{error}</div>}
            
            <form onSubmit={handleAddRecord}>
              <div className="form-group">
                <select value={recordFormData.motivo_tipo} onChange={(e) => setRecordFormData({...recordFormData, motivo_tipo: e.target.value})} required style={{ width: '100%', padding: '0.75rem', fontSize: '1rem', borderRadius: '8px', border: '2px solid #e5e7eb' }}>
                  <option value="Visita">🏥 Visita</option>
                  <option value="Ricovero">🛏️ Ricovero</option>
                </select>
              </div>

              <div className="form-group">
                <label>Sintomi *</label>
                <textarea 
                  value={recordFormData.symptoms} 
                  onChange={(e) => setRecordFormData({...recordFormData, symptoms: e.target.value})} 
                  placeholder="Descrizione dettagliata dei sintomi presentati dal paziente..."
                  required 
                  rows="4"
                ></textarea>
              </div>

              <h4 style={{ color: '#667eea', marginTop: '1.5rem', marginBottom: '1rem' }}>💓 Parametri Vitali</h4>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                <div className="form-group">
                  <label>Pressione Arteriosa</label>
                  <input 
                    type="text" 
                    value={recordFormData.blood_pressure} 
                    onChange={(e) => setRecordFormData({...recordFormData, blood_pressure: e.target.value})} 
                    placeholder="120/80 mmHg" 
                  />
                </div>
                <div className="form-group">
                  <label>Frequenza Cardiaca</label>
                  <input 
                    type="text" 
                    value={recordFormData.heart_rate} 
                    onChange={(e) => setRecordFormData({...recordFormData, heart_rate: e.target.value})} 
                    placeholder="75 bpm" 
                  />
                </div>
                <div className="form-group">
                  <label>Temperatura</label>
                  <input 
                    type="text" 
                    value={recordFormData.temperature} 
                    onChange={(e) => setRecordFormData({...recordFormData, temperature: e.target.value})} 
                    placeholder="36.5 °C" 
                  />
                </div>
                <div className="form-group">
                  <label>Saturazione O2</label>
                  <input 
                    type="text" 
                    value={recordFormData.oxygen_saturation} 
                    onChange={(e) => setRecordFormData({...recordFormData, oxygen_saturation: e.target.value})} 
                    placeholder="98%" 
                  />
                </div>
                <div className="form-group">
                  <label>Frequenza Respiratoria</label>
                  <input 
                    type="text" 
                    value={recordFormData.respiratory_rate} 
                    onChange={(e) => setRecordFormData({...recordFormData, respiratory_rate: e.target.value})} 
                    placeholder="16 atti/min" 
                  />
                </div>
              </div>

              <div className="form-group" style={{ marginTop: '1.5rem' }}>
                <label>📎 Allega Documenti</label>
                <input 
                  type="file" 
                  multiple
                  accept=".txt,.pdf,.json,.jpg,.jpeg,.png"
                  onChange={(e) => setRecordFiles(Array.from(e.target.files))}
                  style={{
                    padding: '0.5rem',
                    border: '2px dashed #667eea',
                    borderRadius: '0.5rem',
                    background: '#f8f9ff',
                    cursor: 'pointer',
                    width: '100%'
                  }}
                />
                <p style={{ fontSize: '0.85rem', color: '#6b7280', marginTop: '0.5rem' }}>
                  Formati supportati: TXT, PDF, JSON, JPG, JPEG, PNG
                </p>
                {recordFiles.length > 0 && (
                  <div style={{ marginTop: '0.5rem' }}>
                    {recordFiles.map((file, idx) => (
                      <div key={idx} style={{ 
                        display: 'flex', 
                        alignItems: 'center', 
                        gap: '0.5rem',
                        padding: '0.25rem 0',
                        fontSize: '0.9rem',
                        color: '#667eea'
                      }}>
                        <span>📄</span>
                        <span>{file.name}</span>
                        <span style={{ color: '#9ca3af' }}>({(file.size / 1024).toFixed(1)} KB)</span>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              <div className="form-group">
                <label>📝 Note del Medico</label>
                <textarea 
                  value={recordFormData.notes} 
                  onChange={(e) => setRecordFormData({...recordFormData, notes: e.target.value})} 
                  placeholder="Annotazioni, osservazioni o intuizioni del medico riguardo al caso..."
                  rows="4"
                  style={{ fontFamily: 'monospace', fontSize: '0.95rem' }}
                ></textarea>
              </div>

              <div className="modal-buttons">
                <button type="button" className="btn btn-secondary" onClick={() => setShowAddRecordForm(false)}>
                  Annulla
                </button>
                <button type="submit" className="btn btn-primary" disabled={loading}>
                  {loading ? 'Salvataggio...' : 'Salva'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* AI Diagnosis Modal */}
      {showDiagnosisModal && foundPatient && (
        <DiagnosisModal 
          patient={foundPatient}
          selectedRecord={selectedRecord !== null ? clinicalRecords[selectedRecord] : null}
          onClose={() => {
            setShowDiagnosisModal(false)
            setSelectedRecord(null)
          }}
        />
      )}
    </>
  )
}
