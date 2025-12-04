"""
EarlyCare Gateway - Main GUI Window
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from pathlib import Path
import threading
import json
from datetime import datetime
from typing import Optional

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.gateway.clinical_gateway import ClinicalGateway
from src.gateway.folder_processor import ClinicalFolderProcessor
from src.strategy.strategy_selector import StrategySelector
from src.observer.metrics_observer import MetricsObserver, AuditObserver
from src.models.patient import Patient, Gender
from gui.patient_form import PatientFormDialog

# MongoDB integration
try:
    from src.database.mongodb_repository import MongoDBPatientRepository
    MONGODB_AVAILABLE = True
except ImportError:
    MONGODB_AVAILABLE = False
    MongoDBPatientRepository = None


class EarlyCareGUI:
    """Main GUI application for EarlyCare Gateway."""
    
    def __init__(self, root):
        self.root = root
        self.root.title("🏥 MAV - Medical Access & Vision")
        self.root.geometry("1200x800")
        
        # Initialize gateway
        self.gateway = None
        self.processor = None
        self.metrics_observer = None
        self.current_folder = None
        self.current_file = None
        self.is_single_file = False
        
        # MongoDB database
        self.db = None
        self.db_connected = False
        
        # Configure style
        self.setup_style()
        
        # Create UI
        self.create_menu()
        self.create_header()
        self.create_main_content()
        self.create_status_bar()
        
        # Initialize system
        self.initialize_system()
    
    def setup_style(self):
        """Setup modern UI style."""
        style = ttk.Style()
        
        # Use 'clam' theme as base
        style.theme_use('clam')
        
        # Colors
        self.colors = {
            'primary': '#2c3e50',
            'secondary': '#3498db',
            'success': '#27ae60',
            'danger': '#e74c3c',
            'warning': '#f39c12',
            'light': '#ecf0f1',
            'dark': '#34495e',
            'white': '#ffffff'
        }
        
        # Configure styles
        style.configure('Header.TFrame', background=self.colors['primary'])
        style.configure('Header.TLabel', 
                       background=self.colors['primary'],
                       foreground=self.colors['white'],
                       font=('Segoe UI', 16, 'bold'))
        
        style.configure('Card.TFrame', 
                       background=self.colors['white'],
                       relief='flat',
                       borderwidth=1)
        
        style.configure('Primary.TButton',
                       background=self.colors['secondary'],
                       foreground=self.colors['white'],
                       font=('Segoe UI', 10, 'bold'),
                       padding=10)
        
        style.map('Primary.TButton',
                 background=[('active', '#2980b9')])
        
        style.configure('Success.TButton',
                       background=self.colors['success'],
                       font=('Segoe UI', 10, 'bold'),
                       padding=10)
    
    def create_menu(self):
        """Create menu bar."""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="📝 Inserisci Dati Paziente...", command=self.open_patient_form)
        file_menu.add_separator()
        file_menu.add_command(label="Apri Cartella Clinica...", command=self.select_folder)
        file_menu.add_command(label="Apri File Singolo...", command=self.select_file)
        file_menu.add_command(label="Crea Template...", command=self.create_template)
        file_menu.add_separator()
        file_menu.add_command(label="Esporta Risultati...", command=self.export_results)
        file_menu.add_separator()
        file_menu.add_command(label="Esci", command=self.root.quit)
        
        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Strumenti", menu=tools_menu)
        tools_menu.add_command(label="Configurazione Gateway", command=self.show_config)
        tools_menu.add_command(label="Metriche Sistema", command=self.show_metrics)
        tools_menu.add_command(label="Log Audit", command=self.show_audit_log)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Aiuto", menu=help_menu)
        help_menu.add_command(label="Documentazione", command=self.show_docs)
        help_menu.add_command(label="Informazioni", command=self.show_about)
    
    def create_header(self):
        """Create header section."""
        header = ttk.Frame(self.root, style='Header.TFrame', height=80)
        header.pack(fill='x', padx=0, pady=0)
        header.pack_propagate(False)
        
        # Title
        title_label = ttk.Label(
            header,
            text="🏥 MAV",
            style='Header.TLabel'
        )
        title_label.pack(side='left', padx=20, pady=20)
        
        # Subtitle
        subtitle_label = ttk.Label(
            header,
            text="Medical Access & Vision",
            style='Header.TLabel',
            font=('Segoe UI', 10)
        )
        subtitle_label.pack(side='left', padx=5, pady=20)
        
        # System status indicator
        self.status_indicator = tk.Canvas(header, width=20, height=20, 
                                         bg=self.colors['primary'], 
                                         highlightthickness=0)
        self.status_indicator.pack(side='right', padx=20, pady=20)
        self.status_circle = self.status_indicator.create_oval(2, 2, 18, 18, 
                                                               fill=self.colors['danger'])
    
    def create_main_content(self):
        """Create main content area."""
        # Main container with padding
        main_container = ttk.Frame(self.root)
        main_container.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Left panel - Input
        left_panel = self.create_input_panel(main_container)
        left_panel.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        # Right panel - Results
        right_panel = self.create_results_panel(main_container)
        right_panel.pack(side='right', fill='both', expand=True, padx=(10, 0))
    
    def create_input_panel(self, parent):
        """Create input panel."""
        panel = ttk.LabelFrame(parent, text="📁 Cartella Clinica", padding=15)
        
        # Folder selection
        folder_frame = ttk.Frame(panel)
        folder_frame.pack(fill='x', pady=(0, 15))
        
        self.folder_var = tk.StringVar(value="Nessuna cartella selezionata")
        folder_label = ttk.Label(
            folder_frame,
            textvariable=self.folder_var,
            font=('Segoe UI', 9),
            foreground=self.colors['dark']
        )
        folder_label.pack(side='left', fill='x', expand=True)
        
        # Export button
        export_btn = ttk.Button(
            folder_frame,
            text="📥 Export",
            command=self.export_patient_records,
            style='Success.TButton'
        )
        export_btn.pack(side='right', padx=(10, 0))
        
        # Upload button with menu
        upload_btn = ttk.Menubutton(
            folder_frame,
            text="📤 Upload",
            style='Primary.TButton'
        )
        upload_btn.pack(side='right', padx=(5, 0))
        
        # Create menu for upload options
        upload_menu = tk.Menu(upload_btn, tearoff=0)
        upload_menu.add_command(label="📁 Cartella Clinica", command=self.select_folder)
        upload_menu.add_command(label="📄 File Singolo", command=self.select_file)
        upload_btn['menu'] = upload_menu
        
        # New Patient button
        new_patient_btn = ttk.Button(
            folder_frame,
            text="📝 Aggiungi Scheda",
            command=self.open_patient_form,
            style='Primary.TButton'
        )
        new_patient_btn.pack(side='right', padx=(5, 0))
        
        # Search frame
        search_frame = ttk.Frame(panel)
        search_frame.pack(fill='x', pady=(0, 15))
        
        ttk.Label(search_frame, text="🔍 Cerca Paziente per Codice Fiscale:").pack(anchor='w', pady=(0, 5))
        
        search_input_frame = ttk.Frame(search_frame)
        search_input_frame.pack(fill='x')
        
        self.search_fiscal_code_var = tk.StringVar()
        search_entry = ttk.Entry(search_input_frame, textvariable=self.search_fiscal_code_var, width=30)
        search_entry.pack(side='left', fill='x', expand=True, padx=(0, 5))
        
        search_btn = ttk.Button(
            search_input_frame,
            text="🔍 Cerca",
            command=self.search_patient,
            style='Primary.TButton'
        )
        search_btn.pack(side='right')
        
        # Bind Enter key to search
        search_entry.bind('<Return>', lambda e: self.search_patient())
        
        # Patient info display
        info_frame = ttk.LabelFrame(panel, text="👤 Informazioni Paziente", padding=10)
        info_frame.pack(fill='both', expand=True, pady=(0, 15))
        
        self.patient_info_text = scrolledtext.ScrolledText(
            info_frame,
            height=8,
            font=('Consolas', 9),
            wrap='word',
            state='disabled'
        )
        self.patient_info_text.pack(fill='both', expand=True)
        
        # Files list
        files_frame = ttk.LabelFrame(panel, text="📄 File Rilevati", padding=10)
        files_frame.pack(fill='both', expand=True, pady=(0, 15))
        
        # Treeview for files
        tree_frame = ttk.Frame(files_frame)
        tree_frame.pack(fill='both', expand=True)
        
        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side='right', fill='y')
        
        self.files_tree = ttk.Treeview(
            tree_frame,
            columns=('Type', 'Size'),
            show='tree headings',
            yscrollcommand=scrollbar.set,
            height=8
        )
        self.files_tree.pack(side='left', fill='both', expand=True)
        scrollbar.config(command=self.files_tree.yview)
        
        self.files_tree.heading('#0', text='File')
        self.files_tree.heading('Type', text='Tipo')
        self.files_tree.heading('Size', text='Dimensione')
        self.files_tree.column('Type', width=80)
        self.files_tree.column('Size', width=80)
        
        # Process button
        self.process_btn_text = tk.StringVar(value="🚀 Elabora Cartella Clinica")
        self.process_btn = ttk.Button(
            panel,
            textvariable=self.process_btn_text,
            command=self.process_data,
            style='Success.TButton',
            state='disabled'
        )
        self.process_btn.pack(fill='x', pady=(0, 0))
        
        return panel
    
    def create_results_panel(self, parent):
        """Create results panel."""
        panel = ttk.LabelFrame(parent, text="📊 Risultati Diagnosi", padding=15)
        
        # Results tabs
        notebook = ttk.Notebook(panel)
        notebook.pack(fill='both', expand=True)
        
        # Diagnosis tab
        diagnosis_frame = ttk.Frame(notebook)
        notebook.add(diagnosis_frame, text="💊 Diagnosi")
        
        self.diagnosis_text = scrolledtext.ScrolledText(
            diagnosis_frame,
            font=('Consolas', 9),
            wrap='word',
            state='disabled'
        )
        self.diagnosis_text.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Details tab
        details_frame = ttk.Frame(notebook)
        notebook.add(details_frame, text="📋 Dettagli")
        
        self.details_text = scrolledtext.ScrolledText(
            details_frame,
            font=('Consolas', 9),
            wrap='word',
            state='disabled'
        )
        self.details_text.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Logs tab
        logs_frame = ttk.Frame(notebook)
        notebook.add(logs_frame, text="📝 Log")
        
        self.logs_text = scrolledtext.ScrolledText(
            logs_frame,
            font=('Consolas', 8),
            wrap='word',
            state='disabled',
            background='#2c3e50',
            foreground='#ecf0f1'
        )
        self.logs_text.pack(fill='both', expand=True, padx=5, pady=5)
        
        return panel
    
    def create_status_bar(self):
        """Create status bar."""
        status_bar = ttk.Frame(self.root, relief='sunken', padding=5)
        status_bar.pack(side='bottom', fill='x')
        
        self.status_var = tk.StringVar(value="Sistema pronto")
        status_label = ttk.Label(
            status_bar,
            textvariable=self.status_var,
            font=('Segoe UI', 9)
        )
        status_label.pack(side='left')
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            status_bar,
            variable=self.progress_var,
            length=200,
            mode='determinate'
        )
        self.progress_bar.pack(side='right', padx=(10, 0))
    
    def initialize_system(self):
        """Initialize gateway and processors."""
        self.log("Inizializzazione sistema...")
        
        try:
            # Create gateway
            self.gateway = ClinicalGateway()
            
            # Setup observers
            self.metrics_observer = MetricsObserver()
            self.audit_observer = AuditObserver(log_file="logs/gui_audit.log")
            self.gateway.attach_observer(self.metrics_observer)
            self.gateway.attach_observer(self.audit_observer)
            
            # Setup strategies
            strategy_selector = StrategySelector.create_default_selector()
            strategy_selector.enable_ensemble(True)
            self.gateway.set_strategy_selector(strategy_selector)
            
            # Create processor
            self.processor = ClinicalFolderProcessor(self.gateway)
            
            # Initialize MongoDB connection (optional)
            if MONGODB_AVAILABLE:
                try:
                    self.db = MongoDBPatientRepository(
                        connection_string="mongodb+srv://angelospeed2003:kjhwoP4rXR3UsnaV@mav.0zz64yh.mongodb.net/",
                        database_name="earlycare"
                    )
                    self.db_connected = True
                    self.log("✅ Database MongoDB connesso")
                except Exception as db_error:
                    self.log(f"⚠ MongoDB non disponibile: {db_error}")
                    self.db_connected = False
            else:
                self.log("⚠ Modulo pymongo non installato - Database disabilitato")
            
            self.log("✅ Sistema inizializzato correttamente")
            self.set_system_status(True)
            self.status_var.set("Sistema pronto - In attesa di cartella clinica")
            
        except Exception as e:
            self.log(f"❌ Errore inizializzazione: {e}")
            messagebox.showerror("Errore", f"Impossibile inizializzare il sistema:\n{e}")
            self.set_system_status(False)
    
    def select_folder(self):
        """Select clinical folder."""
        folder = filedialog.askdirectory(title="Seleziona Cartella Clinica")
        
        if folder:
            self.current_folder = folder
            self.current_file = None
            self.is_single_file = False
            self.folder_var.set(folder)
            self.log(f"📁 Cartella selezionata: {folder}")
            
            # Load and display patient info
            self.load_patient_info(folder)
            
            # Scan files
            self.scan_folder_files(folder)
            
            # Update button text and enable
            self.process_btn_text.set("🚀 Elabora Cartella Clinica")
            self.process_btn['state'] = 'normal'
            self.status_var.set(f"Cartella caricata: {Path(folder).name}")
    
    def select_file(self):
        """Select single clinical file."""
        file = filedialog.askopenfilename(
            title="Seleziona File Clinico",
            filetypes=[
                ("Tutti i file clinici", "*.txt *.md *.note *.csv *.json *.dcm *.png *.jpg"),
                ("Note cliniche", "*.txt *.md *.note"),
                ("Dati segnale", "*.csv *.json"),
                ("Immagini", "*.dcm *.png *.jpg *.jpeg"),
                ("Tutti i file", "*.*")
            ]
        )
        
        if file:
            self.current_file = file
            self.current_folder = None
            self.is_single_file = True
            self.folder_var.set(file)
            self.log(f"📄 File selezionato: {Path(file).name}")
            
            # Clear patient info
            self.patient_info_text['state'] = 'normal'
            self.patient_info_text.delete(1.0, tk.END)
            self.patient_info_text.insert(1.0, f"File singolo selezionato\n\nNome: {Path(file).name}\nDimensione: {Path(file).stat().st_size} bytes\n\nIl sistema creerà un paziente temporaneo per l'elaborazione.")
            self.patient_info_text['state'] = 'disabled'
            
            # Show single file in tree
            self.show_single_file_in_tree(file)
            
            # Update button text and enable
            self.process_btn_text.set("🚀 Elabora File")
            self.process_btn['state'] = 'normal'
            self.status_var.set(f"File caricato: {Path(file).name}")
    
    def load_patient_info(self, folder_path: str):
        """Load and display patient information."""
        info_file = Path(folder_path) / "patient_info.json"
        
        self.patient_info_text['state'] = 'normal'
        self.patient_info_text.delete(1.0, tk.END)
        
        if info_file.exists():
            try:
                with open(info_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                info_text = f"""ID Paziente: {data.get('patient_id', 'N/A')}
