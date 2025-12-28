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
    
    # Try to load from JSON file
    json_path = os.path.join(os.path.dirname(__file__), 'codici_catastali.json')
    
    try:
        if os.path.exists(json_path):
            with open(json_path, 'r', encoding='utf-8') as f:
                _CODICI_CATASTALI = json.load(f)
                print(f"Caricati {len(_CODICI_CATASTALI)} codici catastali")
                return _CODICI_CATASTALI
    except Exception as e:
        print(f"Errore nel caricamento dei codici catastali: {e}")
    
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
    """Get the cadastral code for a municipality by name."""
    codici = load_codici_catastali()
    city_upper = city_name.upper().strip()
    return codici.get(city_upper)


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
        
        if not CODICEFISCALE_LIB_AVAILABLE:
            raise ImportError("La libreria 'codicefiscale' non è installata")
        
        # Get the municipality cadastral code
        municipality_code = get_municipality_code(comune_nascita)
        
        if not municipality_code:
            raise ValueError(f"Codice catastale non trovato per il comune: {comune_nascita}")
        
        # Use the library's build function
        # build(surname, name, birthday, sex, municipality_code)
        cf = build(
            cognome,
            nome,
            data_obj,
            sesso.upper()[0],  # 'M' or 'F'
            municipality_code
        )
        
        return cf
    
    except Exception as e:
        print(f"Errore nel calcolo del CF: {e}")
        import traceback
        traceback.print_exc()
        return None
