"""Codice Fiscale Calculation - Italian Tax Code Generator"""

from datetime import datetime
from typing import Optional, List, Dict
import json
import os

# Prova a usare la libreria python-codicefiscale se disponibile
try:
    from codicefiscale.codicefiscale import encode
    CODICEFISCALE_LIB_AVAILABLE = True
except ImportError:
    CODICEFISCALE_LIB_AVAILABLE = False


# Cache per i comuni
_COMUNI_DATA = None

def load_comuni() -> List[Dict]:
    """Load comuni data from comuni.json file."""
    global _COMUNI_DATA
    
    if _COMUNI_DATA is not None:
        return _COMUNI_DATA
    
    possible_paths = [
        os.path.join(os.path.dirname(__file__), '..', '..', '..', 'frontend', 'node_modules', 'comuni-json', 'comuni.json'),
        os.path.join(os.path.dirname(__file__), '..', '..', '..', 'comuni.json'),
        'comuni.json',
    ]
    
    for path in possible_paths:
        try:
            if os.path.exists(path):
                with open(path, 'r', encoding='utf-8') as f:
                    _COMUNI_DATA = json.load(f)
                    return _COMUNI_DATA
        except Exception as e:
            continue
    
    print("Avviso: File comuni.json non trovato.")
    _COMUNI_DATA = []
    return _COMUNI_DATA


def calculate_codice_fiscale(
    nome: str,
    cognome: str,
    data_nascita,  # Can be datetime or string DD/MM/YYYY
    comune_nascita: str,
    sesso: str
) -> Optional[str]:
    """Calculate Italian Codice Fiscale (Tax Code)."""
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
        
        # Usa la libreria python-codicefiscale se disponibile
        if CODICEFISCALE_LIB_AVAILABLE:
            try:
                # Formato data: DD/MM/YYYY
                data_str = f"{data_obj.day:02d}/{data_obj.month:02d}/{data_obj.year}"
                cf = encode(
                    cognome.upper(),
                    nome.upper(),
                    'M' if sesso.upper() == 'M' else 'F',
                    data_str,
                    comune_nascita.upper()
                )
                print(f"DEBUG CF (library): {cf}")
                return cf
            except Exception as e:
                print(f"DEBUG: Library encoding failed: {e}, falling back to manual")
        
        # Fallback manuale
        if not all([nome, cognome, data_obj, comune_nascita, sesso]):
            return None
        
        def get_consonants(s: str) -> str:
            return ''.join(c for c in s.upper() if c not in 'AEIOU' and c.isalpha())
        
        def get_vowels(s: str) -> str:
            return ''.join(c for c in s.upper() if c in 'AEIOU')
        
        cognome_consonants = get_consonants(cognome)
        cognome_vowels = get_vowels(cognome)
        cognome_code = (cognome_consonants + cognome_vowels)[:3].ljust(3, 'X')
        
        nome_consonants = get_consonants(nome)
        nome_vowels = get_vowels(nome)
        
        if len(nome_consonants) >= 4:
            nome_code = nome_consonants[0] + nome_consonants[2] + nome_consonants[3]
        else:
            nome_code = (nome_consonants + nome_vowels)[:3].ljust(3, 'X')
        
        yy = str(data_obj.year)[-2:]
        month_codes = 'ABCDEHLMPRST'
        mm = month_codes[data_obj.month - 1]
        
        day = data_obj.day
        if sesso.upper() in ['F', 'FEMALE']:
            gg = str(day + 40).zfill(2)
        else:
            gg = str(day).zfill(2)
        
        comuni = load_comuni()
        
        if not comuni:
            comune_consonants = get_consonants(comune_nascita)
            comune_vowels = get_vowels(comune_nascita)
            comune_code = (comune_consonants + comune_vowels)[:4].ljust(4, 'X')
        else:
            comune_found = None
            for c in comuni:
                if c.get('nome', '').upper() == comune_nascita.upper():
                    comune_found = c
                    break
            
            if comune_found and 'codiceCatastale' in comune_found:
                comune_code = comune_found['codiceCatastale']
            else:
                comune_consonants = get_consonants(comune_nascita)
                comune_vowels = get_vowels(comune_nascita)
                comune_code = (comune_consonants + comune_vowels)[:4].ljust(4, 'X')
        
        base_cf = cognome_code + nome_code + yy + mm + gg + comune_code
        
        caratteri = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        valori_pari = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35]
        valori_dispari = [1, 0, 5, 7, 6, 8, 9, 13, 15, 17, 18, 20, 16, 19, 25, 20, 29, 31, 4, 34, 32, 30, 26, 28, 27, 29, 23, 3, 2, 33, 35, 10, 14, 25, 24, 11]
        alfabeto_controllo = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        
        somma = 0
        for i, char in enumerate(base_cf):
            pos = caratteri.find(char)
            if pos >= 0:
                if i % 2 == 1:
                    somma += valori_pari[pos]
                else:
                    somma += valori_dispari[pos]
        
        resto = somma % 26
        control_char = alfabeto_controllo[resto]
        final_cf = (base_cf + control_char).upper()
        
        return final_cf
    
    except Exception as e:
        print(f"Errore nel calcolo del CF: {e}")
        return None
