"""
Script di diagnostica per verificare il setup in produzione
Può essere eseguito direttamente su Render tramite SSH o localmente
"""

import os
import sys
from pathlib import Path

print("\n" + "="*70)
print("🔬 DIAGNOSTICA EARLYCARE GATEWAY")
print("="*70)

# 1. Verifica Python version
print(f"\n1️⃣ Python Version: {sys.version}")

# 2. Verifica working directory
print(f"\n2️⃣ Working Directory:")
print(f"   Current: {os.getcwd()}")
print(f"   __file__: {os.path.abspath(__file__)}")

# 3. Verifica struttura directory
print(f"\n3️⃣ Struttura Directory:")
base_paths = ['.', './src', './webapp', './backend', './backend/src']
for base in base_paths:
    if os.path.exists(base):
        print(f"   ✅ {os.path.abspath(base)}")
        if os.path.exists(os.path.join(base, 'src', 'privacy')):
            privacy_path = os.path.join(base, 'src', 'privacy')
            print(f"      └─ privacy: {os.path.abspath(privacy_path)}")
            json_file = os.path.join(privacy_path, 'codici_catastali.json')
            if os.path.exists(json_file):
                size = os.path.getsize(json_file)
                print(f"         └─ ✅ codici_catastali.json ({size:,} bytes)")
            else:
                print(f"         └─ ❌ codici_catastali.json NON TROVATO")

# 4. Verifica dipendenze Python
print(f"\n4️⃣ Dipendenze Python Installate:")
required_packages = [
    'flask',
    'flask_cors',
    'pymongo',
    'codicefiscale',
    'google.generativeai',
    'reportlab'
]

for package_name in required_packages:
    try:
        if package_name == 'flask_cors':
            __import__('flask_cors')
        elif package_name == 'google.generativeai':
            __import__('google.generativeai')
        else:
            __import__(package_name)
        
        # Prova a ottenere la versione
        try:
            if package_name == 'flask':
                import flask
                version = flask.__version__
            elif package_name == 'flask_cors':
                import flask_cors
                version = flask_cors.__version__ if hasattr(flask_cors, '__version__') else 'N/A'
            elif package_name == 'pymongo':
                import pymongo
                version = pymongo.__version__
            elif package_name == 'codicefiscale':
                import codicefiscale
                version = codicefiscale.__version__ if hasattr(codicefiscale, '__version__') else 'N/A'
            elif package_name == 'google.generativeai':
                import google.generativeai as genai
                version = 'N/A'
            elif package_name == 'reportlab':
                import reportlab
                version = reportlab.Version
            else:
                version = 'N/A'
            
            print(f"   ✅ {package_name:<25} v{version}")
        except:
            print(f"   ✅ {package_name:<25} (versione N/A)")
    except ImportError as e:
        print(f"   ❌ {package_name:<25} NON INSTALLATO - {e}")

# 5. Test caricamento modulo codice fiscale
print(f"\n5️⃣ Test Modulo Codice Fiscale:")
try:
    sys.path.insert(0, os.getcwd())
    from src.privacy.codice_fiscale import load_codici_catastali, get_municipality_code, calculate_codice_fiscale, CODICEFISCALE_LIB_AVAILABLE
    
    print(f"   ✅ Import modulo riuscito")
    print(f"   📦 Libreria codicefiscale disponibile: {CODICEFISCALE_LIB_AVAILABLE}")
    
    # Test caricamento codici
    codici = load_codici_catastali()
    print(f"   🗺️  Codici catastali caricati: {len(codici)}")
    
    # Test ricerca
    test_comuni = ['BARI', 'ROMA', 'MILANO', 'NAPOLI']
    print(f"\n   🔍 Test ricerca comuni:")
    for comune in test_comuni:
        codice = get_municipality_code(comune)
        symbol = "✅" if codice else "❌"
        print(f"      {symbol} {comune}: {codice}")
    
    # Test calcolo CF
    if CODICEFISCALE_LIB_AVAILABLE:
        print(f"\n   🧮 Test calcolo codice fiscale:")
        cf = calculate_codice_fiscale('Mario', 'Rossi', '01/01/1990', 'BARI', 'M')
        if cf:
            print(f"      ✅ Risultato: {cf}")
        else:
            print(f"      ❌ Calcolo fallito")
    else:
        print(f"\n   ⚠️  Test calcolo CF saltato (libreria non disponibile)")
    
except Exception as e:
    print(f"   ❌ ERRORE: {e}")
    import traceback
    traceback.print_exc()

# 6. Verifica connessione MongoDB
print(f"\n6️⃣ Test Connessione MongoDB:")
try:
    from src.config import Config
    print(f"   📝 Connection String: {Config.MONGODB_CONNECTION_STRING[:50]}...")
    print(f"   📝 Database: {Config.MONGODB_DATABASE_NAME}")
    
    from pymongo import MongoClient
    client = MongoClient(
        Config.MONGODB_CONNECTION_STRING,
        serverSelectionTimeoutMS=5000,
        tls=True,
        tlsAllowInvalidCertificates=True
    )
    client.admin.command('ping')
    print(f"   ✅ Connessione MongoDB riuscita")
    
    # Test query pazienti
    db = client[Config.MONGODB_DATABASE_NAME]
    count = db.patients.count_documents({})
    print(f"   📊 Pazienti nel database: {count}")
    
    # Mostra alcuni CF
    if count > 0:
        sample = list(db.patients.find({}, {'codice_fiscale': 1, 'nome': 1, 'cognome': 1}).limit(5))
        print(f"\n   📋 Esempi pazienti:")
        for p in sample:
            print(f"      - {p.get('codice_fiscale')}: {p.get('nome')} {p.get('cognome')}")
    
except Exception as e:
    print(f"   ❌ ERRORE: {e}")

# 7. Variabili d'ambiente
print(f"\n7️⃣ Variabili d'Ambiente:")
env_vars = [
    'RENDER',
    'FLASK_ENV',
    'MONGODB_DATABASE_NAME',
    'GEMINI_API_KEY',
    'FRONTEND_URL'
]
for var in env_vars:
    value = os.getenv(var, 'NOT SET')
    if 'KEY' in var or 'CONNECTION' in var:
        # Nascondi le chiavi sensibili
        if value and value != 'NOT SET':
            value = value[:10] + '...' + value[-5:]
    print(f"   {var}: {value}")

print("\n" + "="*70)
print("✅ DIAGNOSTICA COMPLETATA")
print("="*70 + "\n")
