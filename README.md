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
