import { useState, useEffect } from 'react'
import Login from './pages/Login'
import Dashboard from './pages/Dashboard'
import Profile from './pages/Profile'
import MedicalChatbot from './components/MedicalChatbot'

export default function App() {
  const [currentPage, setCurrentPage] = useState('login')
  const [user, setUser] = useState(null)

  useEffect(() => {
    // Verifica se l'utente è già loggato
    checkAuth()
  }, [])

  const checkAuth = async () => {
    try {
      const res = await fetch('/api/auth/check', { credentials: 'include' })
      if (res.ok) {
        const data = await res.json()
        if (data.authenticated && data.doctor) {
          setUser({
            doctorId: data.doctor.doctor_id,
            firstName: data.doctor.nome,
            lastName: data.doctor.cognome,
            specialization: data.doctor.specializzazione,
            hospital: data.doctor.ospedale_affiliato
          })
          setCurrentPage('dashboard')
        }
      }
    } catch (err) {
      console.log('Non autenticato')
    }
  }

  const handleLogin = (doctor) => {
    setUser({
      doctorId: doctor.doctor_id,
      firstName: doctor.nome,
      lastName: doctor.cognome,
      specialization: doctor.specializzazione,
      hospital: doctor.ospedale_affiliato || ''
    })
    setCurrentPage('dashboard')
  }

  const handleLogout = () => {
    setUser(null)
    setCurrentPage('login')
  }

  return (
    <>
      {currentPage === 'login' && <Login onLogin={handleLogin} />}
      {currentPage === 'dashboard' && <Dashboard user={user} onNavigate={setCurrentPage} onLogout={handleLogout} />}
      {currentPage === 'profile' && <Profile user={user} onNavigate={setCurrentPage} onLogout={handleLogout} />}
      
      {/* Medical Chatbot - disponibile sempre */}
      <MedicalChatbot />
    </>
  )
}
