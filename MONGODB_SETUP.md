# MongoDB Integration for EarlyCare Gateway

Questo documento descrive l'integrazione MongoDB per la gestione dei dati dei pazienti nel sistema EarlyCare Gateway.

## Prerequisiti

1. **MongoDB Server**: Assicurati di avere MongoDB installato e in esecuzione
   - Download: https://www.mongodb.com/try/download/community
   - Porta predefinita: 27017

2. **Installazione dipendenze Python**:
```bash
pip install pymongo
```

## Configurazione

La configurazione di MongoDB si trova in `config/gateway_config.yaml`:

```yaml
database:
  mongodb:
    enabled: true
    connection_string: "mongodb+srv://angelospeed2003:kjhwoP4rXR3UsnaV@mav.0zz64yh.mongodb.net/"
    database_name: "earlycare"
```

### Configurazione con Autenticazione

Se il tuo server MongoDB richiede autenticazione:

```yaml
database:
  mongodb:
    enabled: true
    connection_string: "mongodb+srv://angelospeed2003:kjhwoP4rXR3UsnaV@mav.0zz64yh.mongodb.net/"
    database_name: "earlycare"
    authentication_database: "admin"
```

## Struttura del Database

### Collections

Il database `earlycare` contiene due collection principali:

#### 1. `patients` - Informazioni demografiche dei pazienti
- **Indici**:
  - `patient_id` (unique)
  - `medical_record_number`
  - `date_of_birth`

**Campi**:
- `patient_id`: Identificativo unico del paziente
- `date_of_birth`: Data di nascita
- `gender`: Genere (male, female, other, unknown)
- `medical_record_number`: Numero cartella clinica
- `age`: Età calcolata
- `ethnicity`: Etnia
- `primary_language`: Lingua principale
- `chief_complaint`: Motivo principale della visita
- `medical_history`: Elenco storia clinica
- `current_medications`: Farmaci attuali
- `allergies`: Allergie
- `created_at`: Data creazione
- `updated_at`: Data ultimo aggiornamento

#### 2. `patient_records` - Record clinici completi
- **Indici**:
  - `encounter_id` (unique)
  - `patient.patient_id`
  - `encounter_timestamp`
  - `priority`

**Campi**:
- `encounter_id`: Identificativo incontro clinico
- `patient`: Oggetto paziente completo
- `clinical_data`: Array di dati clinici (ECG, segni vitali, ecc.)
- `encounter_timestamp`: Data e ora dell'incontro
- `priority`: Priorità (routine, urgent, emergency)
- `metadata`: Metadati aggiuntivi
- `created_at`: Data creazione

## Utilizzo

### Inizializzazione Repository

```python
from src.database.mongodb_repository import MongoDBPatientRepository

# Connessione al database
db = MongoDBPatientRepository(
    connection_string="mongodb+srv://angelospeed2003:kjhwoP4rXR3UsnaV@mav.0zz64yh.mongodb.net/",
    database_name="earlycare"
)
```

### Operazioni CRUD sui Pazienti

#### Creazione Paziente

```python
from datetime import datetime
from src.models.patient import Patient, Gender

patient = Patient(
    patient_id="P001",
    date_of_birth=datetime(1985, 3, 15),
    gender=Gender.FEMALE,
    medical_record_number="MRN12345",
    chief_complaint="Chest pain",
    medical_history=["Hypertension", "Type 2 Diabetes"],
    current_medications=["Metformin", "Lisinopril"],
    allergies=["Penicillin"]
)
patient.calculate_age()

# Salva nel database
db.save_patient(patient)
```

#### Lettura Paziente

```python
# Recupera paziente per ID
patient = db.get_patient("P001")
print(f"Patient: {patient.patient_id}, Age: {patient.age}")
```

#### Aggiornamento Paziente

```python
# Modifica informazioni
patient.current_medications.append("Aspirin")

# Aggiorna nel database
db.update_patient(patient)
```

