"""
Clinical Record Form - Form per aggiungere una scheda clinica (episodio clinico)
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from pathlib import Path
import json
from typing import Optional, Dict, Any


class ClinicalRecordDialog:
    """Dialog per creare una nuova scheda clinica per un paziente."""
    
    def __init__(self, parent, patient_info: Optional[Dict[str, Any]] = None, callback=None):
        """
        Initialize clinical record dialog.
        
        Args:
            parent: Parent window
            patient_info: Patient information dictionary
            callback: Function to call with record data when saved
        """
        self.parent = parent
        self.patient_info = patient_info
        self.callback = callback
        self.result = None
        
        # Create dialog window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("📋 Nuova Scheda Clinica")
        self.dialog.geometry("800x900")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (800 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (900 // 2)
        self.dialog.geometry(f"+{x}+{y}")
        
        # Create form
        self.create_form()
    
    def create_form(self):
        """Create the clinical record form."""
        # Main container with scrollbar
        main_frame = ttk.Frame(self.dialog, padding=20)
        main_frame.pack(fill='both', expand=True)
        
        # Canvas for scrolling
        canvas = tk.Canvas(main_frame)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Form title
        title_label = ttk.Label(
            scrollable_frame,
            text="📋 Nuova Scheda Clinica",
            font=('Segoe UI', 16, 'bold')
        )
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 10))
        
        row = 1
        
        # Patient info section (if available)
        if self.patient_info:
            patient_frame = ttk.LabelFrame(scrollable_frame, text="👤 Informazioni Paziente", padding=10)
            patient_frame.grid(row=row, column=0, columnspan=2, sticky='ew', pady=(0, 20))
            
            info_text = f"""
