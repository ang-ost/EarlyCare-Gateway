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
from gui.patient_form import PatientFormDialog


class EarlyCareGUI:
    """Main GUI application for EarlyCare Gateway."""
    
    def __init__(self, root):
        self.root = root
        self.root.title("🏥 EarlyCare Gateway - Clinical Decision Support System")
        self.root.geometry("1200x800")
        
        # Initialize gateway
        self.gateway = None
        self.processor = None
        self.metrics_observer = None
        self.current_folder = None
        self.current_file = None
        self.is_single_file = False
        
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
            text="🏥 EarlyCare Gateway",
            style='Header.TLabel'
        )
        title_label.pack(side='left', padx=20, pady=20)
        
        # Subtitle
        subtitle_label = ttk.Label(
            header,
            text="Clinical Decision Support System",
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
        
        select_folder_btn = ttk.Button(
            folder_frame,
            text="Seleziona Cartella",
            command=self.select_folder,
            style='Primary.TButton'
        )
        select_folder_btn.pack(side='right', padx=(10, 0))
        
        select_file_btn = ttk.Button(
            folder_frame,
            text="Seleziona File",
            command=self.select_file,
            style='Primary.TButton'
        )
        select_file_btn.pack(side='right', padx=(5, 0))
        
        # New Patient button
        new_patient_btn = ttk.Button(
            folder_frame,
            text="📝 Nuovo Paziente",
            command=self.open_patient_form,
            style='Primary.TButton'
        )
        new_patient_btn.pack(side='right', padx=(5, 0))
        
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
            self.log(f"📝 Dati paziente inseriti: {patient_data['patient_id']}")
            
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
                
                messagebox.showinfo(
                    "Informazione",
                    "Dati paziente inseriti.\n\n"
                    "Per procedere con la diagnosi, aggiungi:\n"
                    "• File clinici (note, segnali, immagini)\n"
                    "• Oppure seleziona una cartella clinica esistente"
                )
        
        # Open form dialog
        form = PatientFormDialog(self.root, callback=on_patient_saved)
    
    def display_manual_patient_info(self, patient_data):
        """Display manually entered patient information."""
        self.patient_info_text['state'] = 'normal'
        self.patient_info_text.delete(1.0, tk.END)
        
        # Format full name
        full_name = ""
        if patient_data.get('name') and patient_data.get('surname'):
            full_name = f"{patient_data['name']} {patient_data['surname']}"
        elif patient_data.get('name'):
            full_name = patient_data['name']
        elif patient_data.get('surname'):
            full_name = patient_data['surname']
        
        info_text = f"""Codice Fiscale: {patient_data.get('fiscal_code', 'N/A')}"""
        
        if full_name:
            info_text += f"\nNome: {full_name}"
        
        if patient_data.get('birthplace'):
            info_text += f"\nLuogo di Nascita: {patient_data['birthplace']}"
        
        info_text += f"""
Data di Nascita: {patient_data.get('date_of_birth', 'N/A')}
Sesso: {patient_data.get('gender', 'N/A')}
Sintomo Principale: {patient_data.get('chief_complaint', 'N/A')}

Storia Clinica:
"""
        for h in patient_data.get('medical_history', []):
            info_text += f"• {h}\n"
        
        info_text += "\nFarmaci Attuali:\n"
        for m in patient_data.get('medications', []):
            info_text += f"• {m}\n"
        
        info_text += "\nAllergie:\n"
        for a in patient_data.get('allergies', []):
            info_text += f"• {a}\n"
        
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


def main():
    """Main entry point."""
    root = tk.Tk()
    app = EarlyCareGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
