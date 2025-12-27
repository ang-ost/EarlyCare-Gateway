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
