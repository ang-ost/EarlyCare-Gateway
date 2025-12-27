"""
EarlyCare Gateway - Flask Web Application
"""

from flask import Flask, render_template, request, jsonify, send_file, session, make_response
from flask_cors import CORS, cross_origin
from werkzeug.utils import secure_filename
import os
from pathlib import Path
import json
from datetime import datetime
import sys
from functools import wraps
import zipfile
import io

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
except ImportError as e:
    print(f"Error importing MedicalDiagnosticsAI: {e}")
    AI_AVAILABLE = False
    MedicalDiagnosticsAI = None

app = Flask(__name__)
app.secret_key = Config.FLASK_SECRET_KEY
app.config['UPLOAD_FOLDER'] = Path(__file__).parent / 'uploads'
app.config['MAX_CONTENT_LENGTH'] = Config.MAX_UPLOAD_SIZE_MB * 1024 * 1024

# Enable CORS for frontend communication
# Allow multiple origins for development and production
frontend_url = os.getenv('FRONTEND_URL', 'http://localhost:5173')
allowed_origins = [origin.strip() for origin in frontend_url.split(',')]

# Add localhost for development
if 'localhost' not in frontend_url and '127.0.0.1' not in frontend_url:
    allowed_origins.extend(['http://localhost:5173', 'http://127.0.0.1:5173'])

print(f"🌐 CORS allowed origins: {allowed_origins}")

# Configure CORS with more permissive settings
CORS(app, 
     resources={
         r"/api/*": {
             "origins": allowed_origins,
             "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
             "allow_headers": ["Content-Type", "Authorization", "Accept", "Origin", "X-Requested-With"],
             "expose_headers": ["Content-Type", "Set-Cookie"],
             "supports_credentials": True,
             "max_age": 3600
         }
     })

# Session configuration for production (cross-domain)
is_production = os.getenv('RENDER', '').lower() in ['true', '1', 'yes']
print(f"🔧 Production mode: {is_production}")

app.config['SESSION_COOKIE_SECURE'] = is_production  # HTTPS only in production
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'None' if is_production else 'Lax'  # None for cross-domain
app.config['SESSION_COOKIE_DOMAIN'] = None  # Allow cross-domain cookies
app.config['PERMANENT_SESSION_LIFETIME'] = 86400 * 7  # 7 days

print(f"🍪 Cookie config - Secure: {app.config['SESSION_COOKIE_SECURE']}, SameSite: {app.config['SESSION_COOKIE_SAMESITE']}")

# Add after_request handler to ensure CORS headers on all responses
@app.after_request
def after_request(response):
    origin = request.headers.get('Origin')
    if origin in allowed_origins:
        response.headers['Access-Control-Allow-Origin'] = origin
        response.headers['Access-Control-Allow-Credentials'] = 'true'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, Accept, Origin, X-Requested-With'
        response.headers['Access-Control-Expose-Headers'] = 'Content-Type, Set-Cookie'
    return response


# Ensure upload folder exists
app.config['UPLOAD_FOLDER'].mkdir(exist_ok=True)

# Global variables for system state
gateway = None
processor = None
metrics_observer = None
db = None
db_connected = False
ai_diagnostics = None
chatbot_ai = None


def initialize_system():
    """Initialize the clinical gateway system."""
    global gateway, processor, metrics_observer, db, db_connected, ai_diagnostics, chatbot_ai
    
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
                ai_diagnostics = MedicalDiagnosticsAI(api_key=Config.GEMINI_API_KEY)
                print("✅ AI Medical Diagnostics initialized successfully")
            except Exception as e:
                print(f"⚠️  AI Diagnostics initialization failed: {e}")
                ai_diagnostics = None
        else:
            print("⚠️  AI Diagnostics not available (missing API key or module)")
        
        # Initialize Chatbot AI (con chiave separata)
        if AI_AVAILABLE and hasattr(Config, 'CHATBOT_GEMINI_API_KEY') and Config.CHATBOT_GEMINI_API_KEY:
            try:
                chatbot_ai = MedicalDiagnosticsAI(api_key=Config.CHATBOT_GEMINI_API_KEY)
                print("✅ Chatbot AI initialized successfully (separate API key)")
            except Exception as e:
                print(f"⚠️  Chatbot AI initialization failed: {e}")
                chatbot_ai = None
        else:
            print("⚠️  Chatbot AI not available (missing CHATBOT_GEMINI_API_KEY)")
        
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
    """API root - return status."""
    return jsonify({
        'service': 'EarlyCare Gateway API',
        'version': '1.0.0',
        'status': 'running',
        'db_connected': db_connected
    })


