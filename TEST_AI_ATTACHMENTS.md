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
