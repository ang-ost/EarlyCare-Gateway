"""
Script di test per verificare gli endpoint del backend in produzione
"""

import requests
import json

BACKEND_URL = "https://earlycare-gateway-backend.onrender.com"

print("\n" + "="*70)
print("🧪 TEST ENDPOINT BACKEND")
print("="*70)

# Test 1: Health Check
print("\n1️⃣ TEST HEALTH CHECK")
try:
    response = requests.get(f"{BACKEND_URL}/health", timeout=10)
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")
except Exception as e:
    print(f"   ❌ Errore: {e}")

# Test 2: Calcolo CF (richiede autenticazione - aspettiamoci 401)
print("\n2️⃣ TEST CALCOLO CF (senza autenticazione)")
try:
    data = {
        "nome": "Mario",
        "cognome": "Rossi",
        "data_nascita": "1990-01-01",
        "sesso": "M",
        "comune_nascita": "BARI"
    }
    response = requests.post(
        f"{BACKEND_URL}/api/patient/calculate-cf",
        json=data,
        timeout=10
    )
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.text}")
    
    if response.status_code == 401:
        print(f"   ℹ️  401 Unauthorized è normale - richiede login")
    elif response.status_code == 200:
        print(f"   ✅ CF Calcolato: {response.json().get('codice_fiscale')}")
    else:
        print(f"   ⚠️  Risposta inaspettata")
        
except Exception as e:
    print(f"   ❌ Errore: {e}")

# Test 3: Ricerca Paziente (richiede autenticazione)
print("\n3️⃣ TEST RICERCA PAZIENTE (senza autenticazione)")
try:
    data = {"fiscal_code": "RSSMRA90A01A662H"}
    response = requests.post(
        f"{BACKEND_URL}/api/patient/search",
        json=data,
        timeout=10
    )
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.text}")
    
    if response.status_code == 401:
        print(f"   ℹ️  401 Unauthorized è normale - richiede login")
        
except Exception as e:
    print(f"   ❌ Errore: {e}")

print("\n" + "="*70)
print("📝 NOTE:")
print("   - Status 401 è NORMALE per endpoint protetti")
print("   - Per testare con autenticazione, serve il session cookie")
print("="*70 + "\n")
