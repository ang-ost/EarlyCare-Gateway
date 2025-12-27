import { useState } from 'react'
import { getApiUrl } from '../config'

export default function Profile({ user, onNavigate, onLogout }) {
  const [showMenu, setShowMenu] = useState(false)
  const [showDeleteModal, setShowDeleteModal] = useState(false)
  const [showSuccessModal, setShowSuccessModal] = useState(false)
  const [password, setPassword] = useState('')
  const [deleteError, setDeleteError] = useState('')
  const [deleting, setDeleting] = useState(false)

  const handleLogout = async () => {
    await fetch(getApiUrl('/api/auth/logout'), { method: 'POST', credentials: 'include' })
    onLogout()
  }

  const handleDeleteAccount = async () => {
    if (!password) {
      setDeleteError('Inserisci la password')
      return
    }

    setDeleting(true)
    setDeleteError('')

    try {
      const res = await fetch(getApiUrl('/api/auth/delete-account'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ password })
      })

      const data = await res.json()

      if (!res.ok) {
        setDeleteError(data.error || 'Errore durante l\'eliminazione')
        return
      }

      setShowSuccessModal(true)
      setTimeout(() => {
        onLogout()
      }, 3000)
    } catch (err) {
      setDeleteError('Errore di connessione')
    } finally {
      setDeleting(false)
    }
  }

  return (
    <>
      <header className="header">
        <h1>Medical Access & Vision</h1>
        <div className="header-actions">
          <div className="user-menu">
            <button className="menu-button" onClick={() => setShowMenu(!showMenu)}>
              💼 {user?.firstName} {user?.lastName}
            </button>
            {showMenu && (
              <div className="dropdown-menu">
                <a href="#" onClick={(e) => { e.preventDefault(); setShowMenu(false); onNavigate('dashboard') }}>
                  Dashboard
                </a>
                <button onClick={() => { handleLogout(); setShowMenu(false) }}>
                  Esci
                </button>
              </div>
            )}
          </div>
        </div>
      </header>

      <div className="container">
        <div className="card">
          <h3>Profilo personale</h3>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '2rem' }}>
            <div>
              <p><strong>Nome:</strong> {user?.firstName}</p>
              <p><strong>Cognome:</strong> {user?.lastName}</p>
              <p><strong>ID Medico:</strong> <span style={{ fontFamily: 'monospace', background: '#f3f4f6', padding: '0.25rem 0.5rem', borderRadius: '0.25rem' }}>{user?.doctorId}</span></p>
            </div>
            <div>
              <p><strong>Specializzazione:</strong> {user?.specialization || 'Non specificata'}</p>
              <p><strong>Ospedale:</strong> {user?.hospital || 'Non specificato'}</p>
              <p><strong>Status:</strong> <span style={{ color: '#059669' }}>✓ Attivo</span></p>
            </div>
          </div>
        </div>

        <div className="card">
          <h3 style={{ color: '#dc2626' }}>Pericolo - Zona</h3>
          <p>L'eliminazione dell'account è irreversibile. Tutti i dati associati verranno cancellati.</p>
          <button 
            className="btn btn-danger"
            onClick={() => setShowDeleteModal(true)}
          >
            Elimina account
          </button>
        </div>
      </div>

      {/* Delete Confirmation Modal */}
      {showDeleteModal && (
        <div className="modal-overlay" onClick={() => setShowDeleteModal(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <h3>Conferma eliminazione</h3>
            <p>Sei sicuro di voler eliminare il tuo account? Questa azione è irreversibile.</p>

            {deleteError && <div className="alert alert-danger">{deleteError}</div>}

            <div className="form-group">
              <label>Inserisci la tua password per confermare:</label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
              />
            </div>

            <div className="modal-buttons">
              <button
                className="btn btn-secondary"
                onClick={() => {
                  setShowDeleteModal(false)
                  setPassword('')
                  setDeleteError('')
                }}
              >
                Annulla
              </button>
              <button
                className="btn btn-danger"
                onClick={handleDeleteAccount}
                disabled={deleting}
              >
                {deleting ? 'Eliminazione...' : 'Elimina account'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Success Modal */}
      {showSuccessModal && (
        <div className="modal-overlay">
          <div className="modal success-modal">
            <div className="success-icon"></div>
            <h3>Account eliminato</h3>
            <p>Il tuo account è stato eliminato con successo.</p>
            <p style={{ fontSize: '0.9rem', color: '#6b7280' }}>
              Verrai reindirizzato al login...
            </p>
          </div>
        </div>
      )}
    </>
  )
}