MRN: {data.get('medical_record_number', 'N/A')}
Data di Nascita: {data.get('date_of_birth', 'N/A')}
Sesso: {data.get('gender', 'N/A')}
Sintomo Principale: {data.get('chief_complaint', 'N/A')}

Storia Clinica:
{chr(10).join('• ' + h for h in data.get('medical_history', []))}

Farmaci Attuali:
{chr(10).join('• ' + m for m in data.get('medications', []))}

Allergie:
{chr(10).join('• ' + a for a in data.get('allergies', []))}
"""
                self.patient_info_text.insert(1.0, info_text)
                
            except Exception as e:
                self.patient_info_text.insert(1.0, f"Errore caricamento info: {e}")
        else:
            self.patient_info_text.insert(1.0, "⚠️ File patient_info.json non trovato")
        
        self.patient_info_text['state'] = 'disabled'
    
    def scan_folder_files(self, folder_path: str):
        """Scan and display folder files."""
        # Clear tree
        for item in self.files_tree.get_children():
            self.files_tree.delete(item)
        
        folder = Path(folder_path)
        
        # Count files by type
        counts = {'notes': 0, 'signals': 0, 'images': 0, 'other': 0}
        
        for file_path in folder.rglob('*'):
            if not file_path.is_file() or file_path.name == 'patient_info.json':
                continue
            
            # Determine type
            ext = file_path.suffix.lower()
            if ext in {'.txt', '.md', '.note', '.report'}:
                file_type = '📄 Nota'
                counts['notes'] += 1
            elif ext in {'.csv', '.json', '.dat'}:
                file_type = '📊 Segnale'
                counts['signals'] += 1
            elif ext in {'.dcm', '.png', '.jpg', '.jpeg'}:
                file_type = '🖼️ Immagine'
                counts['images'] += 1
            else:
                file_type = '📎 Altro'
                counts['other'] += 1
            
            # Get size
            size = file_path.stat().st_size
            if size < 1024:
                size_str = f"{size} B"
            elif size < 1024*1024:
                size_str = f"{size/1024:.1f} KB"
            else:
                size_str = f"{size/(1024*1024):.1f} MB"
            
            # Add to tree
            self.files_tree.insert(
                '',
                'end',
                text=file_path.name,
                values=(file_type, size_str)
            )
        
        total = sum(counts.values())
        self.log(f"📊 Trovati {total} file: {counts['notes']} note, {counts['signals']} segnali, {counts['images']} immagini")
    
    def show_single_file_in_tree(self, file_path: str):
        """Show single file in tree."""
        # Clear tree
        for item in self.files_tree.get_children():
            self.files_tree.delete(item)
        
        file_path = Path(file_path)
        
        # Determine type
        ext = file_path.suffix.lower()
        if ext in {'.txt', '.md', '.note', '.report'}:
            file_type = '📄 Nota'
        elif ext in {'.csv', '.json', '.dat'}:
            file_type = '📊 Segnale'
        elif ext in {'.dcm', '.png', '.jpg', '.jpeg'}:
            file_type = '🖼️ Immagine'
        else:
            file_type = '📎 Altro'
        
        # Get size
        size = file_path.stat().st_size
        if size < 1024:
            size_str = f"{size} B"
        elif size < 1024*1024:
            size_str = f"{size/1024:.1f} KB"
        else:
            size_str = f"{size/(1024*1024):.1f} MB"
        
        # Add to tree
        self.files_tree.insert(
            '',
            'end',
            text=file_path.name,
            values=(file_type, size_str)
        )
    
    def process_data(self):
        """Process the clinical file or folder."""
        if not self.current_folder and not self.current_file:
            messagebox.showwarning("Attenzione", "Seleziona prima una cartella o un file clinico")
            return
        
        # Disable button
        self.process_btn['state'] = 'disabled'
        self.status_var.set("Elaborazione in corso...")
        self.progress_var.set(0)
        
        # Clear results
        self.clear_results()
        
        # Process in thread
        thread = threading.Thread(target=self._process_thread)
        thread.daemon = True
        thread.start()
    
    def _process_thread(self):
        """Process file or folder in background thread."""
        try:
            self.log("🚀 Avvio elaborazione...")
            self.root.after(0, lambda: self.progress_var.set(10))
            
            # Process file or folder
            if self.is_single_file:
                decision_support = self.processor.process_single_file(self.current_file)
            else:
                decision_support = self.processor.process_folder(self.current_folder)
            
            self.root.after(0, lambda: self.progress_var.set(80))
            
            # Display results
            self.root.after(0, lambda: self.display_results(decision_support))
            
            self.root.after(0, lambda: self.progress_var.set(100))
            self.log("✅ Elaborazione completata con successo")
            
            # Re-enable button
            self.root.after(0, lambda: self.process_btn.configure(state='normal'))
            self.root.after(0, lambda: self.status_var.set("Elaborazione completata"))
            
        except Exception as e:
            self.log(f"❌ Errore elaborazione: {e}")
            self.root.after(0, lambda: messagebox.showerror("Errore", f"Errore durante l'elaborazione:\n{e}"))
            self.root.after(0, lambda: self.process_btn.configure(state='normal'))
            self.root.after(0, lambda: self.status_var.set("Errore elaborazione"))
            self.root.after(0, lambda: self.progress_var.set(0))
    
    def display_results(self, decision_support):
        """Display processing results."""
        # Diagnosis tab
        self.diagnosis_text['state'] = 'normal'
        self.diagnosis_text.delete(1.0, tk.END)
        
        diagnosis_output = f"""
