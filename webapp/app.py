"""
EarlyCare Gateway - Flask Web Application
"""

from flask import Flask, render_template, request, jsonify, send_file, session
from werkzeug.utils import secure_filename
import os
from pathlib import Path
import json
from datetime import datetime
import sys
from functools import wraps
import zipfile
import io
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
import PyPDF2
import re

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import Config
from src.gateway.clinical_gateway import ClinicalGateway
from src.gateway.folder_processor import ClinicalFolderProcessor
from src.strategy.strategy_selector import StrategySelector
from src.observer.metrics_observer import MetricsObserver, AuditObserver
from src.models.patient import Patient, Gender
from src.models.doctor import Doctor

# MongoDB integration
try:
    from src.database.mongodb_repository import MongoDBPatientRepository
    MONGODB_AVAILABLE = True
except ImportError:
    MONGODB_AVAILABLE = False
    MongoDBPatientRepository = None

# AI Medical Diagnostics
try:
    from src.ai.medical_diagnostics import MedicalDiagnosticsAI
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False
    MedicalDiagnosticsAI = None

app = Flask(__name__)
app.secret_key = Config.FLASK_SECRET_KEY
app.config['UPLOAD_FOLDER'] = Path(__file__).parent / 'uploads'
app.config['MAX_CONTENT_LENGTH'] = Config.MAX_UPLOAD_SIZE_MB * 1024 * 1024

# Session configuration
app.config['SESSION_COOKIE_SECURE'] = False  # Set to True in production with HTTPS
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['PERMANENT_SESSION_LIFETIME'] = 86400 * 7  # 7 days

# Ensure upload folder exists
app.config['UPLOAD_FOLDER'].mkdir(exist_ok=True)

# Global variables for system state
gateway = None
processor = None
metrics_observer = None
db = None
db_connected = False
ai_diagnostics = None


def initialize_system():
    """Initialize the clinical gateway system."""
    global gateway, processor, metrics_observer, db, db_connected, ai_diagnostics
    
    try:
        # Initialize MongoDB
        if MONGODB_AVAILABLE:
            try:
                # Use configuration from .env file
                db = MongoDBPatientRepository(
                    connection_string=Config.MONGODB_CONNECTION_STRING,
                    database_name=Config.MONGODB_DATABASE_NAME,
                    **Config.get_mongodb_connection_params()
                )
                db_connected = True
                print("✅ MongoDB connected successfully")
                Config.print_config(hide_secrets=True)
            except Exception as e:
                print(f"❌ MongoDB connection failed: {e}")
                print("⚠️  Check your .env file configuration")
                db_connected = False
        
        # Initialize AI Diagnostics
        if AI_AVAILABLE and hasattr(Config, 'GEMINI_API_KEY') and Config.GEMINI_API_KEY:
            try:
                ai_diagnostics = MedicalDiagnosticsAI(
                    api_key=Config.GEMINI_API_KEY
                )
                print("✅ AI Medical Diagnostics initialized successfully")
                print(f"   Gemini: ✅")
            except Exception as e:
                print(f"⚠️  AI initialization failed: {e}")
                ai_diagnostics = None
        else:
            print("⚠️  AI Diagnostics not available (missing API key or module)")
        
        # Initialize gateway components
        gateway = ClinicalGateway()
        processor = ClinicalFolderProcessor(gateway)
        
        # Setup observers
        metrics_observer = MetricsObserver()
        audit_observer = AuditObserver()
        
        # Attach observers if gateway supports it
        if hasattr(gateway, 'attach'):
            gateway.attach(metrics_observer)
            gateway.attach(audit_observer)
        else:
            # Gateway doesn't support observer pattern, skip
            print("Gateway doesn't support observer pattern")
        
        # Gateway already has default strategy selector initialized in __init__
        # No need to override it unless we want custom strategies
        
        return True
    except Exception as e:
        print(f"System initialization error: {e}")
        import traceback
        traceback.print_exc()
        return False


# Initialize system on startup
initialize_system()


