# 🚨 PROBLEMA 401 UNAUTHORIZED - SOLUZIONE

## 🎯 Il Problema Reale

Gli endpoint restituiscono **401 Unauthorized** perché:

1. ❌ La variabile d'ambiente `FRONTEND_URL` non è configurata su Render
2. ❌ Il backend non accetta richieste dal frontend perché l'origin non è in `allowed_origins`
3. ❌ I cookie di sessione non vengono accettati

## ✅ SOLUZIONE IMMEDIATA

### Opzione A: Configurare FRONTEND_URL su Render (CONSIGLIATA)

1. **Vai su Render Dashboard**: https://dashboard.render.com
2. **Seleziona `earlycare-gateway-backend`**
3. **Vai su "Environment"** (nel menu a sinistra)
4. **Clicca "Add Environment Variable"**
5. **Aggiungi:**
   - Key: `FRONTEND_URL`
   - Value: `https://earlycare-gateway-frontend.onrender.com` (o il tuo URL frontend esatto)
6. **Salva**
7. Il servizio si re-deploierà automaticamente (2-3 minuti)

### Opzione B: Permettere Tutti gli Origin (TEMPORANEO - PER TEST)

Se vuoi testare subito, posso modificare il codice per accettare tutte le origin in produzione (non sicuro ma funziona per test).

---

## 🔍 Verifica URL Frontend

Prima di configurare, verifica qual è l'URL ESATTO del tuo frontend:

1. Render Dashboard → Servizi
2. Trova il servizio frontend (probabilmente `earlycare-gateway-frontend` o `earlycare-frontend`)
3. Copia l'URL esatto (es. `https://earlycare-gateway-frontend.onrender.com`)

---

## 📝 Configurazione Manuale Render

### Passo 1: Backend Environment Variables

Assicurati che il backend abbia queste variabili:

```
FRONTEND_URL=https://TUO-FRONTEND.onrender.com
RENDER=true
MONGODB_CONNECTION_STRING=mongodb+srv://...
GEMINI_API_KEY=...
CHATBOT_GEMINI_API_KEY=...
```

### Passo 2: Frontend Environment Variables

Assicurati che il frontend abbia:

```
VITE_API_URL=https://earlycare-gateway-backend.onrender.com
```

---

## 🧪 Test Dopo Configurazione

1. **Attendi 2-3 minuti** che Render re-deploya
2. **Ricarica il frontend** (Ctrl+F5)
3. **Fai login di nuovo**
4. **Prova a creare un paziente**

Dovresti vedere nei log Render:
```
🌐 CORS allowed origins: ['https://TUO-FRONTEND.onrender.com']
🔧 Production mode: True
🍪 Cookie config - Secure: True, SameSite: None
```

---

## 🆘 Se Non Puoi Configurare Subito

Posso creare una versione del codice che:
- Permette tutti gli origin temporaneamente
- Logga quale origin sta facendo la richiesta
- Così possiamo vedere esattamente cosa sta succedendo

Vuoi che faccia questa modifica temporanea?

---

## 📊 Checklist

- [ ] Verifica URL frontend esatto su Render
- [ ] Aggiungi `FRONTEND_URL` nelle env variables del backend
- [ ] Aspetta re-deploy automatico (2-3 minuti)
- [ ] Verifica log backend per "CORS allowed origins"
- [ ] Ricarica frontend e re-fai login
- [ ] Test creazione paziente

---

**Qual è l'URL ESATTO del tuo frontend su Render?**
