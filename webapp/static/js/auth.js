// Authentication JavaScript

let isAuthenticated = false;
let currentDoctor = null;

// Initialize authentication on page load
document.addEventListener('DOMContentLoaded', function() {
    checkAuthentication();
    setupAuthEventListeners();
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
            hideAuthModal();
            updateHeaderWithDoctor(data.doctor);
        } else {
            isAuthenticated = false;
            showAuthModal();
        }
    })
    .catch(error => {
        console.error('Error checking authentication:', error);
        showAuthModal();
    });
}

// ========== AUTH MODAL MANAGEMENT ==========

function showAuthModal() {
    const modal = document.getElementById('auth-modal');
    if (modal) {
        modal.style.display = 'flex';
        // Prevent body scroll
        document.body.style.overflow = 'hidden';
    }
}

function hideAuthModal() {
    const modal = document.getElementById('auth-modal');
    if (modal) {
        modal.style.display = 'none';
        // Re-enable body scroll
        document.body.style.overflow = 'auto';
    }
}

function switchToLogin() {
    document.getElementById('registration-form-container').style.display = 'none';
    document.getElementById('registration-success-container').style.display = 'none';
    document.getElementById('login-form-container').style.display = 'block';
    
    // Clear error messages
    const errorDiv = document.getElementById('login-error');
    if (errorDiv) {
        errorDiv.style.display = 'none';
        errorDiv.textContent = '';
    }
}

function switchToRegistration() {
    document.getElementById('login-form-container').style.display = 'none';
    document.getElementById('registration-form-container').style.display = 'block';
    
    // Clear error messages
    const errorDiv = document.getElementById('registration-error');
    if (errorDiv) {
        errorDiv.style.display = 'none';
        errorDiv.textContent = '';
    }
}

// ========== EVENT LISTENERS ==========

function setupAuthEventListeners() {
    // Login form submission
    const loginForm = document.getElementById('login-form');
    if (loginForm) {
        loginForm.addEventListener('submit', handleLoginSubmit);
    }

    // Registration form submission
    const registrationForm = document.getElementById('registration-form');
    if (registrationForm) {
        registrationForm.addEventListener('submit', handleRegistrationSubmit);
    }

    // Prevent modal closing by clicking outside
    const authModal = document.getElementById('auth-modal');
    if (authModal) {
        authModal.addEventListener('click', function(e) {
            if (e.target === authModal) {
                // Prevent closing the modal
                e.preventDefault();
            }
        });
    }
}

// ========== LOGIN ==========

async function handleLoginSubmit(e) {
    e.preventDefault();

    const doctorId = document.getElementById('login-doctor-id').value.trim();
    const password = document.getElementById('login-password').value;
    const errorDiv = document.getElementById('login-error');

    if (!doctorId || !password) {
        showError(errorDiv, 'Inserisci ID medico e password');
        return;
    }

    try {
        const response = await fetch('/api/auth/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                doctor_id: doctorId,
                password: password
            })
        });

        const data = await response.json();

        if (!response.ok) {
            showError(errorDiv, data.error || 'Errore durante il login');
            return;
        }

        // Login successful
        isAuthenticated = true;
        currentDoctor = data.doctor;
        
        // Clear form
        document.getElementById('login-form').reset();
        hideAuthModal();
        updateHeaderWithDoctor(data.doctor);
        showAlert('Accesso effettuato con successo', 'success');

        // Reload page to show main content
        setTimeout(() => {
            location.reload();
        }, 500);

    } catch (error) {
        console.error('Login error:', error);
        showError(errorDiv, 'Errore di comunicazione con il server');
    }
}

// ========== REGISTRATION ==========

