# Come Connettere MongoDB Atlas con l'Estensione VS Code

## 🔌 Connection String per l'Estensione MongoDB VS Code

L'estensione MongoDB di VS Code richiede una connection string **con il database name** specificato.

### ✅ Connection String Corretta:

```
mongodb+srv://angelospeed2003:kjhwoP4rXR3UsnaV@mav.0zz64yh.mongodb.net/earlycare?retryWrites=true&w=majority
```

**Nota la differenza:** `/earlycare` viene PRIMA del `?`

### 📝 Passaggi per Connettere:

#### Metodo 1: Tramite Command Palette

1. Premi `Ctrl+Shift+P` (o `Cmd+Shift+P` su Mac)
2. Cerca e seleziona: **MongoDB: Connect**
3. Scegli: **Connect with Connection String**
4. Incolla la connection string:
   ```
   mongodb+srv://angelospeed2003:kjhwoP4rXR3UsnaV@mav.0zz64yh.mongodb.net/earlycare?retryWrites=true&w=majority
   ```
5. Premi Invio

#### Metodo 2: Tramite MongoDB View

1. Clicca sull'icona MongoDB nella barra laterale (foglia)
2. Clicca su **"Add Connection"**
3. Incolla la connection string completa
4. Opzionale: Dai un nome alla connessione (es: "EarlyCare Atlas")
5. Clicca **Connect**

### 🔐 Connection String Alternativa (Parametri SSL Espliciti)

Se la connessione standard non funziona, prova con parametri SSL espliciti:

```
mongodb+srv://angelospeed2003:kjhwoP4rXR3UsnaV@mav.0zz64yh.mongodb.net/earlycare?retryWrites=true&w=majority&ssl=true&authSource=admin
```

### 🏠 Alternativa: MongoDB Locale

Se continui ad avere problemi SSL (dovuti a Python 3.14 o limitazioni di rete), installa MongoDB Community Edition:

1. **Download:** https://www.mongodb.com/try/download/community
2. **Installa** MongoDB Community Server
3. **Avvia** MongoDB:
   ```powershell
   # Crea la directory dei dati
   mkdir C:\data\db
   
   # Avvia MongoDB
   mongod --dbpath C:\data\db
   ```
4. **Connetti con VS Code** usando:
   ```
   mongodb://localhost:27017/earlycare
   ```

### ⚙️ Configurazione Avanzata (Opzionale)

Se vuoi salvare la connessione nelle impostazioni di VS Code:

1. Apri Settings (`Ctrl+,`)
2. Cerca: `mongodb.connections`
3. Clicca su "Edit in settings.json"
4. Aggiungi:

```json
{
  "mongodb.connections": [
    {
      "id": "earlycare-atlas",
      "connectionString": "mongodb+srv://angelospeed2003:kjhwoP4rXR3UsnaV@mav.0zz64yh.mongodb.net/earlycare?retryWrites=true&w=majority",
      "name": "EarlyCare Atlas"
    }
  ]
}
```

## 🎯 Dopo la Connessione

Una volta connesso, dovresti vedere:

```
📁 EarlyCare Atlas
  └── 📁 earlycare
      ├── 📄 patients
      ├── 📄 patient_records
      ├── 📄 clinical_data
      ├── 📄 decision_support
      └── 📄 audit_logs
```

## 🐛 Troubleshooting

### Problema: "Authentication failed"
- Verifica username/password nella connection string
- Controlla che l'IP sia whitelistato in MongoDB Atlas (vai su Network Access)

### Problema: "SSL handshake failed"
- Stai usando Python 3.14 (versione beta) che ha bug SSL
- **Soluzione:** Installa Python 3.12 stabile
- **Alternativa:** Usa MongoDB locale

### Problema: "Cannot connect to server"
- Verifica la connessione internet
- Controlla il firewall/proxy aziendale
- Prova ad aggiungere il tuo IP in MongoDB Atlas → Network Access → Add IP Address

### Problema: "Database not found"
- Il database verrà creato automaticamente al primo inserimento
- Esegui lo script di inizializzazione:
  ```powershell
  python scripts/initialize_database.py
  ```

## 📚 Risorse Utili

- **Documentazione MongoDB VS Code:** https://www.mongodb.com/docs/mongodb-vscode/
- **MongoDB Atlas:** https://cloud.mongodb.com/
- **Guida MongoDB Compass (GUI):** https://www.mongodb.com/products/compass

## 🔄 Migrazione da Atlas a Locale (Se Necessario)

Se decidi di usare MongoDB locale invece di Atlas:

1. Installa MongoDB Community
2. Modifica `config/gateway_config.yaml`:
   ```yaml
   database:
     mongodb:
       enabled: true
       connection_string: "mongodb://localhost:27017/"
       database_name: "earlycare"
   ```
3. Riavvia l'applicazione

---

**Nota Importante:** La password nella connection string è visibile in chiaro. In produzione, usa variabili d'ambiente:

```python
import os
connection_string = os.getenv("MONGODB_URI")
```
