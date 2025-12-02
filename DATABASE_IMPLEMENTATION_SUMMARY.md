# Database MongoDB - Riepilogo Implementazione

## 📋 Panoramica

È stato implementato un sistema completo di persistenza MongoDB per EarlyCare Gateway che rispecchia fedelmente il funzionamento del codice esistente, includendo tutti i modelli, la pipeline di processamento (Chain of Responsibility), e il supporto decisionale.

---

## 🗂️ File Creati/Modificati

### Nuovi File

1. **`src/database/schemas.py`** (630 righe)
   - Definizioni complete degli schemi MongoDB
   - 5 collection schemas: patients, clinical_data, patient_records, decision_support, audit_logs
   - Validazione JSON Schema integrata
   - Definizioni indici ottimizzati

2. **`src/database/mongodb_repository.py`** (aggiornato, ~450 righe)
   - Repository completo per tutte le operazioni CRUD
   - Gestione clinical_data (text, signal, image)
   - Gestione decision_support
   - Audit logging integrato
   - Statistiche database

3. **`scripts/initialize_database.py`** (200 righe)
   - Script per inizializzare il database
   - Crea collections con schema validation
   - Configura tutti gli indici
   - Verifica struttura database

4. **`examples/example_mongodb_advanced.py`** (520 righe)
   - Workflow completo end-to-end
   - Creazione pazienti multi-modali
   - Processing context dalla chain of responsibility
   - Decision support con diagnosi
   - Audit logging
   - Query avanzate

5. **`MONGODB_SCHEMAS.md`** (1000+ righe)
   - Documentazione completa degli schemi
   - Esempi per ogni collection
   - Relazioni tra collections
   - Query di esempio
   - Best practices

### File Aggiornati

6. **`src/database/__init__.py`**
   - Export schemi e repository

7. **`requirements.txt`**
   - Aggiunto `pymongo>=4.6.0`

8. **`config/gateway_config.yaml`**
   - Sezione configurazione MongoDB

9. **`README.md`**
   - Istruzioni setup MongoDB

---

## 🏗️ Struttura Database

### Collections

#### 1. **patients** - Anagrafica pazienti
- Patient ID univoco
- Dati demografici completi
- Storia clinica, farmaci, allergie
- Timestamp creazione/aggiornamento

#### 2. **clinical_data** - Dati clinici multi-modali
**Schema poliformico** supporta 3 tipi:

- **TEXT**: Note cliniche, report, trascrizioni
  - `text_content`, `language`, `document_type`
  
- **SIGNAL**: ECG, EEG, segni vitali
  - `signal_values[]`, `sampling_rate`, `signal_type`, `duration`
  
- **IMAGE**: X-ray, CT, MRI, DICOM
  - `image_path`, `modality`, `dimensions`, `body_part`

Ogni tipo ha:
- Validazione automatica
- Quality score (0.0-1.0)
- Source tracking
- Metadata estensibili

#### 3. **patient_records** - Record incontri clinici
Memorizza il **workflow completo** della Chain of Responsibility:

```javascript
{
  "encounter_id": "ENC-xxx",
  "patient_id": "P2024001",
  "patient": { /* snapshot paziente */ },
  "clinical_data_refs": ["data_id1", "data_id2"],
  "priority": "urgent",
  
  // ⭐ CONTESTO DI PROCESSAMENTO
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

#### 4. **decision_support** - Risultati AI
Memorizza output completo del sistema decisionale:

- **Diagnoses**: Array di diagnosi con:
  - Condizione e codice ICD
  - Confidence score (0.0-1.0)
  - Evidenze cliniche
  - Fattori di rischio
  - Diagnosi differenziali
  - Test raccomandati
  - Specialisti da consultare

- **Triage**: Urgency level e triage score

- **Alerts/Warnings**: Notifiche critiche

- **Traceability**: 
  - Modelli AI utilizzati
  - Tempi di processamento
  - Feature importance
  - Spiegazioni human-readable

#### 5. **audit_logs** - Compliance e sicurezza
- Log completo di tutte le operazioni
- Tracciamento accessi ai dati
- Validazione strict (errore su schema invalid)
- Filtri per paziente, utente, tipo evento, date

---

## 🔍 Indici Ottimizzati

### Performance-critical indexes

**patients**:
- `patient_id` (UNIQUE)
- `medical_record_number`
- `allergies` (per query allergie specifiche)

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

---

## 🔄 Workflow Completo Supportato

### 1. Registrazione Paziente
```python
patient = Patient(...)
db.save_patient(patient)
db.log_audit_event("create", user_id, "Patient created", patient_id)
```

### 2. Raccolta Dati Clinici
```python
# Testo
text_data = TextData(...)
# Segnale
signal_data = SignalData(...)
# Immagine
image_data = ImageData(...)

# Salvati automaticamente in clinical_data collection
```

### 3. Creazione Record con Processing Context
```python
patient_record = PatientRecord(patient, encounter_id)
patient_record.add_clinical_data(text_data)
patient_record.add_clinical_data(signal_data)

# Aggiungi context dalla Chain of Responsibility
context = {
    "validation": {...},
    "enrichment": {...},
    "triage": {...}
}
patient_record.metadata.update({"processing_context": context})