async function handleRegistrationSubmit(e) {
    e.preventDefault();

    const nome = document.getElementById('reg-nome').value.trim();
    const cognome = document.getElementById('reg-cognome').value.trim();
    const specializzazione = document.getElementById('reg-specializzazione').value.trim();
    const ospedale = document.getElementById('reg-ospedale').value.trim();
    const password = document.getElementById('reg-password').value;
    const passwordConfirm = document.getElementById('reg-password-confirm').value;
    const errorDiv = document.getElementById('registration-error');

    // Validate required fields
    if (!nome || !cognome || !specializzazione || !ospedale || !password) {
        showError(errorDiv, 'Compila tutti i campi obbligatori');
        return;
    }

    // Validate password
    if (password.length < 6) {
        showError(errorDiv, 'La password deve contenere almeno 6 caratteri');
        return;
    }

    if (password !== passwordConfirm) {
        showError(errorDiv, 'Le password non corrispondono');
        return;
    }

    try {
        const response = await fetch('/api/auth/register', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                nome: nome,
                cognome: cognome,
                specializzazione: specializzazione,
                ospedale_affiliato: ospedale,
                password: password
            })
        });

        const data = await response.json();

        if (!response.ok) {
            showError(errorDiv, data.error || 'Errore durante la registrazione');
            return;
        }

        // Registration successful - show success message
        showRegistrationSuccess(data.doctor_id, data.doctor_info);

    } catch (error) {
        console.error('Registration error:', error);
        showError(errorDiv, 'Errore di comunicazione con il server');
    }
}

function showRegistrationSuccess(doctorId, doctorInfo) {
    // Hide registration form
    document.getElementById('registration-form-container').style.display = 'none';
    
    // Show success message
    const successContainer = document.getElementById('registration-success-container');
    successContainer.style.display = 'block';
    
    // Update doctor ID display
    document.getElementById('new-doctor-id').textContent = doctorId;
    
    // Update doctor info
    const infoDiv = document.getElementById('success-doctor-info');
    infoDiv.innerHTML = `
        <p><strong>Nome:</strong> ${doctorInfo.nome} ${doctorInfo.cognome}</p>
        <p><strong>Specializzazione:</strong> ${doctorInfo.specializzazione}</p>
        <p><strong>Ospedale:</strong> ${doctorInfo.ospedale_affiliato}</p>
    `;
    
    // Clear registration form
    document.getElementById('registration-form').reset();
    
    // Scroll to top of modal
    const modal = document.querySelector('.auth-modal-content');
    if (modal) {
        modal.scrollTop = 0;
    }
}

// ========== PASSWORD VISIBILITY TOGGLE ==========

function togglePasswordVisibility(inputId) {
    const input = document.getElementById(inputId);
    const button = event.target.closest('.toggle-password');
    
    if (input.type === 'password') {
        input.type = 'text';
        button.innerHTML = '<i class="fas fa-eye-slash"></i>';
    } else {
        input.type = 'password';
        button.innerHTML = '<i class="fas fa-eye"></i>';
    }
}

// ========== COPY TO CLIPBOARD ==========

function copyDoctorId() {
    const doctorIdElement = document.getElementById('new-doctor-id');
    if (!doctorIdElement) {
        showAlert('Errore: ID non trovato', 'danger');
        return;
    }
    
    const doctorId = doctorIdElement.textContent.trim();
    
    if (!doctorId) {
        showAlert('Errore: ID vuoto', 'danger');
        return;
    }
    
    // Usa l'API moderna clipboard se disponibile
    if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(doctorId)
            .then(() => {
                const button = event.target.closest('.copy-btn');
                if (button) {
                    const originalHTML = button.innerHTML;
                    
                    button.innerHTML = '<i class="fas fa-check"></i>';
                    button.style.backgroundColor = 'var(--success)';
                    
                    setTimeout(() => {
                        button.innerHTML = originalHTML;
                        button.style.backgroundColor = '';
                    }, 2000);
                }
                
                showAlert('ID medico copiato negli appunti', 'success');
            })
            .catch(error => {
                console.error('Error copying to clipboard:', error);
                // Fallback se l'API moderna fallisce
                fallbackCopyToClipboard(doctorId);
            });
    } else {
        // Fallback per browser più vecchi
        fallbackCopyToClipboard(doctorId);
    }
}

