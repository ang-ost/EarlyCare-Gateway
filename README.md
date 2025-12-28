# EarlyCare Gateway - Early Disease Diagnosis System

![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![HIPAA Compliant](https://img.shields.io/badge/HIPAA-Compliant-brightgreen)

## 📋 Table of Contents

- [Overview](#overview)
- [Key Features](#-key-features)
- [Architecture](#-architecture)
- [Quick Start](#-quick-start)
- [Web Application](#-web-application)
- [Authentication System](#-authentication-system)
- [Management Scripts](#-management-scripts)
- [Database Implementation](#-database-implementation)
- [Project Summary](#-project-summary)
- [Clinical System Integration](#-clinical-system-integration)
- [Security & Privacy](#-security--privacy)
- [Configuration](#-configuration)
- [Testing](#-testing)
- [Contributing](#-contributing)
- [License](#-license)

## Overview

EarlyCare Gateway is an intelligent clinical data routing system designed for early disease diagnosis. It routes clinical data (text, signals, images) through configurable checks and enrichments before providing AI-powered decision support. The system emphasizes **privacy**, **traceability**, and **configurable response times** while keeping AI models swappable by pathology, device, or domain.

**Production-ready system** with comprehensive MongoDB persistence, web application interface, and enterprise-grade architecture.

## 🎯 Key Features

- **Multi-Modal Data Support**: Handles text (clinical notes), signals (ECG, EEG), and images (CT, MRI, X-rays)
- **Intelligent Routing**: Chain of Responsibility pattern for flexible data processing pipelines
- **Swappable AI Models**: Strategy pattern allows models to be changed by pathology, device, or clinical domain
- **Real-Time Monitoring**: Observer pattern for metrics, audit trails, and performance tracking
- **Clinical System Integration**: Facade pattern for seamless HL7, FHIR, and DICOM integration
- **HIPAA Compliant**: Built-in anonymization, encryption, and comprehensive audit logging
- **Configurable Triage**: Automatic patient prioritization with configurable response times

## 🏗️ Architecture

### Design Patterns

1. **Chain of Responsibility**: Data flows through validation → enrichment → triage → processing
2. **Strategy**: AI models are swappable based on pathology, device type, or clinical domain
3. **Observer**: Real-time monitoring of system performance, metrics, and audit events
4. **Facade**: Unified interface for HL7, FHIR, and DICOM clinical systems

### System Components

```
EarlyCare-Gateway/
├── src/
│   ├── models/           # Domain models (Patient, ClinicalData, DecisionSupport)
│   ├── gateway/          # Core gateway and chain handlers
│   ├── strategy/         # AI model strategies (pathology, device, domain)
│   ├── observer/         # Monitoring and audit observers
│   ├── facade/           # Clinical system adapters (HL7, FHIR, DICOM)
│   └── privacy/          # Security (anonymization, encryption, audit)
├── config/               # Configuration files
├── examples/             # Usage examples
└── tests/                # Unit and integration tests
```

## 🚀 Quick Start

### Opzione 1: Docker (Consigliato) 🐳

Il modo più semplice per avviare EarlyCare Gateway è usando Docker:

```bash
# Avvia tutti i servizi (Backend, Frontend, MongoDB)
docker-compose up -d

# Verifica lo stato
docker-compose ps
```

Accedi all'applicazione:
- **Frontend**: http://localhost
- **Backend API**: http://localhost:5000
- **MongoDB**: localhost:27017

Per maggiori dettagli, consulta la sezione [Docker Setup](#-docker-setup) più avanti.

### Opzione 2: Installazione Manuale

```bash
# Clone the repository
git clone https://github.com/your-org/earlycare-gateway.git
cd earlycare-gateway

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Initialize MongoDB database (optional, for persistence)
python scripts/initialize_database.py
```

### MongoDB Setup (Optional)

Per abilitare la persistenza dei dati con MongoDB:

1. **Installa MongoDB**: https://www.mongodb.com/try/download/community
2. **Avvia MongoDB**: 
   ```bash
   # Windows
   net start MongoDB
   
   # Linux/Mac
   sudo systemctl start mongod
   ```
3. **Inizializza il database**:
   ```bash
   python scripts/initialize_database.py
   ```

Consulta [MONGODB_SETUP.md](MONGODB_SETUP.md) e [MONGODB_SCHEMAS.md](MONGODB_SCHEMAS.md) per dettagli completi.

### Basic Usage

```python
from src.gateway.clinical_gateway import ClinicalGateway
from src.models.patient import Patient, PatientRecord
from src.models.clinical_data import TextData, DataSource
from src.strategy.strategy_selector import StrategySelector
from src.observer.metrics_observer import MetricsObserver, AuditObserver
from datetime import datetime

# Initialize gateway
gateway = ClinicalGateway()

# Set up monitoring
metrics = MetricsObserver()
audit = AuditObserver()
gateway.attach_observer(metrics)
gateway.attach_observer(audit)

# Configure model strategy
strategy_selector = StrategySelector.create_default_selector()
gateway.set_strategy_selector(strategy_selector)

# Create patient record
patient = Patient(
    patient_id="P12345",
    date_of_birth=datetime(1975, 6, 15),
    gender=Gender.MALE,
    medical_record_number="MRN-12345",
    chief_complaint="Chest pain and shortness of breath"
)

record = PatientRecord(patient=patient, priority="urgent")

# Add clinical data
clinical_note = TextData(
    data_id="NOTE-001",
    patient_id="P12345",
    timestamp=datetime.now(),
    source=DataSource.EHR,
    text_content="Patient presents with chest pain radiating to left arm...",
    document_type="emergency_note"
)
record.add_clinical_data(clinical_note)

# Process through gateway
decision_support = gateway.process_request(record)

# View results
print(f"Urgency: {decision_support.urgency_level.value}")
print(f"Top Diagnosis: {decision_support.get_top_diagnosis().condition}")
print(f"Processing Time: {decision_support.processing_time_ms:.2f}ms")
```

## 📊 Processing Pipeline

The gateway routes clinical data through a configurable chain:

1. **ValidationHandler**: Validates data quality and completeness
2. **EnrichmentHandler**: Adds context and metadata
3. **TriageHandler**: Calculates urgency scores
4. **PrivacyCheckHandler**: Ensures compliance and anonymization
5. **Strategy Execution**: AI models analyze data and generate diagnosis

## 🔒 Security & Privacy

### HIPAA Compliance

- **Data Anonymization**: Automatic PII removal and pseudonymization
- **Encryption**: AES-256 encryption for data at rest and in transit
- **Audit Logging**: Comprehensive, tamper-evident audit trails
- **Access Control**: Role-based access with full audit

### Example: Anonymizing Patient Data

```python
from src.privacy.anonymizer import DataAnonymizer

anonymizer = DataAnonymizer()

# Anonymize text
anonymized_text = anonymizer.anonymize_text(
    "Patient John Doe, SSN 123-45-6789, called from 555-123-4567"
)
# Result: "Patient [NAME], SSN [SSN-REDACTED], called from [PHONE-REDACTED]"

# Generate pseudonym
pseudonym = anonymizer.generate_pseudonym("P12345", "patient")
# Result: "ANON_PATIENT_a3f2c1b..."
```

## 🔌 Clinical System Integration

### Connecting to FHIR Server

```python
from src.facade.clinical_facade import ClinicalSystemFacade

facade = ClinicalSystemFacade()

# Connect to FHIR server
facade.connect_to_system('fhir', {
    'base_url': 'https://fhir.hospital.org/api',
    'api_key': 'your-api-key'
})

# Import patient data
record = facade.import_patient_data('fhir', 'Patient/12345')

# Process through gateway
decision_support = gateway.process_request(record)

# Export results back to EHR
facade.export_decision_support('fhir', decision_support, 'Patient/12345')
```

## 📈 Monitoring & Observability

### Real-Time Metrics

```python
from src.observer.metrics_observer import MetricsObserver, PerformanceObserver

# Attach observers
metrics = MetricsObserver()
performance = PerformanceObserver(alert_threshold_ms=5000)

gateway.attach_observer(metrics)
gateway.attach_observer(performance)

# Get metrics after processing
stats = metrics.get_metrics()
print(f"Total Requests: {stats['requests_total']}")
print(f"Avg Processing Time: {stats['avg_processing_time_ms']:.2f}ms")
print(f"Success Rate: {stats['success_rate']:.2%}")
```

## 🧠 AI Model Strategies

### Swappable Models by Domain

```python
from src.strategy.model_strategy import DomainStrategy, PathologyStrategy
from src.strategy.strategy_selector import StrategySelector

# Create custom strategy selector
selector = StrategySelector()

# Register domain-specific strategies
selector.register_strategy(DomainStrategy("cardiology"))
selector.register_strategy(DomainStrategy("neurology"))
selector.register_strategy(PathologyStrategy("cancer"))

# Enable ensemble mode for multiple models
selector.enable_ensemble(True)

gateway.set_strategy_selector(selector)
```

## 🧪 Testing

```bash
# Run unit tests
pytest tests/unit

# Run integration tests
pytest tests/integration

# Run with coverage
pytest --cov=src tests/
```

## 📝 Configuration

Configuration files are located in `config/`:

- `gateway_config.yaml`: Gateway and chain settings
- `models_config.yaml`: AI model configurations
- `privacy_config.yaml`: Security and privacy settings
- `integrations_config.yaml`: Clinical system connections

## 🔧 Advanced Features

### Custom Chain Handlers

```python
from src.gateway.chain_handler import ChainHandler

class CustomValidationHandler(ChainHandler):
    def _process(self, record, context):
        # Custom validation logic
        return record

# Add to gateway
gateway.set_processing_chain([
    CustomValidationHandler(),
    EnrichmentHandler(),
    TriageHandler()
])
```

### Performance Tuning

- Configure response time thresholds
- Enable/disable specific validators
- Adjust triage scoring weights
- Control model ensemble behavior

## 📄 License

This project is licensed under the MIT License - see LICENSE file for details.

## 🤝 Contributing

Contributions are welcome! Please read CONTRIBUTING.md for guidelines.

## 📞 Support

For questions and support, please open an issue on GitHub or contact the development team.

## ⚠️ Disclaimer

This system is designed for clinical decision support and should not replace professional medical judgment. All diagnoses should be reviewed by qualified healthcare professionals.

---

## 🌐 Web Application

EarlyCare Gateway includes a complete **Web Application** built with Flask for browser-based access.

### 🚀 Starting the Web App

#### Method 1: PowerShell Script (Recommended)
```powershell
.\start_webapp.ps1
```

#### Method 2: Direct Python
```powershell
python run_webapp.py
```

### 🌍 Access the Application

After starting, open your browser at:
- **http://localhost:5000**
- **http://127.0.0.1:5000**

### 🔐 Authentication System

The web application includes a **secure doctor authentication system** with login and registration features:

#### Doctor ID Generation

Each doctor receives a **unique 6-character ID** generated automatically during registration:

**Format**: `MMXXXX` where:
- **M** = First letter of first name (uppercase)
- **M** = First letter of last name (uppercase)
- **XXXX** = 4 random alphanumeric characters (A-Z, 0-9)

**Examples**:
- Doctor: Mario Rossi → `MR7X9Z`
- Doctor: Giovanni Bianchi → `GB2A5K`
- Doctor: Laura Ferrari → `LF1M8P`

**Security Features**:
- ✅ No special characters (safe for all systems)
- ✅ 36^4 ≈ 1.7 million possible combinations
- ✅ Automatic generation (no user input required)
- ✅ Unique per registration
- ✅ Human-readable format

#### Login & Registration

**First Access**:
1. Open http://localhost:5000
2. See blocking authentication modal
3. Click "Registrazione" (Registration)
4. Enter details:
   - First name (Nome)
   - Last name (Cognome)
   - Specialization (Specializzazione) - from dropdown
   - Hospital/Clinic (Ospedale Affiliato)
   - Password (minimum requirements)
5. System auto-generates and displays your Doctor ID
6. **Copy and save your ID** - needed for future logins

**Subsequent Access**:
1. Enter your Doctor ID
2. Enter your password
3. Click "Login"
4. Access all app features

#### Protected Features

The following navbar features require authentication:
- 🔒 Search Patient (Cerca Paziente)
- 🔒 New Patient (Nuovo Paziente)
- 🔒 Add Clinical Record (Aggiungi Scheda)
- 🔒 Export Data (Esporta)
- ✓ Home (always accessible)

#### Session Management

- **Session Duration**: 7 days (persistent)
- **Logout**: Clears session and shows login modal
- **Security**: Passwords hashed with SHA-256
- **Cookies**: HttpOnly, secure cookies

### ✨ Web App Features

#### 1. **Patient Management** (Authenticated)
- Search patients by fiscal code or name/surname
- Add new patients with complete demographics
- View patient information

#### 2. **Clinical Records**
- Create new clinical records
- View patient's clinical history
- Input complete clinical data:
  - Visit reason
  - Current symptoms
  - Diagnosis
  - Treatment
  - Vital signs
  - Additional notes

#### 3. **File Management**
- Upload single files
- Upload complete clinical folders (drag & drop)
- Automatic file processing
- Clinical gateway integration

#### 4. **Data Export**
- Export complete patient data in JSON format
- Includes all clinical records and associated data

#### 5. **System Monitoring**
- View system metrics
- Database connection status
- Real-time status indicator

### 📋 Web App Requirements

- Python 3.8 or higher
- Flask 3.0+
- MongoDB (optional, for data persistence)
- Modern browser (Chrome, Firefox, Edge, Safari)

### 🗂️ Web App Structure

```
webapp/
├── app.py              # Flask backend
├── templates/          # HTML templates
│   ├── base.html      # Base template
│   └── index.html     # Main page
└── static/            # Static files
    ├── css/
    │   └── style.css  # Application styles
    └── js/
        └── main.js    # Client-side JavaScript
```

### 🎨 User Interface

#### Main Layout
- **Header**: Title and system status indicator
- **Navbar**: Navigation menu with quick access to features
- **Left Panel**: Patient search, patient info, file upload
- **Right Panel**: Clinical records display

#### Modal Dialogs
- **Patient Search**: Advanced search form
- **New Patient**: Complete demographic form
- **New Clinical Record**: Complete clinical episode form
- **System Metrics**: Statistics display

### 📱 Responsive Design

Fully responsive interface optimized for:
- Desktop (1200px+)
- Tablet (768px - 1024px)
- Mobile (< 768px)

### ✨ Web Interface Characteristics

- **Universal Access**: Usable from any web browser
- **Modern Interface**: Responsive design with HTML/CSS/JS
- **Multi-user**: Support for concurrent access
- **Accessibility**: Available from any network-connected device
- **Flexible Deployment**: Local or remote web server

---

## 🤖 AI Medical Diagnostics with Multi-Provider Fallback

EarlyCare Gateway includes an **AI-powered medical diagnostics system** with intelligent fallback for maximum reliability.

### 🔧 Problem & Solution

**Challenge**: Google Gemini API can occasionally be unavailable due to:
- Rate limiting
- Quota limits
- Temporary service issues
- API overload

**Solution**: Multi-provider system with:
1. **Retry with Exponential Backoff**: 3 automatic attempts with Gemini (1s → 2s → 4s delays)
2. **Automatic Fallback**: If Gemini fails after 3 attempts, automatically switches to OpenAI GPT-4o-mini
3. **Complete Logging**: All attempts and fallbacks logged for debugging

### 📋 Configuration

#### 1. Install Dependencies

```bash
pip install google-generativeai openai
```

#### 2. Configure API Keys in .env

```env
# Primary (Required)
GEMINI_API_KEY=your_gemini_api_key_here

# Fallback (Optional but Recommended)
OPENAI_API_KEY=your_openai_api_key_here
```

#### 3. Get API Keys

**Google Gemini API Key:**
- Visit https://makersuite.google.com/app/apikey
- Create or select a project
- Generate new API key
- Copy to .env file

**OpenAI API Key (Optional):**
- Visit https://platform.openai.com/api-keys
- Create account or login
- Generate new API key
- Copy to .env file
- **Note**: Requires credit (credit card). GPT-4o-mini costs ~$0.15 per 1M input tokens + $0.60 per 1M output tokens

### 🔄 How It Works

1. **First Call**: System tries Gemini
2. **If Fails**: Waits 1 second and retries
3. **If Fails Again**: Waits 2 seconds and retries
4. **After 3rd Failure**: 
   - If OpenAI configured → automatically switches to GPT-4o-mini
   - If OpenAI not configured → returns error

### 📊 Model Comparison

| Aspect | gemini-3-flash-preview | OpenAI GPT-4o-mini |
|---------|-------------------------|-------------------|
| **Cost** | Free (with limits) | ~$0.15/$0.60 per 1M tokens |
| **Speed** | Very fast | Fast |
| **Quality** | High | High |
| **Reliability** | 95% (rate limits) | 99.9% |
| **Usage** | Primary (always) | Fallback (only if Gemini fails) |

### 🎯 Benefits

✅ **High Reliability**: System works even if one provider is unavailable  
✅ **Cost Effective**: OpenAI only used when necessary (fallback)  
✅ **Zero Downtime**: Automatic and transparent transition  
✅ **Full Monitoring**: Complete logs for every attempt and fallback  
✅ **Flexible**: OpenAI is optional, system works with Gemini only  

### 🔍 Example Logs

**Scenario 1: Gemini works on first attempt**
```
[AI] Calling Gemini API...
[AI] Response received from Gemini
[AI] Diagnosis text extracted, length: 1842 chars
```

**Scenario 2: Gemini fails, retry succeeds**
```
[AI] Tentativo Gemini 1/3 fallito: API overloaded
[AI] Attendo 1s prima di riprovare...
[AI] Calling Gemini API...
[AI] Response received from Gemini
```

**Scenario 3: Gemini fails, uses OpenAI**
```
[AI] Tentativo Gemini 1/3 fallito: Quota exceeded
[AI] Attendo 1s prima di riprovare...
[AI] Tentativo Gemini 2/3 fallito: Quota exceeded
[AI] Attendo 2s prima di riprovare...
[AI] Tentativo Gemini 3/3 fallito: Quota exceeded
[AI] Gemini non disponibile, uso OpenAI come fallback...
[AI] Calling OpenAI API...
✅ Diagnosis generated with model: gpt-4o-mini (fallback)
```

### 🚀 System Startup

```bash
python run_webapp.py
```

**With OpenAI configured:**
```
✅ AI Medical Diagnostics initialized successfully
   Gemini: ✅ | OpenAI Fallback: ✅
```

**Without OpenAI configured:**
```
✅ AI Medical Diagnostics initialized successfully
   Gemini: ✅ | OpenAI Fallback: ❌
⚠️ OpenAI non disponibile (installa: pip install openai)
```

### ✨ Features

- **Single Record Analysis**: Diagnose individual clinical records
- **Complete Patient Analysis**: Analyze all patient data
- **Structured Output**: Comprehensive diagnostic report with:
  - Clinical data analysis
  - Clinical picture
  - Presumptive diagnosis
  - Differential diagnoses
  - Recommended tests
  - Treatment plan
  - Monitoring protocol
  - Urgency level
  - Precautions
  - Prognosis
- **Download Reports**: Export diagnoses as text files

### 📝 Important Notes

1. **OpenAI is Optional**: System works without OpenAI, but with lower reliability
2. **Minimal OpenAI Costs**: Only used as fallback, costs are minimal
3. **Privacy**: Both APIs respect medical privacy (anonymized data)
4. **Model Choice**: GPT-4o-mini chosen for best quality/price/speed ratio

### 🔐 Security

- API keys never exposed in logs
- Patient data anonymized before sending
- HTTPS encrypted connections
- GDPR and HIPAA compliant

### ❓ Troubleshooting

**Problem**: "OpenAI non disponibile"  
**Solution**: Install package: `pip install openai`

**Problem**: "Tutti i tentativi falliti"  
**Cause**: Gemini unavailable and OpenAI not configured  
**Solution**: Add OPENAI_API_KEY to .env file

**Problem**: OpenAI costs too high  
**Solution**: Remove OPENAI_API_KEY from .env (system uses Gemini only)

---

### 📊 API Endpoints

#### Patients
- `POST /api/patient/search` - Search patient
- `POST /api/patient/create` - Create new patient
- `GET /api/patient/<fiscal_code>/records` - Get clinical records

#### Clinical Records
- `POST /api/patient/<fiscal_code>/add-record` - Add record

#### Files
- `POST /api/file/upload` - Upload single file
- `POST /api/folder/upload` - Upload clinical folder

#### System
- `GET /api/metrics` - Get system metrics
- `GET /api/export/<fiscal_code>` - Export patient data

### 🐛 Web App Troubleshooting

#### Port Already in Use
If port 5000 is occupied, modify in `webapp/app.py`:
```python
app.run(debug=True, host='0.0.0.0', port=5001)  # Change port
```

#### Database Not Connected
- Verify MongoDB is running
- Check credentials in `credenziali_db.txt`
- Application works without database

#### File Upload Errors
- Verify `webapp/uploads` folder exists
- Check write permissions
- Maximum file size: 100MB

---

## 💾 Database Implementation

Complete MongoDB persistence system that mirrors all code functionality.

### 📊 Database Collections

#### 1. **patients** - Patient Registry
- Unique patient ID
- Complete demographics
- Medical history, medications, allergies
- Creation/update timestamps

#### 2. **clinical_data** - Multi-modal Clinical Data
**Polymorphic schema** supports 3 types:

- **TEXT**: Clinical notes, reports, transcriptions
  - `text_content`, `language`, `document_type`
  
- **SIGNAL**: ECG, EEG, vital signs
  - `signal_values[]`, `sampling_rate`, `signal_type`, `duration`
  
- **IMAGE**: X-ray, CT, MRI, DICOM
  - `image_path`, `modality`, `dimensions`, `body_part`

Each type has:
- Automatic validation
- Quality score (0.0-1.0)
- Source tracking
- Extensible metadata

#### 3. **patient_records** - Clinical Encounter Records
Stores **complete Chain of Responsibility workflow**:

```javascript
{
  "encounter_id": "ENC-xxx",
  "patient_id": "P2024001",
  "patient": { /* patient snapshot */ },
  "clinical_data_refs": ["data_id1", "data_id2"],
  "priority": "urgent",
  
  // ⭐ PROCESSING CONTEXT
  "processing_context": {
    "validation": {
      "is_valid": true,
      "errors": [],
      "warnings": []
    },
    "enrichment": {
      "age_calculated": true,
      "average_data_quality": 0.95,
      "has_critical_history": true
    },
    "triage": {
      "score": 85.0,
      "priority": "urgent",
      "factors": ["Complex medical history", "Critical symptoms"]
    },
    "privacy": {
      "anonymization_required": false,
      "compliance_flags": ["Consent verified"]
    },
    "processing_times": {
      "ValidationHandler": 12.5,
      "EnrichmentHandler": 8.3,
      "TriageHandler": 5.2
    }
  }
}
```

#### 4. **decision_support** - AI Results
Stores complete decision support output:

- **Diagnoses**: Array of diagnoses with:
  - Condition and ICD code
  - Confidence score (0.0-1.0)
  - Clinical evidence
  - Risk factors
  - Differential diagnoses
  - Recommended tests
  - Specialist consultations

- **Triage**: Urgency level and triage score

- **Alerts/Warnings**: Critical notifications

- **Traceability**: 
  - AI models used
  - Processing times
  - Feature importance
  - Human-readable explanations

#### 5. **audit_logs** - Compliance and Security
- Complete log of all operations
- Data access tracking
- Strict validation (error on invalid schema)
- Filters by patient, user, event type, dates

### 🚀 Database Setup

#### Initial Setup

```bash
# 1. Install MongoDB
# Windows: https://www.mongodb.com/try/download/community
# Linux: sudo apt install mongodb

# 2. Start MongoDB
net start MongoDB  # Windows
sudo systemctl start mongod  # Linux

# 3. Install Python dependencies
pip install -r requirements.txt

# 4. Initialize database
python scripts/initialize_database.py
```

#### Basic Database Usage

```bash
# Basic example
python examples/example_mongodb_usage.py

# Advanced example (Complete workflow)
python examples/example_mongodb_advanced.py
```

### 🔍 Optimized Indexes

Performance-critical indexes:

**patients**:
- `patient_id` (UNIQUE)
- `medical_record_number`
- `allergies`

**clinical_data**:
- `data_id` (UNIQUE)
- `(patient_id, timestamp)` compound (DESC)
- `data_type` + `source`
- `quality_score`

**patient_records**:
- `encounter_id` (UNIQUE)
- `(patient_id, encounter_timestamp)` compound (DESC)
- `priority`
- `processing_context.triage.score` (DESC)

**decision_support**:
- `request_id` (UNIQUE)
- `(patient_id, timestamp)` compound (DESC)
- `urgency_level`
- `triage_score` (DESC)

**audit_logs**:
- `(timestamp, event_type)` compound (DESC)
- `patient_id`
- `user_id`

### 🔄 Complete Workflow Supported

#### 1. Patient Registration
```python
patient = Patient(...)
db.save_patient(patient)
db.log_audit_event("create", user_id, "Patient created", patient_id)
```

#### 2. Clinical Data Collection
```python
# Text
text_data = TextData(...)
# Signal
signal_data = SignalData(...)
# Image
image_data = ImageData(...)

# Automatically saved to clinical_data collection
```

#### 3. Create Record with Processing Context
```python
patient_record = PatientRecord(patient, encounter_id)
patient_record.add_clinical_data(text_data)
patient_record.add_clinical_data(signal_data)

# Add context from Chain of Responsibility
context = {
    "validation": {...},
    "enrichment": {...},
    "triage": {...}
}
patient_record.metadata.update({"processing_context": context})

db.save_patient_record(patient_record)
```

#### 4. Decision Support
```python
decision = DecisionSupport(...)
decision.add_diagnosis(diagnosis)
decision.urgency_level = UrgencyLevel.URGENT

db.save_decision_support(decision, encounter_id)
```

#### 5. Advanced Queries
```python
# All urgent records
urgent = db.find_records_by_priority("urgent")

# Patient clinical data by type
ecg_data = db.get_patient_clinical_data(patient_id, data_type="signal")

# High confidence decisions
high_conf = db.get_decisions_by_urgency("emergency")

# Audit for patient
logs = db.get_audit_logs(patient_id=patient_id)
```

### 📊 Database Statistics

Real-time statistics:

```python
stats = db.get_statistics()
# {
#   "total_patients": 150,
#   "total_clinical_data": 1250,
#   "total_records": 450,
#   "total_decisions": 380,
#   "priority_counts": {
#     "emergency": 12,
#     "urgent": 45,
#     "soon": 89,
#     "routine": 304
#   },
#   "data_type_counts": {
#     "text": 500,
#     "signal": 450,
#     "image": 300
#   }
# }
```

### ✨ Database Features

- ✅ **Code Fidelity**: All existing models supported
- ✅ **Processing Context**: From Chain of Responsibility
- ✅ **Complete Decision Support**: Full AI output
- ✅ **Integrated Audit Logging**: Built-in compliance
- ✅ **Performance**: Optimized indexes for frequent queries
- ✅ **Flexibility**: Polymorphic schema for clinical_data
- ✅ **Compliance**: Complete audit logging
- ✅ **Scalability**: Separation of clinical_data from patient_records

---

## 🔧 Management Scripts

### Delete Doctors Script

Administrative script to manage doctors in the MongoDB database:

```bash
# Interactive menu (guided mode)
python scripts/delete_doctors.py

# List all doctors
python scripts/delete_doctors.py --list

# Delete specific doctor by ID
python scripts/delete_doctors.py --delete MR7X9Z

# Delete all doctors (requires confirmation)
python scripts/delete_doctors.py --delete-all
```

**Features**:
- ✅ Interactive menu or command-line arguments
- ✅ View all doctors with details (ID, name, creation date)
- ✅ Delete individual doctors with confirmation
- ✅ Bulk delete with double-confirmation for safety
- ✅ Formatted output with tables
- ✅ Error handling and validation

**Example Output**:
```
Doctor ID            Nome            Cognome         Created
------------------------------------------------------------------
MR7X9Z               Mario           Rossi           2025-12-06 12:45:00
GB2A5K               Giovanni        Bianchi         2025-12-06 14:30:15
```

---

## 🎯 Project Summary

### ✨ Key Achievements

#### 1. **Comprehensive Architecture** ✓
- **Chain of Responsibility**: Flexible data processing pipeline
- **Strategy Pattern**: Swappable AI models by domain/device/pathology
- **Observer Pattern**: Real-time monitoring and audit trails
- **Facade Pattern**: Unified clinical system integration (HL7, FHIR, DICOM)

#### 2. **Multi-Modal Data Support** ✓
- **Text Data**: Clinical notes, discharge summaries, radiology reports
- **Signal Data**: ECG, EEG, vital signs with validation
- **Image Data**: CT, MRI, X-rays with DICOM metadata

#### 3. **HIPAA Compliance** ✓
- **Anonymization**: PII removal, pseudonymization, k-anonymity
- **Encryption**: AES-256 for data at rest and in transit
- **Audit Logging**: Comprehensive, tamper-evident trails
- **Access Control**: Role-based with consent management

#### 4. **Clinical System Integration** ✓
- **HL7 v2.x Adapter**: Legacy system messaging
- **FHIR R4 Adapter**: Modern REST API integration
- **DICOM Adapter**: PACS connectivity for medical imaging

#### 5. **Intelligent Triage** ✓
- Configurable scoring algorithm
- Age-based prioritization
- Medical history complexity analysis
- Automatic urgency escalation

#### 6. **Monitoring & Observability** ✓
- **Metrics**: Request volumes, processing times, success rates
- **Performance**: Slow request detection, alerting
- **Audit**: Complete access and modification logs
- **Data Quality**: Validation failure tracking

### 🌟 Production-Ready Features

- ✅ Comprehensive error handling
- ✅ Type hints throughout codebase
- ✅ Extensive documentation
- ✅ Configuration-driven behavior
- ✅ Modular and extensible design
- ✅ HIPAA compliance built-in
- ✅ Real-time monitoring
- ✅ Performance optimization hooks
- ✅ Security best practices
- ✅ Clear examples and quickstart
- ✅ Complete MongoDB persistence
- ✅ Web application interface

### 🎓 Use Cases

1. **Emergency Department**: Rapid triage and diagnosis support
2. **Primary Care**: Clinical decision support for general practitioners
3. **Specialist Consultation**: Domain-specific analysis
4. **Research**: De-identified data analysis
5. **Quality Improvement**: Pattern detection in clinical outcomes
6. **Telehealth**: Remote patient monitoring and diagnosis

---

## 🗺️ Roadmap

- [ ] Real-time signal processing for wearable devices
- [ ] Multi-language NLP support
- [ ] Federated learning capabilities
- [ ] Mobile application integration
- [ ] Cloud deployment templates (AWS, Azure, GCP)
- [ ] Advanced explainability features (SHAP, LIME)
- [ ] User authentication for web app
- [ ] Real-time notifications
- [ ] Complete REST API
- [ ] WebSocket integration

---

## 🐳 Docker Setup

EarlyCare Gateway può essere eseguito completamente con Docker per una configurazione semplice e veloce.

### Prerequisiti

- Docker Desktop installato e in esecuzione
- Estensione Docker per VS Code (opzionale ma consigliata)

### Struttura File Docker

- `Dockerfile` - Configurazione per il backend Python/Flask
- `frontend/Dockerfile` - Configurazione per il frontend React/Vite
- `docker-compose.yml` - Orchestrazione di tutti i servizi
- `.dockerignore` - File da escludere dal build

### Configurazione

#### 1. Variabili d'Ambiente

Crea un file `.env` nella root del progetto con le seguenti variabili:

```env
# API Keys
GEMINI_API_KEY=la-tua-chiave-gemini
CHATBOT_GEMINI_API_KEY=la-tua-chiave-chatbot

# Flask Configuration
FLASK_SECRET_KEY=genera-una-chiave-segreta-sicura

# MongoDB Configuration (già configurato in docker-compose.yml)
MONGODB_CONNECTION_STRING=mongodb://admin:admin123@mongodb:27017/
MONGODB_DATABASE_NAME=earlycare_db
```

#### 2. Generare una chiave segreta per Flask

Puoi generare una chiave segreta sicura con:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### Comandi Docker

#### Avviare tutti i servizi

```bash
docker-compose up -d
```

Questo comando avvierà:
- MongoDB (porta 27017)
- Backend Flask (porta 5000)
- Frontend React (porta 80)

#### Vedere i log

```bash
# Tutti i servizi
docker-compose logs -f

# Solo un servizio specifico
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f mongodb
```

#### Fermare i servizi

```bash
docker-compose down
```

#### Fermare e rimuovere i volumi (⚠️ cancella i dati del database)

```bash
docker-compose down -v
```

#### Ricostruire le immagini

```bash
docker-compose build --no-cache
docker-compose up -d
```

### Accesso ai Servizi

Una volta avviati i container:

- **Frontend**: http://localhost
- **Backend API**: http://localhost:5000
- **MongoDB**: localhost:27017 (username: admin, password: admin123)

### Verifica Stato dei Container

#### Con l'estensione Docker di VS Code

1. Clicca sull'icona Docker nella barra laterale
2. Espandi "Containers"
3. Vedrai tutti i container in esecuzione
4. Click destro su un container per:
   - Vedere i log
   - Aprire una shell
   - Fermare/Riavviare il container
   - Ispezionare il container

#### Da linea di comando

```bash
# Lista dei container in esecuzione
docker-compose ps

# Stato di salute dei servizi
docker ps
```

### Troubleshooting

#### Il backend non si connette a MongoDB

Verifica che MongoDB sia in esecuzione e healthy:

```bash
docker-compose logs mongodb
```

#### Errori di build

Pulisci tutto e ricostruisci:

```bash
docker-compose down -v
docker system prune -a
docker-compose build --no-cache
docker-compose up -d
```

#### Vedere cosa succede dentro un container

```bash
docker-compose exec backend bash
docker-compose exec frontend sh
docker-compose exec mongodb mongosh
```

### Sviluppo

Per sviluppare con hot-reload, puoi modificare il docker-compose.yml per montare il codice sorgente come volume:

```yaml
backend:
  volumes:
    - .:/app
    - /app/.venv  # Esclude l'ambiente virtuale locale
```

### Note sulla Sicurezza

⚠️ **IMPORTANTE PER LA PRODUZIONE**:

1. Cambia la password di MongoDB da `admin123` a qualcosa di sicuro
2. Usa una `FLASK_SECRET_KEY` generata in modo sicuro
3. Attiva HTTPS per il frontend
4. Non committare il file `.env` nel repository
5. Usa Docker secrets per gestire le credenziali sensibili

### Backup del Database

```bash
# Backup
docker-compose exec mongodb mongodump --out=/data/backup

# Restore
docker-compose exec mongodb mongorestore /data/backup
```

### Pulizia

Per rimuovere tutto (container, immagini, volumi):

```bash
docker-compose down -v --rmi all
```

---

**Built with ❤️ for better healthcare outcomes**


---


# 🚀 Guida al Deployment su Render

## 📋 Prerequisiti
- Account Render (https://render.com)
- MongoDB Atlas configurato (https://www.mongodb.com/cloud/atlas)
- Repository GitHub/GitLab con il codice

---

## 🔧 1. Deployment Backend (Web Service)

### Configurazione Render:
- **Service Type:** Web Service
- **Root Directory:** `./` (lascia vuoto o usa root)
- **Build Command:** 
  ```bash
  pip install -r requirements.txt
  ```
- **Start Command:**
  ```bash
  gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 120 run_backend:app
  ```

### Environment Variables (IMPORTANTE):
```
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/database?retryWrites=true&w=majority
FLASK_SECRET_KEY=una-stringa-segreta-casuale-molto-lunga
GEMINI_API_KEY=la-tua-chiave-api-gemini
FRONTEND_URL=https://nome-tuo-frontend.onrender.com
RENDER=true
```

**Note:**
- `MONGODB_URI`: Il connection string di MongoDB Atlas
- `FLASK_SECRET_KEY`: Genera una stringa casuale (min 32 caratteri)
- `FRONTEND_URL`: L'URL del frontend che creerai dopo (puoi aggiungerlo dopo il deployment del frontend)
- `RENDER=true`: Indica che siamo in produzione

---

## 🌐 2. Deployment Frontend (Static Site)

### Configurazione Render:
- **Service Type:** Static Site
- **Root Directory:** `frontend`
- **Build Command:**
  ```bash
  npm install && npm run build
  ```
- **Publish Directory:** `dist`

### Environment Variables:
```
VITE_API_URL=https://nome-tuo-backend.onrender.com
```

**IMPORTANTE:** Sostituisci `nome-tuo-backend.onrender.com` con l'URL effettivo del tuo backend deployato.

---

## 🔄 3. Configurazione Post-Deployment

### A. Aggiorna la variabile FRONTEND_URL del backend:
1. Vai al servizio **Backend** su Render
2. Nelle Environment Variables, aggiorna:
   ```
   FRONTEND_URL=https://nome-tuo-frontend.onrender.com
   ```
3. Salva (il servizio si riavvierà automaticamente)

### B. Test della connessione:
1. Apri l'URL del **frontend** nel browser
2. Prova a fare il login
3. Se ricevi errori CORS, verifica che:
   - `FRONTEND_URL` nel backend sia corretto
   - `VITE_API_URL` nel frontend sia corretto
   - Entrambi i servizi siano attivi

---

## 🐛 Risoluzione Problemi Comuni

### Errore: "Errore di connessione" al login
**Causa:** Il frontend non riesce a comunicare con il backend

**Soluzioni:**
1. Verifica che `VITE_API_URL` nel frontend punti all'URL corretto del backend
2. Apri la console del browser (F12) e controlla gli errori di rete
3. Verifica che il backend sia attivo e risponda visitando: `https://nome-backend.onrender.com/health`

### Errore CORS
**Causa:** Configurazione CORS non corretta

**Soluzioni:**
1. Verifica che `FRONTEND_URL` nel backend sia impostato correttamente
2. Assicurati che includa `https://` e non abbia `/` finale
3. Controlla i log del backend su Render per vedere errori CORS

### Errore: Cookie/Session non funziona
**Causa:** Cookie cross-domain non configurati correttamente

**Soluzione:**
- Verifica che `RENDER=true` sia impostato nel backend
- I cookie dovrebbero essere configurati con `SameSite=None; Secure`
- Questo è già gestito automaticamente nel codice

### Backend va in "sleep" (piano gratuito)
**Causa:** Render mette in sleep i servizi gratuiti dopo 15 minuti di inattività

**Soluzioni:**
- Il primo accesso dopo lo sleep richiede 1-2 minuti
- Puoi usare un servizio di "ping" per mantenerlo attivo
- Oppure passa a un piano a pagamento

---

## ✅ Checklist Finale

- [ ] Backend deployato e attivo
- [ ] Frontend deployato e attivo
- [ ] `VITE_API_URL` nel frontend configurato
- [ ] `FRONTEND_URL` nel backend configurato
- [ ] `MONGODB_URI` nel backend configurato
- [ ] `FLASK_SECRET_KEY` nel backend configurato
- [ ] Test login funzionante
- [ ] Console browser senza errori CORS

---

## 📱 Accesso all'Applicazione

Una volta completato il deployment:

1. Apri il browser
2. Vai all'URL del **frontend**: `https://nome-tuo-frontend.onrender.com`
3. Dovresti vedere la pagina di login
4. Inserisci le credenziali e accedi

**Nota:** Il primo accesso può richiedere 1-2 minuti se il backend è in sleep.

---

## 🔒 Sicurezza in Produzione

### Raccomandazioni:
1. **HTTPS:** Render fornisce automaticamente HTTPS
2. **Variabili d'ambiente:** Non committare mai le chiavi API nel codice
3. **FLASK_SECRET_KEY:** Usa una chiave lunga e casuale
4. **MongoDB:** Usa MongoDB Atlas con IP whitelist e autenticazione forte
5. **Rate Limiting:** Considera di aggiungere rate limiting in futuro

---

## 📊 Monitoring

### Log del Backend:
1. Vai al servizio backend su Render
2. Clicca su "Logs" per vedere i log in tempo reale
3. Utile per debug di errori di connessione o autenticazione

### Log del Frontend:
1. Apri la Console del browser (F12)
2. Vai alla tab "Console" per errori JavaScript
3. Vai alla tab "Network" per vedere le richieste API

---

## 🎉 Deployment Completato!

Se tutto è configurato correttamente, la tua applicazione EarlyCare Gateway dovrebbe essere accessibile e funzionante su Render.

Per supporto o problemi, controlla:
- Log di Render per entrambi i servizi
- Console del browser per errori lato client
- Documentazione Render: https://render.com/docs


---


# 🔴 FIX CORS ERROR - Guida Passo-Passo

## ⚡ Azioni Immediate (in ordine):

### 1️⃣ **Fai commit e push del codice aggiornato:**

```bash
git add .
git commit -m "Fix CORS configuration for production"
git push
```

### 2️⃣ **Su Render - Backend - Verifica Environment Variables:**

Vai al backend su Render e assicurati che queste variabili siano settate **ESATTAMENTE** così:

```
FRONTEND_URL=https://earlycare-gateway-frontend.onrender.com
RENDER=true
MONGODB_URI=il-tuo-mongodb-uri
FLASK_SECRET_KEY=una-stringa-segreta-casuale-lunga
```

⚠️ **IMPORTANTE:**
- `FRONTEND_URL` deve essere **HTTPS** (non HTTP)
- **NO** slash `/` alla fine
- `RENDER` deve essere esattamente `true` (lowercase)

### 3️⃣ **Rideploya il Backend:**

- Render farà deploy automaticamente se collegato a Git
- Oppure click su **"Manual Deploy"** → **"Deploy latest commit"**
- Aspetta che il deploy finisca (2-3 minuti)

### 4️⃣ **Verifica i Logs del Backend:**

Una volta deployato:
1. Vai su **Logs**
2. Dovresti vedere questi messaggi all'avvio:
   ```
   🌐 CORS allowed origins: ['https://earlycare-gateway-frontend.onrender.com', ...]
   🔧 Production mode: True
   🍪 Cookie config - Secure: True, SameSite: None
   ```

3. Se NON vedi questi messaggi → problema con le env variables

### 5️⃣ **Test CORS endpoint:**

Apri nel browser:
```
https://earlycare-gateway-backend.onrender.com/health
```

Dovresti vedere:
```json
{
  "status": "healthy",
  "db_connected": true/false,
  "ai_available": true/false,
  "cors_origins": ["https://earlycare-gateway-frontend.onrender.com"],
  "is_production": true
}
```

⚠️ Se `is_production` è `false` → la variabile `RENDER=true` non è settata correttamente

### 6️⃣ **Test dal Frontend:**

1. Apri il frontend: `https://earlycare-gateway-frontend.onrender.com`
2. Apri DevTools (F12) → Console
3. Prova a fare login
4. Controlla la tab **Network**:
   - Cerca la richiesta `login` 
   - Status deve essere **200** o **401** (non errore di rete)
   - Response Headers deve includere:
     ```
     Access-Control-Allow-Origin: https://earlycare-gateway-frontend.onrender.com
     Access-Control-Allow-Credentials: true
     ```

---

## 🔍 Cosa è stato modificato:

### 1. **Configurazione CORS migliorata:**
- Ora usa `resources={r"/api/*": {...}}` per essere più specifico
- Aggiunge header `Accept` agli allowed headers
- Imposta `max_age=3600` per cache pre-flight requests
- Include automaticamente localhost per sviluppo

### 2. **Fix rilevamento produzione:**
- `is_production` ora controlla correttamente la stringa "true"
- Prima faceva un controllo booleano fallimentare

### 3. **Cookie configurati correttamente:**
- `SameSite=None` in produzione (necessario per cross-domain)
- `Secure=True` in produzione (obbligatorio con SameSite=None)

### 4. **Debug logging:**
- Print all'avvio mostra la configurazione
- Nuovo endpoint `/health` mostra CORS origins
- Nuovo endpoint `/api/test-cors` per testare CORS

---

## 🧪 Verifica Rapida:

### Test 1 - Backend attivo:
```bash
curl https://earlycare-gateway-backend.onrender.com/health
```
✅ Deve rispondere con JSON

### Test 2 - CORS da browser:
1. Apri Console del frontend (F12)
2. Esegui:
```javascript
fetch('https://earlycare-gateway-backend.onrender.com/api/test-cors', {
  credentials: 'include'
})
.then(r => r.json())
.then(d => console.log(d))
```
✅ Deve rispondere senza errori CORS

---

## 🚨 Se continua a non funzionare:

### A. Controlla logs backend per errori
Cerca:
- `ModuleNotFoundError: No module named 'flask_cors'`
  → **Fix:** Flask-CORS non installato (dovrebbe essere in requirements.txt)

- `KeyError: 'FRONTEND_URL'`
  → **Fix:** Variabile non settata

### B. Verifica che Flask-CORS sia installato
Controlla `requirements.txt`:
```
Flask-CORS>=4.0.0
```

Se manca, aggiungilo e rideploya.

### C. Cache del browser
- Svuota cache (Ctrl+Shift+Del)
- Prova in modalità incognito
- Hard refresh (Ctrl+F5)

### D. Verifica URL esatti
Nel browser DevTools → Network → Headers:
- **Request URL** deve essere: `https://earlycare-gateway-backend.onrender.com/api/auth/login`
- **Origin** deve essere: `https://earlycare-gateway-frontend.onrender.com`

---

## ✅ Checklist Finale:

Prima del test:
- [ ] Codice pushato su Git
- [ ] Backend riployato su Render
- [ ] `FRONTEND_URL=https://earlycare-gateway-frontend.onrender.com` settato
- [ ] `RENDER=true` settato (lowercase)
- [ ] Logs mostrano configurazione CORS corretta
- [ ] `/health` endpoint risponde con `is_production: true`
- [ ] Cache browser svuotata

Se tutti i check sono ✅ e continua a non funzionare:
- Copia l'errore esatto dalla Console
- Copia i Response Headers dalla tab Network
- Copia i logs del backend

---

## 📋 Recap Variabili d'Ambiente:

### Backend:
```
FRONTEND_URL=https://earlycare-gateway-frontend.onrender.com
RENDER=true
MONGODB_URI=mongodb+srv://user:pass@cluster.mongodb.net/db?retryWrites=true&w=majority
FLASK_SECRET_KEY=stringa-segreta-random-min-32-caratteri
GEMINI_API_KEY=tua-chiave-gemini (opzionale)
```

### Frontend:
```
VITE_API_URL=https://earlycare-gateway-backend.onrender.com
```

(Ricorda: dopo aver modificato VITE_API_URL devi rideoployare il frontend!)


---


# 🆘 DEBUG ERRORE CONNESSIONE - Procedura Completa

## 📝 PASSO 1: Commit e Push delle modifiche

Esegui questi comandi esattamente in questo ordine:

```bash
git add .
git commit -m "Fix CORS with after_request handler"
git push origin master
```

---

## 🔍 PASSO 2: Verifica su Render - Backend

### A. Controlla che il deploy sia partito:
1. Vai su [Render Dashboard](https://dashboard.render.com)
2. Clicca sul tuo servizio Backend
3. Nella sezione "Events" dovresti vedere "Deploy triggered"
4. Aspetta che diventi "Deploy live" (2-5 minuti)

### B. Controlla i LOGS durante il deploy:
1. Clicca su **"Logs"** nel menu laterale
2. Cerca questi messaggi specifici:
   ```
   🌐 CORS allowed origins: ['https://earlycare-gateway-frontend.onrender.com']
   🔧 Production mode: True
   🍪 Cookie config - Secure: True, SameSite: None
   ```

3. ⚠️ **SE NON VEDI QUESTI MESSAGGI:**
   - Le variabili d'ambiente non sono settate correttamente
   - Vai al punto 3

---

## ⚙️ PASSO 3: Verifica Environment Variables

Vai su Render → Backend → **Environment**

Devono esserci ESATTAMENTE queste variabili (copia-incolla):

```
FRONTEND_URL=https://earlycare-gateway-frontend.onrender.com
RENDER=true
```

⚠️ **ATTENZIONE AI DETTAGLI:**
- `RENDER` deve essere `true` (tutto minuscolo)
- `FRONTEND_URL` deve avere `https://` (non `http://`)
- NO spazi prima o dopo `=`
- NO slash `/` alla fine dell'URL

Aggiungi anche (se non ci sono):
```
MONGODB_URI=<il-tuo-mongodb-uri>
FLASK_SECRET_KEY=<stringa-segreta-casuale-lunga>
```

**Dopo aver modificato**, clicca **"Save Changes"** - il backend si riavvierà automaticamente.

---

## 🧪 PASSO 4: Test Backend Health

### Test A - Controlla che il backend risponda:

Apri nel browser:
```
https://earlycare-gateway-backend.onrender.com/health
```

**Risposta attesa:**
```json
{
  "status": "healthy",
  "db_connected": true,
  "ai_available": false,
  "cors_origins": ["https://earlycare-gateway-frontend.onrender.com"],
  "is_production": true
}
```

⚠️ **SE NON RISPONDE O TIMEOUT:**
- Il backend è crashato
- Controlla i logs per errori
- Potrebbero mancare dipendenze (Flask-CORS)

⚠️ **SE `is_production: false`:**
- La variabile `RENDER=true` non è settata
- Torna al PASSO 3

### Test B - Test CORS diretto:

Apri la **Console del browser** (F12) sul frontend e esegui:

```javascript
fetch('https://earlycare-gateway-backend.onrender.com/api/test-cors', {
  method: 'GET',
  credentials: 'include',
  headers: {
    'Content-Type': 'application/json'
  }
})
.then(response => response.json())
.then(data => console.log('✅ CORS OK:', data))
.catch(error => console.error('❌ CORS FAILED:', error));
```

**Risposta attesa:**
```
✅ CORS OK: {message: "CORS is working!", origin: "https://...", allowed_origins: [...]}
```

⚠️ **SE ERRORE:**
- Guarda il messaggio esatto dell'errore
- Vai al PASSO 5

---

## 🌐 PASSO 5: Verifica Frontend

### A. Controlla variabile VITE_API_URL:

Render → Frontend → **Environment**

Deve esserci:
```
VITE_API_URL=https://earlycare-gateway-backend.onrender.com
```

⚠️ **SE HAI MODIFICATO questa variabile:**
- Devi **RIDEOPLOYARE** il frontend
- Click su **"Manual Deploy"** → **"Deploy latest commit"**
- Le variabili VITE sono compilate al build time!

### B. Verifica nel browser:

1. Apri: `https://earlycare-gateway-frontend.onrender.com`
2. Apri DevTools (F12)
3. Vai alla tab **Console**
4. Controlla se ci sono errori JavaScript
5. Vai alla tab **Network**
6. Prova a fare login
7. Clicca sulla richiesta `/login`

**Controlla:**
- **Request URL:** Deve essere `https://earlycare-gateway-backend.onrender.com/api/auth/login`
  - SE è `localhost` → frontend non ha `VITE_API_URL` o non ricompilato
- **Status:** 
  - `(failed) net::ERR_FAILED` → Backend non raggiungibile
  - `0` → Backend non risponde
  - `200/401` → Backend funziona, controlla Response
- **Response Headers:** Deve includere:
  ```
  Access-Control-Allow-Origin: https://earlycare-gateway-frontend.onrender.com
  Access-Control-Allow-Credentials: true
  ```

---

## 🔴 PASSO 6: Errori Specifici e Soluzioni

### Errore: "net::ERR_FAILED" o "Failed to fetch"
**Causa:** Backend non risponde o non esiste

**Soluzione:**
1. Verifica che il backend sia "Live" su Render
2. Verifica l'URL: `https://earlycare-gateway-backend.onrender.com/health`
3. Controlla logs del backend per crash

### Errore: "CORS policy: No 'Access-Control-Allow-Origin'"
**Causa:** Backend non include headers CORS

**Soluzione:**
1. Verifica che le modifiche siano deployate
2. Controlla logs backend per messaggi CORS
3. Verifica `FRONTEND_URL` sia corretto

### Errore: "CORS policy: The value of the 'Access-Control-Allow-Credentials' header"
**Causa:** Cookie Secure mismatch o SameSite

**Soluzione:**
1. Verifica `RENDER=true` nel backend
2. Verifica logs: `🍪 Cookie config - Secure: True, SameSite: None`

### Errore: Backend risponde ma frontend dice "Errore di connessione"
**Causa:** Catch block nel frontend

**Soluzione:**
1. Apri Console → guarda l'errore JavaScript esatto
2. Network → guarda lo Status Code della richiesta
3. Se Status è 500 → errore server, guarda logs backend

---

## 🆘 PASSO 7: Ultima Risorsa - Deploy da Zero

Se nulla funziona:

### 1. Elimina entrambi i servizi su Render
### 2. Ricrea Backend:
- Type: **Web Service**
- Repository: Il tuo GitHub/GitLab
- Branch: `master`
- Root Directory: `./`
- Build Command: `pip install -r requirements.txt`
- Start Command: `gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 120 run_backend:app`
- Environment:
  ```
  FRONTEND_URL=https://TUO-FRONTEND.onrender.com
  RENDER=true
  MONGODB_URI=<tuo-uri>
  FLASK_SECRET_KEY=<chiave-segreta>
  ```

### 3. Ricrea Frontend:
- Type: **Static Site**
- Repository: Il tuo GitHub/GitLab
- Branch: `master`
- Root Directory: `frontend`
- Build Command: `npm install && npm run build`
- Publish Directory: `dist`
- Environment:
  ```
  VITE_API_URL=https://TUO-BACKEND.onrender.com
  ```

### 4. Aggiorna FRONTEND_URL nel backend con l'URL reale del frontend
### 5. Rideploya il backend

---

## 📊 Checklist Debug Finale

Verifica uno per uno:

- [ ] Modifiche commitatte e pushate su Git
- [ ] Backend riployato su Render (status: Live)
- [ ] Logs backend mostrano configurazione CORS corretta
- [ ] `FRONTEND_URL` settato esattamente: `https://earlycare-gateway-frontend.onrender.com`
- [ ] `RENDER=true` settato (lowercase)
- [ ] `/health` endpoint risponde con `is_production: true`
- [ ] Frontend ha `VITE_API_URL=https://earlycare-gateway-backend.onrender.com`
- [ ] Frontend riployato dopo aver aggiunto `VITE_API_URL`
- [ ] Console browser aperta durante il test
- [ ] Network tab mostra URL backend corretto (non localhost)
- [ ] Cache browser svuotata (Ctrl+Shift+Del)

---

## 💬 Come Chiedere Aiuto

Se dopo tutti questi passi continua a non funzionare, fornisci:

1. **Screenshot della Console del browser** (con errori visibili)
2. **Screenshot della tab Network** (della richiesta fallita con Headers)
3. **Logs del backend** (ultimi 50 righe, specialmente all'avvio)
4. **Output di `/health` endpoint**
5. **Screenshot delle Environment Variables** (censura password/secrets)
6. **Errore esatto** che appare sul frontend

Questo aiuterà a identificare il problema specifico.


---


# 🔧 Guida Rapida: Risolvere Errori di Connessione

## ⚠️ Problema: "Errore di connessione" al login

### ✅ CHECKLIST IMMEDIATA:

#### 1. **Verifica URL Backend su Render**
   - Vai al tuo servizio **Backend** su Render
   - Copia l'URL (es: `https://earlycare-backend.onrender.com`)
   - Verifica che sia attivo visitando: `URL/health`

#### 2. **Configura Environment Variable Frontend**
   - Vai al servizio **Frontend** su Render
   - Nelle **Environment Variables** aggiungi:
     ```
     VITE_API_URL=https://il-tuo-backend.onrender.com
     ```
   - ⚠️ **NON** mettere lo slash `/` alla fine
   - ⚠️ **Salva e RIDEPLOYA** il frontend (obbligatorio!)

#### 3. **Configura Environment Variable Backend**
   - Vai al servizio **Backend** su Render
   - Nelle **Environment Variables** aggiungi/verifica:
     ```
     FRONTEND_URL=https://il-tuo-frontend.onrender.com
     RENDER=true
     MONGODB_URI=il-tuo-mongodb-atlas-uri
     FLASK_SECRET_KEY=stringa-segreta-random
     ```

#### 4. **Verifica Console Browser**
   - Apri il frontend deployato
   - Premi F12 per aprire DevTools
   - Vai alla tab **Console**
   - Cerca errori tipo:
     - `Failed to fetch` → Backend non raggiungibile
     - `CORS error` → Configurazione CORS errata
     - `401` → Problema autenticazione
     - `500` → Errore server backend

   - Vai alla tab **Network**
   - Prova a fare login
   - Clicca sulla richiesta `/api/auth/login`
   - Verifica:
     - **Request URL**: Deve puntare al backend (non localhost!)
     - **Status**: Se 0 → backend non raggiungibile

#### 5. **Verifica Logs Backend**
   - Vai al servizio Backend su Render
   - Clicca su **Logs**
   - Cerca errori tipo:
     - `MongoDB connection failed` → Problema database
     - `CORS` → Problema CORS
     - `KeyError` o `Exception` → Errore codice

---

## 🔍 DIAGNOSI ERRORI COMUNI:

### A. Frontend fa richieste a `localhost` invece del backend Render
**Sintomo:** Nella console vedi richieste a `localhost:5000`

**Causa:** `VITE_API_URL` non configurato o frontend non ricompilato

**Soluzione:**
1. Vai a Render → Frontend → Environment
2. Aggiungi: `VITE_API_URL=https://tuo-backend.onrender.com`
3. **Manual Deploy** per ricompilare con la nuova variabile
4. Le variabili Vite vengono "compilate" nel build, non sono dinamiche!

---

### B. Errore CORS (Cross-Origin)
**Sintomo:** Console mostra `CORS policy: No 'Access-Control-Allow-Origin'`

**Causa:** Backend non autorizza il frontend

**Soluzione:**
1. Backend → Environment → Verifica `FRONTEND_URL`
2. Deve essere: `https://tuo-frontend.onrender.com` (HTTPS, non HTTP!)
3. Salva e riavvia backend

---

### C. Backend in Sleep (piano gratuito)
**Sintomo:** Prima richiesta impiega 50+ secondi e va in timeout

**Causa:** Render mette in sleep i servizi gratuiti

**Soluzione:**
- Aspetta 1-2 minuti al primo accesso
- Il backend si "sveglierà"
- Considera un servizio di ping (es: UptimeRobot)

---

### D. MongoDB non connesso
**Sintomo:** Errore "Database non connesso"

**Causa:** `MONGODB_URI` non configurato o errato

**Soluzione:**
1. Vai a MongoDB Atlas
2. Copia il connection string
3. Backend → Environment → `MONGODB_URI`
4. Formato: `mongodb+srv://user:pass@cluster.mongodb.net/db?retryWrites=true&w=majority`

---

## 🧪 TEST RAPIDO:

### 1. Backend funziona?
```bash
curl https://tuo-backend.onrender.com/health
```
Dovrebbe rispondere con status `200`

### 2. Frontend fa richieste corrette?
- Apri il frontend
- F12 → Network
- Prova login
- La richiesta deve andare a: `https://tuo-backend.onrender.com/api/auth/login`
- NON deve andare a: `localhost` o URL sbagliato

---

## 📝 CHECKLIST FINALE:

Prima di chiedere aiuto, verifica:
- [ ] Backend deployato e attivo (Status: Live su Render)
- [ ] Frontend deployato e attivo (Status: Live su Render)
- [ ] `VITE_API_URL` configurato nel frontend (con HTTPS)
- [ ] Frontend **rideoployato** dopo aver aggiunto `VITE_API_URL`
- [ ] `FRONTEND_URL` configurato nel backend (con HTTPS)
- [ ] `MONGODB_URI` configurato e database raggiungibile
- [ ] `FLASK_SECRET_KEY` impostato
- [ ] `RENDER=true` impostato nel backend
- [ ] Console browser aperta per vedere errori dettagliati
- [ ] Logs backend controllati per errori server-side

---

## 🆘 Se nulla funziona:

1. **Ricrea i servizi da zero**:
   - Elimina frontend e backend su Render
   - Ricrea seguendo DEPLOYMENT_RENDER.md

2. **Test in locale**:
   ```bash
   # Backend
   cd backend
   python run_webapp.py
   
   # Frontend (altro terminale)
   cd frontend
   npm run dev
   ```
   Se funziona in locale ma non in produzione → problema configurazione Render

3. **Copia gli errori esatti**:
   - Screenshot console browser
   - Copia logs backend
   - Fornisci dettagli: quale endpoint fallisce, codice errore HTTP

---

## 💡 IMPORTANTE:

Le variabili d'ambiente `VITE_*` sono **compilate al build time**, non runtime!

Questo significa:
- Ogni volta che cambi `VITE_API_URL` devi **rideoployare**
- Non basta salvare la variabile, serve rebuild completo
- Click su "Manual Deploy" nel frontend dopo ogni modifica

Le variabili del backend invece sono runtime e basta riavviare.


---


# Test AI Analysis of Attachments

## Modifiche Implementate

### 1. Backend - webapp/app.py
- Modificato l'endpoint `/api/diagnostics/generate` per decodificare gli allegati base64
- Gli allegati vengono ora passati all'IA con tutto il loro contenuto (non solo il nome)
- Struttura dati allegati: `{'name', 'type', 'size', 'content'}`

### 2. AI Module - src/ai/medical_diagnostics.py
- Aggiunto supporto multimodale per analisi di immagini
- Usa Gemini API con capacità vision per analizzare immagini mediche
- Processa immagini da base64 usando PIL/Pillow
- TODO: Estrazione testo da PDF allegati

### 3. Dependencies - requirements.txt
- Aggiunto `Pillow>=10.0.0` per processamento immagini

## Come Testare

### Preparazione
1. Assicurati che il server Flask sia in esecuzione (`python run_webapp.py`)
2. Assicurati che il frontend sia in esecuzione (`npm run dev` in `frontend/`)
3. Avere una chiave API Google Gemini valida configurata

### Test Scenario 1: Analisi con Immagini Mediche

1. **Login** nel sistema
2. **Seleziona un paziente** o creane uno nuovo
3. **Crea una nuova scheda clinica** con:
   - Tipo: Visita o Ricovero
   - Motivo principale
   - Sintomi
   - Segni vitali
   - **Allega documenti**: Carica una o più immagini mediche (es. radiografie, ECG, foto di lesioni, ecc.)

4. **Salva** la scheda clinica
5. **Seleziona** la scheda clinica appena creata dalla lista
6. **Clicca su "Analisi IA"**

### Risultato Atteso

L'IA analizzerà:
- Tutti i dati clinici (sintomi, segni vitali, note, ecc.)
- **TUTTE le immagini allegate**, fornendo:
  - Descrizione delle immagini
  - Interpretazione medica delle immagini
  - Diagnosi basata su dati clinici + immagini
  - Raccomandazioni specifiche basate sulle immagini

### Test Scenario 2: Verifica Log

Controlla i log del server Flask per vedere:
```
[AI] Formatting patient data...
[AI] Processing N attachments...
[AI] Added image: filename.jpg (1024x768)
[AI] Added image: filename2.png (800x600)
[AI] Calling Gemini API...
[AI] Response received from Gemini
[AI] Diagnosis text extracted, length: XXXX chars
```

### Formati Supportati

**Immagini (supportate):**
- JPG/JPEG
- PNG
- GIF
- BMP
- TIFF

**PDF (non ancora implementato):**
- L'IA riconosce i PDF allegati ma non ne estrae ancora il testo
- TODO futuro: implementare estrazione testo da PDF

## Limitazioni Attuali

1. **Dimensioni**: Gemini API ha limiti sulla dimensione delle immagini. Immagini molto grandi potrebbero causare errori
2. **Numero**: Non c'è limite sul numero di immagini, ma più immagini = più tempo di elaborazione
3. **PDF**: I PDF vengono riconosciuti ma il loro contenuto non viene ancora estratto per l'analisi

## Troubleshooting

### Errore: "No module named 'PIL'"
```bash
pip install Pillow>=10.0.0
```

### Errore: "API quota exceeded"
- Verifica di avere crediti API Gemini disponibili
- Considera di ridurre il numero di immagini allegate

### L'IA non menziona le immagini
- Verifica che le immagini siano state correttamente salvate nella scheda clinica
- Controlla i log del server per vedere se le immagini sono state processate
- Verifica che il formato dell'immagine sia supportato (JPG, PNG, GIF, BMP, TIFF)

## Esempio Output Atteso

Quando l'IA analizza una scheda clinica con immagini allegate, la risposta dovrebbe includere sezioni come:

```
ANALISI DATI CLINICI:
...

ANALISI IMMAGINI ALLEGATE:
Immagine 1 (radiografia_torace.jpg): Si osserva...
Immagine 2 (ecg_12derivazioni.png): Il tracciato mostra...

QUADRO CLINICO:
In base ai dati clinici forniti e alle immagini analizzate...

DIAGNOSI PRESUNTIVA:
Considerando i sintomi riportati e i reperti evidenziati nelle immagini...
```

## Prossimi Sviluppi

- [ ] Estrazione testo da PDF allegati
- [ ] Supporto per altri formati (DICOM per immagini mediche)
- [ ] Anteprima delle immagini nell'interfaccia quando si visualizza la diagnosi
- [ ] Ottimizzazione dimensioni immagini prima dell'invio all'API
