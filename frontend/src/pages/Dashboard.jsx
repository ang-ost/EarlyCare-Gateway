import { useState, useEffect } from 'react'
import { getApiUrl } from '../config'
import Toast from '../components/Toast'
import DiagnosisModal from '../components/DiagnosisModal'
import comuni from 'comuni-json/comuni.json'

export default function Dashboard({ user, onNavigate, onLogout }) {
  const [showMenu, setShowMenu] = useState(false)
  const [showPatientForm, setShowPatientForm] = useState(false)
  const [showAddRecordForm, setShowAddRecordForm] = useState(false)
  const [showPatientSearch, setShowPatientSearch] = useState(false)
  const [showDiagnosisModal, setShowDiagnosisModal] = useState(false)

  const [searchFiscalCode, setSearchFiscalCode] = useState('')

  // Initialize state from sessionStorage if available
  const [foundPatient, setFoundPatient] = useState(() => {
    const saved = sessionStorage.getItem('foundPatient')
    return saved ? JSON.parse(saved) : null
  })

  const [clinicalRecords, setClinicalRecords] = useState(() => {
    const saved = sessionStorage.getItem('clinicalRecords')
    return saved ? JSON.parse(saved) : []
  })

  const [expandedRecord, setExpandedRecord] = useState(null)
  const [selectedRecord, setSelectedRecord] = useState(null)
  const [selectedRecords, setSelectedRecords] = useState([])
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
    allergie: '',
    malattie_permanenti: '',
    is_foreign: false
  })

  const [recordFormData, setRecordFormData] = useState({
    motivo_tipo: 'Visita',
    motivo: 'Visita di Controllo',
    priority: 'routine',
    symptoms: '',
    notes: '',
    blood_pressure: '',
    heart_rate: '',
    temperature: '',
    oxygen_saturation: '',
    respiratory_rate: ''
  })

  const [recordFiles, setRecordFiles] = useState([])
  const [uploadedFiles, setUploadedFiles] = useState([])
  const [isDragging, setIsDragging] = useState(false)
  const [comuniSuggest, setComuniSuggest] = useState([])
  const [showComuniList, setShowComuniList] = useState(false)
  const [calculatedCF, setCalculatedCF] = useState('')

  // Persist patient data to sessionStorage
  useEffect(() => {
    if (foundPatient) {
      sessionStorage.setItem('foundPatient', JSON.stringify(foundPatient))
    } else {
      sessionStorage.removeItem('foundPatient')
    }
  }, [foundPatient])

  // Persist clinical records to sessionStorage
  useEffect(() => {
    sessionStorage.setItem('clinicalRecords', JSON.stringify(clinicalRecords))
  }, [clinicalRecords])

  const handleLogout = async () => {
    sessionStorage.removeItem('foundPatient')
    sessionStorage.removeItem('clinicalRecords')
    await fetch(getApiUrl('/api/auth/logout'), { method: 'POST', credentials: 'include' })
    onLogout()
  }

  // Filtra i comuni in base a quello che digita l'utente
  const handleComuneInput = (value) => {
    const updatedData = { ...createFormData, comune_nascita: value }
    setCreateFormData(updatedData)

    if (value.length > 0) {
      const filtered = comuni.filter(c =>
        c.nome.toUpperCase().startsWith(value.toUpperCase())
      ).slice(0, 10) // Mostra solo i primi 10
      setComuniSuggest(filtered)
      setShowComuniList(true)
    } else {
      setComuniSuggest([])
      setShowComuniList(false)
    }
  }

  // Seleziona un comune dalla lista
  const selectComune = (comune) => {
    const updatedData = { ...createFormData, comune_nascita: comune.nome }
    setCreateFormData(updatedData)
    setShowComuniList(false)
    setComuniSuggest([])
  }

  const handleCreateFormChange = (e) => {
    const { name, value, type, checked } = e.target
    const val = type === 'checkbox' ? checked : value
    setCreateFormData({ ...createFormData, [name]: val })
  }

  const handleExport = async () => {
    if (!foundPatient) {
      setToast({ type: 'warning', message: 'Seleziona prima un paziente' })
      return
    }

    try {
      const fiscalCode = foundPatient.codice_fiscale || foundPatient.fiscal_code

      let url = getApiUrl(`/api/export/${fiscalCode}`)
      let options = { credentials: 'include' }

      if (selectedRecords.length > 0) {
        url = getApiUrl(`/api/export/${fiscalCode}`)
        options = {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          credentials: 'include',
          body: JSON.stringify({ indexes: selectedRecords })
        }
      }

      const res = await fetch(url, options)

      if (!res.ok) {
        const errorData = await res.json()
        setToast({ type: 'error', message: errorData.error || 'Errore durante l\'export' })
        return
      }

      const blob = await res.blob()
      const downloadUrl = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = downloadUrl
      const fileName = selectedRecords.length > 0
        ? `schede_cliniche_${fiscalCode}_${new Date().toISOString().slice(0, 10)}.pdf`
        : `cartella_clinica_${fiscalCode}_${new Date().toISOString().slice(0, 10)}.pdf`
      a.download = fileName
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(downloadUrl)
      document.body.removeChild(a)

      const message = selectedRecords.length > 0
        ? `${selectedRecords.length} scheda/e esportata/e con successo`
        : 'Cartella clinica esportata con successo'
      setToast({ type: 'success', message })
    } catch (err) {
      setToast({ type: 'error', message: 'Errore di connessione' })
    }
  }

  // Calcola il CF man mano che si inseriscono i dati
  useEffect(() => {
    const { nome, cognome, data_nascita, sesso, comune_nascita, is_foreign } = createFormData

    if (is_foreign) {
      setCalculatedCF('')
      return
    }

    if (nome && cognome && data_nascita && sesso && comune_nascita) {
      // Chiama il backend per calcolare il CF
      const fetchCF = async () => {
        try {
          const res = await fetch(getApiUrl('/api/patient/calculate-cf'), {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include',
            body: JSON.stringify({
              nome: nome.trim(),
              cognome: cognome.trim(),
              data_nascita: data_nascita.trim(),
              sesso: sesso.trim(),
              comune_nascita: comune_nascita.trim()
            })
          })
          const data = await res.json()
          if (res.ok && data.codice_fiscale) {
            setCalculatedCF(data.codice_fiscale)
          } else {
            setCalculatedCF('⚠️ Errore nel calcolo')
          }
        } catch (err) {
          setCalculatedCF('⚠️ Errore di connessione')
        }
      }
      fetchCF()
    } else {
      setCalculatedCF('')
    }
  }, [createFormData.nome, createFormData.cognome, createFormData.data_nascita, createFormData.sesso, createFormData.comune_nascita, createFormData.is_foreign])

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
      const res = await fetch(getApiUrl('/api/patient/search'), {
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
        const recordsRes = await fetch(getApiUrl(`/api/patient/${searchFiscalCode.trim().toUpperCase()}/records`), {
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
      if (!createFormData.is_foreign && (!calculatedCF || calculatedCF.startsWith('⚠️'))) {
        setToast({ type: 'error', message: 'Codice fiscale non valido o non calcolato' })
        setLoading(false)
        return
      }

      const res = await fetch(getApiUrl('/api/patient/create'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({
          nome: createFormData.nome,
          cognome: createFormData.cognome,
          codice_fiscale: calculatedCF, // Passed but ignored by backend if is_foreign is true
          data_nascita: createFormData.data_nascita,
          data_decesso: createFormData.data_decesso || undefined,
          comune_nascita: createFormData.comune_nascita,
          sesso: createFormData.sesso,
          allergie: createFormData.allergie,
          malattie_permanenti: createFormData.malattie_permanenti,
          is_foreign: createFormData.is_foreign
        })
      })

      const data = await res.json()
      if (!res.ok) {
        // Handle validation errors from backend
        if (data.errors && Array.isArray(data.errors)) {
          const errorMessages = data.errors.map(err => `${err.field}: ${err.message}`).join('\n')
          setToast({ type: 'error', message: errorMessages })
        } else {
          setToast({ type: 'error', message: data.error || 'Errore nella creazione' })
        }
        return
      }

      setToast({ type: 'success', message: 'Paziente creato con successo!' })

      // Imposta il nuovo paziente come attivo
      if (data.patient) {
        setFoundPatient(data.patient)
        setClinicalRecords([])
        setSelectedRecord(null)
        setExpandedRecord(null)
      }

      setShowPatientForm(false)
      setCreateFormData({
        nome: '',
        cognome: '',
        data_nascita: '',
        data_decesso: '',
        comune_nascita: '',
        sesso: 'M',
        allergie: '',
        malattie_permanenti: '',
        is_foreign: false
      })
    } catch (err) {
      setToast({ type: 'error', message: 'Errore di connessione: ' + err.message })
    } finally {
      setLoading(false)
    }
  }

  const handleUploadFiles = async (files) => {
    if (!foundPatient) {
      setToast({ type: 'warning', message: 'Seleziona prima un paziente', icon: '⚠️' })
      return
    }

    if (!files || files.length === 0) {
      return
    }

    setLoading(true)
    setToast({ type: 'info', message: `Caricamento e conversione di ${files.length} file in corso...`, icon: '⏳' })

    try {
      const formData = new FormData()
      formData.append('fiscal_code', foundPatient.codice_fiscale || foundPatient.fiscal_code)

      files.forEach((file) => {
        formData.append('files[]', file)
      })

      const res = await fetch(getApiUrl('/api/folder/upload'), {
        method: 'POST',
        credentials: 'include',
        body: formData
      })

      const data = await res.json()
      if (!res.ok) {
        setToast({ type: 'error', message: data.error || 'Errore nel caricamento', icon: '❌' })
        return
      }

      // Mostra risultato con diagnosi se disponibile
      let successMessage = data.message || 'File convertiti e aggiunti alle schede cliniche!'
      if (data.diagnosis && data.confidence) {
        successMessage += ` | Diagnosi: ${data.diagnosis} (${(data.confidence * 100).toFixed(0)}%)`
      }

      setToast({ type: 'success', message: successMessage, icon: '✅' })
      setUploadedFiles([])

      // Ricarica le schede cliniche
      const fiscalCode = foundPatient.codice_fiscale || foundPatient.fiscal_code
      const recordsRes = await fetch(getApiUrl(`/api/patient/${fiscalCode}/records`), {
        credentials: 'include'
      })
      if (recordsRes.ok) {
        const recordsData = await recordsRes.json()
        setClinicalRecords(recordsData.records || [])
      }
    } catch (err) {
      setToast({ type: 'error', message: 'Errore di connessione: ' + err.message, icon: '❌' })
    } finally {
      setLoading(false)
    }
  }

  const handleAddRecord = async (e) => {
    e.preventDefault()
    if (!foundPatient) {
      setToast({ type: 'warning', message: 'Seleziona un paziente' })
      return
    }

    setError('')
    setLoading(true)

    try {
      const formData = new FormData()
      formData.append('motivo_tipo', recordFormData.motivo_tipo)
      formData.append('motivo', recordFormData.motivo)
      formData.append('priority', recordFormData.priority)
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

      const res = await fetch(getApiUrl(`/api/patient/${foundPatient.codice_fiscale}/add-record`), {
        method: 'POST',
        credentials: 'include',
        body: formData
      })

      const data = await res.json()
      if (!res.ok) {
        // Handle validation errors from backend
        if (data.errors && Array.isArray(data.errors)) {
          const errorMessages = data.errors.map(err => `${err.field}: ${err.message}`).join('\n')
          setToast({ type: 'error', message: errorMessages })
        } else {
          setToast({ type: 'error', message: data.error || 'Errore nell\'aggiunta della scheda' })
        }
        return
      }

      setToast({ type: 'success', message: 'Scheda aggiunta con successo!' })
      setShowAddRecordForm(false)
      setRecordFormData({
        motivo_tipo: 'Visita',
        motivo: 'Visita di Controllo',
        priority: 'routine',
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
      const recordsRes = await fetch(getApiUrl(`/api/patient/${foundPatient.codice_fiscale}/records`), {
        credentials: 'include'
      })
      if (recordsRes.ok) {
        const recordsData = await recordsRes.json()
        setClinicalRecords(recordsData.records || [])
      }
    } catch (err) {
      setToast({ type: 'error', message: 'Errore di connessione: ' + err.message })
    } finally {
      setLoading(false)
    }
  }

  return (
    <>
      {toast && <Toast type={toast.type} message={toast.message} icon={toast.icon} onClose={() => setToast(null)} />}

      <header className="header">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', width: '100%' }}>
          <div style={{ cursor: 'pointer' }} onClick={() => onNavigate('dashboard')}>
            <h1 style={{ margin: 0, fontSize: '1.5rem' }}>Medical Access & Vision</h1>
          </div>
          <div style={{ display: 'flex', gap: '2rem', alignItems: 'center' }}>
            <div className="user-menu">
              <button className="menu-button" onClick={() => setShowMenu(!showMenu)}>
                💼 {user?.firstName} {user?.lastName}
              </button>
              {showMenu && (
                <div className="dropdown-menu">
                  <a href="#" onClick={(e) => { e.preventDefault(); setShowMenu(false); onNavigate('profile') }}>
                    💼 Il Mio Profilo
                  </a>
                  <button onClick={() => { handleLogout(); setShowMenu(false) }}>
                    🔐 Esci
                  </button>
                </div>
              )}
            </div>
          </div>
        </div>
      </header>

      {/* Navbar */}
      <nav style={{
        background: 'linear-gradient(90deg, #1e3a8a 0%, #1e40af 100%)',
        padding: '0.5rem 0',
        display: 'flex',
        gap: '0',
        borderBottom: '3px solid rgba(30, 58, 138, 0.3)',
        boxShadow: '0 4px 12px rgba(30, 58, 138, 0.2)'
      }}>
        <button onClick={() => {
          if (foundPatient) {
            handleExport()
          } else {
            setToast({ type: 'warning', message: 'Seleziona prima un paziente' })
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
          transition: 'all 0.3s ease',
          cursor: foundPatient ? 'pointer' : 'not-allowed',
          opacity: foundPatient ? 1 : 0.5,
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
          Esporta
        </button>
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
          Ricerca Paziente
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
          Nuovo Paziente
        </button>
        <button onClick={() => {
          if (foundPatient) {
            setShowAddRecordForm(true)
          } else {
            setToast({ type: 'warning', message: 'Seleziona prima un paziente' })
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
          Nuova Scheda
        </button>
      </nav>

      <div className="container">
        {/* Two Panel Layout */}
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '2rem', margin: '2rem 0' }}>

          {/* Left Panel */}
          <div className="card">
            <h3 style={{ marginTop: 0, color: '#1e3a8a' }}>📋 Cartella Clinica</h3>

            {/* Patient Info Section */}
            <div style={{ marginBottom: '2rem', paddingBottom: '1.5rem', borderBottom: '1px solid #e5e7eb' }}>
              <h4 style={{ marginBottom: '1rem' }}>Informazioni Paziente</h4>
              {foundPatient ? (
                <div style={{ background: '#f3f4f6', padding: '1rem', borderRadius: '0.5rem' }}>
                  <p><strong>{foundPatient.nome} {foundPatient.cognome}</strong></p>
                  <p style={{ color: '#6b7280', fontSize: '0.9rem', margin: '0.25rem 0' }}>CF: {foundPatient.codice_fiscale}</p>
                  <p style={{ color: '#6b7280', fontSize: '0.9rem', margin: '0.25rem 0' }}>Nato: {new Date(foundPatient.data_nascita).toLocaleDateString('it-IT')}</p>
                  {foundPatient.comune_nascita && (
                    <p style={{ color: '#6b7280', fontSize: '0.9rem', margin: '0.25rem 0' }}>Comune: {foundPatient.comune_nascita}</p>
                  )}
                  {foundPatient.gender && (
                    <p style={{ color: '#6b7280', fontSize: '0.9rem', margin: '0.25rem 0' }}>
                      Genere: {
                        (() => {
                          const g = foundPatient.gender.toString().toLowerCase()
                          if (g === 'male' || g === 'm' || g === 'maschio') return 'Maschile'
                          if (g === 'female' || g === 'f' || g === 'femmina') return 'Femminile'
                          return foundPatient.gender
                        })()
                      }
                    </p>
                  )}
                  {foundPatient.age && (
                    <p style={{ color: '#6b7280', fontSize: '0.9rem', margin: '0.25rem 0' }}>Età: {foundPatient.age} anni</p>
                  )}
                  {foundPatient.malattie_permanenti && foundPatient.malattie_permanenti.length > 0 && (
                    <p style={{ color: '#dc2626', fontSize: '0.85rem' }}>
                      Malattie: {foundPatient.malattie_permanenti.join(', ')}
                    </p>
                  )}
                </div>
              ) : (
                <p style={{ color: '#1e3a8a', fontStyle: 'italic' }}>Nessun paziente selezionato</p>
              )}
            </div>

            {/* Patient List Section - if multiple homonyms */}
            {/* File Upload Section */}
            <div>
              <h4 style={{ marginBottom: '1rem' }}>📤 Carica File Clinici</h4>
              <div
                style={{
                  border: `2px dashed ${isDragging ? '#764ba2' : '#667eea'}`,
                  borderRadius: '0.5rem',
                  padding: '2rem',
                  textAlign: 'center',
                  color: '#667eea',
                  cursor: 'pointer',
                  transition: 'all 0.3s',
                  background: isDragging ? '#f0f4ff' : 'transparent'
                }}
                onDragEnter={(e) => {
                  e.preventDefault()
                  e.stopPropagation()
                  setIsDragging(true)
                }}
                onDragOver={(e) => {
                  e.preventDefault()
                  e.stopPropagation()
                  setIsDragging(true)
                }}
                onDragLeave={(e) => {
                  e.preventDefault()
                  e.stopPropagation()
                  setIsDragging(false)
                }}
                onDrop={(e) => {
                  e.preventDefault()
                  e.stopPropagation()
                  setIsDragging(false)
                  const files = Array.from(e.dataTransfer.files)
                  const pdfFiles = files.filter(file => file.type === 'application/pdf' || file.name.toLowerCase().endsWith('.pdf'))
                  const rejectedCount = files.length - pdfFiles.length

                  if (pdfFiles.length > 0) {
                    setUploadedFiles(prev => [...prev, ...pdfFiles])
                    setToast({ type: 'success', message: `${pdfFiles.length} file PDF aggiunti`, icon: '✅' })
                  }

                  if (rejectedCount > 0) {
                    setToast({ type: 'warning', message: `${rejectedCount} file ignorati (solo PDF accettati)`, icon: '⚠️' })
                  }
                }}
                onClick={() => document.getElementById('fileUploadInput').click()}
              >
                <input
                  id="fileUploadInput"
                  type="file"
                  multiple
                  accept=".pdf,application/pdf"
                  onChange={(e) => {
                    const files = Array.from(e.target.files)
                    setUploadedFiles(prev => [...prev, ...files])
                    setToast({ type: 'success', message: `${files.length} file aggiunti`, icon: '✅' })
                  }}
                  style={{ display: 'none' }}
                />
                <div style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>{isDragging ? '📥' : '📄'}</div>
                <p style={{ margin: '0.5rem 0' }}>
                  {isDragging ? 'Rilascia i file PDF qui' : 'Trascina file PDF qui o clicca per selezionare'}
                </p>
                <button type="button" className="btn btn-secondary" style={{ marginTop: '0.5rem', pointerEvents: 'none' }}>
                  📁 Seleziona PDF
                </button>
                <p style={{ fontSize: '0.85rem', color: '#6b7280', marginTop: '0.75rem' }}>
                  Solo file PDF esportati dalla piattaforma
                </p>
              </div>

              {uploadedFiles.length > 0 && (
                <div style={{ marginTop: '1rem' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
                    <p style={{ fontWeight: '600', color: '#667eea' }}>📎 File caricati ({uploadedFiles.length})</p>
                    <div style={{ display: 'flex', gap: '0.5rem' }}>
                      <button
                        onClick={() => handleUploadFiles(uploadedFiles)}
                        className="btn btn-primary"
                        disabled={loading}
                        style={{
                          background: 'linear-gradient(135deg, #1e3a8a 0%, #1e40af 100%)',
                          border: 'none',
                          color: 'white',
                          cursor: loading ? 'not-allowed' : 'pointer',
                          padding: '0.5rem 1rem',
                          fontSize: '0.85rem',
                          borderRadius: '0.5rem',
                          fontWeight: '600',
                          opacity: loading ? 0.6 : 1
                        }}
                      >
                        {loading ? '⏳ Elaborazione...' : '🔄 Converti e Carica'}
                      </button>
                      <button
                        onClick={() => setUploadedFiles([])}
                        style={{
                          background: 'transparent',
                          border: 'none',
                          color: '#ef4444',
                          cursor: 'pointer',
                          padding: '0.25rem 0.5rem',
                          fontSize: '0.85rem'
                        }}
                      >
                        🗑️ Rimuovi tutti
                      </button>
                    </div>
                  </div>
                  <div style={{
                    display: 'flex',
                    flexDirection: 'column',
                    gap: '0.5rem',
                    maxHeight: '200px',
                    overflowY: 'auto',
                    padding: '0.5rem',
                    border: '1px solid #e5e7eb',
                    borderRadius: '0.5rem',
                    background: '#f9fafb'
                  }}>
                    {uploadedFiles.map((file, idx) => (
                      <div key={idx} style={{
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'space-between',
                        gap: '0.5rem',
                        padding: '0.5rem',
                        fontSize: '0.9rem',
                        background: 'white',
                        borderRadius: '0.25rem',
                        border: '1px solid #e5e7eb'
                      }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', flex: 1 }}>
                          <span>📄</span>
                          <span style={{ color: '#667eea', fontWeight: '500' }}>{file.name}</span>
                          <span style={{ color: '#9ca3af', fontSize: '0.85rem' }}>({(file.size / 1024).toFixed(1)} KB)</span>
                        </div>
                        <button
                          onClick={(e) => {
                            e.stopPropagation()
                            setUploadedFiles(prev => prev.filter((_, i) => i !== idx))
                          }}
                          style={{
                            background: 'transparent',
                            border: 'none',
                            color: '#ef4444',
                            cursor: 'pointer',
                            padding: '0.25rem',
                            fontSize: '1rem'
                          }}
                        >
                          ✕
                        </button>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Right Panel */}
          <div className="card">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem', gap: '1rem' }}>
              <h3 style={{ margin: 0, color: '#1e3a8a' }}>🩺 Schede Cliniche</h3>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                {selectedRecords.length > 0 && (
                  <button
                    className="btn"
                    onClick={async () => {
                      if (!confirm(`Sei sicuro di voler eliminare ${selectedRecords.length} scheda/e clinica/che?`)) {
                        return
                      }

                      setLoading(true)
                      try {
                        const fiscalCode = foundPatient.codice_fiscale || foundPatient.fiscal_code
                        const res = await fetch(getApiUrl(`/api/patient/${fiscalCode}/records/delete`), {
                          method: 'DELETE',
                          headers: { 'Content-Type': 'application/json' },
                          credentials: 'include',
                          body: JSON.stringify({ indexes: selectedRecords })
                        })

                        const data = await res.json()
                        if (!res.ok) {
                          setToast({ type: 'error', message: data.error || 'Errore nell\'eliminazione', icon: '❌' })
                          return
                        }

                        setToast({ type: 'success', message: `${selectedRecords.length} scheda/e eliminata/e con successo`, icon: '✅' })
                        setSelectedRecords([])
                        setSelectedRecord(null)

                        // Ricarica le schede cliniche
                        const recordsRes = await fetch(getApiUrl(`/api/patient/${fiscalCode}/records`), {
                          credentials: 'include'
                        })
                        if (recordsRes.ok) {
                          const recordsData = await recordsRes.json()
                          setClinicalRecords(recordsData.records || [])
                        }
                      } catch (err) {
                        setToast({ type: 'error', message: 'Errore di connessione: ' + err.message, icon: '❌' })
                      } finally {
                        setLoading(false)
                      }
                    }}
                    style={{
                      background: '#ef4444',
                      color: 'white',
                      border: 'none',
                      padding: '0.5rem 1rem',
                      fontSize: '0.9rem',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '0.5rem',
                      boxShadow: '0 4px 6px rgba(239, 68, 68, 0.3)'
                    }}
                  >
                    🗑️ Elimina ({selectedRecords.length})
                  </button>
                )}
                {selectedRecord !== null && (
                  <button
                    className="btn btn-primary"
                    onClick={() => setShowDiagnosisModal(true)}
                    style={{
                      background: 'linear-gradient(135deg, #1e3a8a 0%, #1e40af 100%)',
                      border: 'none',
                      padding: '0.5rem 1rem',
                      fontSize: '0.9rem',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '0.5rem',
                      boxShadow: '0 4px 6px rgba(30, 58, 138, 0.3)'
                    }}
                  >
                    💉 Diagnosi AI
                  </button>
                )}
                <span style={{
                  background: '#1e3a8a',
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
                    style={{
                      padding: '1rem',
                      border: selectedRecord === idx ? '3px solid #667eea' : (selectedRecords.includes(idx) ? '2px solid #f59e0b' : '1px solid #e5e7eb'),
                      borderRadius: '0.5rem',
                      background: selectedRecord === idx ? 'linear-gradient(135deg, #f0f4ff 0%, #faf5ff 100%)' : (selectedRecords.includes(idx) ? '#fef3c7' : (expandedRecord === idx ? '#f0f4ff' : 'white')),
                      cursor: 'pointer',
                      transition: 'all 0.3s',
                      boxShadow: selectedRecord === idx ? '0 4px 12px rgba(102, 126, 234, 0.2)' : (selectedRecords.includes(idx) ? '0 2px 8px rgba(245, 158, 11, 0.2)' : 'none'),
                      position: 'relative'
                    }}
                  >
                    {/* Checkbox per selezione multipla */}
                    <div
                      style={{
                        position: 'absolute',
                        top: '0.5rem',
                        left: '0.5rem',
                        zIndex: 10
                      }}
                      onClick={(e) => e.stopPropagation()}
                    >
                      <input
                        type="checkbox"
                        checked={selectedRecords.includes(idx)}
                        onChange={(e) => {
                          e.stopPropagation()
                          if (selectedRecords.includes(idx)) {
                            setSelectedRecords(selectedRecords.filter(i => i !== idx))
                          } else {
                            setSelectedRecords([...selectedRecords, idx])
                          }
                        }}
                        style={{
                          width: '20px',
                          height: '20px',
                          cursor: 'pointer',
                          accentColor: '#667eea'
                        }}
                      />
                    </div>

                    {selectedRecord === idx && (
                      <div style={{
                        position: 'absolute',
                        top: '0.5rem',
                        right: '0.5rem',
                        background: '#1e3a8a',
                        color: 'white',
                        padding: '0.25rem 0.5rem',
                        borderRadius: '0.25rem',
                        fontSize: '0.75rem',
                        fontWeight: '600',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '0.25rem'
                      }}>
                        Selezionata
                      </div>
                    )}
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start' }}>
                      <div
                        onClick={(e) => {
                          // Clicco sul contenuto per selezionare la scheda
                          if (selectedRecord === idx) {
                            setSelectedRecord(null)
                          } else {
                            setSelectedRecord(idx)
                          }
                        }}
                        style={{ flex: 1, paddingLeft: '2rem', cursor: 'pointer' }}
                      >
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.25rem' }}>
                          <p style={{ fontWeight: '600', margin: 0 }}>{record.motivo_tipo || record.tipo_scheda}</p>
                          {record.priority && (
                            <span style={{
                              fontSize: '0.75rem',
                              padding: '0.1rem 0.5rem',
                              borderRadius: '9999px',
                              fontWeight: '500',
                              backgroundColor: {
                                'routine': '#dcfce7',
                                'soon': '#fef9c3',
                                'urgent': '#ffedd5',
                                'emergency': '#fee2e2'
                              }[record.priority] || '#f3f4f6',
                              color: {
                                'routine': '#166534',
                                'soon': '#854d0e',
                                'urgent': '#9a3412',
                                'emergency': '#991b1b'
                              }[record.priority] || '#374151'
                            }}>
                              {{
                                'routine': '🟢 Routine',
                                'soon': '🟡 Presto',
                                'urgent': '🟠 Urgente',
                                'emergency': '🔴 Emergenza'
                              }[record.priority] || record.priority}
                            </span>
                          )}
                        </div>
                        {(record.motivo || record.chief_complaint) && (
                          <p style={{ fontSize: '0.9rem', color: '#374151', margin: '0.25rem 0', fontStyle: 'italic' }}>
                            {record.motivo || record.chief_complaint}
                          </p>
                        )}
                        <p style={{ fontSize: '0.85rem', color: '#1e3a8a', margin: '0.25rem 0 0 0' }}>
                          {new Date(record.timestamp).toLocaleDateString('it-IT')} {new Date(record.timestamp).toLocaleTimeString('it-IT', { hour: '2-digit', minute: '2-digit' })}
                        </p>
                        {record.doctor_name && (
                          <p style={{ fontSize: '0.75rem', color: '#1e3a8a', margin: '0.25rem 0 0 0', fontWeight: '500' }}>
                            Dr. {record.doctor_name}
                          </p>
                        )}
                      </div>
                      <button
                        onClick={(e) => {
                          e.stopPropagation()
                          setExpandedRecord(expandedRecord === idx ? null : idx)
                        }}
                        style={{
                          background: 'transparent',
                          border: 'none',
                          color: '#667eea',
                          fontSize: '1.2rem',
                          cursor: 'pointer',
                          padding: '0.5rem',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          transition: 'transform 0.3s'
                        }}
                      >
                        {expandedRecord === idx ? '▼' : '▶'}
                      </button>
                    </div>

                    {expandedRecord === idx && (
                      <div style={{ marginTop: '1rem', paddingTop: '1rem', borderTop: '1px solid #e5e7eb', fontSize: '0.9rem' }}>
                        {record.symptoms && (
                          <div style={{ marginBottom: '1rem' }}>
                            <p style={{ fontWeight: '600', color: '#1e3a8a', marginBottom: '0.25rem' }}>Sintomi:</p>
                            <p style={{ margin: 0, lineHeight: '1.6' }}>{record.symptoms}</p>
                          </div>
                        )}

                        {record.vital_signs && Object.keys(record.vital_signs).length > 0 && (
                          <div style={{ marginBottom: '1rem' }}>
                            <p style={{ fontWeight: '600', color: '#1e3a8a', marginBottom: '0.5rem' }}>Parametri Vitali:</p>
                            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.5rem', fontSize: '0.85rem' }}>
                              {record.vital_signs.blood_pressure && <p style={{ margin: 0 }}>Pressione: {record.vital_signs.blood_pressure}</p>}
                              {record.vital_signs.heart_rate && <p style={{ margin: 0 }}>FC: {record.vital_signs.heart_rate}</p>}
                              {record.vital_signs.temperature && <p style={{ margin: 0 }}>Temp: {record.vital_signs.temperature}</p>}
                              {record.vital_signs.oxygen_saturation && <p style={{ margin: 0 }}>SpO2: {record.vital_signs.oxygen_saturation}</p>}
                              {record.vital_signs.respiratory_rate && <p style={{ margin: 0 }}>FR: {record.vital_signs.respiratory_rate}</p>}
                            </div>
                          </div>
                        )}

                        {record.attachments && record.attachments.length > 0 && (
                          <div style={{ marginBottom: '1rem' }}>
                            <p style={{ fontWeight: '600', color: '#1e3a8a', marginBottom: '0.5rem' }}>Allegati:</p>
                            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
                              {record.attachments.map((file, fileIdx) => (
                                <div
                                  key={fileIdx}
                                  onClick={(e) => {
                                    e.stopPropagation()
                                    if (file.content) {
                                      try {
                                        const byteCharacters = atob(file.content)
                                        const byteNumbers = new Array(byteCharacters.length)
                                        for (let i = 0; i < byteCharacters.length; i++) {
                                          byteNumbers[i] = byteCharacters.charCodeAt(i)
                                        }
                                        const byteArray = new Uint8Array(byteNumbers)
                                        const blob = new Blob([byteArray], { type: file.type || 'application/octet-stream' })
                                        const url = URL.createObjectURL(blob)

                                        if (file.type && file.type.startsWith('image/')) {
                                          window.open(url, '_blank')
                                        } else if (file.type === 'application/pdf') {
                                          window.open(url, '_blank')
                                        } else {
                                          const a = document.createElement('a')
                                          a.href = url
                                          a.download = file.name || 'file'
                                          document.body.appendChild(a)
                                          a.click()
                                          document.body.removeChild(a)
                                        }

                                        setTimeout(() => URL.revokeObjectURL(url), 100)
                                      } catch (error) {
                                        console.error('Errore apertura file:', error)
                                        setToast({ type: 'error', message: 'Errore nell\'apertura del file' })
                                      }
                                    }
                                  }}
                                  style={{
                                    padding: '0.25rem 0.75rem',
                                    background: '#f0f9ff',
                                    borderRadius: '0.25rem',
                                    fontSize: '0.85rem',
                                    display: 'flex',
                                    alignItems: 'center',
                                    gap: '0.25rem',
                                    cursor: file.content ? 'pointer' : 'default',
                                    transition: 'all 0.2s',
                                    border: '1px solid transparent'
                                  }}
                                  onMouseEnter={(e) => {
                                    if (file.content) {
                                      e.currentTarget.style.background = '#dbeafe'
                                      e.currentTarget.style.borderColor = '#3b82f6'
                                      e.currentTarget.style.transform = 'translateY(-1px)'
                                    }
                                  }}
                                  onMouseLeave={(e) => {
                                    e.currentTarget.style.background = '#f0f9ff'
                                    e.currentTarget.style.borderColor = 'transparent'
                                    e.currentTarget.style.transform = 'translateY(0)'
                                  }}
                                >
                                  <span>📄</span>
                                  <span style={{ color: file.content ? '#1e40af' : '#6b7280' }}>{file.name || file}</span>
                                  {file.content && <span style={{ fontSize: '0.7rem', color: '#3b82f6' }}>↗</span>}
                                </div>
                              ))}
                            </div>
                          </div>
                        )}

                        {record.notes && (
                          <div>
                            <p style={{ fontWeight: '600', color: '#1e3a8a', marginBottom: '0.25rem' }}>🖊️ Note del Medico:</p>
                            <p style={{ margin: 0, padding: '0.5rem', background: '#f9fafb', borderRadius: '0.25rem', fontFamily: 'monospace', fontSize: '0.85rem', lineHeight: '1.6', whiteSpace: 'pre-wrap' }}>
                              {record.notes}
                            </p>
                          </div>
                        )}

                        {record.diagnosis && (
                          <div style={{ marginTop: '1rem' }}>
                            <p style={{ fontWeight: '600', color: '#1e3a8a', marginBottom: '0.25rem' }}>Diagnosi:</p>
                            <p style={{ margin: 0 }}>{record.diagnosis}</p>
                          </div>
                        )}

                        {record.treatment && (
                          <div style={{ marginTop: '1rem' }}>
                            <p style={{ fontWeight: '600', color: '#1e3a8a', marginBottom: '0.25rem' }}>Trattamento:</p>
                            <p style={{ margin: 0 }}>{record.treatment}</p>
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            ) : (
              <p style={{ color: '#1e3a8a', fontStyle: 'italic' }}>Nessuna scheda clinica disponibile</p>
            )}
          </div>
        </div>
      </div>

      {/* Search Modal */}
      {showPatientSearch && (
        <div className="modal-overlay" onClick={() => setShowPatientSearch(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <h3>Ricerca Paziente</h3>
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
            <h3>Nuovo Paziente</h3>
            {error && <div className="alert alert-danger">{error}</div>}

            <form onSubmit={handleCreatePatient}>
              <h4 style={{ color: '#1e3a8a', marginTop: '1.5rem', marginBottom: '1rem' }}>Dati Anagrafici</h4>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                <div className="form-group">
                  <label>Nome *</label>
                  <input type="text" value={createFormData.nome} onChange={handleCreateFormChange} name="nome" required />
                </div>
                <div className="form-group">
                  <label>Cognome *</label>
                  <input type="text" value={createFormData.cognome} onChange={handleCreateFormChange} name="cognome" required />
                </div>
              </div>

              <div className="form-group" style={{ marginBottom: '1rem', marginTop: '0.5rem' }}>
                <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', cursor: 'pointer' }}>
                  <input
                    type="checkbox"
                    name="is_foreign"
                    checked={createFormData.is_foreign}
                    onChange={handleCreateFormChange}
                    style={{ width: '1.2rem', height: '1.2rem' }}
                  />
                  <span>Paziente Straniero (Genera ID casuale)</span>
                </label>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                <div className="form-group">
                  <label>Data Nascita *</label>
                  <input type="date" value={createFormData.data_nascita} onChange={handleCreateFormChange} name="data_nascita" required />
                </div>
                <div className="form-group">
                  <label>Data Decesso</label>
                  <input type="date" value={createFormData.data_decesso} onChange={handleCreateFormChange} name="data_decesso" />
                </div>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                <div className="form-group" style={{ position: 'relative' }}>
                  <label>Comune Nascita {!createFormData.is_foreign && '*'}</label>
                  <input
                    type="text"
                    value={createFormData.comune_nascita}
                    onChange={(e) => handleComuneInput(e.target.value)}
                    name="comune_nascita"
                    placeholder={createFormData.is_foreign ? "Inserisci città o stato..." : "Inizia a digitare il nome del comune..."}
                    required={!createFormData.is_foreign}
                  />
                  {showComuniList && comuniSuggest.length > 0 && !createFormData.is_foreign && (
                    <div style={{
                      position: 'absolute',
                      top: '100%',
                      left: 0,
                      right: 0,
                      backgroundColor: 'white',
                      border: '1px solid #ddd',
                      borderRadius: '4px',
                      maxHeight: '200px',
                      overflowY: 'auto',
                      zIndex: 10,
                      marginTop: '4px'
                    }}>
                      {comuniSuggest.map((comune, idx) => (
                        <div
                          key={idx}
                          onClick={() => selectComune(comune)}
                          style={{
                            padding: '8px 12px',
                            cursor: 'pointer',
                            backgroundColor: idx % 2 === 0 ? '#f9f9f9' : 'white',
                            borderBottom: '1px solid #eee',
                            fontSize: '0.95rem'
                          }}
                          onMouseEnter={(e) => e.target.style.backgroundColor = '#e8f1ff'}
                          onMouseLeave={(e) => e.target.style.backgroundColor = idx % 2 === 0 ? '#f9f9f9' : 'white'}
                        >
                          {comune.nome}
                        </div>
                      ))}
                    </div>
                  )}
                </div>
                <div className="form-group">
                  <label>Sesso *</label>
                  <div style={{ display: 'flex', gap: '1.5rem', paddingTop: '0.5rem' }}>
                    <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', cursor: 'pointer', margin: 0 }}>
                      <input type="radio" name="sesso" value="M" checked={createFormData.sesso === 'M'} onChange={handleCreateFormChange} required />
                      <span>Maschio</span>
                    </label>
                    <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', cursor: 'pointer', margin: 0 }}>
                      <input type="radio" name="sesso" value="F" checked={createFormData.sesso === 'F'} onChange={handleCreateFormChange} required />
                      <span>Femmina</span>
                    </label>
                  </div>
                </div>
              </div>

              {calculatedCF && !createFormData.is_foreign && (
                <div style={{
                  backgroundColor: '#f0f4ff',
                  border: '2px solid #1e3a8a',
                  borderRadius: '8px',
                  padding: '1rem',
                  marginTop: '1.5rem',
                  marginBottom: '1.5rem'
                }}>
                  <p style={{ margin: 0, fontSize: '0.9rem', color: '#6b7280', marginBottom: '0.5rem' }}>📋 Codice Fiscale</p>
                  <p style={{ margin: 0, fontSize: '1.2rem', fontWeight: 'bold', color: '#1e3a8a', fontFamily: 'monospace' }}>{calculatedCF}</p>
                </div>
              )}

              {createFormData.is_foreign && (
                <div style={{
                  backgroundColor: '#fef3c7',
                  border: '2px solid #d97706',
                  borderRadius: '8px',
                  padding: '1rem',
                  marginTop: '1.5rem',
                  marginBottom: '1.5rem'
                }}>
                  <p style={{ margin: 0, fontSize: '0.9rem', color: '#92400e', marginBottom: '0.5rem' }}>🌍 ID Paziente Straniero</p>
                  <p style={{ margin: 0, fontSize: '1rem', fontWeight: 'bold', color: '#d97706' }}>Verrà generato automaticamente al salvataggio</p>
                </div>
              )}

              <h4 style={{ color: '#1e3a8a', marginTop: '1.5rem', marginBottom: '1rem', borderTop: '1px solid #e5e7eb', paddingTop: '1.5rem' }}>Informazioni Cliniche</h4>

              <div className="form-group">
                <label>Allergie</label>
                <textarea value={createFormData.allergie} onChange={(e) => setCreateFormData({ ...createFormData, allergie: e.target.value })} placeholder="Separare con virgola o punto e virgola" rows="2"></textarea>
              </div>

              <div className="form-group">
                <label>Malattie Permanenti</label>
                <textarea value={createFormData.malattie_permanenti} onChange={(e) => setCreateFormData({ ...createFormData, malattie_permanenti: e.target.value })} placeholder="Separare con virgola o punto e virgola" rows="2"></textarea>
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
            <h3>📄 Aggiungi Scheda Clinica</h3>
            <p style={{ color: '#6b7280', marginBottom: '1rem' }}>Paziente: <strong>{foundPatient.nome} {foundPatient.cognome}</strong></p>
            {error && <div className="alert alert-danger">{error}</div>}

            <form onSubmit={handleAddRecord}>
              <div className="form-group">
                <select value={recordFormData.motivo_tipo} onChange={(e) => {
                  const tipo = e.target.value
                  setRecordFormData({
                    ...recordFormData,
                    motivo_tipo: tipo,
                    motivo: tipo === 'Visita' ? 'Visita di Controllo' : 'Ricovero Ospedaliero'
                  })
                }} required style={{ width: '100%', padding: '0.75rem', fontSize: '1rem', borderRadius: '8px', border: '2px solid #e5e7eb' }}>
                  <option value="Visita">🏥 Visita</option>
                  <option value="Ricovero">🛏️ Ricovero</option>
                </select>
              </div>

              <div className="form-group">
                <label>Priorità</label>
                <select
                  value={recordFormData.priority}
                  onChange={(e) => setRecordFormData({ ...recordFormData, priority: e.target.value })}
                  style={{ width: '100%', padding: '0.75rem', fontSize: '1rem', borderRadius: '8px', border: '2px solid #e5e7eb' }}
                >
                  <option value="routine">🟢 Routine</option>
                  <option value="soon">🟡 Presto</option>
                  <option value="urgent">🟠 Urgente</option>
                  <option value="emergency">🔴 Emergenza</option>
                </select>
              </div>

              <div className="form-group">
                <label>Sintomi *</label>
                <textarea
                  value={recordFormData.symptoms}
                  onChange={(e) => setRecordFormData({ ...recordFormData, symptoms: e.target.value })}
                  placeholder="Descrizione dettagliata dei sintomi presentati dal paziente..."
                  required
                  rows="4"
                ></textarea>
              </div>

              <h4 style={{ color: '#1e3a8a', marginTop: '1.5rem', marginBottom: '1rem' }}>Parametri Vitali</h4>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                <div className="form-group">
                  <label>Pressione Arteriosa</label>
                  <input
                    type="text"
                    value={recordFormData.blood_pressure}
                    onChange={(e) => setRecordFormData({ ...recordFormData, blood_pressure: e.target.value })}
                    placeholder="120/80 mmHg"
                  />
                </div>
                <div className="form-group">
                  <label>Frequenza Cardiaca</label>
                  <input
                    type="text"
                    value={recordFormData.heart_rate}
                    onChange={(e) => setRecordFormData({ ...recordFormData, heart_rate: e.target.value })}
                    placeholder="75 bpm"
                  />
                </div>
                <div className="form-group">
                  <label>Temperatura</label>
                  <input
                    type="text"
                    value={recordFormData.temperature}
                    onChange={(e) => setRecordFormData({ ...recordFormData, temperature: e.target.value })}
                    placeholder="36.5 °C"
                  />
                </div>
                <div className="form-group">
                  <label>Saturazione O2</label>
                  <input
                    type="text"
                    value={recordFormData.oxygen_saturation}
                    onChange={(e) => setRecordFormData({ ...recordFormData, oxygen_saturation: e.target.value })}
                    placeholder="98%"
                  />
                </div>
                <div className="form-group">
                  <label>Frequenza Respiratoria</label>
                  <input
                    type="text"
                    value={recordFormData.respiratory_rate}
                    onChange={(e) => setRecordFormData({ ...recordFormData, respiratory_rate: e.target.value })}
                    placeholder="16 atti/min"
                  />
                </div>
              </div>

              <div className="form-group" style={{ marginTop: '1.5rem' }}>
                <label>Allega Documenti</label>
                <input
                  type="file"
                  multiple
                  accept=".txt,.pdf,.json,.jpg,.jpeg,.png"
                  onChange={(e) => setRecordFiles(Array.from(e.target.files))}
                  style={{
                    padding: '0.5rem',
                    border: '2px dashed #1e3a8a',
                    borderRadius: '0.5rem',
                    background: '#f0f9ff',
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
                <label>Note del Medico</label>
                <textarea
                  value={recordFormData.notes}
                  onChange={(e) => setRecordFormData({ ...recordFormData, notes: e.target.value })}
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