═══════════════════════════════════════════════════════════════
  RISULTATI DIAGNOSI
═══════════════════════════════════════════════════════════════

🆔 Request ID: {decision_support.request_id}
👤 Paziente: {decision_support.patient_id}
⏱️  Tempo elaborazione: {decision_support.processing_time_ms:.2f}ms
🚨 Livello urgenza: {decision_support.urgency_level.value.upper()}
📈 Punteggio triage: {decision_support.triage_score:.1f}/100

"""
        
        if decision_support.diagnoses:
            diagnosis_output += f"\n💊 DIAGNOSI ({len(decision_support.diagnoses)}):\n"
            diagnosis_output += "─" * 60 + "\n"
            
            for i, diagnosis in enumerate(decision_support.diagnoses, 1):
                diagnosis_output += f"\n{i}. {diagnosis.condition}\n"
                diagnosis_output += f"   Confidenza: {diagnosis.confidence_score:.1%} ({diagnosis.confidence_level.value})\n"
                
                if diagnosis.evidence:
                    diagnosis_output += f"   Evidenze:\n"
                    for evidence in diagnosis.evidence[:5]:
                        diagnosis_output += f"   • {evidence}\n"
                
                if diagnosis.recommended_tests:
                    diagnosis_output += f"   Test raccomandati:\n"
                    for test in diagnosis.recommended_tests[:3]:
                        diagnosis_output += f"   • {test}\n"
                
                if diagnosis.recommended_specialists:
                    diagnosis_output += f"   Consulti specialistici:\n"
                    for specialist in diagnosis.recommended_specialists:
                        diagnosis_output += f"   • {specialist}\n"
                
                diagnosis_output += "\n"
        
        if decision_support.alerts:
            diagnosis_output += f"\n⚠️  ALERT CRITICI:\n"
            diagnosis_output += "─" * 60 + "\n"
            for alert in decision_support.alerts:
                diagnosis_output += f"• {alert}\n"
        
        if decision_support.warnings:
            diagnosis_output += f"\n⚡ AVVISI:\n"
            diagnosis_output += "─" * 60 + "\n"
            for warning in decision_support.warnings:
                diagnosis_output += f"• {warning}\n"
        
        self.diagnosis_text.insert(1.0, diagnosis_output)
        self.diagnosis_text['state'] = 'disabled'
        
        # Details tab
        self.details_text['state'] = 'normal'
        self.details_text.delete(1.0, tk.END)
        
        details_output = f"""
