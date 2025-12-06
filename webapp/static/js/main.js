// EarlyCare Gateway - Web App JavaScript

let currentPatient = null;
let selectedFiles = [];

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    setupDragAndDrop();
    setupCalculateButtonMonitoring();
});

// Monitor form fields for Calculate button activation
function setupCalculateButtonMonitoring() {
    const form = document.getElementById('patient-form');
    if (!form) return;
    
    const fieldsToMonitor = ['nome', 'cognome', 'data_nascita', 'comune_nascita'];
    const calculateBtn = document.getElementById('btn-calculate-cf');
    
    function checkFieldsAndUpdateButton() {
        const nome = form.querySelector('[name="nome"]')?.value.trim();
        const cognome = form.querySelector('[name="cognome"]')?.value.trim();
        const dataNascita = form.querySelector('[name="data_nascita"]')?.value;
        const comuneNascita = form.querySelector('[name="comune_nascita"]')?.value.trim();
        const sesso = form.querySelector('input[name="sesso"]:checked')?.value;
        
        if (nome && cognome && dataNascita && comuneNascita && sesso) {
            calculateBtn?.classList.add('active');
        } else {
            calculateBtn?.classList.remove('active');
        }
    }
    
    // Monitor text inputs
    fieldsToMonitor.forEach(fieldName => {
        const field = form.querySelector(`[name="${fieldName}"]`);
        if (field) {
            field.addEventListener('input', checkFieldsAndUpdateButton);
            field.addEventListener('change', checkFieldsAndUpdateButton);
        }
    });
    
    // Monitor radio buttons
    const radioButtons = form.querySelectorAll('input[name="sesso"]');
    radioButtons.forEach(radio => {
        radio.addEventListener('change', checkFieldsAndUpdateButton);
    });
}

// Modal Functions
function openModal(modalId) {
    document.getElementById(modalId).style.display = 'flex';
}

function closeModal(modalId) {
    document.getElementById(modalId).style.display = 'none';
}

function showLoading() {
    document.getElementById('loading-overlay').style.display = 'flex';
}

function hideLoading() {
    document.getElementById('loading-overlay').style.display = 'none';
}

// Patient Search Functions
function openPatientSearch() {
    openModal('patient-search-modal');
}

function searchPatient() {
    const fiscalCode = document.getElementById('search-fiscal-code').value.trim().toUpperCase();
    
    if (!fiscalCode) {
        showAlert('Inserisci un codice fiscale', 'danger');
        return;
    }
    
    performSearchByFiscalCode(fiscalCode);
}

function performSearch() {
    const fiscalCode = document.getElementById('modal-search-cf').value.trim().toUpperCase();
    
    if (!fiscalCode) {
        showAlert('Inserisci il codice fiscale', 'danger');
        return;
    }
    
    performSearchByFiscalCode(fiscalCode);
    closeModal('patient-search-modal');
}

function performSearchByFiscalCode(fiscalCode) {
    showLoading();
    
    fetch('/api/patient/search', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            fiscal_code: fiscalCode
        })
    })
    .then(response => response.json())
    .then(data => {
        hideLoading();
        
        if (data.success && data.patient) {
            loadPatient(data.patient);
            showAlert('Paziente trovato con successo', 'success');
        } else {
            showAlert(data.message || 'Paziente non trovato', 'danger');
        }
    })
    .catch(error => {
        hideLoading();
        showAlert('Errore durante la ricerca: ' + error.message, 'danger');
    });
}

