"""
Clinical Folder Processor - Process complete patient clinical folders
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

from ..models.patient import Patient, PatientRecord, Gender
from ..models.clinical_data import TextData, SignalData, ImageData, DataSource
from ..models.decision import DecisionSupport
from .clinical_gateway import ClinicalGateway


class ClinicalFolderProcessor:
    """
    Processes complete clinical folders containing patient data and various clinical documents.
    
    Supported formats:
    - Text files: .txt, .pdf, .doc, .docx (clinical notes, reports)
    - Signal data: .csv, .json (ECG, EEG, vital signs)
    - Images: .dcm, .png, .jpg (DICOM, X-rays, scans)
    - Metadata: patient_info.json
    """
    
    def __init__(self, gateway: Optional[ClinicalGateway] = None):
        """
        Initialize folder processor.
        
        Args:
            gateway: ClinicalGateway instance. If None, creates a new one.
        """
        self.gateway = gateway or ClinicalGateway()
        
        # Supported file extensions
        self.text_extensions = {'.txt', '.md', '.note', '.report'}
        self.signal_extensions = {'.csv', '.json', '.dat'}
        self.image_extensions = {'.dcm', '.png', '.jpg', '.jpeg', '.tif', '.tiff'}
        
    def process_single_file(
        self,
        file_path: str,
        patient_id: Optional[str] = None
    ) -> DecisionSupport:
        """
        Process a single clinical file.
        
        Args:
            file_path: Path to clinical file (text, signal, or image)
            patient_id: Optional patient ID. If None, generates one from filename.
            
        Returns:
            DecisionSupport with diagnosis and recommendations
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        if not file_path.is_file():
            raise ValueError(f"Not a file: {file_path}")
        
        print(f"\n📄 Processing single file: {file_path.name}")
        print("=" * 60)
        
        # Generate patient ID if not provided
        if not patient_id:
            patient_id = f"P-{file_path.stem}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Create default patient
        print(f"\n1️⃣  Creating patient record...")
        patient = Patient(
            patient_id=patient_id,
            date_of_birth=datetime(1970, 1, 1),
            gender=Gender.UNKNOWN,
            medical_record_number=patient_id
        )
        print(f"   ✓ Patient: {patient.patient_id}")
        
        # Create patient record
        record = PatientRecord(patient=patient)
        
        # Load the file
        print(f"\n2️⃣  Loading clinical data...")
        ext = file_path.suffix.lower()
        
        try:
            if ext in self.text_extensions:
                data = self._load_text_file(file_path, patient_id)
                if data:
                    record.add_clinical_data(data)
                    print(f"   ✓ Loaded text document: {file_path.name}")
            
            elif ext in self.signal_extensions:
                data = self._load_signal_file(file_path, patient_id)
                if data:
                    record.add_clinical_data(data)
                    print(f"   ✓ Loaded signal data: {file_path.name}")
            
            elif ext in self.image_extensions:
                data = self._load_image_file(file_path, patient_id)
                if data:
                    record.add_clinical_data(data)
                    print(f"   ✓ Loaded image: {file_path.name}")
            
            else:
                raise ValueError(f"Unsupported file type: {ext}")
        
        except Exception as e:
            raise ValueError(f"Error loading file: {e}")
        
        # Process through gateway
        print(f"\n3️⃣  Processing through gateway pipeline...")
        decision_support = self.gateway.process_request(record)
        
        print("\n✅ Processing complete!")
        return decision_support
    
    def process_folder(
        self,
        folder_path: str,
        patient_info_file: str = "patient_info.json"
    ) -> DecisionSupport:
        """
        Process a complete clinical folder.
        
        Folder structure expected:
        ```
        patient_folder/
        ├── patient_info.json          # Patient demographics and history
        ├── notes/                     # Clinical notes
        │   ├── admission_note.txt
        │   ├── progress_note.txt
        │   └── discharge_summary.txt
        ├── signals/                   # Signal data
        │   ├── ecg_data.csv
        │   └── vitals.json
        └── images/                    # Medical images
            ├── chest_xray.dcm
            └── ct_scan.dcm
        ```
        
        Args:
            folder_path: Path to patient folder
            patient_info_file: Name of patient info JSON file
            
        Returns:
            DecisionSupport with diagnosis and recommendations
        """
        folder_path = Path(folder_path)
        
        if not folder_path.exists():
            raise FileNotFoundError(f"Folder not found: {folder_path}")
        
        print(f"\n📁 Processing clinical folder: {folder_path.name}")
        print("=" * 60)
        
        # 1. Load patient information
        print("\n1️⃣  Loading patient information...")
        patient = self._load_patient_info(folder_path / patient_info_file)
        print(f"   ✓ Patient: {patient.patient_id} (Age: {patient.calculate_age()})")
        
        # 2. Create patient record
        record = PatientRecord(patient=patient)
        
        # 3. Scan and load clinical data
        print("\n2️⃣  Scanning clinical data...")
        data_count = self._scan_and_load_data(folder_path, record)
        print(f"   ✓ Loaded {data_count} clinical data items")
        
        # 4. Process through gateway
        print("\n3️⃣  Processing through gateway pipeline...")
        decision_support = self.gateway.process_request(record)
        
        print("\n✅ Processing complete!")
        return decision_support
    
    def _load_patient_info(self, info_file: Path) -> Patient:
        """Load patient information from JSON file."""
        if not info_file.exists():
            # Create default patient if file doesn't exist
            print("   ⚠️  No patient_info.json found, using default patient")
            return Patient(
                patient_id=f"P-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                date_of_birth=datetime(1970, 1, 1),
                gender=Gender.UNKNOWN,
                medical_record_number="UNKNOWN"
            )
        
        with open(info_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Parse date of birth
        dob_str = data.get('date_of_birth', '1970-01-01')
        try:
            dob = datetime.strptime(dob_str, '%Y-%m-%d')
        except ValueError:
            dob = datetime(1970, 1, 1)
        
        # Parse gender
        gender_map = {
            'M': Gender.MALE, 'male': Gender.MALE,
            'F': Gender.FEMALE, 'female': Gender.FEMALE,
            'O': Gender.OTHER, 'other': Gender.OTHER
        }
        gender = gender_map.get(data.get('gender', 'unknown'), Gender.UNKNOWN)
        
        return Patient(
            patient_id=data.get('patient_id', 'UNKNOWN'),
            date_of_birth=dob,
            gender=gender,
            medical_record_number=data.get('medical_record_number', 'UNKNOWN'),
            chief_complaint=data.get('chief_complaint'),
            medical_history=data.get('medical_history', []),
            current_medications=data.get('medications', []),
            allergies=data.get('allergies', [])
        )
    
    def _scan_and_load_data(self, folder_path: Path, record: PatientRecord) -> int:
        """Scan folder and load all clinical data."""
        count = 0
        
        # Process all files recursively
        for file_path in folder_path.rglob('*'):
            if not file_path.is_file():
                continue
            
            # Skip patient info file
            if file_path.name == 'patient_info.json':
                continue
            
            ext = file_path.suffix.lower()
            
            try:
                # Text documents
                if ext in self.text_extensions:
                    data = self._load_text_file(file_path, record.patient.patient_id)
                    if data:
                        record.add_clinical_data(data)
                        count += 1
                        print(f"   📄 {file_path.name}")
                
                # Signal data
                elif ext in self.signal_extensions:
                    data = self._load_signal_file(file_path, record.patient.patient_id)
                    if data:
                        record.add_clinical_data(data)
                        count += 1
                        print(f"   📊 {file_path.name}")
                
                # Images
                elif ext in self.image_extensions:
                    data = self._load_image_file(file_path, record.patient.patient_id)
                    if data:
                        record.add_clinical_data(data)
                        count += 1
                        print(f"   🖼️  {file_path.name}")
                        
            except Exception as e:
                print(f"   ⚠️  Error loading {file_path.name}: {e}")
        
        return count
    
    def _load_text_file(self, file_path: Path, patient_id: str) -> Optional[TextData]:
        """Load text clinical document."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Determine document type from filename or path
            doc_type = self._infer_document_type(file_path)
            
            return TextData(
                data_id=f"TEXT-{file_path.stem}",
                patient_id=patient_id,
                timestamp=datetime.fromtimestamp(file_path.stat().st_mtime),
                source=DataSource.EHR,
                text_content=content,
                document_type=doc_type
            )
        except Exception as e:
            print(f"   Error reading {file_path}: {e}")
            return None
    
    def _load_signal_file(self, file_path: Path, patient_id: str) -> Optional[SignalData]:
        """Load signal data file (CSV or JSON)."""
        try:
            if file_path.suffix == '.json':
                with open(file_path, 'r') as f:
                    data = json.load(f)
                
                return SignalData(
                    data_id=f"SIGNAL-{file_path.stem}",
                    patient_id=patient_id,
                    timestamp=datetime.fromtimestamp(file_path.stat().st_mtime),
                    source=DataSource.WEARABLE,
                    signal_values=data.get('values', []),
                    sampling_rate=data.get('sampling_rate', 100.0),
                    signal_type=data.get('type', 'UNKNOWN'),
                    units=data.get('units', 'unit'),
                    duration=data.get('duration', len(data.get('values', [])) / data.get('sampling_rate', 100.0))
                )
            
            elif file_path.suffix == '.csv':
                # Simple CSV parsing
                import csv
                values = []
                with open(file_path, 'r') as f:
                    reader = csv.reader(f)
                    for row in reader:
                        try:
                            values.extend([float(x) for x in row if x.strip()])
                        except ValueError:
                            continue
                
                # Infer signal type from filename
                signal_type = 'ECG' if 'ecg' in file_path.stem.lower() else 'SIGNAL'
                
                return SignalData(
                    data_id=f"SIGNAL-{file_path.stem}",
                    patient_id=patient_id,
                    timestamp=datetime.fromtimestamp(file_path.stat().st_mtime),
                    source=DataSource.WEARABLE,
                    signal_values=values,
                    sampling_rate=250.0,  # Default
                    signal_type=signal_type,
                    units='mV',
                    duration=len(values) / 250.0
                )
        except Exception as e:
            print(f"   Error reading signal {file_path}: {e}")
            return None
    
    def _load_image_file(self, file_path: Path, patient_id: str) -> Optional[ImageData]:
        """Load medical image file."""
        try:
            # Infer modality from filename or path
            modality = self._infer_modality(file_path)
            
            # For now, just reference the file path
            # In production, you'd load and process the actual image
            return ImageData(
                data_id=f"IMAGE-{file_path.stem}",
                patient_id=patient_id,
                timestamp=datetime.fromtimestamp(file_path.stat().st_mtime),
                source=DataSource.IMAGING,
                image_path=str(file_path.absolute()),
                image_format=file_path.suffix[1:].upper(),
                modality=modality,
                dimensions=(512, 512, 1)  # Default dimensions
            )
        except Exception as e:
            print(f"   Error loading image {file_path}: {e}")
            return None
    
    def _infer_document_type(self, file_path: Path) -> str:
        """Infer document type from filename."""
        name_lower = file_path.stem.lower()
        
        if 'admission' in name_lower:
            return 'admission_note'
        elif 'discharge' in name_lower:
            return 'discharge_summary'
        elif 'progress' in name_lower:
            return 'progress_note'
        elif 'radiology' in name_lower or 'rad' in name_lower:
            return 'radiology_report'
        elif 'lab' in name_lower:
            return 'laboratory_report'
        elif 'pathology' in name_lower:
            return 'pathology_report'
        elif 'emergency' in name_lower or 'ed' in name_lower:
            return 'emergency_note'
        else:
            return 'clinical_note'
    
    def _infer_modality(self, file_path: Path) -> str:
        """Infer imaging modality from filename."""
        name_lower = str(file_path).lower()
        
        if 'ct' in name_lower or 'tac' in name_lower:
            return 'CT'
        elif 'mri' in name_lower or 'rm' in name_lower:
            return 'MRI'
        elif 'xray' in name_lower or 'rx' in name_lower or 'x-ray' in name_lower:
            return 'X-RAY'
        elif 'us' in name_lower or 'ultrasound' in name_lower or 'echo' in name_lower:
            return 'US'
        elif 'pet' in name_lower:
            return 'PET'
        elif 'pathology' in name_lower or 'histo' in name_lower:
            return 'PATHOLOGY'
        else:
            return 'UNKNOWN'
    
    def create_folder_template(self, output_path: str):
        """
        Create a template clinical folder structure with example files.
        
        Args:
            output_path: Path where to create the template
        """
        base_path = Path(output_path)
        base_path.mkdir(parents=True, exist_ok=True)
        
        # Create subdirectories
        (base_path / 'notes').mkdir(exist_ok=True)
        (base_path / 'signals').mkdir(exist_ok=True)
        (base_path / 'images').mkdir(exist_ok=True)
        
        # Create patient_info.json template
        patient_template = {
            "patient_id": "P12345",
            "medical_record_number": "MRN-12345",
            "date_of_birth": "1975-06-15",
            "gender": "M",
            "chief_complaint": "Chest pain and shortness of breath",
            "medical_history": [
                "Hypertension",
                "Type 2 Diabetes",
                "Hyperlipidemia"
            ],
            "medications": [
                "Metformin 500mg BID",
                "Lisinopril 10mg daily",
                "Atorvastatin 20mg daily"
            ],
            "allergies": [
                "Penicillin"
            ]
        }
        
        with open(base_path / 'patient_info.json', 'w', encoding='utf-8') as f:
            json.dump(patient_template, f, indent=2)
        
        # Create example clinical note
        note_content = """EMERGENCY DEPARTMENT NOTE

Chief Complaint: Chest pain radiating to left arm

History of Present Illness:
Patient is a 50-year-old male presenting with acute onset substernal chest pain 
started 2 hours ago. Pain is described as crushing, 8/10 severity, radiating 
to left arm. Associated with diaphoresis, nausea, and shortness of breath.
Denies recent trauma or fever.

Past Medical History:
- Hypertension (on Lisinopril)
- Type 2 Diabetes (on Metformin)
- Hyperlipidemia (on Atorvastatin)

Vital Signs:
BP: 165/95 mmHg
HR: 105 bpm
RR: 22/min
SpO2: 94% on room air
Temp: 37.1°C

Physical Examination:
General: Anxious, diaphoretic
Cardiovascular: Tachycardic, regular rhythm, no murmurs
Respiratory: Clear to auscultation bilaterally
Abdomen: Soft, non-tender

Assessment & Plan:
Acute chest pain, concerning for acute coronary syndrome.
- ECG obtained
- Cardiac enzymes ordered
- Cardiology consult requested
- Patient placed on telemetry monitoring
"""
        
        with open(base_path / 'notes' / 'admission_note.txt', 'w', encoding='utf-8') as f:
            f.write(note_content)
        
        # Create example ECG data (JSON format)
        ecg_data = {
            "type": "ECG",
            "sampling_rate": 250.0,
            "units": "mV",
            "duration": 2.0,
            "values": [0.1, 0.15, 0.9, 0.2, -0.05] * 100  # Mock ECG values
        }
        
        with open(base_path / 'signals' / 'ecg_data.json', 'w') as f:
            json.dump(ecg_data, f, indent=2)
        
        # Create README
        readme = """# Clinical Folder Template

This folder contains a template structure for clinical data input.

## Structure:
- patient_info.json: Patient demographics and medical history
- notes/: Clinical notes and reports (.txt files)
- signals/: Signal data like ECG, EEG (.json or .csv files)
- images/: Medical images (.dcm, .png, .jpg files)

## Usage:
1. Update patient_info.json with actual patient data
2. Add clinical notes in notes/ folder
3. Add signal data in signals/ folder
4. Add medical images in images/ folder
5. Process with: python process_clinical_folder.py path/to/this/folder
"""
        
        with open(base_path / 'README.md', 'w', encoding='utf-8') as f:
            f.write(readme)
        
        print(f"✅ Template clinical folder created at: {base_path}")
        print(f"\nStructure:")
        print(f"  {base_path}/")
        print(f"  ├── patient_info.json")
        print(f"  ├── notes/")
        print(f"  │   └── admission_note.txt")
        print(f"  ├── signals/")
        print(f"  │   └── ecg_data.json")
        print(f"  ├── images/")
        print(f"  └── README.md")