Nome: {self.patient_info.get('nome', '')} {self.patient_info.get('cognome', '')}
Codice Fiscale: {self.patient_info.get('codice_fiscale', '')}
Data di Nascita: {self.patient_info.get('data_nascita', '')}
            """.strip()
            
            ttk.Label(
                patient_frame,
                text=info_text,
                font=('Segoe UI', 10),
                justify='left'
            ).pack(anchor='w')
            
            row += 1
        
        # ==== TIPO DI EPISODIO ====
        ttk.Label(
            scrollable_frame,
            text="Tipo di Episodio *:",
            font=('Segoe UI', 11, 'bold')
        ).grid(row=row, column=0, sticky='w', pady=5)
        
        self.tipo_episodio_var = tk.StringVar(value="Visita")
        tipo_frame = ttk.Frame(scrollable_frame)
        tipo_frame.grid(row=row, column=1, sticky='w', pady=5)
        
        ttk.Radiobutton(
            tipo_frame,
            text="Visita",
            variable=self.tipo_episodio_var,
            value="Visita"
        ).pack(side='left', padx=5)
        
        ttk.Radiobutton(
            tipo_frame,
            text="Ricovero",
            variable=self.tipo_episodio_var,
            value="Ricovero"
        ).pack(side='left', padx=5)
        
        row += 1
        
        # ==== DATA E ORA ====
        ttk.Label(
            scrollable_frame,
            text="Data e Ora *:",
            font=('Segoe UI', 11, 'bold')
        ).grid(row=row, column=0, sticky='w', pady=5)
        
        datetime_frame = ttk.Frame(scrollable_frame)
        datetime_frame.grid(row=row, column=1, sticky='ew', pady=5)
        
        now = datetime.now()
        
        self.data_var = tk.StringVar(value=now.strftime("%d/%m/%Y"))
        ttk.Entry(
            datetime_frame,
            textvariable=self.data_var,
            width=15,
            font=('Segoe UI', 10)
        ).pack(side='left', padx=(0, 10))
        
        self.ora_var = tk.StringVar(value=now.strftime("%H:%M"))
        ttk.Entry(
            datetime_frame,
            textvariable=self.ora_var,
            width=10,
            font=('Segoe UI', 10)
        ).pack(side='left')
        
        row += 1
        
        # ==== MOTIVO ====
        ttk.Label(
            scrollable_frame,
            text="Motivo della Visita/Ricovero *:",
            font=('Segoe UI', 11, 'bold')
        ).grid(row=row, column=0, sticky='nw', pady=5)
        
        self.motivo_text = tk.Text(
            scrollable_frame,
            height=4,
            width=50,
            wrap='word',
            font=('Segoe UI', 10)
        )
        self.motivo_text.grid(row=row, column=1, sticky='ew', pady=5)
        
        row += 1
        
        # ==== PARAMETRI VITALI ====
        vitals_header = ttk.Label(
            scrollable_frame,
            text="🩺 PARAMETRI VITALI",
            font=('Segoe UI', 12, 'bold')
        )
        vitals_header.grid(row=row, column=0, columnspan=2, sticky='w', pady=(20, 10))
        
        row += 1
        
        # Pressione Arteriosa
        ttk.Label(
            scrollable_frame,
            text="Pressione Arteriosa (mmHg):",
            font=('Segoe UI', 10)
        ).grid(row=row, column=0, sticky='w', pady=5)
        
        pressure_frame = ttk.Frame(scrollable_frame)
        pressure_frame.grid(row=row, column=1, sticky='w', pady=5)
        
        self.sistolica_var = tk.StringVar()
        ttk.Entry(
            pressure_frame,
            textvariable=self.sistolica_var,
            width=8,
            font=('Segoe UI', 10)
        ).pack(side='left')
        
        ttk.Label(pressure_frame, text=" / ", font=('Segoe UI', 10)).pack(side='left')
        
        self.diastolica_var = tk.StringVar()
        ttk.Entry(
            pressure_frame,
            textvariable=self.diastolica_var,
            width=8,
            font=('Segoe UI', 10)
        ).pack(side='left')
        
        ttk.Label(
            pressure_frame,
            text="(es: 120/80)",
            font=('Segoe UI', 8),
            foreground='gray'
        ).pack(side='left', padx=(5, 0))
        
        row += 1
        
        # Frequenza Cardiaca
        ttk.Label(
            scrollable_frame,
            text="Frequenza Cardiaca (bpm):",
            font=('Segoe UI', 10)
        ).grid(row=row, column=0, sticky='w', pady=5)
        
        self.fc_var = tk.StringVar()
        ttk.Entry(
            scrollable_frame,
            textvariable=self.fc_var,
            width=15,
            font=('Segoe UI', 10)
        ).grid(row=row, column=1, sticky='w', pady=5)
        
        row += 1
        
        # Temperatura
        ttk.Label(
            scrollable_frame,
            text="Temperatura (°C):",
            font=('Segoe UI', 10)
        ).grid(row=row, column=0, sticky='w', pady=5)
        
        self.temp_var = tk.StringVar()
        ttk.Entry(
            scrollable_frame,
            textvariable=self.temp_var,
            width=15,
            font=('Segoe UI', 10)
        ).grid(row=row, column=1, sticky='w', pady=5)
        
        row += 1
        
        # Frequenza Respiratoria
        ttk.Label(
            scrollable_frame,
            text="Frequenza Respiratoria (atti/min):",
            font=('Segoe UI', 10)
        ).grid(row=row, column=0, sticky='w', pady=5)
        
        self.fr_var = tk.StringVar()
        ttk.Entry(
            scrollable_frame,
            textvariable=self.fr_var,
            width=15,
            font=('Segoe UI', 10)
        ).grid(row=row, column=1, sticky='w', pady=5)
        
        row += 1
        
        # Saturazione O2
        ttk.Label(
            scrollable_frame,
            text="Saturazione O₂ (%):",
            font=('Segoe UI', 10)
        ).grid(row=row, column=0, sticky='w', pady=5)
        
        self.spo2_var = tk.StringVar()
        ttk.Entry(
            scrollable_frame,
            textvariable=self.spo2_var,
            width=15,
            font=('Segoe UI', 10)
        ).grid(row=row, column=1, sticky='w', pady=5)
        
        row += 1
        
        # ==== SINTOMI E ANAMNESI ====
        symptoms_header = ttk.Label(
            scrollable_frame,
            text="📝 SINTOMI E ANAMNESI",
            font=('Segoe UI', 12, 'bold')
        )
        symptoms_header.grid(row=row, column=0, columnspan=2, sticky='w', pady=(20, 10))
        
        row += 1
        
        # Sintomi Presenti
        ttk.Label(
            scrollable_frame,
            text="Sintomi Presenti:",
            font=('Segoe UI', 10)
        ).grid(row=row, column=0, sticky='nw', pady=5)
        
        self.sintomi_text = tk.Text(
            scrollable_frame,
            height=4,
            width=50,
            wrap='word',
            font=('Segoe UI', 10)
        )
        self.sintomi_text.grid(row=row, column=1, sticky='ew', pady=5)
        
        row += 1
        
        # Farmaci Attuali
        ttk.Label(
            scrollable_frame,
            text="Farmaci in Assunzione:",
            font=('Segoe UI', 10)
        ).grid(row=row, column=0, sticky='nw', pady=5)
        
        self.farmaci_text = tk.Text(
            scrollable_frame,
            height=3,
            width=50,
            wrap='word',
            font=('Segoe UI', 10)
        )
        self.farmaci_text.grid(row=row, column=1, sticky='ew', pady=5)
        
        ttk.Label(
            scrollable_frame,
            text="(Una per riga)",
            font=('Segoe UI', 8),
            foreground='gray'
        ).grid(row=row+1, column=1, sticky='w')
        
        row += 2
        
        # ==== ESAME OBIETTIVO ====
        exam_header = ttk.Label(
            scrollable_frame,
            text="🔬 ESAME OBIETTIVO",
            font=('Segoe UI', 12, 'bold')
        )
        exam_header.grid(row=row, column=0, columnspan=2, sticky='w', pady=(20, 10))
        
        row += 1
        
        ttk.Label(
            scrollable_frame,
            text="Esame Obiettivo:",
            font=('Segoe UI', 10)
        ).grid(row=row, column=0, sticky='nw', pady=5)
        
        self.esame_text = tk.Text(
            scrollable_frame,
            height=5,
            width=50,
            wrap='word',
            font=('Segoe UI', 10)
        )
        self.esame_text.grid(row=row, column=1, sticky='ew', pady=5)
        
        row += 1
        
        # ==== DIAGNOSI E TERAPIA ====
        diagnosis_header = ttk.Label(
            scrollable_frame,
            text="💊 DIAGNOSI E TERAPIA",
            font=('Segoe UI', 12, 'bold')
        )
        diagnosis_header.grid(row=row, column=0, columnspan=2, sticky='w', pady=(20, 10))
        
        row += 1
        
        # Diagnosi
        ttk.Label(
            scrollable_frame,
            text="Diagnosi:",
            font=('Segoe UI', 10)
        ).grid(row=row, column=0, sticky='nw', pady=5)
        
        self.diagnosi_text = tk.Text(
            scrollable_frame,
            height=3,
            width=50,
            wrap='word',
            font=('Segoe UI', 10)
        )
        self.diagnosi_text.grid(row=row, column=1, sticky='ew', pady=5)
        
        row += 1
        
        # Piano Terapeutico
        ttk.Label(
            scrollable_frame,
            text="Piano Terapeutico:",
            font=('Segoe UI', 10)
        ).grid(row=row, column=0, sticky='nw', pady=5)
        
        self.terapia_text = tk.Text(
            scrollable_frame,
            height=4,
            width=50,
            wrap='word',
            font=('Segoe UI', 10)
        )
        self.terapia_text.grid(row=row, column=1, sticky='ew', pady=5)
        
        row += 1
        
        # Note Aggiuntive
        ttk.Label(
            scrollable_frame,
            text="Note Aggiuntive:",
            font=('Segoe UI', 10)
        ).grid(row=row, column=0, sticky='nw', pady=5)
        
        self.note_text = tk.Text(
            scrollable_frame,
            height=3,
            width=50,
            wrap='word',
            font=('Segoe UI', 10)
        )
        self.note_text.grid(row=row, column=1, sticky='ew', pady=5)
        
        row += 1
        
        # Configure grid column weights
        scrollable_frame.columnconfigure(1, weight=1)
        
        # Buttons frame
        button_frame = ttk.Frame(self.dialog)
        button_frame.pack(fill='x', padx=20, pady=(10, 20))
        
        # Save button
        save_btn = ttk.Button(
            button_frame,
            text="💾 Salva Scheda Clinica",
            command=self.save_record,
            style='Primary.TButton'
        )
        save_btn.pack(side='left', padx=5, ipadx=20, ipady=5)
        
        # Cancel button
        cancel_btn = ttk.Button(
            button_frame,
            text="❌ Annulla",
            command=self.cancel
        )
        cancel_btn.pack(side='right', padx=5, ipadx=10, ipady=5)
        
        # Required fields note
        note_label = ttk.Label(
            button_frame,
            text="* Campi obbligatori",
            font=('Segoe UI', 8),
            foreground='red'
        )
        note_label.pack(side='right', padx=20)
    
    def validate_required_fields(self):
        """Validate required fields."""
        if not self.tipo_episodio_var.get():
            messagebox.showerror("Errore", "Tipo di Episodio è obbligatorio")
            return False
        
        if not self.data_var.get():
            messagebox.showerror("Errore", "Data è obbligatoria")
            return False
        
        if not self.ora_var.get():
            messagebox.showerror("Errore", "Ora è obbligatoria")
            return False
        
        motivo = self.motivo_text.get(1.0, tk.END).strip()
        if not motivo:
            messagebox.showerror("Errore", "Motivo della Visita/Ricovero è obbligatorio")
            return False
        
        # Validate date format
        try:
            day, month, year = self.data_var.get().strip().split('/')
            datetime(int(year), int(month), int(day))
        except:
            messagebox.showerror("Errore", "Formato Data non valido (usa GG/MM/AAAA)")
            return False
        
        # Validate time format
        try:
            hour, minute = self.ora_var.get().strip().split(':')
            if not (0 <= int(hour) <= 23 and 0 <= int(minute) <= 59):
                raise ValueError
        except:
            messagebox.showerror("Errore", "Formato Ora non valido (usa HH:MM)")
            return False
        
        return True
    
    def get_record_data(self):
        """Get clinical record data from form."""
        # Parse text fields
        sintomi = self.sintomi_text.get(1.0, tk.END).strip()
        farmaci = [line.strip() for line in self.farmaci_text.get(1.0, tk.END).split('\n') if line.strip()]
        esame_obiettivo = self.esame_text.get(1.0, tk.END).strip()
        diagnosi = self.diagnosi_text.get(1.0, tk.END).strip()
        piano_terapeutico = self.terapia_text.get(1.0, tk.END).strip()
        note = self.note_text.get(1.0, tk.END).strip()
        motivo = self.motivo_text.get(1.0, tk.END).strip()
        
        # Build datetime string
        data = self.data_var.get().strip()
        ora = self.ora_var.get().strip()
        day, month, year = data.split('/')
        datetime_str = f"{year}-{month.zfill(2)}-{day.zfill(2)}T{ora}:00"
        
        # Build pressure string
        pressure = ""
        if self.sistolica_var.get() and self.diastolica_var.get():
            pressure = f"{self.sistolica_var.get()}/{self.diastolica_var.get()}"
        
        data = {
            "patient_id": self.patient_info.get('patient_id', '') if self.patient_info else '',
            "patient": {
                "patient_id": self.patient_info.get('patient_id', '') if self.patient_info else '',
                "nome": self.patient_info.get('nome', '') if self.patient_info else '',
                "cognome": self.patient_info.get('cognome', '') if self.patient_info else '',
                "codice_fiscale": self.patient_info.get('codice_fiscale', '') if self.patient_info else ''
            },
            "tipo_episodio": self.tipo_episodio_var.get(),
            "encounter_timestamp": datetime_str,
            "chief_complaint": motivo,
            "current_medications": farmaci,
            "vital_signs": {
                "blood_pressure": pressure or None,
                "heart_rate": self.fc_var.get().strip() or None,
                "temperature": self.temp_var.get().strip() or None,
                "respiratory_rate": self.fr_var.get().strip() or None,
                "spo2": self.spo2_var.get().strip() or None
            },
            "sintomi": sintomi,
            "esame_obiettivo": esame_obiettivo,
            "diagnosis": diagnosi,
            "treatment_plan": piano_terapeutico,
            "notes": note,
            "priority": "routine"  # Default, could be calculated based on vital signs
        }
        
        return data
    
    def save_record(self):
        """Save clinical record."""
        if not self.validate_required_fields():
            return
        
        self.result = self.get_record_data()
        
        # Call callback if provided
        if self.callback:
            self.callback(self.result)
        
        messagebox.showinfo("Successo", "Scheda clinica salvata con successo!")
        self.dialog.destroy()
    
    def cancel(self):
        """Cancel record creation."""
        self.result = None
        self.dialog.destroy()
    
    def show(self):
        """Show dialog and wait for result."""
        self.dialog.wait_window()
        return self.result