function displayPatientList(patients) {
    // Hide patient info, show patients list
    document.getElementById('patients-list-section').style.display = 'block';
    document.getElementById('patients-count').textContent = patients.length;
    
    const container = document.getElementById('patients-list');
    container.innerHTML = '';
    
    patients.forEach(patient => {
        const patientCard = document.createElement('div');
        patientCard.className = 'patient-card';
        patientCard.style.cursor = 'pointer';
        patientCard.style.transition = 'all 0.3s ease';
        
        const birthDate = patient.data_nascita ? new Date(patient.data_nascita).toLocaleDateString('it-IT') : 'N/A';
        
        patientCard.innerHTML = `
            <div style="display: flex; justify-content: space-between; align-items: start;">
                <div style="flex: 1;">
                    <h4 style="margin: 0 0 0.5rem 0; color: var(--primary);">
                        <i class="fas fa-user-circle"></i> ${patient.nome} ${patient.cognome}
                    </h4>
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 0.5rem; font-size: 0.9rem;">
                        <div><strong>CF:</strong> ${patient.codice_fiscale}</div>
                        <div><strong>Data Nascita:</strong> ${birthDate}</div>
                        ${patient.comune_nascita ? `<div><strong>Luogo:</strong> ${patient.comune_nascita}</div>` : ''}
                    </div>
                    ${patient.allergie && patient.allergie.length > 0 ? `
                        <div style="margin-top: 0.5rem; font-size: 0.85rem; color: var(--danger);">
                            <i class="fas fa-exclamation-triangle"></i> Allergie: ${patient.allergie.join(', ')}
                        </div>
                    ` : ''}
                </div>
                <div>
                    <span class="badge" style="background-color: var(--success); cursor: pointer;">
                        <i class="fas fa-arrow-right"></i> Seleziona
                    </span>
                </div>
            </div>
        `;
        
        // Hover effect
        patientCard.addEventListener('mouseenter', () => {
            patientCard.style.backgroundColor = 'var(--light)';
            patientCard.style.transform = 'translateX(5px)';
        });
        patientCard.addEventListener('mouseleave', () => {
            patientCard.style.backgroundColor = '';
            patientCard.style.transform = '';
        });
        
        // Click to select
        patientCard.addEventListener('click', () => {
            loadPatient(patient);
            // Hide patients list after selection
            document.getElementById('patients-list-section').style.display = 'none';
            closeModal('patient-search-modal');
            showAlert(`Paziente selezionato: ${patient.nome} ${patient.cognome}`, 'success');
        });
        
        container.appendChild(patientCard);
    });
    
    // Close search modal if open
    closeModal('patient-search-modal');
    showAlert(`Trovati ${patients.length} pazienti omonimi. Seleziona quello corretto.`, 'info');
}

function loadPatient(patient) {
    currentPatient = patient;
    
    // Display patient info
    const patientInfo = `
Nome: ${patient.nome} ${patient.cognome}
Codice Fiscale: ${patient.codice_fiscale}
Data di Nascita: ${patient.data_nascita}
Sesso: ${patient.sesso}
${patient.luogo_nascita ? 'Luogo di Nascita: ' + patient.luogo_nascita : ''}
${patient.indirizzo ? 'Indirizzo: ' + patient.indirizzo : ''}
${patient.telefono ? 'Telefono: ' + patient.telefono : ''}
${patient.email ? 'Email: ' + patient.email : ''}
    `.trim();
    
    document.getElementById('patient-info').innerHTML = `<pre>${patientInfo}</pre>`;
    
    // Enable action buttons
    document.getElementById('btn-add-record').disabled = false;
    document.getElementById('btn-export').disabled = false;
    
    // Load clinical records
    loadClinicalRecords(patient.codice_fiscale);
}

function loadClinicalRecords(fiscalCode) {
    fetch(`/api/patient/${fiscalCode}/records`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                displayClinicalRecords(data.records);
            }
        })
        .catch(error => {
            console.error('Error loading records:', error);
        });
}

function displayClinicalRecords(records) {
    const container = document.getElementById('clinical-records');
    const countBadge = document.getElementById('records-count');
    
    if (!records || records.length === 0) {
        container.innerHTML = '<p class="text-muted">Nessuna scheda clinica disponibile</p>';
        countBadge.textContent = '0';
        return;
    }
    
    // Update count badge
    countBadge.textContent = records.length;
    
    container.innerHTML = records.map((record, index) => {
        const date = new Date(record.timestamp).toLocaleString('it-IT');
        const tipoLabel = record.tipo_scheda || 'Visita';
        return `
            <div class="record-card">
                <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 0.5rem;">
                    <div class="record-date">
                        <i class="fas fa-calendar"></i> ${date}
                    </div>
                    <span class="badge" style="background-color: var(--info);">#${records.length - index}</span>
                </div>
                <h5>${tipoLabel}: ${record.chief_complaint || 'Nessun motivo specificato'}</h5>
                ${record.symptoms ? `<p><strong>Sintomi:</strong> ${record.symptoms}</p>` : ''}
                ${record.diagnosis ? `<p><strong>Diagnosi:</strong> ${record.diagnosis}</p>` : ''}
                ${record.treatment ? `<p><strong>Trattamento:</strong> ${record.treatment}</p>` : ''}
                ${record.notes ? `<p><strong>Note:</strong> ${record.notes}</p>` : ''}
                ${record.vital_signs && Object.keys(record.vital_signs).length > 0 ? `
                    <div style="margin-top: 0.5rem; padding: 0.5rem; background-color: var(--light); border-radius: 4px;">
                        <strong>Parametri Vitali:</strong>
                        ${record.vital_signs.blood_pressure ? `<span style="margin-left: 0.5rem;">PA: ${record.vital_signs.blood_pressure}</span>` : ''}
                        ${record.vital_signs.heart_rate ? `<span style="margin-left: 0.5rem;">FC: ${record.vital_signs.heart_rate} bpm</span>` : ''}
                        ${record.vital_signs.temperature ? `<span style="margin-left: 0.5rem;">T: ${record.vital_signs.temperature}°C</span>` : ''}
                        ${record.vital_signs.oxygen_saturation ? `<span style="margin-left: 0.5rem;">SpO2: ${record.vital_signs.oxygen_saturation}%</span>` : ''}
                    </div>
                ` : ''}
            </div>
        `;
    }).join('');
}