═══════════════════════════════════════════════════════════════
  DETTAGLI ELABORAZIONE
═══════════════════════════════════════════════════════════════

🤖 Modelli AI utilizzati:
{chr(10).join('• ' + model for model in decision_support.models_used)}

📊 Metadati processamento:
{json.dumps(decision_support.metadata, indent=2, ensure_ascii=False)}

"""
        
        if decision_support.clinical_notes:
            details_output += f"\n📝 Note Cliniche:\n"
            details_output += "─" * 60 + "\n"
            for note in decision_support.clinical_notes:
                details_output += f"• {note}\n"
        
        if decision_support.explanation:
            details_output += f"\n💡 Spiegazione:\n"
            details_output += "─" * 60 + "\n"
            details_output += decision_support.explanation + "\n"
        
        self.details_text.insert(1.0, details_output)
        self.details_text['state'] = 'disabled'
        
        # Store for export
        self.last_results = decision_support
    
    def clear_results(self):
        """Clear all result displays."""
        for text_widget in [self.diagnosis_text, self.details_text]:
            text_widget['state'] = 'normal'
            text_widget.delete(1.0, tk.END)
            text_widget['state'] = 'disabled'
    
    def log(self, message: str):
        """Add message to log."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        
        self.logs_text['state'] = 'normal'
        self.logs_text.insert(tk.END, log_entry)
        self.logs_text.see(tk.END)
        self.logs_text['state'] = 'disabled'
    
    def set_system_status(self, ready: bool):
        """Update system status indicator."""
        color = self.colors['success'] if ready else self.colors['danger']
        self.status_indicator.itemconfig(self.status_circle, fill=color)
    
    def create_template(self):
        """Create template folder."""
        folder = filedialog.askdirectory(title="Seleziona dove creare il template")
        
        if folder:
            try:
                self.processor.create_folder_template(folder)
                self.log(f"✅ Template creato in: {folder}")
                messagebox.showinfo("Successo", f"Template creato con successo in:\n{folder}")
            except Exception as e:
                self.log(f"❌ Errore creazione template: {e}")
                messagebox.showerror("Errore", f"Impossibile creare template:\n{e}")
    
    def export_results(self):
        """Export results to JSON."""
        if not hasattr(self, 'last_results'):
            messagebox.showwarning("Attenzione", "Nessun risultato da esportare")
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            initialfile=f"results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(self.last_results.to_dict(), f, indent=2, ensure_ascii=False)
                self.log(f"💾 Risultati esportati in: {file_path}")
                messagebox.showinfo("Successo", f"Risultati esportati in:\n{file_path}")
            except Exception as e:
                messagebox.showerror("Errore", f"Impossibile esportare risultati:\n{e}")
    
    def show_metrics(self):
        """Show system metrics."""
        if not self.metrics_observer:
            return
        
        metrics = self.metrics_observer.get_metrics()
        
        metrics_window = tk.Toplevel(self.root)
        metrics_window.title("Metriche Sistema")
        metrics_window.geometry("500x400")
        
        text = scrolledtext.ScrolledText(metrics_window, font=('Consolas', 9))
        text.pack(fill='both', expand=True, padx=10, pady=10)
        
        metrics_text = f"""
═══════════════════════════════════════════════════
  METRICHE SISTEMA
═══════════════════════════════════════════════════

Richieste elaborate: {metrics['requests_completed']}
Richieste fallite: {metrics['requests_failed']}
Success rate: {metrics['success_rate']:.1%}

Tempo medio elaborazione: {metrics['avg_processing_time_ms']:.2f}ms
Tempo minimo: {metrics['min_processing_time_ms']:.2f}ms
Tempo massimo: {metrics['max_processing_time_ms']:.2f}ms

Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        text.insert(1.0, metrics_text)
        text['state'] = 'disabled'
    
    def show_config(self):
        """Show configuration."""
        messagebox.showinfo("Configurazione", "Funzionalità configurazione in sviluppo")
    
    def show_audit_log(self):
        """Show audit log."""
        messagebox.showinfo("Log Audit", "Funzionalità log audit in sviluppo")
    
    def show_docs(self):
        """Show documentation."""
        docs_window = tk.Toplevel(self.root)
        docs_window.title("Documentazione")
        docs_window.geometry("700x500")
        
        text = scrolledtext.ScrolledText(docs_window, font=('Segoe UI', 10), wrap='word')
        text.pack(fill='both', expand=True, padx=10, pady=10)
        
        docs_text = """
═══════════════════════════════════════════════════════════════
  EARLYCARE GATEWAY - GUIDA RAPIDA
═══════════════════════════════════════════════════════════════

INTRODUZIONE
EarlyCare Gateway è un sistema di supporto alle decisioni cliniche che
elabora cartelle cliniche complete per fornire diagnosi assistite da AI.

STRUTTURA CARTELLA CLINICA
Una cartella clinica deve contenere:

📁 cartella_paziente/
├── patient_info.json          # Info demografiche (opzionale)
├── notes/                     # Note cliniche (.txt, .md)
├── signals/                   # Dati segnale (.csv, .json)
└── images/                    # Immagini mediche (.dcm, .png, .jpg)

UTILIZZO
1. Seleziona una cartella clinica tramite "File > Apri Cartella Clinica"
2. Verifica le informazioni del paziente e i file rilevati
3. Clicca "Elabora Cartella Clinica"
4. Visualizza i risultati nei tab Diagnosi, Dettagli, Log
5. Esporta i risultati tramite "File > Esporta Risultati"

CREAZIONE TEMPLATE
Per creare una cartella template di esempio:
1. Vai su "File > Crea Template"
2. Seleziona una cartella di destinazione
3. Modifica i file del template con i dati reali
4. Elabora la cartella

