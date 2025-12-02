# MongoDB Database Schema Documentation

Documentazione completa degli schemi MongoDB per EarlyCare Gateway.

## Indice

1. [Panoramica](#panoramica)
2. [Collections](#collections)
3. [Schemi Dettagliati](#schemi-dettagliati)
4. [Relazioni tra Collections](#relazioni-tra-collections)
5. [Indici](#indici)
6. [Esempi di Query](#esempi-di-query)

---

## Panoramica

Il database EarlyCare Gateway utilizza MongoDB per memorizzare dati clinici completi, supportando:

- **Multi-modalità**: Testi, segnali, immagini
- **Validazione automatica**: Schema validation integrata
- **Tracciabilità**: Audit logging completo
- **Performance**: Indici ottimizzati per query frequenti
- **Workflow completo**: Dalla raccolta dati alla decisione clinica

### Database: `earlycare`

**Collections principali:**
- `patients` - Informazioni demografiche dei pazienti
- `clinical_data` - Dati clinici multi-modali
- `patient_records` - Record di incontri clinici completi
- `decision_support` - Risultati di supporto decisionale
- `audit_logs` - Log di audit per compliance

---

## Collections

### 1. `patients`
**Scopo**: Memorizza informazioni demografiche e anamnestiche dei pazienti

**Documenti**: ~1KB per paziente

**Validazione**: Moderate (warn)

### 2. `clinical_data`
**Scopo**: Memorizza tutti i tipi di dati clinici (testo, segnali, immagini)

**Documenti**: Variabile (1KB-100MB)

**Validazione**: Moderate (warn)

### 3. `patient_records`
**Scopo**: Memorizza record completi di incontri clinici con contesto di processamento

**Documenti**: ~5-20KB per record

**Validazione**: Moderate (warn)

### 4. `decision_support`
**Scopo**: Memorizza risultati di analisi AI e supporto decisionale

**Documenti**: ~10-50KB per decisione

**Validazione**: Moderate (warn)

### 5. `audit_logs`
**Scopo**: Traccia tutte le operazioni per compliance e sicurezza

**Documenti**: ~500 bytes per evento

**Validazione**: Strict (error)

---

## Schemi Dettagliati

### patients

```javascript
{
  "_id": ObjectId,                    // MongoDB ID
  "patient_id": String,               // ID univoco paziente (UNIQUE INDEX)
  "date_of_birth": Date,              // Data di nascita
  "gender": String,                   // "male", "female", "other", "unknown"
  "medical_record_number": String,    // Numero cartella clinica (INDEXED)
  "age": Int | null,                  // Età calcolata
  "ethnicity": String | null,         // Etnia
  "primary_language": String,         // Lingua (default: "en")
  "chief_complaint": String | null,   // Motivo principale visita
  "medical_history": Array<String>,   // Storia clinica
  "current_medications": Array<String>, // Farmaci attuali
  "allergies": Array<String>,         // Allergie (INDEXED)
  "created_at": Date,                 // Timestamp creazione
  "updated_at": Date                  // Timestamp ultimo aggiornamento
}
```

**Campi obbligatori**: `patient_id`, `date_of_birth`, `gender`, `medical_record_number`

**Esempi di valori**:
```javascript
{
  "patient_id": "P2024001",
  "date_of_birth": ISODate("1975-03-15"),
  "gender": "female",
  "medical_record_number": "MRN789456",
  "age": 49,
  "chief_complaint": "Chest pain",
  "medical_history": ["Hypertension", "Type 2 Diabetes"],
  "current_medications": ["Metformin 1000mg", "Lisinopril 10mg"],
  "allergies": ["Penicillin"]
}
```

---

### clinical_data

**Schema poliformico** - campi diversi in base a `data_type`

#### Campi comuni a tutti i tipi:

```javascript
{
  "_id": ObjectId,
  "data_id": String,              // ID univoco dato (UNIQUE INDEX)
  "patient_id": String,           // Riferimento paziente (INDEXED)
  "timestamp": Date,              // Timestamp raccolta (INDEXED)
  "source": String,               // Fonte dati (INDEXED)
  "data_type": String,            // "text", "signal", "image" (INDEXED)
  "quality_score": Double | null, // Score qualità 0.0-1.0
  "is_validated": Boolean,        // Flag validazione
  "metadata": Object,             // Metadati aggiuntivi
  "created_at": Date
}
```

**Valori per `source`**: 
- `"electronic_health_record"`
- `"laboratory"`
- `"imaging"`
- `"wearable_device"`
- `"manual_entry"`

#### Campi specifici per TEXT data:

```javascript
{
  // ... campi comuni ...
  "data_type": "text",
  "text_content": String,         // Contenuto testuale
  "language": String,             // Codice lingua
  "document_type": String | null  // Tipo documento (admission_note, discharge_summary, etc.)
}
```

**Esempio**:
```javascript
{
  "data_id": "TXT-P2024001-20241202143022",
  "patient_id": "P2024001",
  "timestamp": ISODate("2024-12-02T14:30:22"),
  "source": "electronic_health_record",
  "data_type": "text",
  "text_content": "Patient presents with chest pain...",
  "language": "en",
  "document_type": "admission_note",
  "quality_score": 0.95,
  "is_validated": true
}
```

#### Campi specifici per SIGNAL data:

```javascript
{
  // ... campi comuni ...
  "data_type": "signal",
  "signal_values": Array<Number>, // Array valori segnale
  "sampling_rate": Double,        // Frequenza campionamento (Hz)
  "signal_type": String,          // Tipo segnale (ECG, EEG, etc.)
  "units": String,                // Unità misura
  "duration": Double              // Durata in secondi
}
```

**Esempio**:
```javascript
{
  "data_id": "SIG-P2024001-20241202143025",
  "patient_id": "P2024001",
  "timestamp": ISODate("2024-12-02T14:30:25"),
  "source": "wearable_device",
  "data_type": "signal",
  "signal_values": [0.8, 0.85, 0.9, ...], // 1000 valori
  "sampling_rate": 250.0,
  "signal_type": "ECG Lead II",
  "units": "mV",
  "duration": 4.0,
  "quality_score": 0.92
}
```

#### Campi specifici per IMAGE data:

```javascript
{
  // ... campi comuni ...
  "data_type": "image",
  "image_path": String,           // Percorso file immagine
  "image_format": String,         // Formato (DICOM, PNG, JPEG, etc.)
  "modality": String,             // Modalità imaging (X-Ray, CT, MRI, etc.)
  "dimensions": Object,           // Dimensioni immagine
  "body_part": String | null,     // Parte corpo
  "contrast_used": Boolean        // Contrasto utilizzato
}
```

**Esempio**:
```javascript
{
  "data_id": "IMG-P2024001-20241202143030",
  "patient_id": "P2024001",
  "timestamp": ISODate("2024-12-02T14:30:30"),
  "source": "imaging",
  "data_type": "image",
  "image_path": "/images/chest_xray_P2024001.dcm",
  "image_format": "DICOM",
  "modality": "X-Ray",
  "dimensions": {
    "width": 1024,
    "height": 1024,
    "depth": 1
  },
  "body_part": "Chest",
  "contrast_used": false,
  "quality_score": 0.98
}
```

---

### patient_records

Record completo di un incontro clinico con contesto di processamento.

```javascript
{
  "_id": ObjectId,
  "encounter_id": String,              // ID incontro (UNIQUE INDEX)
  "patient_id": String,                // ID paziente (INDEXED)
  "patient": Object,                   // Snapshot informazioni paziente
  "clinical_data_refs": Array<String>, // Array di data_id (riferimenti)
  "encounter_timestamp": Date,         // Timestamp incontro (INDEXED)
  "priority": String,                  // "routine", "soon", "urgent", "emergency" (INDEXED)
  "metadata": Object,                  // Metadati generali
  "processing_context": {              // Contesto dalla pipeline di processamento
    "validation": {
      "is_valid": Boolean,
      "errors": Array<String>,
      "warnings": Array<String>
    },
    "enrichment": {
      "age_calculated": Boolean,
      "processing_timestamp": String,
      "data_count": Int,
      "average_data_quality": Double,
      "has_text_data": Boolean,
      "has_signal_data": Boolean,
      "has_image_data": Boolean,
      "has_critical_history": Boolean
    },
    "triage": {
      "score": Double,                 // Score triage 0-100
      "priority": String,
      "factors": Array<String>         // Fattori che hanno influenzato il triage
    },
    "privacy": {
      "pii_detected": Boolean,
      "anonymization_required": Boolean,
      "compliance_flags": Array<String>
    },
    "processing_times": Object         // Tempi processamento per handler (ms)
  },
  "created_at": Date
}
```

**Esempio**:
```javascript
{
  "encounter_id": "ENC-20241202143022",
  "patient_id": "P2024001",
  "patient": {
    "patient_id": "P2024001",
    "age": 49,
    "gender": "female",
    // ... altri dati paziente ...
  },
  "clinical_data_refs": [
    "TXT-P2024001-20241202143022",
    "SIG-P2024001-20241202143025",
    "IMG-P2024001-20241202143030"
  ],
  "encounter_timestamp": ISODate("2024-12-02T14:30:22"),
  "priority": "urgent",
  "processing_context": {
    "validation": {
      "is_valid": true,
      "errors": [],
      "warnings": []
    },
    "enrichment": {
      "average_data_quality": 0.95,
      "has_critical_history": true
    },
    "triage": {
      "score": 85.0,
      "priority": "urgent",
      "factors": [
        "Complex medical history",
        "Critical symptoms"
      ]
    },
    "processing_times": {
      "ValidationHandler": 12.5,
      "EnrichmentHandler": 8.3,
      "TriageHandler": 5.2
    }
  }
}
```

---

### decision_support

Risultati dell'analisi AI e supporto decisionale clinico.

```javascript
{
  "_id": ObjectId,
  "request_id": String,              // ID richiesta (UNIQUE INDEX)
  "patient_id": String,              // ID paziente (INDEXED)
  "encounter_id": String,            // ID incontro (INDEXED)
  "timestamp": Date,                 // Timestamp generazione (INDEXED)
  
  "diagnoses": Array<{               // Lista diagnosi
    "condition": String,
    "icd_code": String | null,
    "confidence_score": Double,      // 0.0-1.0
    "confidence_level": String,      // "very_low", "low", "medium", "high", "very_high"
    "evidence": Array<String>,
    "risk_factors": Array<String>,
    "differential_diagnoses": Array<String>,
    "recommended_tests": Array<String>,
    "recommended_specialists": Array<String>
  }>,
  
  "urgency_level": String,           // "routine", "soon", "urgent", "emergency" (INDEXED)
  "triage_score": Double,            // 0-100 (INDEXED)
  
  "alerts": Array<String>,           // Alert critici
  "warnings": Array<String>,         // Warning
  "clinical_notes": Array<String>,   // Note cliniche
  
  "models_used": Array<String>,      // Modelli AI utilizzati
  "processing_time_ms": Double,      // Tempo processamento
  
  "explanation": String | null,      // Spiegazione decisione
  "feature_importance": Object,      // Importanza features
  
  "metadata": Object,
  "created_at": Date
}
```

**Esempio**:
```javascript
{
  "request_id": "REQ-20241202143035",
  "patient_id": "P2024001",
  "encounter_id": "ENC-20241202143022",
  "timestamp": ISODate("2024-12-02T14:30:35"),
  "diagnoses": [
    {
      "condition": "Acute Coronary Syndrome",
      "icd_code": "I24.9",
      "confidence_score": 0.82,
      "confidence_level": "high",
      "evidence": [
        "Chest pain with radiation",
        "Elevated cardiac biomarkers"
      ],
      "recommended_tests": [
        "Coronary angiography",
        "Echocardiogram"
      ],
      "recommended_specialists": ["Cardiology"]
    }
  ],
  "urgency_level": "urgent",
  "triage_score": 85.0,
  "alerts": [
    "CRITICAL: Suspected ACS - immediate cardiology consult"
  ],
  "models_used": [
    "CardioNet-v2.3",
    "ClinicalBERT-diagnosis"
  ],
  "processing_time_ms": 2847.5,
  "explanation": "High probability of acute coronary syndrome...",
  "feature_importance": {
    "chest_pain_severity": 0.35,
    "ecg_changes": 0.28,
    "cardiac_biomarkers": 0.22
  }
}
```

---

### audit_logs

Log completo per audit e compliance.

```javascript
{
  "_id": ObjectId,
  "event_id": String,              // ID evento (UNIQUE INDEX)
  "timestamp": Date,               // Timestamp evento (INDEXED)
  "event_type": String,            // Tipo evento (INDEXED)
  "user_id": String,               // ID utente (INDEXED)
  "patient_id": String | null,     // ID paziente (INDEXED)
  "resource_type": String | null,  // Tipo risorsa
  "resource_id": String | null,    // ID risorsa
  "action": String,                // Descrizione azione
  "ip_address": String | null,     // IP utente
  "success": Boolean,              // Successo operazione
  "error_message": String | null,  // Messaggio errore
  "metadata": Object               // Metadati aggiuntivi
}
```

**Valori per `event_type`**:
- `"access"` - Accesso a risorse
- `"create"` - Creazione record
- `"update"` - Aggiornamento record
- `"delete"` - Eliminazione record
- `"export"` - Esportazione dati
- `"anonymize"` - Anonimizzazione
- `"process"` - Processamento dati
- `"error"` - Eventi di errore

**Esempio**:
```javascript
{
  "event_id": "AUD-20241202143022123456",
  "timestamp": ISODate("2024-12-02T14:30:22"),
  "event_type": "create",
  "user_id": "SYSTEM",
  "patient_id": "P2024001",
  "resource_type": "patient",
  "resource_id": "P2024001",
  "action": "Created patient record for P2024001",
  "success": true,
  "metadata": {}
}
```

---

## Relazioni tra Collections

```
patients (1) ──────┬──── (N) clinical_data
                   │         └─ data_id
                   │
                   ├──── (N) patient_records
                   │         ├─ clinical_data_refs[] → clinical_data.data_id
                   │         └─ encounter_id
                   │
                   ├──── (N) decision_support
                   │         └─ encounter_id → patient_records.encounter_id
                   │
                   └──── (N) audit_logs
```

**Pattern di riferimento**:
- `clinical_data` → riferimenti memorizzati in `patient_records.clinical_data_refs[]`
- `decision_support` → collegato tramite `encounter_id`
- Tutte le collections → collegate tramite `patient_id`

---

## Indici

### patients
- `patient_id` (UNIQUE)
- `medical_record_number`
- `date_of_birth`
- `created_at` (DESC)
- `allergies`

### clinical_data
- `data_id` (UNIQUE)
- `patient_id`
- `timestamp` (DESC)
- `data_type`
- `source`
- `(patient_id, timestamp)` (COMPOUND, DESC)
- `quality_score`

### patient_records
- `encounter_id` (UNIQUE)
- `patient_id`
- `encounter_timestamp` (DESC)
- `priority`
- `(patient_id, encounter_timestamp)` (COMPOUND, DESC)
- `processing_context.triage.score` (DESC)

### decision_support
- `request_id` (UNIQUE)
- `patient_id`
- `encounter_id`
- `timestamp` (DESC)
- `urgency_level`
- `triage_score` (DESC)
- `(patient_id, timestamp)` (COMPOUND, DESC)

### audit_logs
- `event_id` (UNIQUE)
- `timestamp` (DESC)
- `event_type`
- `user_id`
- `patient_id`
- `(timestamp, event_type)` (COMPOUND, DESC)

---

## Esempi di Query

### 1. Recuperare paziente con storia clinica complessa

```javascript
db.patients.find({
  $expr: { $gt: [{ $size: "$medical_history" }, 3] }
})
```

### 2. Trovare tutti i dati ECG di un paziente

```javascript
db.clinical_data.find({
  "patient_id": "P2024001",
  "data_type": "signal",
  "signal_type": /ECG/i
}).sort({ "timestamp": -1 })
```

### 3. Record con priorità urgent/emergency degli ultimi 7 giorni

```javascript
db.patient_records.find({
  "encounter_timestamp": {
    $gte: new Date(Date.now() - 7*24*60*60*1000)
  },
  "priority": { $in: ["urgent", "emergency"] }
}).sort({ "encounter_timestamp": -1 })
```

### 4. Diagnosi con alta confidenza

```javascript
db.decision_support.find({
  "diagnoses.confidence_score": { $gte: 0.8 }
}).sort({ "timestamp": -1 })
```

### 5. Pazienti con allergia specifica

```javascript
db.patients.find({
  "allergies": "Penicillin"
})
```

### 6. Dati clinici con qualità bassa

```javascript
db.clinical_data.find({
  "quality_score": { $lt: 0.7 }
}).sort({ "timestamp": -1 })
```

### 7. Audit log per un paziente

```javascript
db.audit_logs.find({
  "patient_id": "P2024001",
  "timestamp": {
    $gte: new Date("2024-12-01"),
    $lte: new Date("2024-12-31")
  }
}).sort({ "timestamp": -1 })
```

### 8. Record con processing context completo

```javascript
db.patient_records.find({
  "processing_context.triage.score": { $gte: 80 },
  "processing_context.enrichment.average_data_quality": { $gte: 0.9 }
})
```

### 9. Decisioni che richiedono consulto cardiologico

```javascript
db.decision_support.find({
  "diagnoses.recommended_specialists": "Cardiology"
})
```

### 10. Statistiche giornaliere

```javascript
db.patient_records.aggregate([
  {
    $match: {
      "encounter_timestamp": {
        $gte: new Date("2024-12-02T00:00:00"),
        $lt: new Date("2024-12-03T00:00:00")
      }
    }
  },
  {
    $group: {
      _id: "$priority",
      count: { $sum: 1 },
      avg_triage_score: {
        $avg: "$processing_context.triage.score"
      }
    }
  },
  {
    $sort: { count: -1 }
  }
])
```

---

## Best Practices

### Performance
- Utilizzare sempre gli indici nelle query
- Limitare i risultati con `.limit()`
- Usare proiezioni per ridurre i dati trasferiti
- Evitare query su array molto grandi senza indici

### Sicurezza
- Validare sempre i dati in input
- Utilizzare audit logging per ogni operazione sensibile
- Implementare controlli di accesso basati su ruoli
- Anonimizzare dati quando necessario

### Manutenzione
- Monitorare dimensioni collections
- Archiviare dati vecchi periodicamente
- Eseguire backup regolari
- Verificare integrità indici

---

## Inizializzazione

Per inizializzare il database con tutti gli schemi:

```bash
python scripts/initialize_database.py
```

Per testare l'integrazione completa:

```bash
python examples/example_mongodb_advanced.py
```

---

**Versione**: 1.0.0  
**Data**: 2 Dicembre 2024  
**Autore**: EarlyCare Gateway Team