// Patient Form Functions
function openPatientForm() {
    document.getElementById('patient-form').reset();
    openModal('patient-form-modal');
    // Reset calculate button state
    setTimeout(() => {
        const calculateBtn = document.getElementById('btn-calculate-cf');
        if (calculateBtn) {
            calculateBtn.classList.remove('active');
        }
    }, 100);
}

function savePatient() {
    const form = document.getElementById('patient-form');
    const formData = new FormData(form);
    
    if (!form.checkValidity()) {
        form.reportValidity();
        return;
    }
    
    const patientData = {};
    formData.forEach((value, key) => {
        if (value && value.trim() !== '') {
            // Process list fields (allergie, malattie_permanenti)
            if (key === 'allergie' || key === 'malattie_permanenti') {
                // Split by comma or semicolon and trim each item
                const items = value.split(/[,;]/).map(item => item.trim()).filter(item => item);
                patientData[key] = items;
            } else {
                patientData[key] = value;
            }
        }
    });
    
    showLoading();
    
    fetch('/api/patient/create', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(patientData)
    })
    .then(response => response.json())
    .then(data => {
        hideLoading();
        
        if (data.success) {
            showAlert('Paziente creato con successo', 'success');
            closeModal('patient-form-modal');
            // Automatically load the new patient
            performSearchByFiscalCode(patientData.codice_fiscale.toUpperCase());
        } else {
            // Check if error is due to duplicate patient
            if (data.error && data.error.includes('già esistente')) {
                // Patient already exists, close modal and load existing patient
                closeModal('patient-form-modal');
                showAlert('⚠️ Paziente già presente nel database. Caricamento dati...', 'warning');
                // Load the existing patient
                setTimeout(() => {
                    performSearchByFiscalCode(patientData.codice_fiscale.toUpperCase());
                }, 500);
            } else {
                showAlert(data.error || 'Errore durante la creazione del paziente', 'danger');
            }
        }
    })
    .catch(error => {
        hideLoading();
        showAlert('Errore: ' + error.message, 'danger');
    });
}

// Clinical Record Functions
function openAddRecordForm() {
    if (!currentPatient) {
        showAlert('Seleziona prima un paziente', 'danger');
        openPatientSearch();
        return;
    }
    
    document.getElementById('clinical-record-form').reset();
    openModal('add-record-modal');
}

function saveClinicalRecord() {
    if (!currentPatient) {
        showAlert('Nessun paziente selezionato', 'danger');
        return;
    }
    
    const form = document.getElementById('clinical-record-form');
    const formData = new FormData(form);
    
    if (!form.checkValidity()) {
        form.reportValidity();
        return;
    }
    
    const recordData = {
        tipo_scheda: formData.get('tipo_scheda'),
        chief_complaint: formData.get('chief_complaint'),
        symptoms: formData.get('symptoms'),
        diagnosis: formData.get('diagnosis'),
        treatment: formData.get('treatment'),
        notes: formData.get('notes'),
        vital_signs: {
            blood_pressure: formData.get('blood_pressure'),
            heart_rate: formData.get('heart_rate'),
            temperature: formData.get('temperature'),
            oxygen_saturation: formData.get('oxygen_saturation')
        }
    };
    
    showLoading();
    
    fetch(`/api/patient/${currentPatient.codice_fiscale}/add-record`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(recordData)
    })
    .then(response => response.json())
    .then(data => {
        hideLoading();
        
        if (data.success) {
            showAlert('Scheda clinica aggiunta con successo', 'success');
            closeModal('add-record-modal');
            loadClinicalRecords(currentPatient.codice_fiscale);
        } else {
            showAlert(data.error || 'Errore durante il salvataggio', 'danger');
        }
    })
    .catch(error => {
        hideLoading();
        showAlert('Errore: ' + error.message, 'danger');
    });
}

