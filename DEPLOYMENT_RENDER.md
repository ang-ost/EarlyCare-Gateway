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