db.save_patient_record(patient_record)
```

### 4. Decision Support
```python
decision = DecisionSupport(...)
decision.add_diagnosis(diagnosis)
decision.urgency_level = UrgencyLevel.URGENT

db.save_decision_support(decision, encounter_id)
```

### 5. Query Avanzate
```python
# Tutti i record urgenti
urgent = db.find_records_by_priority("urgent")

# Dati clinici di un paziente per tipo
ecg_data = db.get_patient_clinical_data(patient_id, data_type="signal")

# Decisioni con alta confidenza
high_conf = db.get_decisions_by_urgency("emergency")

# Audit per paziente
logs = db.get_audit_logs(patient_id=patient_id)
```

---

## 📊 Statistiche Database

Il repository fornisce statistiche in tempo reale:

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

---

## 🎯 Mapping Modelli → MongoDB

### Patient Model → patients collection
✅ Tutti i campi del dataclass Patient
✅ Enumerazione Gender
✅ Liste (medical_history, medications, allergies)
✅ Metodi (calculate_age, anonymize)

### ClinicalData Models → clinical_data collection
✅ TextData, SignalData, ImageData
✅ Inheritance preservata con campo data_type
✅ Campi specifici per tipo
✅ Validazione per tipo

### PatientRecord → patient_records collection
✅ Snapshot completo paziente
✅ Riferimenti a clinical_data (non embedded)
✅ **Processing context completo** dalla chain
✅ Metadata estensibili

### DecisionSupport → decision_support collection
✅ Array di DiagnosisResult
✅ Enumerazioni (UrgencyLevel, ConfidenceLevel)
✅ Traceability completa
✅ Explainability (explanation, feature_importance)

---

## 🚀 Come Usare

### Setup Iniziale

```bash
# 1. Installa MongoDB
# Windows: https://www.mongodb.com/try/download/community
# Linux: sudo apt install mongodb

# 2. Avvia MongoDB
net start MongoDB  # Windows
sudo systemctl start mongod  # Linux

# 3. Installa dipendenze Python
pip install -r requirements.txt

# 4. Inizializza database
python scripts/initialize_database.py
```

### Esempio Base

```bash
python examples/example_mongodb_usage.py
```

### Esempio Avanzato (Workflow Completo)

```bash
python examples/example_mongodb_advanced.py
```

---

## 📖 Documentazione

- **[MONGODB_SETUP.md](MONGODB_SETUP.md)**: Guida setup e configurazione
- **[MONGODB_SCHEMAS.md](MONGODB_SCHEMAS.md)**: Documentazione completa schemi
- **[examples/example_mongodb_advanced.py](examples/example_mongodb_advanced.py)**: Workflow end-to-end

---

## ✨ Caratteristiche Principali

### ✅ Fedeltà al Codice
- Tutti i modelli esistenti supportati
- Processing context dalla Chain of Responsibility
- Decision support completo
- Audit logging integrato

### ✅ Performance
- Indici ottimizzati per query frequenti
- Compound indexes per query multi-campo
- Proiezioni per ridurre trasferimento dati

### ✅ Flessibilità
- Schema poliformico per clinical_data
- Metadata estensibili
- Validazione configurabile (moderate/strict)

### ✅ Compliance
- Audit logging completo
- Support per anonimizzazione
- Tracciabilità end-to-end

### ✅ Scalabilità
- Separazione clinical_data da patient_records
- Riferimenti invece di embedding
- Indici per query veloci

---

## 🔐 Sicurezza

- Schema validation per integrità dati
- Audit logs con validation strict
- Support anonimizzazione integrato
- Configurazione autenticazione MongoDB

---

## 🎓 Esempi di Query Comuni

```python
# 1. Pazienti con allergie specifiche
db.find_patients({"allergies": "Penicillin"})

# 2. Record urgenti ultimi 7 giorni
urgent = db.find_records_by_priority("urgent", limit=50)

# 3. Dati ECG di un paziente
ecg = db.get_patient_clinical_data(
    patient_id="P2024001",
    data_type="signal"
)

# 4. Decisioni che richiedono cardiologo
decisions = db.decision_support_collection.find({
    "diagnoses.recommended_specialists": "Cardiology"
})

# 5. Audit log per compliance
logs = db.get_audit_logs(
    patient_id="P2024001",
    start_date=datetime(2024, 12, 1),
    end_date=datetime(2024, 12, 31)
)
```

---

## 📝 Note Tecniche

### Schema Validation
- **Level**: moderate (warn) per collections operative
- **Level**: strict (error) per audit_logs
- Validazione JSON Schema completa

### Naming Conventions
- Snake_case per campi MongoDB
- Enum values: lowercase strings
- IDs: Prefissi descrittivi (P-, ENC-, TXT-, SIG-, IMG-, REQ-, AUD-)

### Date Handling
- Tutti i timestamp: BSON Date
- Timezone: UTC
- Creazione automatica created_at

---

## 🎉 Conclusione

Il database MongoDB è completamente integrato con il sistema EarlyCare Gateway, fornendo:

✅ **Persistenza completa** di tutti i dati  
✅ **Schema validation** per integrità  
✅ **Indici ottimizzati** per performance  
✅ **Audit logging** per compliance  
✅ **Workflow end-to-end** documentato  
✅ **Scalabilità** per produzione  

Pronto per essere usato in sviluppo e produzione! 🚀