// File Upload Functions
function setupDragAndDrop() {
    const uploadArea = document.getElementById('upload-area');
    
    if (!uploadArea) return;
    
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        uploadArea.addEventListener(eventName, preventDefaults, false);
    });
    
    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }
    
    ['dragenter', 'dragover'].forEach(eventName => {
        uploadArea.addEventListener(eventName, () => {
            uploadArea.classList.add('drag-over');
        });
    });
    
    ['dragleave', 'drop'].forEach(eventName => {
        uploadArea.addEventListener(eventName, () => {
            uploadArea.classList.remove('drag-over');
        });
    });
    
    uploadArea.addEventListener('drop', handleDrop);
}

function handleDrop(e) {
    const dt = e.dataTransfer;
    const files = dt.files;
    handleFiles(files);
}

function handleFileSelect(event) {
    const files = event.target.files;
    handleFiles(files);
}

function handleFiles(files) {
    selectedFiles = Array.from(files);
    displayFilesList();
}

function displayFilesList() {
    const filesList = document.getElementById('files-list');
    
    if (selectedFiles.length === 0) {
        filesList.innerHTML = '';
        return;
    }
    
    filesList.innerHTML = `
        <div style="margin-top: 1rem;">
            <h4>File Selezionati (${selectedFiles.length})</h4>
            ${selectedFiles.map((file, index) => `
                <div class="file-item">
                    <span>
                        <i class="fas fa-file"></i> ${file.name} (${formatFileSize(file.size)})
                    </span>
                    <button class="btn btn-danger" onclick="removeFile(${index})" style="padding: 0.25rem 0.5rem;">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
            `).join('')}
            <button class="btn btn-primary" onclick="uploadFiles()" style="margin-top: 1rem;">
                <i class="fas fa-upload"></i> Carica File
            </button>
        </div>
    `;
}

function removeFile(index) {
    selectedFiles.splice(index, 1);
    displayFilesList();
}

function uploadFiles() {
    if (!currentPatient) {
        showAlert('Seleziona prima un paziente', 'danger');
        return;
    }
    
    if (selectedFiles.length === 0) {
        showAlert('Nessun file selezionato', 'danger');
        return;
    }
    
    const formData = new FormData();
    formData.append('fiscal_code', currentPatient.codice_fiscale);
    
    if (selectedFiles.length === 1) {
        // Single file upload
        formData.append('file', selectedFiles[0]);
        uploadSingleFile(formData);
    } else {
        // Multiple files (folder) upload
        selectedFiles.forEach(file => {
            formData.append('files[]', file);
        });
        uploadFolder(formData);
    }
}

function uploadSingleFile(formData) {
    showLoading();
    
    fetch('/api/file/upload', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        hideLoading();
        
        if (data.success) {
            showAlert('File caricato ed elaborato con successo', 'success');
            selectedFiles = [];
            displayFilesList();
            loadClinicalRecords(currentPatient.codice_fiscale);
        } else {
            showAlert(data.error || 'Errore durante il caricamento', 'danger');
        }
    })
    .catch(error => {
        hideLoading();
        showAlert('Errore: ' + error.message, 'danger');
    });
}

function uploadFolder(formData) {
    showLoading();
    
    fetch('/api/folder/upload', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        hideLoading();
        
        if (data.success) {
            showAlert('Cartella caricata ed elaborata con successo', 'success');
            selectedFiles = [];
            displayFilesList();
            loadClinicalRecords(currentPatient.codice_fiscale);
        } else {
            showAlert(data.error || 'Errore durante il caricamento', 'danger');
        }
    })
    .catch(error => {
        hideLoading();
        showAlert('Errore: ' + error.message, 'danger');
    });
}