# ========== AUTHENTICATION DECORATOR ==========
def require_login(f):
    """Decorator to require doctor login for protected routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'doctor_id' not in session:
            return jsonify({'error': 'Non autorizzato. Effettua il login.'}), 401
        return f(*args, **kwargs)
    return decorated_function


# ========== PDF PARSING UTILITIES ==========
def extract_clinical_records_from_pdf(pdf_path):
    """
    Extracts clinical records from an exported PDF.
    Returns a list of clinical records if the PDF is an exported clinical record,
    otherwise returns None.
    """
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()
        
        print(f"DEBUG PDF: Extracted text length: {len(text)}")
        
        # Check if this is an exported clinical record PDF
        if "Cartella Clinica Elettronica" not in text or "EarlyCare Gateway" not in text:
            print("DEBUG PDF: Not an exported clinical record PDF")
            return None
        
        print("DEBUG PDF: This is an exported clinical record PDF")
        records = []
        
        # Split by "Scheda Clinica #" to find individual records
        record_pattern = r'Scheda Clinica #(\d+) - ([\d/]+ [\d:]+)'
        matches = list(re.finditer(record_pattern, text))
        
        print(f"DEBUG PDF: Found {len(matches)} schede cliniche")
        
        for i, match in enumerate(matches):
            start_pos = match.start()
            end_pos = matches[i + 1].start() if i + 1 < len(matches) else len(text)
            record_text = text[start_pos:end_pos]
            
            print(f"\nDEBUG PDF: Processing record #{i+1}")
            print(f"DEBUG PDF: Record text length: {len(record_text)}")
            print(f"DEBUG PDF: Record text preview: {record_text[:200]}...")
            
            # Extract fields using regex
            encounter_id_match = re.search(r'ID Incontro:\s*(.+?)(?:\n|Motivo)', record_text)
            chief_complaint_match = re.search(r'Motivo Principale:\s*(.+?)(?:\n|Sintomi)', record_text)
            symptoms_match = re.search(r'Sintomi:\s*(.+?)(?:\n|Priorit)', record_text)
            priority_match = re.search(r'Priorità:\s*(.+?)(?:\n|Pressione|Note|Scheda)', record_text)
            
            # Extract vital signs
            bp_match = re.search(r'Pressione Sanguigna:\s*(.+?)(?:\n|Frequenza)', record_text)
            hr_match = re.search(r'Frequenza Cardiaca:\s*(.+?)(?:\n|Temperatura)', record_text)
            temp_match = re.search(r'Temperatura:\s*(.+?)°C', record_text)
            o2_match = re.search(r'Saturazione O2:\s*(.+?)(?:\n|Frequenza)', record_text)
            rr_match = re.search(r'Frequenza Respiratoria:\s*(.+?)(?:\n|Note|Scheda)', record_text)
            
            # Extract notes
            notes_match = re.search(r'Note:\s*(.+?)(?:Scheda Clinica #|Documento generato|\Z)', record_text, re.DOTALL)
            
            # Parse timestamp
            timestamp_str = match.group(2)
            try:
                timestamp = datetime.strptime(timestamp_str, '%d/%m/%Y %H:%M:%S')
            except:
                timestamp = datetime.now()
            
            # Generate unique encounter_id for each import to avoid duplicates
            unique_encounter_id = f'ENC-IMPORTED-{datetime.now().strftime("%Y%m%d%H%M%S")}-{i}'
            
            record = {
                'timestamp': timestamp.isoformat(),
                'encounter_id': unique_encounter_id,
                'motivo_tipo': 'Importato da PDF',
                'motivo': chief_complaint_match.group(1).strip() if chief_complaint_match else 'N/A',
                'chief_complaint': chief_complaint_match.group(1).strip() if chief_complaint_match else 'N/A',
                'symptoms': symptoms_match.group(1).strip() if symptoms_match else '',
                'notes': notes_match.group(1).strip() if notes_match else '',
                'priority': priority_match.group(1).strip() if priority_match else 'routine',
                'vital_signs': {
                    'blood_pressure': bp_match.group(1).strip() if bp_match else '',
                    'heart_rate': hr_match.group(1).strip() if hr_match else '',
                    'temperature': temp_match.group(1).strip() if temp_match else '',
                    'oxygen_saturation': o2_match.group(1).strip() if o2_match else '',
                    'respiratory_rate': rr_match.group(1).strip() if rr_match else ''
                },
                'attachments': [],
                'doctor_name': 'Importato da PDF',
                'doctor_specialization': '',
                'original_encounter_id': encounter_id_match.group(1).strip() if encounter_id_match else 'N/A'
            }
            
            print(f"DEBUG PDF: Record extracted - ID: {record['encounter_id']}, Motivo: {record['motivo']}")
            records.append(record)
        
        print(f"DEBUG PDF: Total records extracted: {len(records)}")
        return records if records else None
        
    except Exception as e:
        print(f"Error extracting records from PDF: {e}")
        import traceback
        traceback.print_exc()
        return None

# ========== AUTHENTICATION ROUTES ==========

@app.route('/api/auth/register', methods=['POST'])
def register_doctor():
    """Register a new doctor."""
    data = request.json
    
    try:
        # Validate required fields
        required_fields = ['nome', 'cognome', 'password', 'specializzazione', 'ospedale_affiliato']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'Campo obbligatorio mancante: {field}'}), 400
        
        # Validate password strength (at least 6 characters)
        if len(data['password']) < 6:
            return jsonify({'error': 'La password deve contenere almeno 6 caratteri'}), 400
        
        # Generate unique doctor ID
        doctor_id = Doctor.generate_doctor_id(data['nome'], data['cognome'])
        
        # Ensure ID is unique
        if db_connected:
            while db.doctor_id_exists(doctor_id):
                doctor_id = Doctor.generate_doctor_id(data['nome'], data['cognome'])
        
        # Create doctor object
        doctor = Doctor(
            doctor_id=doctor_id,
            nome=data['nome'].strip().title(),
            cognome=data['cognome'].strip().title(),
            specializzazione=data['specializzazione'].strip().title(),
            ospedale_affiliato=data['ospedale_affiliato'].strip().title(),
            password_hash=Doctor.hash_password(data['password'])
        )
        
        # Save to database
        if not db_connected:
            return jsonify({'error': 'Database non connesso'}), 500
        
        if not db.save_doctor(doctor):
            return jsonify({'error': 'Errore durante la registrazione. ID medico potrebbe esistere già.'}), 400
        
        return jsonify({
            'success': True,
            'message': 'Registrazione completata con successo',
            'doctor_id': doctor_id,
            'doctor_info': {
                'nome': doctor.nome,
                'cognome': doctor.cognome,
                'specializzazione': doctor.specializzazione,
                'ospedale_affiliato': doctor.ospedale_affiliato
            }
        }), 201
        
    except Exception as e:
        print(f"Error in registration: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/api/auth/login', methods=['POST'])
def login_doctor():
    """Authenticate a doctor."""
    data = request.json
    
    try:
        # Validate required fields
        if not data.get('doctor_id') or not data.get('password'):
            return jsonify({'error': 'ID medico e password obbligatori'}), 400
        
        doctor_id = data['doctor_id'].strip()
        password = data['password']
        
        if not db_connected:
            return jsonify({'error': 'Database non connesso'}), 500
        
        # Verify credentials
        if not db.verify_doctor_login(doctor_id, password):
            return jsonify({'error': 'ID medico o password non validi'}), 401
        
        # Get doctor info
        doctor_data = db.find_doctor_by_id(doctor_id)
        
        # Store in session
        session['doctor_id'] = doctor_id
        session['doctor_nome'] = doctor_data['nome']
        session['doctor_cognome'] = doctor_data['cognome']
        session['doctor_specializzazione'] = doctor_data.get('specializzazione', '')
        session.permanent = True
        
        return jsonify({
            'success': True,
            'message': 'Login effettuato con successo',
            'doctor': {
                'doctor_id': doctor_id,
                'nome': doctor_data['nome'],
                'cognome': doctor_data['cognome'],
                'specializzazione': doctor_data.get('specializzazione', '')
            }
        }), 200
        
    except Exception as e:
        print(f"Error in login: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/api/auth/logout', methods=['POST'])
def logout_doctor():
    """Logout a doctor."""
    session.clear()
    return jsonify({'success': True, 'message': 'Logout effettuato'}), 200


@app.route('/api/auth/check', methods=['GET'])
def check_auth():
    """Check if user is authenticated."""
    if 'doctor_id' in session:
        doctor_id = session['doctor_id']
        try:
            if db_connected:
                doctor_data = db.find_doctor_by_id(doctor_id)
                return jsonify({
                    'authenticated': True,
                    'doctor': {
                        'doctor_id': doctor_id,
                        'nome': doctor_data.get('nome', ''),
                        'cognome': doctor_data.get('cognome', ''),
                        'specializzazione': doctor_data.get('specializzazione', ''),
                        'ospedale_affiliato': doctor_data.get('ospedale_affiliato', '')
                    }
                }), 200
        except Exception as e:
            print(f"Error in check_auth: {e}")
        
        return jsonify({
            'authenticated': True,
            'doctor': {
                'doctor_id': doctor_id,
                'nome': session.get('doctor_nome', ''),
                'cognome': session.get('doctor_cognome', ''),
                'specializzazione': session.get('doctor_specializzazione', '')
            }
        }), 200
    return jsonify({'authenticated': False}), 200


@app.route('/')
def index():
    """Home page - redirect to login if not authenticated."""
    if 'doctor_id' not in session:
        return render_template('login.html')
    return render_template('index.html', db_connected=db_connected)


@app.route('/profile')
def profile():
    """Doctor profile page."""
    if 'doctor_id' not in session:
        return render_template('login.html')
    
    try:
        doctor_data = db.find_doctor_by_id(session['doctor_id'])
        if not doctor_data:
            session.clear()
            return render_template('login.html')
        
        return render_template('profile.html', doctor=doctor_data, db_connected=db_connected)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/auth/delete-account', methods=['POST'])
@require_login
def delete_account():
    """Delete doctor account."""
    try:
        doctor_id = session['doctor_id']
        password = request.json.get('password')
        
        if not password:
            return jsonify({'error': 'Password richiesta'}), 400
        
        # Verify password before deletion
        doctor_data = db.find_doctor_by_id(doctor_id)
        if not doctor_data:
            return jsonify({'error': 'Medico non trovato'}), 404
        
        # doctor_data is a dict, use Doctor.verify_password static method
        if not Doctor.verify_password(password, doctor_data['password_hash']):
            return jsonify({'error': 'Password non corretta'}), 401
        
        # Delete the account
        db.delete_doctor_by_id(doctor_id)
        
        # Clear session
        session.clear()
        
        return jsonify({'success': True}), 200
    except Exception as e:
        print(f"Error deleting account: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/patient/search', methods=['POST'])
@require_login
def search_patient():
    """Search for a patient by fiscal code."""
    data = request.json
    fiscal_code = data.get('fiscal_code', '').strip().upper()
    
    if not db_connected:
        return jsonify({'error': 'Database non connesso'}), 500
    
    if not fiscal_code:
        return jsonify({'error': 'Codice fiscale obbligatorio'}), 400
    
    try:
        patient_data = db.find_by_fiscal_code(fiscal_code)
        if patient_data:
            return jsonify({'success': True, 'patient': patient_data})
        return jsonify({'success': False, 'message': 'Paziente non trovato'})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/patient/create', methods=['POST'])
@require_login
def create_patient():
    """Create a new patient."""
    data = request.json
    
    if not db_connected:
        return jsonify({'error': 'Database non connesso'}), 500
    
    try:
        # Validate required fields
        required_fields = ['nome', 'cognome', 'codice_fiscale', 'data_nascita', 'comune_nascita']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'Campo obbligatorio mancante: {field}'}), 400
        
        # Check if patient already exists
        existing = db.find_by_fiscal_code(data['codice_fiscale'].upper())
        if existing:
            return jsonify({'error': 'Paziente già esistente con questo codice fiscale'}), 400
        
        # Get gender from form data or determine from codice fiscale
        codice_fiscale = data['codice_fiscale'].upper()
        
        if data.get('sesso'):
            # Use gender from form if provided
            gender = Gender.MALE if data['sesso'].upper() in ['M', 'MALE', 'MASCHIO'] else Gender.FEMALE
        else:
            # Determine gender from codice fiscale (character at position 9-10)
            try:
                day_digit = int(codice_fiscale[9:11])
                gender = Gender.FEMALE if day_digit > 40 else Gender.MALE
            except:
                # Fallback to MALE
                gender = Gender.MALE
        
        # Parse dates
        data_nascita = datetime.strptime(data['data_nascita'], '%Y-%m-%d')
        data_decesso = None
        if data.get('data_decesso'):
            data_decesso = datetime.strptime(data['data_decesso'], '%Y-%m-%d')
        
        # Create patient
        patient = Patient(
            patient_id=codice_fiscale,
            nome=data['nome'].title(),
            cognome=data['cognome'].title(),
            data_nascita=data_nascita,
            comune_nascita=data['comune_nascita'].title(),
            codice_fiscale=codice_fiscale,
            data_decesso=data_decesso,
            gender=gender
        )
        
        # Add allergie (list)
        if data.get('allergie'):
            if isinstance(data['allergie'], list):
                patient.allergie = data['allergie']
            else:
                patient.allergie = [data['allergie']]
        
        # Add malattie_permanenti (list)
        if data.get('malattie_permanenti'):
            if isinstance(data['malattie_permanenti'], list):
                patient.malattie_permanenti = data['malattie_permanenti']
            else:
                patient.malattie_permanenti = [data['malattie_permanenti']]
        
        # Save to database
        db.save_patient(patient)
        
        return jsonify({'success': True, 'message': 'Paziente creato con successo'})
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/api/patient/<fiscal_code>/records', methods=['GET'])
@require_login
def get_patient_records(fiscal_code):
    """Get all clinical records for a patient."""
    if not db_connected:
        return jsonify({'error': 'Database non connesso'}), 500
    
    try:
        patient_data = db.find_by_fiscal_code(fiscal_code)
        if not patient_data:
            return jsonify({'error': 'Paziente non trovato'}), 404
        
        records = patient_data.get('cartelle_cliniche', [])
        return jsonify({'success': True, 'records': records})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/patient/<fiscal_code>/records/delete', methods=['DELETE'])
@require_login
def delete_clinical_records(fiscal_code):
    """Delete multiple clinical records from a patient."""
    if not db_connected:
        return jsonify({'error': 'Database non connesso'}), 500
    
    try:
        data = request.json
        indexes = data.get('indexes', [])
        
        if not indexes:
            return jsonify({'error': 'Nessuna scheda selezionata'}), 400
        
        # Get patient data
        patient_data = db.find_by_fiscal_code(fiscal_code)
        if not patient_data:
            return jsonify({'error': 'Paziente non trovato'}), 404
        
        # Delete records by indexes
        success = db.delete_clinical_records(fiscal_code, indexes)
        
        if success:
            return jsonify({
                'success': True, 
                'message': f'{len(indexes)} scheda/e clinica/che eliminata/e con successo'
            })
        else:
            return jsonify({'error': 'Errore durante l\'eliminazione delle schede'}), 500
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/patient/<fiscal_code>/add-record', methods=['POST'])
@require_login
def add_clinical_record(fiscal_code):
    """Add a clinical record to a patient."""
    if not db_connected:
        return jsonify({'error': 'Database non connesso'}), 500
    
    try:
        # Get current doctor from session
        doctor_id = session.get('doctor_id')
        doctor_data = db.find_doctor_by_id(doctor_id) if doctor_id else None
        
        # Handle both JSON and FormData
        if request.is_json:
            data = request.json
            attachments = []
        else:
            data = request.form
            attachments = []
            
            # Handle file uploads
            if 'files' in request.files:
                files = request.files.getlist('files')
                upload_folder = app.config['UPLOAD_FOLDER'] / fiscal_code / datetime.now().strftime('%Y%m%d_%H%M%S')
                upload_folder.mkdir(parents=True, exist_ok=True)
                
                pdf_records_imported = 0
                for file in files:
                    if file and file.filename:
                        filename = secure_filename(file.filename)
                        filepath = upload_folder / filename
                        file.save(filepath)
                        
                        # Check if it's a PDF and try to extract clinical records
                        if filename.lower().endswith('.pdf'):
                            extracted_records = extract_clinical_records_from_pdf(str(filepath))
                            if extracted_records:
                                # Import each record as a separate clinical record
                                for record in extracted_records:
                                    record['doctor_id'] = doctor_id
                                    record['doctor_name'] = f"{doctor_data.get('nome', '')} {doctor_data.get('cognome', '')}" if doctor_data else 'Importato da PDF'
                                    record['doctor_specialization'] = doctor_data.get('specializzazione', '') if doctor_data else ''
                                    db.add_clinical_record(fiscal_code, record)
                                    pdf_records_imported += 1
                                
                                # If we imported records from PDF, skip creating a new record from form
                                if pdf_records_imported > 0:
                                    return jsonify({
                                        'success': True, 
                                        'message': f'{pdf_records_imported} schede cliniche importate dal PDF con successo',
                                        'imported_count': pdf_records_imported
                                    })
                        
                        # If not a clinical record PDF, treat as normal attachment
                        attachments.append({
                            'name': filename,
                            'path': str(filepath),
                            'size': filepath.stat().st_size,
                            'type': file.content_type
                        })
        
        # Parse vital_signs if it's a string
        vital_signs = data.get('vital_signs', {})
        if isinstance(vital_signs, str):
            import json
            vital_signs = json.loads(vital_signs)
        
        # Create record with new structure
        record = {
            'timestamp': datetime.now().isoformat(),
            'motivo_tipo': data.get('motivo_tipo', 'Visita'),
            'motivo': data.get('motivo', ''),
            'tipo_scheda': data.get('motivo_tipo', data.get('tipo_scheda', 'Visita')),  # Backward compatibility
            'chief_complaint': data.get('motivo', data.get('chief_complaint', '')),  # Backward compatibility
            'symptoms': data.get('symptoms', ''),
            'diagnosis': data.get('diagnosis', ''),
            'treatment': data.get('treatment', ''),
            'notes': data.get('notes', ''),
            'vital_signs': vital_signs,
            'attachments': attachments,
            'lab_results': data.get('lab_results', []),
            'imaging': data.get('imaging', []),
            'doctor_id': doctor_id,
            'doctor_name': f"{doctor_data.get('nome', '')} {doctor_data.get('cognome', '')}" if doctor_data else 'Sconosciuto',
            'doctor_specialization': doctor_data.get('specializzazione', '') if doctor_data else ''
        }
        
        # Add to patient
        db.add_clinical_record(fiscal_code, record)
        
        return jsonify({'success': True, 'message': 'Scheda clinica aggiunta con successo'})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/folder/upload', methods=['POST'])
@require_login
def upload_folder():
    """Process uploaded clinical folder."""
    if 'files[]' not in request.files:
        return jsonify({'error': 'Nessun file caricato'}), 400
    
    files = request.files.getlist('files[]')
    fiscal_code = request.form.get('fiscal_code')
    
    try:
        # Create temporary folder for upload
        temp_folder = app.config['UPLOAD_FOLDER'] / fiscal_code / datetime.now().strftime('%Y%m%d_%H%M%S')
        temp_folder.mkdir(parents=True, exist_ok=True)
        
        # Save all files
        saved_files = []
        attachments = []
        pdf_files = []
        for file in files:
            if file.filename:
                filename = secure_filename(file.filename)
                filepath = temp_folder / filename
                file.save(filepath)
                saved_files.append(str(filepath))
                attachments.append({
                    'name': filename,
                    'path': str(filepath),
                    'size': filepath.stat().st_size,
                    'type': file.content_type or 'application/octet-stream'
                })
                
                # Track PDF files for later extraction
                if filename.lower().endswith('.pdf'):
                    pdf_files.append(str(filepath))
        
        # Check if any PDF files contain exported clinical records
        extracted_records_count = 0
        for pdf_path in pdf_files:
            print(f"Checking PDF for clinical records: {pdf_path}")
            extracted_records = extract_clinical_records_from_pdf(pdf_path)
            if extracted_records:
                print(f"✅ Found {len(extracted_records)} clinical records in PDF")
                # Get current doctor from session
                doctor_id = session.get('doctor_id')
                doctor_data = db.find_doctor_by_id(doctor_id) if doctor_id and db_connected else None
                
                # Import each record as a separate clinical record
                for record in extracted_records:
                    record['doctor_id'] = doctor_id
                    record['doctor_name'] = f"{doctor_data.get('nome', '')} {doctor_data.get('cognome', '')}" if doctor_data else 'Importato da PDF'
                    record['doctor_specialization'] = doctor_data.get('specializzazione', '') if doctor_data else ''
                    db.add_clinical_record(fiscal_code, record)
                    extracted_records_count += 1
                    print(f"✅ Imported record: {record.get('chief_complaint', 'N/A')}")
        
        # If we extracted records from PDF, return success message
        if extracted_records_count > 0:
            return jsonify({
                'success': True,
                'message': f'{extracted_records_count} schede cliniche importate dal PDF con successo',
                'imported_count': extracted_records_count
            })
        
        # Process folder
        if processor:
            results = processor.process_folder(str(temp_folder))
            
            # Get current doctor from session
            doctor_id = session.get('doctor_id')
            doctor_data = db.find_doctor_by_id(doctor_id) if doctor_id and db_connected else None
            
            # Save results if database is connected
            if db_connected and fiscal_code:
                # Convert DecisionSupport results to clinical record format
                top_diagnosis = results.get_top_diagnosis()
                
                # Extract file content for notes
                notes_content = []
                for filepath in saved_files:
                    try:
                        file_path = Path(filepath)
                        if file_path.suffix.lower() in ['.txt', '.md', '.note']:
                            with open(filepath, 'r', encoding='utf-8') as f:
                                notes_content.append(f"=== {file_path.name} ===\n{f.read()}\n")
                        elif file_path.suffix.lower() == '.pdf':
                            notes_content.append(f"=== {file_path.name} ===\n[File PDF caricato]\n")
                    except:
                        pass
                
                # Create clinical record from processing results
                record = {
                    'timestamp': datetime.now().isoformat(),
                    'motivo_tipo': 'Caricamento File',
                    'motivo': f'File caricati e processati automaticamente ({len(files)} file)',
                    'tipo_scheda': 'Caricamento File',
                    'chief_complaint': f'Processamento automatico di {len(files)} file clinici',
                    'symptoms': '\n'.join(results.clinical_notes) if results.clinical_notes else '',
                    'diagnosis': top_diagnosis.condition if top_diagnosis else 'In analisi',
                    'treatment': '\n'.join([f"- {test}" for test in top_diagnosis.recommended_tests]) if top_diagnosis and top_diagnosis.recommended_tests else '',
                    'notes': '\n'.join(notes_content) if notes_content else f'File processati: {", ".join([Path(f).name for f in saved_files])}',
                    'vital_signs': {},
                    'attachments': attachments,
                    'lab_results': [],
                    'imaging': [],
                    'doctor_id': doctor_id,
                    'doctor_name': f"{doctor_data.get('nome', '')} {doctor_data.get('cognome', '')}" if doctor_data else 'Sistema Automatico',
                    'doctor_specialization': doctor_data.get('specializzazione', '') if doctor_data else 'AI Processing',
                    # Additional metadata
                    'ai_processing': {
                        'model_used': results.models_used,
                        'processing_time_ms': results.processing_time_ms,
                        'confidence': top_diagnosis.confidence_score if top_diagnosis else 0.0,
                        'alerts': results.alerts,
                        'warnings': results.warnings,
                        'all_diagnoses': [
                            {
                                'condition': d.condition,
                                'confidence': d.confidence_score,
                                'evidence': d.evidence
                            } for d in results.diagnoses
                        ]
                    }
                }
                
                db.add_clinical_record(fiscal_code, record)
                
                return jsonify({
                    'success': True, 
                    'message': f'{len(files)} file processati e convertiti in scheda clinica',
                    'diagnosis': top_diagnosis.condition if top_diagnosis else None,
                    'confidence': top_diagnosis.confidence_score if top_diagnosis else 0.0
                })
            else:
                return jsonify({'error': 'Database non connesso'}), 500
        else:
            return jsonify({'error': 'Processore non inizializzato'}), 500
            
    except Exception as e:
        import traceback
        print(f"Error in upload_folder: {e}")
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500


@app.route('/api/file/upload', methods=['POST'])
@require_login
def upload_file():
    """Process single uploaded file."""
    if 'file' not in request.files:
        return jsonify({'error': 'Nessun file caricato'}), 400
    
    file = request.files['file']
    fiscal_code = request.form.get('fiscal_code')
    
    try:
        if file.filename:
            # Save file
            filename = secure_filename(file.filename)
            temp_folder = app.config['UPLOAD_FOLDER'] / fiscal_code / datetime.now().strftime('%Y%m%d_%H%M%S')
            temp_folder.mkdir(parents=True, exist_ok=True)
            filepath = temp_folder / filename
            file.save(filepath)
            
            # Process file
            if gateway:
                result = gateway.process_data(str(filepath))
                
                # Save to database if connected
                if db_connected and fiscal_code:
                    record = {
                        'timestamp': datetime.now().isoformat(),
                        'type': 'file_processing',
                        'filename': filename,
                        'result': result,
                    }
                    db.add_clinical_record(fiscal_code, record)
                
                return jsonify({'success': True, 'result': result})
            else:
                return jsonify({'error': 'Gateway non inizializzato'}), 500
                
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/metrics', methods=['GET'])
@require_login
def get_metrics():
    """Get system metrics."""
    if metrics_observer:
        metrics = metrics_observer.get_summary()
        return jsonify({'success': True, 'metrics': metrics})
    return jsonify({'error': 'Metrics observer non disponibile'}), 500


@app.route('/api/export/<fiscal_code>', methods=['GET'])
@require_login
def export_patient_data(fiscal_code):
    """Export patient data and clinical records as PDF file."""
    if not db_connected:
        return jsonify({'error': 'Database non connesso'}), 500
    
    try:
        # Get patient data
        patient_data = db.find_by_fiscal_code(fiscal_code)
        if not patient_data:
            return jsonify({'error': 'Paziente non trovato'}), 404
        
        print(f"DEBUG: Patient data keys: {list(patient_data.keys())}")
        print(f"DEBUG: Comune Nascita (luogo_nascita): '{patient_data.get('luogo_nascita')}'")
        print(f"DEBUG: Gender (sesso): '{patient_data.get('sesso')}'")
        print(f"DEBUG: Age: '{patient_data.get('age')}'")
        print(f"DEBUG: Data nascita: '{patient_data.get('data_nascita')}'")
        
        # Get clinical records
        clinical_records = []
        try:
            clinical_records = db.get_patient_clinical_records(fiscal_code)
            print(f"DEBUG: Found {len(clinical_records)} clinical records")
            if clinical_records:
                print(f"DEBUG: First record keys: {list(clinical_records[0].keys())}")
        except Exception as e:
            print(f"Warning: Could not load clinical records: {e}")
        
        # Create PDF file in memory
        memory_file = io.BytesIO()
        doc = SimpleDocTemplate(memory_file, pagesize=A4, 
                               leftMargin=2*cm, rightMargin=2*cm,
                               topMargin=2*cm, bottomMargin=2*cm)
        
        # Build content
        story = []
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#2563eb'),
            spaceAfter=30,
            alignment=TA_CENTER
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#1e40af'),
            spaceAfter=12,
            spaceBefore=12
        )
        
        # Title
        story.append(Paragraph("Cartella Clinica Elettronica", title_style))
        story.append(Spacer(1, 0.5*cm))
        
        # Patient Information Section
        story.append(Paragraph("Informazioni Paziente", heading_style))
        
        # Formatta la data di nascita
        data_nascita = patient_data.get('data_nascita', 'N/A')
        if isinstance(data_nascita, datetime):
            data_nascita = data_nascita.strftime('%d/%m/%Y')
        elif isinstance(data_nascita, str) and data_nascita != 'N/A':
            # Se è una stringa in formato YYYY-MM-DD, convertila
            try:
                from datetime import datetime as dt
                data_obj = dt.strptime(data_nascita, '%Y-%m-%d')
                data_nascita = data_obj.strftime('%d/%m/%Y')
                # Calcola l'età se non è disponibile
                if not patient_data.get('age'):
                    today = datetime.now()
                    age = today.year - data_obj.year - ((today.month, today.day) < (data_obj.month, data_obj.day))
                    patient_data['age'] = age
            except:
                pass
        
        # Gestisci i campi che potrebbero essere None - usa le chiavi corrette restituite da find_by_fiscal_code
        comune_nascita = patient_data.get('luogo_nascita') or patient_data.get('comune_nascita') or 'N/A'
        gender = patient_data.get('sesso') or patient_data.get('gender') or 'N/A'
        age = patient_data.get('age')
        age_str = str(age) if age is not None else 'N/A'
        
        patient_info = [
            ['Nome:', patient_data.get('nome', 'N/A')],
            ['Cognome:', patient_data.get('cognome', 'N/A')],
            ['Codice Fiscale:', fiscal_code],
            ['Data di Nascita:', str(data_nascita)],
            ['Comune di Nascita:', comune_nascita],
            ['Genere:', gender],
            ['Età:', age_str],
        ]
        
        patient_table = Table(patient_info, colWidths=[5*cm, 12*cm])
        patient_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e0e7ff')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        
        story.append(patient_table)
        story.append(Spacer(1, 1*cm))
        
        # Clinical Records Section
        if clinical_records:
            story.append(Paragraph(f"Schede Cliniche ({len(clinical_records)})", heading_style))
            story.append(Spacer(1, 0.3*cm))
            
            for idx, record in enumerate(clinical_records, 1):
                # Record header
                timestamp = record.get('timestamp', 'N/A')
                if isinstance(timestamp, datetime):
                    timestamp = timestamp.strftime('%d/%m/%Y %H:%M:%S')
                elif isinstance(timestamp, str):
                    try:
                        ts = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                        timestamp = ts.strftime('%d/%m/%Y %H:%M:%S')
                    except:
                        pass
                
                record_title = f"Scheda Clinica #{idx} - {timestamp}"
                story.append(Paragraph(record_title, styles['Heading3']))
                
                # Record details
                record_data = [
                    ['ID Incontro:', str(record.get('encounter_id', 'N/A'))],
                    ['Motivo Principale:', record.get('chief_complaint', 'N/A')],
                    ['Sintomi:', record.get('symptoms', 'N/A')],
                    ['Priorità:', record.get('priority', 'N/A')],
                ]
                
                # Add vital signs if available
                vital_signs = record.get('vital_signs', {})
                if vital_signs:
                    if vital_signs.get('blood_pressure'):
                        record_data.append(['Pressione Sanguigna:', vital_signs['blood_pressure']])
                    if vital_signs.get('heart_rate'):
                        record_data.append(['Frequenza Cardiaca:', vital_signs['heart_rate']])
                    if vital_signs.get('temperature'):
                        record_data.append(['Temperatura:', vital_signs['temperature'] + '°C'])
                    if vital_signs.get('oxygen_saturation'):
                        record_data.append(['Saturazione O2:', vital_signs['oxygen_saturation']])
                    if vital_signs.get('respiratory_rate'):
                        record_data.append(['Frequenza Respiratoria:', vital_signs['respiratory_rate']])
                
                record_table = Table(record_data, colWidths=[5*cm, 12*cm])
                record_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f3f4f6')),
                    ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                    ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                    ('ALIGN', (1, 0), (1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                    ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 0), (-1, -1), 9),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('LEFTPADDING', (0, 0), (-1, -1), 8),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 8),
                    ('TOPPADDING', (0, 0), (-1, -1), 6),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ]))
                
                story.append(record_table)
                
                # Add notes if available
                if 'notes' in record and record['notes']:
                    story.append(Spacer(1, 0.3*cm))
                    story.append(Paragraph('<b>Note:</b>', styles['Normal']))
                    notes_text = record['notes']
                    if isinstance(notes_text, list):
                        notes_text = ', '.join(str(n) for n in notes_text)
                    story.append(Paragraph(str(notes_text), styles['Normal']))
                
                story.append(Spacer(1, 0.5*cm))
        else:
            story.append(Paragraph("Nessuna scheda clinica disponibile", styles['Normal']))
        
        # Footer
        story.append(Spacer(1, 1*cm))
        footer_style = ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=8,
            textColor=colors.grey,
            alignment=TA_CENTER
        )
        story.append(Paragraph(
            f"Documento generato il {datetime.now().strftime('%d/%m/%Y alle %H:%M:%S')}",
            footer_style
        ))
        story.append(Paragraph("EarlyCare Gateway - Sistema di Gestione Cartelle Cliniche", footer_style))
        
        # Build PDF
        doc.build(story)
        
        # Seek to beginning of file
        memory_file.seek(0)
        
        # Generate filename
        filename = f"cartella_clinica_{fiscal_code}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
        return send_file(
            memory_file,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        print(f"Error in export: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/api/debug/check-doctor/<doctor_id>', methods=['GET'])
def debug_check_doctor(doctor_id):
    """DEBUG: Check if a doctor exists in the database."""
    if not db_connected:
        return jsonify({'error': 'Database non connesso'}), 500
    
    try:
        doctor = db.find_doctor_by_id(doctor_id)
        if doctor:
            return jsonify({
                'found': True,
                'doctor_id': doctor.get('doctor_id'),
                'nome': doctor.get('nome'),
                'cognome': doctor.get('cognome'),
                'is_active': doctor.get('is_active')
            }), 200
        else:
            return jsonify({'found': False, 'error': f'Doctor {doctor_id} not found in database'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ========== AI MEDICAL DIAGNOSTICS ROUTES ==========

@app.route('/api/diagnostics/generate', methods=['POST'])
@require_login
def generate_diagnosis():
    """
    Generate AI-powered medical diagnosis for a patient.
    Requires doctor authentication.
    """
    if not db_connected:
        return jsonify({'error': 'Database non connesso'}), 500
    
    if not ai_diagnostics:
        return jsonify({'error': 'Servizio di diagnostica AI non disponibile'}), 503
    
    try:
        data = request.json
        fiscal_code = data.get('fiscal_code')
        clinical_record = data.get('clinical_record')  # Scheda specifica se presente
        
        if not fiscal_code:
            return jsonify({'error': 'Codice fiscale mancante'}), 400
        
        # Get patient object from database
        patient = db.get_patient(fiscal_code)
        
        if not patient:
            return jsonify({'error': 'Paziente non trovato'}), 404
        
        # Convert Patient object to dictionary for AI
        patient_data = db._patient_to_dict(patient)
        
        # Add codice_fiscale if not present
        if 'codice_fiscale' not in patient_data or not patient_data['codice_fiscale']:
            patient_data['codice_fiscale'] = fiscal_code
        
        # Se è stata passata una scheda specifica, usa solo quella
        if clinical_record:
            # Analizza solo la scheda specifica
            patient_data['motivo_tipo'] = clinical_record.get('motivo_tipo') or clinical_record.get('tipo_scheda')
            patient_data['motivo'] = clinical_record.get('motivo') or clinical_record.get('chief_complaint')
            patient_data['sintomi'] = clinical_record.get('symptoms', '')
            patient_data['segni_vitali'] = clinical_record.get('vital_signs', {})
            patient_data['note'] = clinical_record.get('notes', '')
            patient_data['diagnosi_precedenti'] = clinical_record.get('diagnosis', '')
            patient_data['trattamento'] = clinical_record.get('treatment', '')
            patient_data['timestamp_visita'] = clinical_record.get('timestamp')
            patient_data['dottore'] = clinical_record.get('doctor_name', '')
            
            # Aggiungi info su allegati se presenti
            if clinical_record.get('attachments'):
                patient_data['allegati'] = [att.get('name', att) for att in clinical_record['attachments']]
        else:
            # Altrimenti usa tutti i record clinici disponibili
            try:
                clinical_records = db.get_patient_clinical_records(fiscal_code)
                if clinical_records:
                    # Add the most recent clinical data
                    latest_record = clinical_records[0] if len(clinical_records) > 0 else {}
                    if latest_record:
                        patient_data['ultima_visita'] = latest_record.get('timestamp')
                        patient_data['sintomi'] = latest_record.get('symptoms', [])
                        patient_data['segni_vitali'] = latest_record.get('vital_signs', {})
                        patient_data['diagnosi_precedenti'] = latest_record.get('diagnosis', '')
                        patient_data['trattamento'] = latest_record.get('treatment', '')
                        patient_data['note'] = latest_record.get('notes', '')
                        
                    # Add count of records for context
                    patient_data['numero_visite'] = len(clinical_records)
            except Exception as e:
                print(f"Warning: Could not load clinical records: {e}")
        
        # Check if doctor has access to this patient (if doctor_id field exists)
        doctor_id = session.get('doctor_id')
        # Note: Not all patients have doctor_id field, so we skip this check for now
        
        # Generate diagnosis using AI
        print(f"Generating diagnosis for patient: {fiscal_code}")
        diagnosis_result = ai_diagnostics.generate_diagnosis(patient_data)
        print(f"Diagnosis result success: {diagnosis_result.get('success')}")
        
        if not diagnosis_result.get('success'):
            error_msg = diagnosis_result.get('error', 'Unknown error')
            print(f"Diagnosis generation failed: {error_msg}")
            return jsonify({
                'error': 'Errore nella generazione della diagnosi',
                'details': error_msg
            }), 500
        
        # Save diagnosis to database (optional: you could add a diagnoses collection)
        diagnosis_record = {
            'patient_id': fiscal_code,
            'doctor_id': doctor_id,
            'diagnosis': diagnosis_result['diagnosis'],
            'timestamp': diagnosis_result['timestamp'],
            'model': diagnosis_result['model'],
            'metadata': diagnosis_result['metadata']
        }
        
        # Optionally save to a diagnoses collection
        try:
            db.db['diagnoses'].insert_one(diagnosis_record)
        except:
            pass  # If collection doesn't exist, we'll just return the result
        
        return jsonify({
            'success': True,
            'diagnosis': diagnosis_result['diagnosis'],
            'timestamp': diagnosis_result['timestamp'],
            'patient_id': fiscal_code,
            'metadata': diagnosis_result['metadata']
        }), 200
        
    except Exception as e:
        print(f"Error in generate_diagnosis: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/api/diagnostics/history/<fiscal_code>', methods=['GET'])
@require_login
def get_diagnosis_history(fiscal_code):
    """
    Get diagnosis history for a patient.
    Requires doctor authentication.
    """
    if not db_connected:
        return jsonify({'error': 'Database non connesso'}), 500
    
    try:
        # Get patient object to verify it exists
        patient = db.get_patient(fiscal_code)
        
        if not patient:
            return jsonify({'error': 'Paziente non trovato'}), 404
        
        # Check if doctor has access to this patient (if needed)
        # Note: Not enforcing doctor_id check for now as not all patients have this field
        
        # Get diagnosis history
        diagnoses = list(db.db['diagnoses'].find(
            {'patient_id': fiscal_code},
            {'_id': 0}
        ).sort('timestamp', -1).limit(10))
        
        return jsonify({
            'success': True,
            'patient_id': fiscal_code,
            'diagnoses': diagnoses,
            'count': len(diagnoses)
        }), 200
        
    except Exception as e:
        print(f"Error in get_diagnosis_history: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/diagnostics/status', methods=['GET'])
def diagnostics_status():
    """Check if AI diagnostics service is available."""
    return jsonify({
        'available': ai_diagnostics is not None,
        'model': 'gemini-2.5-flash' if ai_diagnostics else None
    }), 200


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
