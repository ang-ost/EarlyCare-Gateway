// Authentication JavaScript - For page-based login system

let isAuthenticated = false;
let currentDoctor = null;
let sessionCheckInterval = null;

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    const isLoginPage = window.location.pathname === '/' && 
                        document.getElementById('loginForm') !== null;
    
    if (!isLoginPage) {
        // On authenticated pages, check session
        checkAuthentication();
        startSessionChecks();
    }
});

// ========== AUTHENTICATION CHECK ==========

function checkAuthentication() {
    fetch('/api/auth/check', {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.authenticated) {
            isAuthenticated = true;
            currentDoctor = data.doctor;
            updateHeaderWithDoctor(data.doctor);
            setupAuthenticatedUI();
        } else {
            isAuthenticated = false;
            redirectToLogin();
        }
    })
    .catch(error => {
        console.error('Error checking authentication:', error);
        redirectToLogin();
    });
}

function setupAuthenticatedUI() {
    // Show authenticated UI elements
    const doctorDropdown = document.getElementById('doctorDropdown');
    if (doctorDropdown) {
        doctorDropdown.style.display = 'flex';
    }
}

// ========== SESSION MANAGEMENT ==========

function startSessionChecks() {
    // Check session every 5 minutes
    sessionCheckInterval = setInterval(() => {
        if (isAuthenticated) {
            verifySessionActive();
        }
    }, 5 * 60 * 1000);
}

function stopSessionChecks() {
    if (sessionCheckInterval) {
        clearInterval(sessionCheckInterval);
    }
}

function verifySessionActive() {
    fetch('/api/auth/check', {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (!data.authenticated) {
            // Session expired
            handleSessionExpired();
        }
    })
    .catch(error => {
        console.error('Error verifying session:', error);
    });
}

function handleSessionExpired() {
    isAuthenticated = false;
    currentDoctor = null;
    alert('La tua sessione è scaduta. Per favore effettua di nuovo il login.');
    redirectToLogin();
}

// ========== NAVIGATION FUNCTIONS ==========

function redirectToLogin() {
    const currentPath = window.location.pathname;
    if (currentPath !== '/' && currentPath !== '/login') {
        window.location.href = '/';
    }
}

function toggleDoctorDropdown() {
    const dropdownMenu = document.getElementById('dropdownMenu');
    if (dropdownMenu) {
        dropdownMenu.classList.toggle('show');
    }
}

// Close dropdown when clicking outside
document.addEventListener('click', function(event) {
    const doctorDropdown = document.getElementById('doctorDropdown');
    if (doctorDropdown && !doctorDropdown.contains(event.target)) {
        const dropdownMenu = document.getElementById('dropdownMenu');
        if (dropdownMenu) {
            dropdownMenu.classList.remove('show');
        }
    }
});

// ========== LOGOUT ==========

async function handleLogout() {
    try {
        const response = await fetch('/api/auth/logout', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });

        if (response.ok) {
            isAuthenticated = false;
            currentDoctor = null;
            stopSessionChecks();
            window.location.href = '/';
        }
    } catch (error) {
        console.error('Error during logout:', error);
        window.location.href = '/';
    }
}

// ========== FUNCTION WRAPPERS FOR PROTECTED FEATURES ==========

function withAuthCheck(callback) {
    if (!isAuthenticated) {
        alert('Devi essere loggato per accedere a questa funzionalità.');
        redirectToLogin();
        return;
    }

    // Verify session is still active
    fetch('/api/auth/check', {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.authenticated) {
            // Session is valid, execute callback
            callback();
        } else {
            // Session expired
            handleSessionExpired();
        }
    })
    .catch(error => {
        console.error('Error checking session:', error);
        alert('Errore di connessione. Verifica la tua connessione.');
    });
}

// ========== PROTECTED FEATURE HANDLERS ==========

function openPatientSearch() {
    withAuthCheck(() => {
        // Load patient search modal - implement based on your modal system
        console.log('Loading patient search...');
    });
}

function openPatientForm() {
    withAuthCheck(() => {
        // Load new patient form modal
        console.log('Loading patient form...');
    });
}

function openAddRecordForm() {
    withAuthCheck(() => {
        // Load add clinical record form modal
        console.log('Loading add record form...');
    });
}

function exportPatientData() {
    withAuthCheck(() => {
        // Load export data modal
        console.log('Loading export...');
    });
}

// ========== UTILITY FUNCTIONS ==========

function updateHeaderWithDoctor(doctor) {
    const doctorNameEl = document.getElementById('doctorName');
    if (doctorNameEl) {
        const fullName = `${doctor.nome} ${doctor.cognome}`;
        doctorNameEl.textContent = fullName;
    }
}