// Export Functions
function exportPatientData() {
    if (!currentPatient) {
        showAlert('Nessun paziente selezionato', 'danger');
        return;
    }
    
    window.location.href = `/api/export/${currentPatient.codice_fiscale}`;
}

// Metrics Functions
function showMetrics() {
    openModal('metrics-modal');
    loadMetrics();
}

function loadMetrics() {
    fetch('/api/metrics')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                displayMetrics(data.metrics);
            } else {
                document.getElementById('metrics-content').innerHTML = 
                    '<p class="text-muted">Nessuna metrica disponibile</p>';
            }
        })
        .catch(error => {
            document.getElementById('metrics-content').innerHTML = 
                `<p class="text-muted">Errore: ${error.message}</p>`;
        });
}

function displayMetrics(metrics) {
    const content = document.getElementById('metrics-content');
    
    content.innerHTML = `
        <div class="info-box">
            <pre>${JSON.stringify(metrics, null, 2)}</pre>
        </div>
    `;
}

// Fiscal Code Calculation
function calculateFiscalCode() {
    const nome = document.getElementsByName('nome')[0].value.trim().toUpperCase();
    const cognome = document.getElementsByName('cognome')[0].value.trim().toUpperCase();
    const dataNascita = document.getElementsByName('data_nascita')[0].value;
    const comuneNascita = document.getElementById('comune_nascita').value.trim().toUpperCase();
    const sessoRadio = document.querySelector('input[name="sesso"]:checked');
    const sesso = sessoRadio ? sessoRadio.value : '';
    
    if (!nome || !cognome || !dataNascita || !comuneNascita || !sesso) {
        showAlert('Compilare Nome, Cognome, Data di Nascita, Comune di Nascita e Sesso prima di calcolare il codice fiscale', 'danger');
        return;
    }
    
    try {
        const [year, month, day] = dataNascita.split('-').map(Number);
        
        // Step 1: Cognome (3 lettere)
        const cognomeCode = encodeSurname(cognome);
        
        // Step 2: Nome (3 lettere)
        const nomeCode = encodeName(nome);
        
        // Step 3: Anno (ultime 2 cifre)
        const annoCode = String(year % 100).padStart(2, '0');
        
        // Step 4: Mese (lettera)
        const monthCodes = ['A', 'B', 'C', 'D', 'E', 'H', 'L', 'M', 'P', 'R', 'S', 'T'];
        const meseCode = monthCodes[month - 1];
        
        // Step 5: Giorno (+ 40 per femmine)
        const giornoCode = String(day + (sesso === 'F' ? 40 : 0)).padStart(2, '0');
        
        // Step 6: Comune (codice catastale)
        const comuneCode = getCadastralCode(comuneNascita);
        
        // Primi 15 caratteri
        const partialCode = cognomeCode + nomeCode + annoCode + meseCode + giornoCode + comuneCode;
        
        // Step 7: Carattere di controllo
        const checkChar = calculateCheckCharacter(partialCode);
        
        // Codice fiscale completo
        const codiceFiscale = partialCode + checkChar;
        
        document.getElementById('codice_fiscale').value = codiceFiscale;
        showAlert('Codice fiscale calcolato con successo', 'success');
    } catch (error) {
        showAlert('Errore nel calcolo del codice fiscale: ' + error.message, 'danger');
    }
}

function encodeSurname(surname) {
    surname = surname.replace(/[^A-Z]/g, '');
    const consonants = surname.replace(/[AEIOU]/g, '');
    const vowels = surname.replace(/[^AEIOU]/g, '');
    return (consonants + vowels + 'XXX').substring(0, 3);
}

function encodeName(name) {
    name = name.replace(/[^A-Z]/g, '');
    const consonants = name.replace(/[AEIOU]/g, '');
    const vowels = name.replace(/[^AEIOU]/g, '');
    
    if (consonants.length >= 4) {
        return consonants[0] + consonants[2] + consonants[3];
    } else {
        return (consonants + vowels + 'XXX').substring(0, 3);
    }
}

