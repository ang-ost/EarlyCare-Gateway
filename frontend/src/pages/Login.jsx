import { useState } from 'react'

export default function Login({ onLogin }) {
  const [tab, setTab] = useState('login')
  const [formData, setFormData] = useState({
    doctorId: '',
    password: '',
    firstName: '',
    lastName: '',
    email: '',
    specialization: '',
    hospital: ''
  })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const [newDoctorId, setNewDoctorId] = useState('')
  const [showSuccessModal, setShowSuccessModal] = useState(false)

  const handleChange = (e) => {
    const { name, value } = e.target
    setFormData(prev => ({ ...prev, [name]: value }))
  }

  const handleLogin = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      const res = await fetch('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({
          doctor_id: formData.doctorId,
          password: formData.password
        })
      })

      const data = await res.json()

      if (!res.ok) {
        setError(data.error || 'Errore di accesso')
        return
      }

      onLogin(data.doctor)
    } catch (err) {
      setError('Errore di connessione')
    } finally {
      setLoading(false)
    }
  }

  const handleRegister = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      const res = await fetch('/api/auth/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          nome: formData.firstName,
          cognome: formData.lastName,
          password: formData.password,
          specializzazione: formData.specialization,
          ospedale_affiliato: formData.hospital
        })
      })

      const data = await res.json()

      if (!res.ok) {
        setError(data.error || 'Errore nella registrazione')
        console.error('Registration error:', data)
        return
      }

      if (!data.doctor_id) {
        setError('Errore: ID medico non generato')
        console.error('No doctor_id in response:', data)
        return
      }

      setNewDoctorId(data.doctor_id)
      setShowSuccessModal(true)
      setFormData({ doctorId: '', password: '', firstName: '', lastName: '', email: '', specialization: '', hospital: '' })
    } catch (err) {
      setError('Errore di connessione: ' + err.message)
      console.error('Registration error:', err)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="login-container">
      <div className="login-box">
        <h2>Medical Access & Vision</h2>

        <div className="tabs">
          <button
            className={`tab-button ${tab === 'login' ? 'active' : ''}`}
            onClick={() => { setTab('login'); setError('') }}
          >
            Accedi
          </button>
          <button
            className={`tab-button ${tab === 'register' ? 'active' : ''}`}
            onClick={() => { setTab('register'); setError('') }}
          >
            Registrati
          </button>
        </div>

        {error && <div className="alert alert-danger">{error}</div>}

        {tab === 'login' && (
          <form onSubmit={handleLogin}>
            <div className="form-group">
              <label>ID Medico (NNXXXX)</label>
              <input
                type="text"
                name="doctorId"
                value={formData.doctorId}
                onChange={handleChange}
                placeholder="es. MR0001"
                required
              />
            </div>
            <div className="form-group">
              <label>Password</label>
              <input
                type="password"
                name="password"
                value={formData.password}
                onChange={handleChange}
                required
              />
            </div>
            <button type="submit" className="btn btn-primary btn-block" disabled={loading}>
              {loading ? 'Accesso in corso...' : 'Accedi'}
            </button>
          </form>
        )}

        {tab === 'register' && (
          <form onSubmit={handleRegister}>
            <div className="form-group">
              <label>Nome</label>
              <input
                type="text"
                name="firstName"
                value={formData.firstName}
                onChange={handleChange}
                required
              />
            </div>
            <div className="form-group">
              <label>Cognome</label>
              <input
                type="text"
                name="lastName"
                value={formData.lastName}
                onChange={handleChange}
                required
              />
            </div>
            <div className="form-group">
              <label>Specializzazione</label>
              <select
                name="specialization"
                value={formData.specialization}
                onChange={handleChange}
                required
                style={{ width: '100%', padding: '0.75rem', fontSize: '1rem', borderRadius: '0.375rem', border: '1px solid #e2e8f0' }}
              >
                <option value="">-- Seleziona Specializzazione --</option>
                <option value="Cardiologia">Cardiologia</option>
                <option value="Chirurgia Generale">Chirurgia Generale</option>
                <option value="Dermatologia">Dermatologia</option>
                <option value="Endocrinologia">Endocrinologia</option>
                <option value="Gastroenterologia">Gastroenterologia</option>
                <option value="Ginecologia">Ginecologia</option>
                <option value="Neurologia">Neurologia</option>
                <option value="Oftalmologia">Oftalmologia</option>
                <option value="Oncologia">Oncologia</option>
                <option value="Ortopedia">Ortopedia</option>
                <option value="Otorinolaringoiatria">Otorinolaringoiatria</option>
                <option value="Pediatria">Pediatria</option>
                <option value="Pneumologia">Pneumologia</option>
                <option value="Psichiatria">Psichiatria</option>
                <option value="Radiologia">Radiologia</option>
                <option value="Reumatologia">Reumatologia</option>
                <option value="Urologia">Urologia</option>
                <option value="Medicina Interna">Medicina Interna</option>
              </select>
            </div>
            <div className="form-group">
              <label>Ospedale</label>
              <input
                type="text"
                name="hospital"
                value={formData.hospital}
                onChange={handleChange}
                required
              />
            </div>
            <div className="form-group">
              <label>Password</label>
              <input
                type="password"
                name="password"
                value={formData.password}
                onChange={handleChange}
                required
              />
            </div>
            <button type="submit" className="btn btn-primary btn-block" disabled={loading}>
              {loading ? 'Registrazione in corso...' : 'Registrati'}
            </button>
          </form>
        )}
      </div>

      {/* Success Modal - Registrazione */}
      {showSuccessModal && (
        <div className="modal-overlay" onClick={() => setShowSuccessModal(false)}>
          <div className="modal success-modal" onClick={(e) => e.stopPropagation()}>
            <div className="success-icon"></div>
            <h3>Registrazione completata!</h3>
            
            <div style={{ 
              marginTop: '1.5rem', 
              padding: '1rem', 
              background: '#f9fafb', 
              borderRadius: '0.5rem', 
              border: '2px solid #667eea',
              textAlign: 'center'
            }}>
              <p style={{ fontSize: '0.85rem', color: '#6b7280', marginBottom: '0.5rem' }}>Il tuo ID medico è:</p>
              <p style={{ 
                fontSize: '1.8rem', 
                fontWeight: 'bold', 
                fontFamily: 'monospace', 
                color: '#667eea', 
                letterSpacing: '2px',
                marginBottom: '1rem'
              }}>
                {newDoctorId}
              </p>
              <button 
                className="btn btn-secondary" 
                style={{ width: '100%' }}
                onClick={() => {
                  navigator.clipboard.writeText(newDoctorId)
                  alert('ID copiato negli appunti!')
                }}
              >
                🆔 Copia ID
              </button>
              <p style={{ fontSize: '0.8rem', color: '#dc2626', fontWeight: 'bold', marginTop: '0.75rem' }}>
                ⓘ Salva questo ID, ti servirà per il login!
              </p>
            </div>

            <button 
              className="btn btn-primary btn-block" 
              style={{ marginTop: '1.5rem' }}
              onClick={() => {
                setShowSuccessModal(false)
                setNewDoctorId('')
                setTab('login')
              }}
            >
              Accedi ora
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
