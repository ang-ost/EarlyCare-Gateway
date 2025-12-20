"""
EarlyCare Gateway - Web Application Launcher (from root)

Avvia l'applicazione web di EarlyCare Gateway.

Utilizzo:
    python run_backend.py

L'applicazione sarà disponibile su: http://localhost:5000
"""

import sys
from pathlib import Path

# Add backend folder to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

from webapp.app import app

if __name__ == "__main__":
    print("=" * 60)
    print("🏥 EarlyCare Gateway - Medical Access & Vision")
    print("=" * 60)
    print()
    print("Avvio dell'applicazione web...")
    print()
    print("L'applicazione sarà disponibile su:")
    print("  → http://localhost:5000")
    print("  → http://127.0.0.1:5000")
    print()
    print("Premi CTRL+C per terminare l'applicazione")
    print("=" * 60)
    print()
    
    app.run(debug=False, host='0.0.0.0', port=5000)