SUPPORTO
Per maggiori informazioni consulta README.md e ARCHITECTURE.md
nella directory del progetto.
"""
        text.insert(1.0, docs_text)
        text['state'] = 'disabled'
    
    def show_about(self):
        """Show about dialog."""
        messagebox.showinfo(
            "Informazioni",
            "EarlyCare Gateway v1.0\n\n"
            "Clinical Decision Support System\n"
            "basato su Design Patterns e AI\n\n"
            "© 2025 - MIT License"
        )
    
    def open_patient_form(self):
        """Open patient data entry form."""
        def on_patient_saved(patient_data, file_path=None):
            """Callback when patient data is saved."""
            fiscal_code = patient_data.get('fiscal_code', patient_data.get('patient_id', ''))
            self.log(f"📝 Dati paziente inseriti: {fiscal_code}")
            
            # Save to MongoDB if available
            if self.db_connected and self.db:
                try:
                    # Check if patient already exists by fiscal code
                    existing_patient = self.db.get_patient(fiscal_code)
                    
                    if existing_patient:
                        # Patient exists - add new record to their clinical folder
                        self.log(f"ℹ Paziente già presente nel database: {fiscal_code}")
                        self.log(f"📁 Aggiungo nuova scheda alla cartella clinica esistente...")
                        
                        # Create PatientRecord with new clinical data
                        from src.models.patient import PatientRecord
                        from src.models.clinical_data import TextData, DataType, DataSource
                        import uuid
                        
                        # Create clinical data from form
                        clinical_data = []
                        
                        # Add chief complaint as clinical data
                        chief_complaint = patient_data.get('chief_complaint', '')
                        if chief_complaint:
                            chief_complaint_data = TextData(
                                data_id=str(uuid.uuid4()),
                                patient_id=fiscal_code,
                                timestamp=datetime.now(),
                                source=DataSource.MANUAL,
                                text_content=chief_complaint,
                                language='it',
                                document_type='chief_complaint'
                            )
                            clinical_data.append(chief_complaint_data)
                        
                        # Add vital signs if present
                        vital_signs = patient_data.get('vital_signs', {})
                        if any(vital_signs.values()):
                            vital_text = "Parametri Vitali:\n"
                            if vital_signs.get('blood_pressure'):
                                vital_text += f"- Pressione: {vital_signs['blood_pressure']}\n"
                            if vital_signs.get('heart_rate'):
                                vital_text += f"- Freq. Cardiaca: {vital_signs['heart_rate']} bpm\n"
                            if vital_signs.get('temperature'):
                                vital_text += f"- Temperatura: {vital_signs['temperature']} °C\n"
                            if vital_signs.get('respiratory_rate'):
                                vital_text += f"- Freq. Respiratoria: {vital_signs['respiratory_rate']} atti/min\n"
                            if vital_signs.get('spo2'):
                                vital_text += f"- SpO2: {vital_signs['spo2']}%\n"
                            
                            vital_data = TextData(
                                data_id=str(uuid.uuid4()),
                                patient_id=fiscal_code,
                                timestamp=datetime.now(),
                                source=DataSource.MANUAL,
                                text_content=vital_text,
                                language='it',
                                document_type='vital_signs'
                            )
                            clinical_data.append(vital_data)
                        
                        # Create new patient record
                        new_record = PatientRecord(
                            patient=existing_patient,
                            clinical_data=clinical_data,
                            encounter_id=str(uuid.uuid4()),
                            encounter_timestamp=datetime.now(),
                            priority='routine',
                            chief_complaint=patient_data.get('chief_complaint', ''),
                            current_medications=patient_data.get('medications', []),
                            metadata={
                                'source': 'GUI Manual Entry',
                                'entry_date': datetime.now().isoformat(),
                                'vital_signs': vital_signs
                            }
                        )
                        
                        # Save patient record
                        if self.db.save_patient_record(new_record):
                            self.log(f"✓ Nuova scheda aggiunta alla cartella clinica del paziente")
                        else:
                            self.log(f"⚠ Errore nel salvare la nuova scheda clinica")
                    
                    else:
                        # Patient doesn't exist - create new patient
                        self.log(f"🆕 Nuovo paziente - creo record nel database...")
                        
                        # Convert patient_data to Patient object
                        patient = self.convert_form_data_to_patient(patient_data)
                        
                        # Save to database
                        if self.db.save_patient(patient):
                            self.log(f"✓ Nuovo paziente salvato nel database MongoDB")
                            
                            # Also create first patient record
                            from src.models.patient import PatientRecord
                            from src.models.clinical_data import TextData, DataType, DataSource
                            import uuid
                            
                            # Create clinical data from form
                            clinical_data = []
                            
                            # Add chief complaint
                            chief_complaint = patient_data.get('chief_complaint', '')
                            if chief_complaint:
                                chief_complaint_data = TextData(
                                    data_id=str(uuid.uuid4()),
                                    patient_id=fiscal_code,
                                    timestamp=datetime.now(),
                                    source=DataSource.MANUAL,
                                    text_content=chief_complaint,
                                    language='it',
                                    document_type='chief_complaint'
                                )
                                clinical_data.append(chief_complaint_data)
                            
                            # Add vital signs if present
                            vital_signs = patient_data.get('vital_signs', {})
                            if any(vital_signs.values()):
                                vital_text = "Parametri Vitali:\n"
                                if vital_signs.get('blood_pressure'):
                                    vital_text += f"- Pressione: {vital_signs['blood_pressure']}\n"
                                if vital_signs.get('heart_rate'):
                                    vital_text += f"- Freq. Cardiaca: {vital_signs['heart_rate']} bpm\n"
                                if vital_signs.get('temperature'):
                                    vital_text += f"- Temperatura: {vital_signs['temperature']} °C\n"
                                if vital_signs.get('respiratory_rate'):
                                    vital_text += f"- Freq. Respiratoria: {vital_signs['respiratory_rate']} atti/min\n"
                                if vital_signs.get('spo2'):
                                    vital_text += f"- SpO2: {vital_signs['spo2']}%\n"
                                
                                vital_data = TextData(
                                    data_id=str(uuid.uuid4()),
                                    patient_id=fiscal_code,
                                    timestamp=datetime.now(),
                                    source=DataSource.MANUAL,
                                    text_content=vital_text,
                                    language='it',
                                    document_type='vital_signs'
                                )
                                clinical_data.append(vital_data)
                            
                            # Create initial patient record
                            initial_record = PatientRecord(
                                patient=patient,
                                clinical_data=clinical_data,
                                encounter_id=str(uuid.uuid4()),
                                encounter_timestamp=datetime.now(),
                                priority='routine',
                                chief_complaint=patient_data.get('chief_complaint', ''),
                                current_medications=patient_data.get('medications', []),
                                metadata={
                                    'source': 'GUI Manual Entry',
                                    'entry_date': datetime.now().isoformat(),
                                    'vital_signs': vital_signs,
                                    'initial_record': True
                                }
                            )
                            
                            # Save initial patient record
                            if self.db.save_patient_record(initial_record):
                                self.log(f"✓ Cartella clinica iniziale creata")
                        else:
                            self.log(f"⚠ Errore nel salvataggio del nuovo paziente")
                            
                except Exception as e:
                    self.log(f"❌ Errore salvando paziente nel database: {e}")
                    import traceback
                    traceback.print_exc()
                    messagebox.showwarning(
                        "Avviso Database",
                        f"Impossibile salvare nel database MongoDB:\n{e}\n\nI dati sono comunque disponibili per l'elaborazione."
                    )
            
            if file_path:
                # If exported to file, load that folder
                folder_path = Path(file_path).parent
                self.current_folder = str(folder_path)
                self.current_file = None
                self.is_single_file = False
                self.folder_var.set(str(folder_path))
                
                # Display patient info
                self.display_manual_patient_info(patient_data)
                
                # Check for other files in the folder
                self.scan_folder_files(str(folder_path))
                
                self.process_btn_text.set("🚀 Elabora Cartella Clinica")
                self.process_btn['state'] = 'normal'
                self.status_var.set(f"Paziente caricato: {patient_data['patient_id']}")
            else:
                # If not exported, just display the info
                self.display_manual_patient_info(patient_data)
                self.status_var.set(f"Dati paziente inseriti: {patient_data['patient_id']}")
        
        # Open form dialog
        form = PatientFormDialog(self.root, callback=on_patient_saved)
    
    def convert_form_data_to_patient(self, patient_data):
        """
        Convert form data dictionary to Patient object.
        
        Args:
            patient_data: Dictionary with patient data from form
            
        Returns:
            Patient object
        """
        # Parse date of birth
        dob_str = patient_data.get('data_nascita', patient_data.get('date_of_birth', ''))
        try:
            # Try format YYYY-MM-DD
            if '-' in dob_str:
                dob = datetime.strptime(dob_str, '%Y-%m-%d')
            # Try format DD/MM/YYYY
            elif '/' in dob_str:
                dob = datetime.strptime(dob_str, '%d/%m/%Y')
            else:
                dob = datetime.now()
        except:
            dob = datetime.now()
        
        # Map gender
        gender_map = {
            'M': Gender.MALE,
            'F': Gender.FEMALE,
            'Altro': Gender.OTHER
        }
        gender_value = gender_map.get(patient_data.get('gender', 'M'), Gender.UNKNOWN)
        
        # Create Patient object with new fields
        patient = Patient(
            patient_id=patient_data.get('patient_id', ''),
            nome=patient_data.get('nome', ''),
            cognome=patient_data.get('cognome', ''),
            data_nascita=dob,
            comune_nascita=patient_data.get('comune_nascita', ''),
            codice_fiscale=patient_data.get('codice_fiscale', ''),
            data_decesso=None,  # Optional
            allergie=patient_data.get('allergie', []),
            malattie_permanenti=patient_data.get('malattie_permanenti', []),
            gender=gender_value,
            medical_record_number=patient_data.get('medical_record_number', ''),
            age=None,  # Will be calculated
            ethnicity=None,
            primary_language='it'
        )
        
        # Calculate age
        patient.calculate_age()
        
        return patient
    
    def display_manual_patient_info(self, patient_data):
        """Display manually entered patient information."""
        self.patient_info_text['state'] = 'normal'
        self.patient_info_text.delete(1.0, tk.END)
        
        # Format full name
        full_name = ""
        nome = patient_data.get('nome', patient_data.get('name', ''))
        cognome = patient_data.get('cognome', patient_data.get('surname', ''))
        
        if nome and cognome:
            full_name = f"{nome} {cognome}"
        elif nome:
            full_name = nome
        elif cognome:
            full_name = cognome
        
        codice_fiscale = patient_data.get('codice_fiscale', patient_data.get('fiscal_code', 'N/A'))
        info_text = f"""Codice Fiscale: {codice_fiscale}"""
        
        if full_name:
            info_text += f"\nNome: {full_name}"
        
        comune_nascita = patient_data.get('comune_nascita', patient_data.get('birthplace', ''))
        if comune_nascita:
            info_text += f"\nLuogo di Nascita: {comune_nascita}"
        
        data_nascita = patient_data.get('data_nascita', patient_data.get('date_of_birth', 'N/A'))
        info_text += f"""