// Funzione di fallback per la copia negli appunti
function fallbackCopyToClipboard(text) {
    const textArea = document.createElement('textarea');
    textArea.value = text;
    textArea.style.position = 'fixed';
    textArea.style.left = '-999999px';
    textArea.style.top = '-999999px';
    document.body.appendChild(textArea);
    textArea.focus();
    textArea.select();
    
    try {
        const successful = document.execCommand('copy');
        document.body.removeChild(textArea);
        
        if (successful) {
            const button = event.target.closest('.copy-btn');
            if (button) {
                const originalHTML = button.innerHTML;
                
                button.innerHTML = '<i class="fas fa-check"></i>';
                button.style.backgroundColor = 'var(--success)';
                
                setTimeout(() => {
                    button.innerHTML = originalHTML;
                    button.style.backgroundColor = '';
                }, 2000);
            }
            
            showAlert('ID medico copiato negli appunti', 'success');
        } else {
            showAlert('Errore nella copia dell\'ID', 'danger');
        }
    } catch (err) {
        document.body.removeChild(textArea);
        console.error('Fallback copy failed:', err);
        showAlert('Impossibile copiare. Copia manualmente l\'ID: ' + text, 'warning');
    }
}

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
            showAlert('Logout effettuato', 'success');
            
            // Reload page to show login modal
            setTimeout(() => {
                location.reload();
            }, 500);
        }
    } catch (error) {
        console.error('Logout error:', error);
        showAlert('Errore durante il logout', 'danger');
    }
}

// ========== HEADER UPDATE ==========

function updateHeaderWithDoctor(doctor) {
    const headerRight = document.querySelector('.header-right');
    if (!headerRight) return;

    // Check if we should update the header (don't duplicate if already updated)
    if (headerRight.querySelector('.doctor-info-display')) {
        return;
    }

    // Find the status indicator
    const statusIndicator = headerRight.querySelector('.status-indicator');
    
    if (statusIndicator) {
        // Insert doctor info and logout button before status indicator
        const doctorInfoHTML = `
            <div class="header-right-auth">
                <div class="doctor-info-display">
                    <div class="doctor-name"><i class="fas fa-user-md"></i> Dott. ${doctor.nome} ${doctor.cognome}</div>
                    <div style="font-size: 0.8rem; opacity: 0.8;">${doctor.specializzazione}</div>
                </div>
                <button onclick="handleLogout()" class="logout-btn">
                    <i class="fas fa-sign-out-alt"></i> Esci
                </button>
            </div>
        `;
        
        statusIndicator.insertAdjacentHTML('beforebegin', doctorInfoHTML);
    }
}

// ========== UTILITY FUNCTIONS ==========

function checkAuthAndExecute(callback) {
    /**
     * Controlla se l'utente è autenticato.
     * Se sì, esegue la callback.
     * Se no, mostra il modal di login.
     */
    if (isAuthenticated && currentDoctor) {
        // Utente autenticato - esegui la funzione
        if (typeof callback === 'function') {
            callback();
        }
    } else {
        // Utente non autenticato - mostra modal
        showAuthModal();
        switchToLogin();
    }
    return false;
}

function showError(errorDiv, message) {
    if (errorDiv) {
        errorDiv.textContent = message;
        errorDiv.style.display = 'block';
        
        // Auto-hide after 5 seconds
        setTimeout(() => {
            errorDiv.style.display = 'none';
        }, 5000);
    }
}

function showAlert(message, type = 'info') {
    // Use the existing showAlert function from main.js if available
    if (typeof window.showAlert === 'function') {
        window.showAlert(message, type);
    } else {
        console.log(`[${type.toUpperCase()}] ${message}`);
    }
}