#### Eliminazione Paziente

```python
db.delete_patient("P001")
```

### Ricerca Pazienti

```python
# Trova tutti i pazienti di genere femminile
female_patients = db.find_patients({"gender": "female"})

# Trova pazienti con allergie specifiche
penicillin_allergy = db.find_patients({"allergies": "Penicillin"})

# Trova pazienti nati dopo una certa data
from datetime import datetime
recent_patients = db.find_patients({
    "date_of_birth": {"$gte": datetime(2000, 1, 1)}
})
```

### Gestione Patient Records

#### Salvataggio Record Clinico

```python
from src.models.patient import PatientRecord
from src.models.clinical_data import ClinicalData, ClinicalDataType

# Crea dati clinici
ecg_data = ClinicalData(
    data_type=ClinicalDataType.ECG,
    timestamp=datetime.now(),
    values={"heart_rate": 85, "rhythm": "normal sinus"},
    unit="bpm",
    source="ECG Monitor"
)

# Crea record paziente
patient_record = PatientRecord(
    patient=patient,
    encounter_id="ENC001",
    encounter_timestamp=datetime.now(),
    priority="urgent"
)
patient_record.add_clinical_data(ecg_data)

# Salva nel database
db.save_patient_record(patient_record)
```

#### Recupero Record

```python
# Ottieni ultimi 10 record per un paziente
records = db.get_patient_records("P001", limit=10)

# Ottieni record per encounter ID
record = db.get_record_by_encounter("ENC001")

# Trova record per priorità
urgent_records = db.find_records_by_priority("urgent", limit=50)

# Ottieni record delle ultime 24 ore
recent = db.get_recent_records(hours=24, limit=100)
```

### Statistiche Database

```python
stats = db.get_statistics()
print(f"Total patients: {stats['total_patients']}")
print(f"Total records: {stats['total_records']}")
print(f"Emergency cases: {stats['priority_counts']['emergency']}")
```

## Script di Esempio

Esegui lo script di esempio per testare l'integrazione:

```bash
python examples/example_mongodb_usage.py
```

## Sicurezza e Privacy

### Anonimizzazione

I modelli `Patient` e `PatientRecord` supportano l'anonimizzazione:

```python
# Anonimizza prima di salvare
anonymized_patient = patient.anonymize()
db.save_patient(anonymized_patient)
```

### Best Practices

1. **Backup regolari**: Configura backup automatici del database
2. **Autenticazione**: Usa sempre autenticazione in produzione
3. **Crittografia**: Abilita crittografia at-rest e in-transit
4. **Accesso limitato**: Concedi solo i permessi necessari
5. **Audit logging**: Monitora tutti gli accessi ai dati sensibili

## Monitoraggio

### Log

Il repository MongoDB logga automaticamente le operazioni:

```python
import logging
logging.basicConfig(level=logging.INFO)
```

### Performance

Gli indici sono creati automaticamente per ottimizzare le query più comuni:
- Ricerca per `patient_id`
- Ricerca per `medical_record_number`
- Query per `priority`
- Ordinamento per `encounter_timestamp`

## Troubleshooting

### MongoDB non si connette

```python
# Verifica che MongoDB sia in esecuzione
# Windows:
net start MongoDB

# Linux/Mac:
sudo systemctl start mongod
```

### Errore di autenticazione

Verifica le credenziali nel connection string:
```
mongodb+srv://angelospeed2003:kjhwoP4rXR3UsnaV@mav.0zz64yh.mongodb.net/
```

### Indici mancanti

Gli indici vengono creati automaticamente all'inizializzazione. Per ricrearli manualmente:

```python
db._create_indexes()
```

## Riferimenti

- [MongoDB Documentation](https://docs.mongodb.com/)
- [PyMongo Documentation](https://pymongo.readthedocs.io/)
- [MongoDB Query Operators](https://docs.mongodb.com/manual/reference/operator/query/)
