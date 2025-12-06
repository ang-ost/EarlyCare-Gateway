# EarlyCare Gateway - Web Application

## 🌐 Applicazione Web

L'applicazione EarlyCare Gateway è ora disponibile come **Web App** accessibile tramite browser.

## 🚀 Avvio Rapido

### Metodo 1: Script PowerShell (Consigliato)
```powershell
.\start_webapp.ps1
```

### Metodo 2: Python diretto
```powershell
python run_webapp.py
```

## 🌍 Accesso all'Applicazione

Dopo l'avvio, apri il browser e vai su:
- **http://localhost:5000**
- **http://127.0.0.1:5000**

## ✨ Funzionalità

### 1. **Gestione Pazienti**
- Ricerca pazienti per codice fiscale o nome/cognome
- Inserimento nuovi pazienti con dati anagrafici completi
- Visualizzazione informazioni paziente

### 2. **Schede Cliniche**
- Creazione nuove schede cliniche
- Visualizzazione storico schede del paziente
- Inserimento dati clinici completi:
  - Motivo della visita
  - Sintomi attuali
  - Diagnosi
  - Trattamento
  - Parametri vitali
  - Note aggiuntive

### 3. **Gestione File**
- Upload file singoli
- Upload cartelle cliniche complete (drag & drop)
- Elaborazione automatica dei file caricati
- Integrazione con il gateway clinico

### 4. **Esportazione Dati**
- Esportazione completa dei dati paziente in formato JSON
- Include tutte le schede cliniche e i dati associati

### 5. **Monitoraggio Sistema**
- Visualizzazione metriche sistema
- Stato connessione database
- Indicatore di stato in tempo reale

## 📋 Requisiti

- Python 3.8 o superiore
- Flask 3.0+
- MongoDB (opzionale, per persistenza dati)
- Browser moderno (Chrome, Firefox, Edge, Safari)

## 🔧 Installazione Dipendenze

Le dipendenze vengono installate automaticamente con lo script di avvio, oppure manualmente con:

```powershell
pip install -r requirements.txt
```

## 🗂️ Struttura Progetto

```
webapp/
├── app.py              # Backend Flask
├── templates/          # Template HTML
│   ├── base.html      # Template base
│   └── index.html     # Pagina principale
└── static/            # File statici
    ├── css/
    │   └── style.css  # Stili dell'applicazione
    └── js/
        └── main.js    # JavaScript client-side
```

## 🎨 Interfaccia Utente

### Layout Principale
- **Header**: Titolo e indicatore stato sistema
- **Navbar**: Menu di navigazione con accesso rapido alle funzionalità
- **Pannello Sinistro**: Ricerca pazienti, info paziente, upload file
- **Pannello Destro**: Visualizzazione schede cliniche

### Modal Dialog
- **Ricerca Paziente**: Form di ricerca avanzata
- **Nuovo Paziente**: Form dati anagrafici completo
- **Nuova Scheda Clinica**: Form completo per episodio clinico
- **Metriche Sistema**: Visualizzazione statistiche

## 🔒 Sicurezza

- Validazione input lato client e server
- Sanitizzazione nomi file
- Gestione sicura degli upload
- Sessioni Flask con secret key

## 📱 Responsive Design

L'interfaccia è completamente responsive e ottimizzata per:
- Desktop (1200px+)
- Tablet (768px - 1024px)
- Mobile (< 768px)

## 🔄 Differenze con GUI Desktop

| Funzionalità | GUI Desktop (Tkinter) | Web App (Flask) |
|--------------|----------------------|-----------------|
| Accesso | Applicazione locale | Browser web |
| Interfaccia | Finestre native | HTML/CSS/JS |
| Multi-utente | No | Sì (potenziale) |
| Accessibilità | Solo computer locale | Da qualsiasi dispositivo |
| Deployment | Installazione locale | Server web |

## 🚦 Utilizzo

1. **Avvia l'applicazione**
   ```powershell
   .\start_webapp.ps1
   ```

2. **Apri il browser** su http://localhost:5000

3. **Crea o cerca un paziente**
   - Clicca su "Cerca Paziente" o "Nuovo Paziente"
   - Inserisci i dati richiesti

4. **Aggiungi schede cliniche**
   - Seleziona un paziente
   - Clicca su "Aggiungi Scheda"
   - Compila il form clinico

5. **Carica file**
   - Trascina file nell'area upload
   - Oppure clicca per selezionare
   - Clicca "Carica File" per elaborare

6. **Esporta dati**
   - Seleziona un paziente
   - Clicca "Esporta"
   - Il file JSON verrà scaricato

## 🛠️ Configurazione

La configurazione del gateway rimane invariata e utilizza gli stessi file YAML:
- `config/gateway_config.yaml`
- `config/models_config.yaml`
- `config/privacy_config.yaml`
- `config/integrations_config.yaml`

## 📊 API Endpoints

### Pazienti
- `POST /api/patient/search` - Ricerca paziente
- `POST /api/patient/create` - Crea nuovo paziente
- `GET /api/patient/<fiscal_code>/records` - Ottieni schede cliniche

### Schede Cliniche
- `POST /api/patient/<fiscal_code>/add-record` - Aggiungi scheda

### File
- `POST /api/file/upload` - Upload file singolo
- `POST /api/folder/upload` - Upload cartella clinica

### Sistema
- `GET /api/metrics` - Ottieni metriche sistema
- `GET /api/export/<fiscal_code>` - Esporta dati paziente

## 🐛 Troubleshooting

### Porta già in uso
Se la porta 5000 è occupata, modifica in `webapp/app.py`:
```python
app.run(debug=True, host='0.0.0.0', port=5001)  # Cambia porta
```

### Database non connesso
- Verifica che MongoDB sia in esecuzione
- Controlla le credenziali in `credenziali_db.txt`
- L'applicazione funziona anche senza database

### Errori upload file
- Verifica che la cartella `webapp/uploads` esista
- Controlla i permessi di scrittura
- Dimensione massima file: 100MB

## 📝 Note

- I dati caricati vengono salvati in `webapp/uploads/`
- Le esportazioni vengono salvate in `webapp/uploads/exports/`
- La sessione rimane attiva finché il browser è aperto
- I file temporanei vengono organizzati per codice fiscale e timestamp

## 🎯 Prossimi Sviluppi

- [ ] Autenticazione utenti
- [ ] Gestione ruoli e permessi
- [ ] Dashboard analitiche
- [ ] Notifiche in tempo reale
- [ ] API REST completa
- [ ] Integrazione WebSocket

## 📞 Supporto

Per problemi o domande, consulta la documentazione principale in `README.md` o `GUI_README.md`.
