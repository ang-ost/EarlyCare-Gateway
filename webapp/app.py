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


def initialize_system():
    """Initialize the clinical gateway system."""
    global gateway, processor, metrics_observer, db, db_connected
    
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
        
        # Setup strategy selector
        selector = StrategySelector()
        gateway.set_strategy_selector(selector)
        
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
        return jsonify({
            'authenticated': True,
            'doctor': {
                'doctor_id': session['doctor_id'],
                'nome': session.get('doctor_nome', ''),
                'cognome': session.get('doctor_cognome', ''),
                'specializzazione': session.get('doctor_specializzazione', '')
            }
        }), 200
    return jsonify({'authenticated': False}), 200


@app.route('/')
def index():
    """Home page."""
    return render_template('index.html', db_connected=db_connected)


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
    data = request.json
    
    if not db_connected:
        return jsonify({'error': 'Database non connesso'}), 500
    
    try:
        # Create record
        record = {
            'timestamp': datetime.now().isoformat(),
            'tipo_scheda': data.get('tipo_scheda', 'Visita'),
            'chief_complaint': data.get('chief_complaint'),
            'symptoms': data.get('symptoms'),
            'diagnosis': data.get('diagnosis'),
            'treatment': data.get('treatment'),
            'notes': data.get('notes'),
            'vital_signs': data.get('vital_signs', {}),
            'lab_results': data.get('lab_results', []),
            'imaging': data.get('imaging', []),
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
        for file in files:
            if file.filename:
                filename = secure_filename(file.filename)
                filepath = temp_folder / filename
                file.save(filepath)
                saved_files.append(str(filepath))
        
        # Process folder
        if processor:
            results = processor.process_folder(str(temp_folder))
            
            # Save results if database is connected
            if db_connected and fiscal_code:
                # Add processing results to patient record
                record = {
                    'timestamp': datetime.now().isoformat(),
                    'type': 'folder_processing',
                    'results': results,
                    'files': saved_files
                }
                db.add_clinical_record(fiscal_code, record)
            
            return jsonify({'success': True, 'results': results})
        else:
            return jsonify({'error': 'Processore non inizializzato'}), 500
            
    except Exception as e:
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
    """Export patient data as JSON."""
    if not db_connected:
        return jsonify({'error': 'Database non connesso'}), 500
    
    try:
        patient_data = db.find_by_fiscal_code(fiscal_code)
        if not patient_data:
            return jsonify({'error': 'Paziente non trovato'}), 404
        
        # Create export file
        export_folder = app.config['UPLOAD_FOLDER'] / 'exports'
        export_folder.mkdir(exist_ok=True)
        export_file = export_folder / f"{fiscal_code}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(export_file, 'w', encoding='utf-8') as f:
            json.dump(patient_data, f, ensure_ascii=False, indent=2, default=str)
        
        return send_file(export_file, as_attachment=True)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
