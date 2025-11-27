# 🖥️ EarlyCare Gateway - Interfaccia Grafica

## 📋 Panoramica

L'interfaccia grafica (GUI) di EarlyCare Gateway fornisce un modo intuitivo per processare cartelle cliniche e visualizzare i risultati diagnostici.

## 🚀 Avvio Rapido

### Avviare l'interfaccia grafica:
```bash
python run_gui.py
```

## 🎨 Caratteristiche

### 1. **Interfaccia Moderna**
- Design professionale con tema chiaro
- Layout organizzato con pannelli distinti
- Indicatore di stato del sistema in tempo reale
- Barra di progresso per operazioni lunghe

### 2. **Gestione Cartelle Cliniche**
- 📁 Selezione intuitiva della cartella
- 👤 Visualizzazione automatica info paziente
- 📄 Elenco dettagliato di tutti i file rilevati
- 🔍 Classificazione automatica per tipo (note, segnali, immagini)

### 3. **Elaborazione**
- 🚀 Pulsante di elaborazione con feedback visivo
- ⚙️ Processamento in background (non blocca l'interfaccia)
- 📊 Barra di progresso in tempo reale
- 📝 Log dettagliati delle operazioni

### 4. **Visualizzazione Risultati**
Organizzati in 3 tab:

#### **💊 Diagnosi**
- Informazioni paziente e request ID
- Livello di urgenza e punteggio triage
- Lista diagnosi con confidenza
- Evidenze cliniche
- Test e consulti raccomandati
- Alert e avvisi critici

#### **📋 Dettagli**
- Modelli AI utilizzati
- Metadati del processamento
- Note cliniche aggiuntive
- Spiegazioni del processo decisionale

#### **📝 Log**
- Log in tempo reale delle operazioni
- Timestamp per ogni evento
- Messaggi di errore e warning
- Tema scuro per ridurre affaticamento visivo

### 5. **Menu e Funzionalità**

#### **File**
- Apri Cartella Clinica
- Crea Template (genera struttura esempio)
- Esporta Risultati (salva in JSON)
- Esci

#### **Strumenti**
- Configurazione Gateway
- Metriche Sistema (statistiche in tempo reale)
- Log Audit (tracciamento completo)

#### **Aiuto**
- Documentazione integrata
- Informazioni sull'applicazione

## 📁 Struttura Cartella Clinica

La GUI supporta automaticamente questa struttura:

```
cartella_paziente/
├── patient_info.json          # Info demografiche (opzionale)
│   ├── patient_id
│   ├── date_of_birth
│   ├── gender
│   ├── chief_complaint
│   ├── medical_history
│   ├── medications
│   └── allergies
│
├── notes/                     # Note cliniche
│   ├── ammissione.txt
│   ├── progressi.txt
│   └── dimissione.txt
│
├── signals/                   # Dati segnale
│   ├── ecg_data.json
│   └── vitali.csv
│
└── images/                    # Immagini mediche
    ├── rx_torace.dcm
    └── tac.png
```

## 🎯 Workflow Tipico

### 1. **Preparazione**
```bash
# Avvia l'interfaccia
python run_gui.py

# Il sistema si inizializza automaticamente
# Indicatore verde = sistema pronto
```

### 2. **Caricamento Cartella**
- Clicca "Seleziona Cartella" o File > Apri Cartella Clinica
- Naviga alla cartella del paziente
- La GUI caricherà automaticamente:
  - Informazioni paziente (da patient_info.json)
  - Lista di tutti i file rilevati
  - Classificazione per tipo

### 3. **Verifica Dati**
- Controlla le informazioni paziente nel pannello sinistro
- Verifica i file rilevati nell'elenco
- Assicurati che tutti i file necessari siano presenti

### 4. **Elaborazione**
- Clicca "🚀 Elabora Cartella Clinica"
- Osserva la barra di progresso
- Monitora i log in tempo reale (tab Log)
- L'elaborazione avviene in background (interfaccia resta responsiva)

### 5. **Visualizzazione Risultati**
- **Tab Diagnosi**: Visualizza diagnosi, urgenza, raccomandazioni
- **Tab Dettagli**: Esamina metadati e spiegazioni
- **Tab Log**: Verifica il processo di elaborazione

### 6. **Esportazione**
- File > Esporta Risultati
- Scegli nome e percorso file
- Salva in formato JSON per analisi successive

## 🔧 Funzionalità Avanzate

### **Creazione Template**
Per creare rapidamente una cartella di esempio:
1. File > Crea Template
2. Scegli cartella di destinazione
3. Il sistema crea una struttura completa con:
   - patient_info.json esempio
   - Note cliniche campione
   - Dati ECG simulati
   - README con istruzioni

### **Metriche Sistema**
Strumenti > Metriche Sistema mostra:
- Numero richieste elaborate
- Success rate
- Tempi di elaborazione (medio/min/max)
- Statistiche aggregate

### **Elaborazione Multipla**
Puoi elaborare più cartelle in sequenza:
1. Elabora prima cartella
2. Esporta risultati (opzionale)
3. Seleziona nuova cartella
4. Elabora di nuovo

## 🎨 Personalizzazione

### **Colori e Tema**
I colori sono definiti in `gui/main_window.py`:
```python
self.colors = {
    'primary': '#2c3e50',     # Blu scuro
    'secondary': '#3498db',   # Blu
    'success': '#27ae60',     # Verde
    'danger': '#e74c3c',      # Rosso
    'warning': '#f39c12',     # Arancione
    'light': '#ecf0f1',       # Grigio chiaro
    'dark': '#34495e',        # Grigio scuro
    'white': '#ffffff'        # Bianco
}
```

### **Dimensioni Finestra**
Modifica in `__init__`:
```python
self.root.geometry("1200x800")  # Larghezza x Altezza
```

## 🐛 Risoluzione Problemi

### **L'interfaccia non si avvia**
```bash
# Verifica che tkinter sia installato
python -c "import tkinter"

# Su Linux potrebbe servire:
# sudo apt-get install python3-tk
```

### **Errore "Sistema non inizializzato"**
- Verifica che tutti i file di configurazione esistano (config/*.yaml)
- Controlla i log nella directory `logs/`
- L'indicatore rosso nel header indica problema di inizializzazione

### **Elaborazione bloccata**
- L'elaborazione avviene in thread separato
- Se si blocca, verifica il tab Log per errori
- Riavvia l'applicazione se necessario

### **File non rilevati**
Estensioni supportate:
- **Testi**: .txt, .md, .note, .report
- **Segnali**: .csv, .json, .dat
- **Immagini**: .dcm, .png, .jpg, .jpeg, .tif, .tiff

Verifica che i file abbiano le estensioni corrette.

## 📊 Performance

### **Tempi Tipici**
- Caricamento cartella: < 1 secondo
- Elaborazione (10 file): 100-500ms
- Elaborazione (50 file): 500-2000ms
- Visualizzazione risultati: < 100ms

### **Ottimizzazione**
L'elaborazione avviene in thread separato per:
- Non bloccare l'interfaccia
- Permettere cancellazione (feature futura)
- Mostrare progresso in tempo reale

## 🔒 Sicurezza

- I dati del paziente rimangono locali
- Nessun invio a server esterni
- Audit log completo delle operazioni
- Risultati esportabili con controllo dell'utente

## 📝 Shortcut Tastiera

(Da implementare in versioni future)
- `Ctrl+O`: Apri cartella
- `Ctrl+P`: Elabora
- `Ctrl+S`: Esporta risultati
- `Ctrl+Q`: Esci

## 🚀 Prossimi Sviluppi

- [ ] Drag & drop per cartelle
- [ ] Anteprima immagini mediche
- [ ] Grafici interattivi per segnali
- [ ] Comparazione tra multiple diagnosi
- [ ] Tema scuro completo
- [ ] Editor configurazione integrato
- [ ] Esportazione PDF dei risultati
- [ ] Multi-lingua (EN/IT)

## 💡 Tips & Tricks

1. **Usa il template**: Prima volta? Crea un template per capire la struttura
2. **Verifica prima**: Controlla sempre i file rilevati prima di elaborare
3. **Salva i risultati**: Esporta sempre in JSON per archivio
4. **Monitora i log**: Il tab Log è prezioso per debugging
5. **Metriche utili**: Controlla le metriche per vedere performance sistema

## 📞 Supporto

Per problemi o domande:
1. Consulta questa documentazione
2. Verifica i log in `logs/gui_audit.log`
3. Controlla README.md e ARCHITECTURE.md del progetto
4. Apri una issue su GitHub

---

**Versione GUI**: 1.0  
**Ultima modifica**: 27 Novembre 2025  
**Compatibilità**: Python 3.8+, Windows/Linux/macOS