Data di Nascita: {data_nascita}
Sesso: {patient_data.get('gender', 'N/A')}
Sintomo Principale: {patient_data.get('chief_complaint', 'N/A')}

Storia Clinica:
"""
        for h in patient_data.get('medical_history', []):
            info_text += f"• {h}\n"
        
        info_text += "\nFarmaci Attuali:\n"
        for m in patient_data.get('medications', []):
            info_text += f"• {m}\n"
        
        allergie = patient_data.get('allergie', patient_data.get('allergies', []))
        info_text += "\nAllergie:\n"
        for a in allergie:
            info_text += f"• {a}\n"
        
        malattie = patient_data.get('malattie_permanenti', [])
        if malattie:
            info_text += "\nMalattie Permanenti:\n"
            for m in malattie:
                info_text += f"• {m}\n"
        
        # Add vital signs if present
        vitals = patient_data.get('vital_signs', {})
        if any(vitals.values()):
            info_text += "\nParametri Vitali:\n"
            if vitals.get('blood_pressure'):
                info_text += f"• Pressione: {vitals['blood_pressure']} mmHg\n"
            if vitals.get('heart_rate'):
                info_text += f"• Frequenza Cardiaca: {vitals['heart_rate']} bpm\n"
            if vitals.get('temperature'):
                info_text += f"• Temperatura: {vitals['temperature']} °C\n"
            if vitals.get('respiratory_rate'):
                info_text += f"• Frequenza Respiratoria: {vitals['respiratory_rate']} atti/min\n"
            if vitals.get('spo2'):
                info_text += f"• SpO2: {vitals['spo2']}%\n"
        
        self.patient_info_text.insert(1.0, info_text)
        self.patient_info_text['state'] = 'disabled'
    
    def export_patient_records(self):
        """Export patient clinical records to ZIP file."""
        # Check if database is connected
        if not self.db_connected or not self.db:
            messagebox.showwarning(
                "Database Non Connesso",
                "Impossibile esportare: database MongoDB non connesso.\n\n"
                "Assicurati che il database sia configurato correttamente."
            )
            return
        
        # Create dialog to ask for fiscal code
        dialog = tk.Toplevel(self.root)
        dialog.title("Export Cartella Clinica")
        dialog.geometry("500x180")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Center dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (500 // 2)
        y = (dialog.winfo_screenheight() // 2) - (180 // 2)
        dialog.geometry(f"+{x}+{y}")
        
        # Content frame
        content = ttk.Frame(dialog, padding=20)
        content.pack(fill='both', expand=True)
        
        # Title
        title_label = ttk.Label(
            content,
            text="📥 Export Cartella Clinica",
            font=('Segoe UI', 12, 'bold')
        )
        title_label.pack(pady=(0, 15))
        
        # Fiscal code input
        ttk.Label(content, text="Codice Fiscale del Paziente:").pack(anchor='w', pady=(0, 5))
        fiscal_code_var = tk.StringVar()
        fiscal_code_entry = ttk.Entry(content, textvariable=fiscal_code_var, width=40)
        fiscal_code_entry.pack(fill='x', pady=(0, 20))
        fiscal_code_entry.focus()
        
        # Buttons frame
        button_frame = ttk.Frame(content)
        button_frame.pack(fill='x')
        
        def do_export():
            fiscal_code = fiscal_code_var.get().strip().upper()
            
            if not fiscal_code:
                messagebox.showerror("Errore", "Inserire il codice fiscale del paziente", parent=dialog)
                return
            
            dialog.destroy()
            self._export_patient_to_zip(fiscal_code)
        
        def cancel():
            dialog.destroy()
        
        # Export button
        export_button = ttk.Button(
            button_frame,
            text="📥 Export",
            command=do_export,
            style='Success.TButton'
        )
        export_button.pack(side='left', padx=(0, 5))
        
        # Cancel button
        cancel_button = ttk.Button(
            button_frame,
            text="❌ Annulla",
            command=cancel
        )
        cancel_button.pack(side='left')
        
        # Bind Enter key to export
        dialog.bind('<Return>', lambda e: do_export())
        dialog.bind('<Escape>', lambda e: cancel())
    
    def _export_patient_to_zip(self, fiscal_code: str):
        """
        Export patient records to ZIP file.
        
        Args:
            fiscal_code: Patient fiscal code
        """
        try:
            self.log(f"🔍 Ricerca paziente: {fiscal_code}")
            
            # Get patient from database
            patient = self.db.get_patient(fiscal_code)
            if not patient:
                messagebox.showerror(
                    "Paziente Non Trovato",
                    f"Nessun paziente trovato con codice fiscale: {fiscal_code}"
                )
                self.log(f"❌ Paziente non trovato: {fiscal_code}")
                return
            
            # Get all patient records
            records = self.db.get_patient_records(fiscal_code, limit=1000)
            if not records:
                messagebox.showwarning(
                    "Nessuna Scheda",
                    f"Paziente trovato ma senza schede cliniche.\n\n"
                    f"Codice Fiscale: {fiscal_code}"
                )
                self.log(f"⚠ Nessuna scheda clinica per: {fiscal_code}")
                return
            
            self.log(f"✓ Trovato paziente con {len(records)} schede cliniche")
            
            # Ask where to save
            default_filename = f"cartella_clinica_{fiscal_code}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
            zip_path = filedialog.asksaveasfilename(
                defaultextension=".zip",
                filetypes=[("ZIP files", "*.zip"), ("All files", "*.*")],
                initialfile=default_filename,
                title="Salva Cartella Clinica"
            )
            
            if not zip_path:
                self.log("⊘ Export annullato dall'utente")
                return
            
            # Create ZIP file
            import zipfile
            import tempfile
            
            self.log(f"📦 Creazione archivio ZIP: {Path(zip_path).name}")
            
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # Add patient info
                patient_info = {
                    "patient_id": patient.patient_id,
                    "medical_record_number": patient.medical_record_number,
                    "date_of_birth": patient.date_of_birth.isoformat(),
                    "gender": patient.gender.value,
                    "age": patient.age,
                    "primary_language": patient.primary_language,
                    "medical_history": patient.medical_history,
                    "allergies_and_diseases": patient.allergies_and_diseases,
                    "export_date": datetime.now().isoformat(),
                    "total_records": len(records)
                }
                
                zipf.writestr(
                    "patient_info.json",
                    json.dumps(patient_info, indent=2, ensure_ascii=False, default=str)
                )
                
                # Add each patient record
                for idx, record in enumerate(records, 1):
                    # Format date from encounter_timestamp
                    encounter_date = record.get("encounter_timestamp")
                    if encounter_date:
                        date_str = encounter_date.strftime('%d-%m-%Y_%H-%M-%S')
                    else:
                        date_str = "unknown_date"
                    
                    record_filename = f"scheda_{idx:03d}_{date_str}.json"
                    
                    # Clean record for JSON serialization
                    record_clean = {
                        "encounter_id": record.get("encounter_id"),
                        "encounter_timestamp": record.get("encounter_timestamp").isoformat() if record.get("encounter_timestamp") else None,
                        "priority": record.get("priority"),
                        "chief_complaint": record.get("chief_complaint"),
                        "current_medications": record.get("current_medications", []),
                        "clinical_data": record.get("clinical_data", []),
                        "metadata": record.get("metadata", {}),
                        "processing_context": record.get("processing_context", {})
                    }
                    
                    zipf.writestr(
                        f"records/{record_filename}",
                        json.dumps(record_clean, indent=2, ensure_ascii=False, default=str)
                    )
                
                # Add summary
                summary = {
                    "patient_id": fiscal_code,
                    "export_date": datetime.now().isoformat(),
                    "total_records": len(records),
                    "records_list": [
                        {
                            "number": idx,
                            "encounter_id": rec.get("encounter_id"),
                            "date": rec.get("encounter_timestamp").isoformat() if rec.get("encounter_timestamp") else None,
                            "priority": rec.get("priority"),
                            "chief_complaint": rec.get("chief_complaint")
                        }
                        for idx, rec in enumerate(records, 1)
                    ]
                }
                
                zipf.writestr(
                    "README.json",
                    json.dumps(summary, indent=2, ensure_ascii=False, default=str)
                )
            
            self.log(f"✓ Export completato: {Path(zip_path).name}")
            self.log(f"  • {len(records)} schede cliniche esportate")
            
            messagebox.showinfo(
                "Export Completato",
                f"Cartella clinica esportata con successo!\n\n"
                f"Paziente: {fiscal_code}\n"
                f"Schede: {len(records)}\n"
                f"File: {Path(zip_path).name}"
            )
            
        except Exception as e:
            self.log(f"❌ Errore durante export: {e}")
            import traceback
            traceback.print_exc()
            messagebox.showerror(
                "Errore Export",
                f"Si è verificato un errore durante l'export:\n\n{e}"
            )
    
    def search_patient(self):
        """Search and display patient information and records."""
        fiscal_code = self.search_fiscal_code_var.get().strip().upper()
        
        if not fiscal_code:
            messagebox.showwarning("Attenzione", "Inserire il codice fiscale del paziente")
            return
        
        # Check if database is connected
        if not self.db_connected or not self.db:
            messagebox.showwarning(
                "Database Non Connesso",
                "Impossibile cercare: database MongoDB non connesso.\n\n"
                "Assicurati che il database sia configurato correttamente."
            )
            return
        
        try:
            self.log(f"🔍 Ricerca paziente: {fiscal_code}")
            
            # Get patient from database
            patient = self.db.get_patient(fiscal_code)
            if not patient:
                messagebox.showinfo(
                    "Paziente Non Trovato",
                    f"Nessun paziente trovato con codice fiscale: {fiscal_code}"
                )
                self.log(f"❌ Paziente non trovato: {fiscal_code}")
                return
            
            # Get all patient records
            records = self.db.get_patient_records(fiscal_code, limit=1000)
            
            self.log(f"✓ Paziente trovato con {len(records)} schede cliniche")
            
            # Create search results window
            self._show_patient_details_window(patient, records)
            
        except Exception as e:
            self.log(f"❌ Errore durante ricerca: {e}")
            import traceback
            traceback.print_exc()
            messagebox.showerror(
                "Errore Ricerca",
                f"Si è verificato un errore durante la ricerca:\n\n{e}"
            )
    
    def _show_patient_details_window(self, patient, records):
        """
        Show patient details and records in a dedicated window.
        
        Args:
            patient: Patient object
            records: List of patient records
        """
        # Create new window
        details_window = tk.Toplevel(self.root)
        details_window.title(f"📋 Cartella Clinica - {patient.patient_id}")
        details_window.geometry("1000x700")
        
        # Main container
        main_container = ttk.Frame(details_window, padding=20)
        main_container.pack(fill='both', expand=True)
        
        # Title
        title_label = ttk.Label(
            main_container,
            text=f"📋 Cartella Clinica Paziente",
            font=('Segoe UI', 14, 'bold')
        )
        title_label.pack(pady=(0, 15))
        
        # Patient info section
        info_frame = ttk.LabelFrame(main_container, text="👤 Dati Paziente", padding=15)
        info_frame.pack(fill='x', pady=(0, 15))
        
        # Patient info text with scrollbar
        info_text_frame = ttk.Frame(info_frame)
        info_text_frame.pack(fill='both', expand=True)
        
        info_scrollbar = ttk.Scrollbar(info_text_frame, orient="vertical")
        info_scrollbar.pack(side='right', fill='y')
        
        info_text = tk.Text(
            info_text_frame, 
            height=8, 
            wrap='word', 
            font=('Consolas', 10),
            yscrollcommand=info_scrollbar.set
        )
        info_text.pack(side='left', fill='both', expand=True)
        info_scrollbar.config(command=info_text.yview)
        
        patient_info = f"""Codice Fiscale: {patient.patient_id}
