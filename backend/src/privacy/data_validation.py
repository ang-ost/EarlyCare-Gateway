"""Data validation and normalization utilities for patient data."""

from typing import Dict, List, Tuple, Any
from datetime import datetime
import re


class ValidationError(Exception):
    """Custom exception for validation errors."""
    def __init__(self, errors: List[Dict[str, str]]):
        self.errors = errors
        super().__init__(f"Validation failed: {errors}")


def validate_patient_data(data: Dict[str, Any]) -> Tuple[bool, List[Dict[str, str]]]:
    """
    Validate patient creation/update data.
    
    Args:
        data: Patient data dictionary
    
    Returns:
        Tuple of (is_valid, errors_list)
    """
    errors = []
    
    # Nome validation
    nome = data.get('nome', '').strip()
    if not nome:
        errors.append({'field': 'nome', 'message': 'Nome obbligatorio'})
    elif len(nome) < 2:
        errors.append({'field': 'nome', 'message': 'Nome troppo corto (minimo 2 caratteri)'})
    elif len(nome) > 50:
        errors.append({'field': 'nome', 'message': 'Nome troppo lungo (massimo 50 caratteri)'})
    
    # Cognome validation
    cognome = data.get('cognome', '').strip()
    if not cognome:
        errors.append({'field': 'cognome', 'message': 'Cognome obbligatorio'})
    elif len(cognome) < 2:
        errors.append({'field': 'cognome', 'message': 'Cognome troppo corto (minimo 2 caratteri)'})
    elif len(cognome) > 50:
        errors.append({'field': 'cognome', 'message': 'Cognome troppo lungo (massimo 50 caratteri)'})
    
    # Data nascita validation
    data_nascita = data.get('data_nascita')
    if not data_nascita:
        errors.append({'field': 'data_nascita', 'message': 'Data di nascita obbligatoria'})
    else:
        try:
            birth_date = datetime.strptime(data_nascita, '%Y-%m-%d')
            today = datetime.now()
            if birth_date > today:
                errors.append({'field': 'data_nascita', 'message': 'Data di nascita non può essere nel futuro'})
            age = today.year - birth_date.year
            if age > 150:
                errors.append({'field': 'data_nascita', 'message': 'Data di nascita non valida'})
        except ValueError:
            errors.append({'field': 'data_nascita', 'message': 'Formato data non valido (YYYY-MM-DD)'})
    
    # Comune nascita validation
    comune_nascita = data.get('comune_nascita', '').strip()
    if not comune_nascita:
        errors.append({'field': 'comune_nascita', 'message': 'Comune di nascita obbligatorio'})
    elif len(comune_nascita) < 2:
        errors.append({'field': 'comune_nascita', 'message': 'Comune di nascita non valido'})
    
    # Sesso validation
    sesso = data.get('sesso', '').upper()
    if not sesso:
        errors.append({'field': 'sesso', 'message': 'Sesso obbligatorio'})
    elif sesso not in ['M', 'F', 'MALE', 'FEMALE', 'MASCHIO', 'FEMMINA']:
        errors.append({'field': 'sesso', 'message': 'Sesso non valido (M o F)'})
    
    # Data decesso validation (optional)
    if data.get('data_decesso'):
        try:
            death_date = datetime.strptime(data['data_decesso'], '%Y-%m-%d')
            birth_date = datetime.strptime(data_nascita, '%Y-%m-%d') if data_nascita else None
            
            if birth_date and death_date < birth_date:
                errors.append({'field': 'data_decesso', 'message': 'Data di decesso non può essere prima della data di nascita'})
            
            today = datetime.now()
            if death_date > today:
                errors.append({'field': 'data_decesso', 'message': 'Data di decesso non può essere nel futuro'})
        except ValueError:
            errors.append({'field': 'data_decesso', 'message': 'Formato data non valido (YYYY-MM-DD)'})
    
    return len(errors) == 0, errors