@app.route('/api/profile')
@require_login
def profile():
    """Get doctor profile."""
    try:
        doctor_data = db.find_doctor_by_id(session['doctor_id'])
        if not doctor_data:
            session.clear()
            return jsonify({'error': 'Medico non trovato'}), 404
        
        return jsonify({'doctor': doctor_data, 'db_connected': db_connected}), 200
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
                
                for file in files:
                    if file and file.filename:
                        filename = secure_filename(file.filename)
                        filepath = upload_folder / filename
                        file.save(filepath)
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
    """Export patient data and clinical records as ZIP file."""
    if not db_connected:
        return jsonify({'error': 'Database non connesso'}), 500
    
    try:
        # Get patient data
        patient_data = db.find_by_fiscal_code(fiscal_code)
        if not patient_data:
            return jsonify({'error': 'Paziente non trovato'}), 404
        
        # Get clinical records
        clinical_records = []
        try:
            clinical_records = list(db.get_clinical_records(fiscal_code))
        except Exception as e:
            print(f"Warning: Could not load clinical records: {e}")
        
        # Create ZIP file in memory
        memory_file = io.BytesIO()
        with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zf:
            # Add patient info
            patient_json = json.dumps(patient_data, ensure_ascii=False, indent=2, default=str)
            zf.writestr('patient_info.json', patient_json)
            
            # Add clinical records
            if clinical_records:
                records_json = json.dumps(clinical_records, ensure_ascii=False, indent=2, default=str)
                zf.writestr('clinical_records.json', records_json)
                
                # Create individual record files
                for idx, record in enumerate(clinical_records):
                    record_filename = f"record_{idx+1}_{record.get('timestamp', 'unknown')}.json"
                    record_json = json.dumps(record, ensure_ascii=False, indent=2, default=str)
                    zf.writestr(f"records/{record_filename}", record_json)
            
            # Add README
            readme_content = f"""Cartella Clinica - {patient_data.get('first_name', '')} {patient_data.get('last_name', '')}
Codice Fiscale: {fiscal_code}
Data Export: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}

Contenuto:
- patient_info.json: Informazioni anagrafiche del paziente
- clinical_records.json: Tutte le schede cliniche
- records/: Schede cliniche individuali
"""
            zf.writestr('README.txt', readme_content)
        
        # Seek to beginning of file
        memory_file.seek(0)
        
        # Generate filename
        filename = f"cartella_clinica_{fiscal_code}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
        
        return send_file(
            memory_file,
            mimetype='application/zip',
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
                # Prepara allegati con contenuto base64 per analisi IA
                import base64
                decoded_attachments = []
                for att in clinical_record['attachments']:
                    if isinstance(att, dict) and 'content' in att:
                        # Mantieni il contenuto base64 per l'analisi IA
                        decoded_attachments.append({
                            'name': att.get('name', 'unknown'),
                            'type': att.get('type', 'application/octet-stream'),
                            'size': att.get('size', 0),
                            'content': att['content']  # Base64 string
                        })
                    elif isinstance(att, str):
                        decoded_attachments.append({'name': att})
                
                patient_data['allegati'] = decoded_attachments
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
        
        # Check for quota exceeded error
        error_message = str(e)
        if 'quota' in error_message.lower() or '429' in error_message or 'ResourceExhausted' in error_message:
            return jsonify({
                'error': 'Quota API superata',
                'message': 'Il servizio di diagnostica AI ha raggiunto il limite giornaliero di richieste. Riprova domani o contatta l\'amministratore per aumentare la quota.'
            }), 429
        
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


# ========== MEDICAL CHATBOT ROUTES ==========

@app.route('/api/chatbot/ask', methods=['POST'])
def chatbot_ask():
    """
    Medical chatbot endpoint - answers only medical questions.
    Uses strict prompt to prevent misuse.
    Uses separate API key (CHATBOT_GEMINI_API_KEY).
    """
    if not chatbot_ai:
        return jsonify({
            'success': False,
            'response': 'Mi dispiace, il servizio di assistenza medica non è al momento disponibile.'
        }), 503
    
    try:
        data = request.json
        question = data.get('question', '').strip()
        
        if not question:
            return jsonify({
                'success': False,
                'response': 'Per favore, scrivi una domanda.'
            }), 400
        
        # Create strict medical chatbot prompt
        chatbot_prompt = f"""Sei un assistente medico virtuale professionale e rigoroso.

REGOLE RIGIDE:
1. Rispondi SOLO a domande di carattere medico, sanitario o relativo alla salute
2. Se la domanda NON è medica, rispondi esattamente: "Mi dispiace, posso rispondere solo a domande di carattere medico e sanitario. Come posso aiutarti con questioni relative alla salute?"
3. Non rispondere a domande su: tempo, sport, cucina, politica, intrattenimento, tecnologia (non medica), o qualsiasi argomento non medico
4. Fornisci risposte complete, chiare e professionali
5. Usa linguaggio italiano professionale ma comprensibile
6. Alla fine del messaggio inserisci sempre: 'Posso commettere errori: per informazioni mediche è sempre meglio chiedere a un medico o a un professionista qualificato.'

7. Non fare diagnosi, suggerisci sempre di consultare un medico per diagnosi precise
8. IMPORTANTE: Scrivi SOLO testo semplice senza formattazione. NON usare: *, #, -, o altri simboli markdown. Usa solo testo normale con a capo per separare i paragrafi.

Domanda dell'utente: {question}

Fornisci una risposta appropriata seguendo rigorosamente le regole sopra."""

        # Generate response using Chatbot AI (con chiave API separata)
        response = chatbot_ai.model.generate_content(
            chatbot_prompt,
            generation_config={
                'temperature': 0.3,
                'top_p': 0.9,
                'top_k': 40,
                'max_output_tokens': 2048,
            }
        )
        
        if not response or not hasattr(response, 'text'):
            return jsonify({
                'success': False,
                'response': 'Mi dispiace, si è verificato un errore. Riprova.'
            }), 500
        
        answer = response.text.strip()
        
        # Log chatbot interaction (optional)
        print(f"[CHATBOT] Q: {question[:50]}... | A: {answer[:50]}...")
        
        return jsonify({
            'success': True,
            'response': answer
        }), 200
        
    except Exception as e:
        print(f"Error in chatbot_ask: {e}")
        import traceback
        traceback.print_exc()
        
        # Check for quota exceeded error
        error_message = str(e)
        if 'quota' in error_message.lower() or '429' in error_message:
            return jsonify({
                'success': False,
                'response': 'Il servizio di chatbot ha raggiunto il limite giornaliero di richieste. Riprova domani o contatta l\'amministratore per aumentare la quota API.'
            }), 429
        
        return jsonify({
            'success': False,
            'response': 'Mi dispiace, si è verificato un errore tecnico. Riprova più tardi.'
        }), 500


@app.route('/health')
def health():
    """Health check endpoint for Docker."""
    return jsonify({
        'status': 'healthy',
        'db_connected': db_connected,
        'ai_available': ai_diagnostics is not None,
        'cors_origins': allowed_origins,
        'is_production': is_production
    }), 200


@app.route('/api/test-cors', methods=['GET', 'OPTIONS'])
def test_cors():
    """Test CORS configuration."""
    return jsonify({
        'message': 'CORS is working!',
        'origin': request.headers.get('Origin'),
        'allowed_origins': allowed_origins
    }), 200


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