function getCadastralCode(birthplace) {
    const cadastralCodes = {
        'ROMA': 'H501', 'MILANO': 'F205', 'NAPOLI': 'F839', 'TORINO': 'L219',
        'PALERMO': 'G273', 'GENOVA': 'D969', 'BOLOGNA': 'A944', 'FIRENZE': 'D612',
        'BARI': 'A662', 'CATANIA': 'C351', 'VENEZIA': 'L736', 'VERONA': 'L781',
        'MESSINA': 'F158', 'PADOVA': 'G224', 'TRIESTE': 'L424', 'BRESCIA': 'B157',
        'PARMA': 'G337', 'TARANTO': 'L049', 'PRATO': 'G999', 'MODENA': 'F257',
        'REGGIO CALABRIA': 'H224', 'REGGIO EMILIA': 'H223', 'PERUGIA': 'G478',
        'LIVORNO': 'E625', 'RAVENNA': 'H199', 'CAGLIARI': 'B354', 'FOGGIA': 'D643',
        'RIMINI': 'H294', 'SALERNO': 'H703', 'FERRARA': 'D548', 'SASSARI': 'I452',
        'MONZA': 'F704', 'SIRACUSA': 'I754', 'PESCARA': 'G482', 'BERGAMO': 'A794',
        'TRENTO': 'L378', 'FORLI': 'D704', 'VICENZA': 'L840', 'TERNI': 'L117',
        'BOLZANO': 'A952', 'NOVARA': 'F952', 'PIACENZA': 'G535', 'ANCONA': 'A271',
        'ANDRIA': 'A285', 'AREZZO': 'A390', 'UDINE': 'L483', 'CESENA': 'C573',
        'LECCE': 'E506', 'PESARO': 'G479', 'BARLETTA': 'A669', 'ALESSANDRIA': 'A182',
        'LA SPEZIA': 'E463', 'PISA': 'G702', 'CATANZARO': 'C352', 'PISTOIA': 'G713',
        'LUCCA': 'E715', 'BRINDISI': 'B180', 'COMO': 'C933', 'VARESE': 'L682'
    };
    
    const clean = birthplace.replace(/[^A-Z ]/g, '').trim();
    
    if (cadastralCodes[clean]) {
        return cadastralCodes[clean];
    }
    
    // Genera codice semplificato per comuni non in lista
    const compact = clean.replace(/ /g, '');
    if (compact) {
        const firstLetter = compact[0];
        const hash = Math.abs(compact.split('').reduce((acc, c) => acc + c.charCodeAt(0), 0));
        const digits = String(hash % 1000).padStart(3, '0');
        return firstLetter + digits;
    }
    
    return 'Z999';
}

function calculateCheckCharacter(code) {
    const oddValues = {
        '0': 1, '1': 0, '2': 5, '3': 7, '4': 9, '5': 13, '6': 15, '7': 17, '8': 19, '9': 21,
        'A': 1, 'B': 0, 'C': 5, 'D': 7, 'E': 9, 'F': 13, 'G': 15, 'H': 17, 'I': 19, 'J': 21,
        'K': 2, 'L': 4, 'M': 18, 'N': 20, 'O': 11, 'P': 3, 'Q': 6, 'R': 8, 'S': 12, 'T': 14,
        'U': 16, 'V': 10, 'W': 22, 'X': 25, 'Y': 24, 'Z': 23
    };
    
    const evenValues = {
        '0': 0, '1': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9,
        'A': 0, 'B': 1, 'C': 2, 'D': 3, 'E': 4, 'F': 5, 'G': 6, 'H': 7, 'I': 8, 'J': 9,
        'K': 10, 'L': 11, 'M': 12, 'N': 13, 'O': 14, 'P': 15, 'Q': 16, 'R': 17, 'S': 18, 'T': 19,
        'U': 20, 'V': 21, 'W': 22, 'X': 23, 'Y': 24, 'Z': 25
    };
    
    const checkLetters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ';
    
    let total = 0;
    for (let i = 0; i < code.length; i++) {
        const char = code[i];
        if (i % 2 === 0) {
            total += oddValues[char] || 0;
        } else {
            total += evenValues[char] || 0;
        }
    }
    
    return checkLetters[total % 26];
}

// Utility Functions
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}

function showAlert(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type}`;
    alertDiv.textContent = message;
    
    const mainContent = document.querySelector('.main-content');
    mainContent.insertBefore(alertDiv, mainContent.firstChild);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        alertDiv.remove();
    }, 5000);
}

// Close modals when clicking outside
window.onclick = function(event) {
    if (event.target.classList.contains('modal')) {
        event.target.style.display = 'none';
    }
}