MRN: {patient.medical_record_number}
Data di Nascita: {patient.date_of_birth.strftime('%d/%m/%Y')}
Età: {patient.age if patient.age else 'N/A'} anni
Sesso: {patient.gender.value}
Lingua: {patient.primary_language}

Storia Clinica:
"""
        for h in patient.medical_history:
            patient_info += f"  • {h}\n"
        
        patient_info += "\nAllergie e Malattie:\n"
        for a in patient.allergies_and_diseases:
            patient_info += f"  • {a}\n"
        
        info_text.insert('1.0', patient_info)
        info_text.config(state='disabled')
        
        # Records section
        records_frame = ttk.LabelFrame(main_container, text=f"📁 Schede Cliniche ({len(records)})", padding=15)
        records_frame.pack(fill='both', expand=True)
        
        # Create canvas with horizontal scrollbar for records
        canvas = tk.Canvas(records_frame)
        h_scrollbar = ttk.Scrollbar(records_frame, orient="horizontal", command=canvas.xview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(xscrollcommand=h_scrollbar.set)
        
        canvas.pack(side="top", fill="both", expand=True)
        h_scrollbar.pack(side="bottom", fill="x")
        
        # Display each record horizontally
        if records:
            for idx, record in enumerate(records, 1):
                # Container for each record card
                record_container = ttk.Frame(scrollable_frame)
                record_container.pack(side='left', fill='both', expand=True, padx=5, pady=5)
                
                record_frame = ttk.LabelFrame(
                    record_container,
                    text=f"Scheda #{idx}",
                    padding=10
                )
                record_frame.pack(fill='both', expand=True)
                
                # Record details with vertical scrollbar
                encounter_date = record.get('encounter_timestamp')
                date_str = encounter_date.strftime('%d/%m/%Y %H:%M:%S') if encounter_date else 'N/A'
                
                # Text widget with its own scrollbar
                text_scroll_frame = ttk.Frame(record_frame)
                text_scroll_frame.pack(fill='both', expand=True)
                
                record_scrollbar = ttk.Scrollbar(text_scroll_frame, orient="vertical")
                record_scrollbar.pack(side='right', fill='y')
                
                record_text = tk.Text(
                    text_scroll_frame, 
                    height=25, 
                    width=60,
                    wrap='word', 
                    font=('Consolas', 9),
                    yscrollcommand=record_scrollbar.set
                )
                record_text.pack(side='left', fill='both', expand=True)
                record_scrollbar.config(command=record_text.yview)
                
                # Build comprehensive record info
                record_info = f"""═══════════════════════════════════════════════════════════════