def normalize_patient_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalize patient data for database storage.
    
    Args:
        data: Raw patient data
    
    Returns:
        Normalized patient data
    """
    normalized = {}
    
    # Normalize text fields (trim, title case)
    normalized['nome'] = data.get('nome', '').strip().title()
    normalized['cognome'] = data.get('cognome', '').strip().title()
    normalized['comune_nascita'] = data.get('comune_nascita', '').strip().title()
    
    # Dates (keep as is if valid)
    normalized['data_nascita'] = data.get('data_nascita', '').strip()
    if data.get('data_decesso'):
        normalized['data_decesso'] = data['data_decesso'].strip()
    else:
        normalized['data_decesso'] = None
    
    # Sesso (normalize to M/F)
    sesso = data.get('sesso', '').upper()
    if sesso in ['F', 'FEMALE', 'FEMMINA']:
        normalized['sesso'] = 'F'
    else:
        normalized['sesso'] = 'M'
    
    # Parse allergie (split by comma or semicolon)
    allergie_str = data.get('allergie', '').strip()
    if allergie_str:
        allergie = [a.strip().title() for a in re.split('[,;]', allergie_str) if a.strip()]
        normalized['allergie'] = allergie
    else:
        normalized['allergie'] = []
    
    # Parse malattie permanenti (split by comma or semicolon)
    malattie_str = data.get('malattie_permanenti', '').strip()
    if malattie_str:
        malattie = [m.strip().title() for m in re.split('[,;]', malattie_str) if m.strip()]
        normalized['malattie_permanenti'] = malattie
    else:
        normalized['malattie_permanenti'] = []
    
    return normalized


def validate_file_upload(filename: str, file_size: int, allowed_extensions: List[str] = None) -> Tuple[bool, str]:
    """
    Validate file upload.
    
    Args:
        filename: Name of the file
        file_size: Size of file in bytes
        allowed_extensions: List of allowed file extensions (without dot)
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    # Default allowed extensions
    if allowed_extensions is None:
        allowed_extensions = ['pdf', 'jpg', 'jpeg', 'png', 'doc', 'docx', 'xls', 'xlsx', 'txt']
    
    # Check file extension
    if '.' not in filename:
        return False, 'File deve avere un\'estensione'
    
    ext = filename.rsplit('.', 1)[1].lower()
    if ext not in allowed_extensions:
        return False, f'Tipo di file non consentito. Estensioni consentite: {", ".join(allowed_extensions)}'
    
    # Check file size (max 10MB)
    max_size = 10 * 1024 * 1024  # 10MB in bytes
    if file_size > max_size:
        return False, f'File troppo grande (massimo 10MB). Tamanho: {file_size / 1024 / 1024:.1f}MB'
    
    # Check file size minimum (at least 1KB)
    if file_size < 1024:
        return False, 'File troppo piccolo o vuoto'
    
    return True, ''


def validate_record_data(data: Dict[str, Any]) -> Tuple[bool, List[Dict[str, str]]]:
    """
    Validate clinical record data.
    
    Args:
        data: Record data dictionary
    
    Returns:
        Tuple of (is_valid, errors_list)
    """
    errors = []
    
    # Motivo tipo validation
    motivo_tipo = data.get('motivo_tipo', '').strip()
    allowed_tipos = ['Visita', 'Consulto', 'Terapia', 'Esame', 'Intervento', 'Ricovero', 'Altro']
    
    if not motivo_tipo:
        errors.append({'field': 'motivo_tipo', 'message': 'Tipo di motivo obbligatorio'})
    elif motivo_tipo not in allowed_tipos:
        errors.append({'field': 'motivo_tipo', 'message': f'Tipo non valido. Consentiti: {", ".join(allowed_tipos)}'})
    
    # Motivo validation
    motivo = data.get('motivo', '').strip()
    if not motivo:
        errors.append({'field': 'motivo', 'message': 'Motivo della visita obbligatorio'})
    elif len(motivo) < 5:
        errors.append({'field': 'motivo', 'message': 'Motivo troppo corto (minimo 5 caratteri)'})
    
    # Vital signs validation (optional but if provided must be valid)
    vital_signs = data.get('vital_signs', {})
    
    if vital_signs.get('blood_pressure'):
        if not re.match(r'^\d+/\d+$', vital_signs['blood_pressure']):
            errors.append({'field': 'blood_pressure', 'message': 'Formato non valido (es: 120/80)'})
    
    if vital_signs.get('heart_rate'):
        try:
            hr = int(vital_signs['heart_rate'])
            if hr < 30 or hr > 250:
                errors.append({'field': 'heart_rate', 'message': 'Frequenza cardiaca non valida (30-250 bpm)'})
        except ValueError:
            errors.append({'field': 'heart_rate', 'message': 'Frequenza cardiaca deve essere un numero'})
    
    if vital_signs.get('temperature'):
        try:
            temp = float(vital_signs['temperature'])
            if temp < 35 or temp > 42:
                errors.append({'field': 'temperature', 'message': 'Temperatura non valida (35-42°C)'})
        except ValueError:
            errors.append({'field': 'temperature', 'message': 'Temperatura deve essere un numero'})
    
    if vital_signs.get('oxygen_saturation'):
        try:
            spo2 = int(vital_signs['oxygen_saturation'])
            if spo2 < 50 or spo2 > 100:
                errors.append({'field': 'oxygen_saturation', 'message': 'Saturazione O2 non valida (50-100%)'})
        except ValueError:
            errors.append({'field': 'oxygen_saturation', 'message': 'Saturazione O2 deve essere un numero'})
    
    if vital_signs.get('respiratory_rate'):
        try:
            rr = int(vital_signs['respiratory_rate'])
            if rr < 8 or rr > 40:
                errors.append({'field': 'respiratory_rate', 'message': 'Frequenza respiratoria non valida (8-40 atti/min)'})
        except ValueError:
            errors.append({'field': 'respiratory_rate', 'message': 'Frequenza respiratoria deve essere un numero'})
    
    return len(errors) == 0, errors
