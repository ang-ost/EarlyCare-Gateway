"""Codice Fiscale Calculation - Italian Tax Code Generator"""

from datetime import datetime
from typing import Optional
import json
import os

try:
    from codicefiscale import build
    CODICEFISCALE_LIB_AVAILABLE = True
except ImportError:
    CODICEFISCALE_LIB_AVAILABLE = False
    print("ATTENZIONE: Libreria 'codicefiscale' non installata. Installare con: pip install codicefiscale")


# Cache per i codici catastali
_CODICI_CATASTALI = None


def load_codici_catastali() -> dict:
    """Load cadastral codes from JSON file."""
    global _CODICI_CATASTALI
    
    if _CODICI_CATASTALI is not None:
        return _CODICI_CATASTALI
    
    # Try multiple paths for JSON file (for different deployment scenarios)
    possible_paths = [
        os.path.join(os.path.dirname(__file__), 'codici_catastali.json'),
        os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'privacy', 'codici_catastali.json'),
        os.path.join(os.getcwd(), 'src', 'privacy', 'codici_catastali.json'),
        os.path.join(os.getcwd(), 'backend', 'src', 'privacy', 'codici_catastali.json'),
    ]
    
    for json_path in possible_paths:
        try:
            if os.path.exists(json_path):
                print(f"Tentativo di caricamento da: {json_path}")
                with open(json_path, 'r', encoding='utf-8') as f:
                    _CODICI_CATASTALI = json.load(f)
                    print(f"✓ Caricati {len(_CODICI_CATASTALI)} codici catastali da {json_path}")
                    return _CODICI_CATASTALI
        except Exception as e:
            print(f"Errore nel caricamento da {json_path}: {e}")
            continue
    
    # If we get here, file was not found
    print(f"⚠️ ATTENZIONE: File codici_catastali.json non trovato in nessuno dei path")
    print(f"   Directory corrente: {os.getcwd()}")
    print(f"   __file__ path: {os.path.dirname(__file__)}")
    
    # Fallback con comuni principali
    _CODICI_CATASTALI = {
        'BARI': 'A662',
        'ROMA': 'H501',
        'MILANO': 'F205',
        'NAPOLI': 'F839',
        'TORINO': 'L219',
        'PALERMO': 'G273',
        'GENOVA': 'D969',
        'BOLOGNA': 'A944',
        'FIRENZE': 'D612',
    }
    print(f"Usando fallback con {len(_CODICI_CATASTALI)} comuni principali")
    return _CODICI_CATASTALI


def get_municipality_code(city_name: str) -> Optional[str]:
    """Get the cadastral code for a municipality by name.
    
    Performs case-insensitive search and tries multiple variations.
    """
    codici = load_codici_catastali()
    city_upper = city_name.upper().strip()
    
    # Try exact match first
    if city_upper in codici:
        return codici[city_upper]
    
    # Try variations (comune vs città, etc.)
    # Remove common prefixes/suffixes
    variations = [
        city_upper,
        city_upper.replace('COMUNE DI ', '').replace('CITTA DI ', '').replace('CITTÀ DI ', ''),
        city_upper.replace(' DI ', ' '),
    ]
    
    for variation in variations:
        if variation in codici:
            print(f"✓ Trovato codice per '{city_name}' usando variazione '{variation}'")
            return codici[variation]
    
    # Try partial match (starts with)
    for key in codici.keys():
        if key.startswith(city_upper) or city_upper.startswith(key):
            print(f"✓ Trovato codice per '{city_name}' con match parziale '{key}'")
            return codici[key]
    
    print(f"✗ Codice catastale non trovato per: {city_name}")
    print(f"   Variazioni provate: {variations}")
    return None


def calculate_codice_fiscale(
    nome: str,
    cognome: str,
    data_nascita,  # Can be datetime or string DD/MM/YYYY
    comune_nascita: str,
    sesso: str
) -> Optional[str]:
    """Calculate Italian Codice Fiscale (Tax Code).
    
    Args:
        nome: First name
        cognome: Last name
        data_nascita: Birth date (datetime object or string in DD/MM/YYYY format)
        comune_nascita: Birth municipality name
        sesso: Gender ('M' or 'F')
    
    Returns:
        Calculated fiscal code or None if calculation fails
    """
    try:
        print(f"\n=== Calcolo Codice Fiscale ===")
        print(f"Nome: {nome}, Cognome: {cognome}")
        print(f"Data nascita: {data_nascita}, Comune: {comune_nascita}, Sesso: {sesso}")
        
        # Convert string to datetime if needed
        if isinstance(data_nascita, str):
            # Try DD/MM/YYYY format first
            if '/' in data_nascita:
                data_obj = datetime.strptime(data_nascita, '%d/%m/%Y')
            else:
                # Assume YYYY-MM-DD
                data_obj = datetime.strptime(data_nascita, '%Y-%m-%d')
        else:
            data_obj = data_nascita
        
        print(f"Data convertita: {data_obj}")
        
        if not CODICEFISCALE_LIB_AVAILABLE:
            error_msg = "La libreria 'codicefiscale' non è installata"
            print(f"❌ {error_msg}")
            raise ImportError(error_msg)
        
        # Get the municipality cadastral code
        municipality_code = get_municipality_code(comune_nascita)
        
        if not municipality_code:
            error_msg = f"Codice catastale non trovato per il comune: {comune_nascita}"
            print(f"❌ {error_msg}")
            # Lista dei comuni disponibili per debugging
            codici = load_codici_catastali()
            if codici:
                print(f"Comuni disponibili (primi 10): {list(codici.keys())[:10]}")
            raise ValueError(error_msg)
        
        print(f"Codice catastale trovato: {municipality_code}")
        
        # Use the library's build function
        # build(surname, name, birthday, sex, municipality_code)
        cf = build(
            cognome,
            nome,
            data_obj,
            sesso.upper()[0],  # 'M' or 'F'
            municipality_code
        )
        
        print(f"✓ Codice fiscale calcolato: {cf}")
        return cf
    
    except Exception as e:
        print(f"❌ Errore nel calcolo del CF: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return None