INFORMAZIONI SCHEDA
═══════════════════════════════════════════════════════════════
Data Visita:        {date_str}
Encounter ID:       {record.get('encounter_id', 'N/A')}
Priorità:           {record.get('priority', 'N/A').upper()}

───────────────────────────────────────────────────────────────
DATI PAZIENTE (snapshot al momento della visita)
───────────────────────────────────────────────────────────────
"""
                # Patient snapshot data
                patient_snapshot = record.get('patient', {})
                if patient_snapshot:
                    dob = patient_snapshot.get('date_of_birth')
                    if dob:
                        dob_str = dob.strftime('%d/%m/%Y') if hasattr(dob, 'strftime') else str(dob)
                    else:
                        dob_str = 'N/A'
                    
                    record_info += f"""Codice Fiscale:     {patient_snapshot.get('patient_id', 'N/A')}
Data Nascita:       {dob_str}
Età:                {patient_snapshot.get('age', 'N/A')} anni
Sesso:              {patient_snapshot.get('gender', 'N/A')}
MRN:                {patient_snapshot.get('medical_record_number', 'N/A')}
Lingua:             {patient_snapshot.get('primary_language', 'N/A')}

Storia Clinica:
"""
                    medical_history = patient_snapshot.get('medical_history', [])
                    if medical_history:
                        for h in medical_history:
                            record_info += f"  • {h}\n"
                    else:
                        record_info += "  Nessuna\n"
                    
                    record_info += "\nAllergie e Malattie:\n"
                    allergies = patient_snapshot.get('allergies_and_diseases', [])
                    if allergies:
                        for a in allergies:
                            record_info += f"  • {a}\n"
                    else:
                        record_info += "  Nessuna\n"
                
                record_info += """
───────────────────────────────────────────────────────────────
DATI VISITA
───────────────────────────────────────────────────────────────
Sintomo Principale:
  """
                record_info += record.get('chief_complaint', 'N/A') + "\n"
                
                record_info += "\nFarmaci Attuali:\n"
                medications = record.get('current_medications', [])
                if medications:
                    for med in medications:
                        record_info += f"  • {med}\n"
                else:
                    record_info += "  Nessuno\n"
                
                # Clinical data
                record_info += "\n───────────────────────────────────────────────────────────────\n"
                record_info += "DATI CLINICI\n"
                record_info += "───────────────────────────────────────────────────────────────\n"
                
                clinical_data = record.get('clinical_data', [])
                if clinical_data:
                    for idx_data, data in enumerate(clinical_data, 1):
                        data_type = data.get('data_type', 'unknown')
                        doc_type = data.get('document_type', 'N/A')
                        timestamp = data.get('timestamp')
                        if timestamp:
                            ts_str = timestamp.strftime('%d/%m/%Y %H:%M:%S') if hasattr(timestamp, 'strftime') else str(timestamp)
                        else:
                            ts_str = 'N/A'
                        
                        record_info += f"\n[{idx_data}] Tipo: {data_type} | Documento: {doc_type} | Data: {ts_str}\n"
                        
                        if data_type == 'text':
                            content = data.get('text_content', '')
                            record_info += f"    {content}\n"
                        elif data_type == 'signal':
                            signal_type = data.get('signal_type', 'N/A')
                            sampling_rate = data.get('sampling_rate', 'N/A')
                            duration = data.get('duration', 'N/A')
                            record_info += f"    Tipo Segnale: {signal_type}\n"
                            record_info += f"    Frequenza: {sampling_rate} Hz | Durata: {duration}s\n"
                        elif data_type == 'image':
                            modality = data.get('modality', 'N/A')
                            body_part = data.get('body_part', 'N/A')
                            record_info += f"    Modalità: {modality} | Parte: {body_part}\n"
                else:
                    record_info += "  Nessun dato clinico presente\n"
                
                # Metadata
                metadata = record.get('metadata', {})
                if metadata:
                    record_info += "\n───────────────────────────────────────────────────────────────\n"
                    record_info += "METADATI\n"
                    record_info += "───────────────────────────────────────────────────────────────\n"
                    for key, value in metadata.items():
                        if key not in ['processing_context']:  # Skip complex nested data
                            record_info += f"  {key}: {value}\n"
                
                record_info += "\n═══════════════════════════════════════════════════════════════\n"
                
                record_text.insert('1.0', record_info)
                record_text.config(state='disabled')
        else:
            no_records_label = ttk.Label(
                scrollable_frame,
                text="Nessuna scheda clinica presente",
                font=('Segoe UI', 10, 'italic'),
                foreground='gray'
            )
            no_records_label.pack(pady=20)
        
        # Close button
        close_btn = ttk.Button(
            main_container,
            text="Chiudi",
            command=details_window.destroy
        )
        close_btn.pack(pady=(15, 0))
        
        # Bind mouse wheel for scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)


def main():
    """Main entry point."""
    root = tk.Tk()
    app = EarlyCareGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
