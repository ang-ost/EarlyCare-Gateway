"""
Add Clinical Record Form - Form for adding clinical records to existing patients
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import json


class AddRecordDialog:
    """Dialog for adding a clinical record to an existing patient."""
    
    def __init__(self, parent, patient_data=None, callback=None):
        """
        Initialize add record form dialog.
        
        Args:
            parent: Parent window
            patient_data: Existing patient data (dict with nome, cognome, codice_fiscale)
            callback: Function to call with record data when saved
        """
        self.parent = parent
        self.patient_data = patient_data
        self.callback = callback
        self.result = None
        
        # Create dialog window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("📋 Nuova Scheda Clinica")
        self.dialog.geometry("800x700")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (800 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (700 // 2)
        self.dialog.geometry(f"+{x}+{y}")
        
        # Create form
        self.create_form()
    
    def create_form(self):
        """Create the clinical record entry form."""
        # Main container
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
            text="Nuova Scheda Clinica - Problematica Attuale",
            font=('Segoe UI', 14, 'bold')
        )
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 10))
        
        row = 1
        
        # ==== DATI PROBLEMA ATTUALE ====
        
        # Motivo principale *
        ttk.Label(scrollable_frame, text="Motivo Principale della Visita *:", font=('Segoe UI', 10)).grid(row=row, column=0, sticky='w', pady=8)
        self.chief_complaint_var = tk.StringVar()
        chief_entry = tk.Entry(scrollable_frame, textvariable=self.chief_complaint_var, width=50, font=('Segoe UI', 10), exportselection=0)
        chief_entry.grid(row=row, column=1, sticky='ew', pady=8)
        row += 1
        
        # Sintomi attuali *
        ttk.Label(scrollable_frame, text="Sintomi Attuali *:", font=('Segoe UI', 10)).grid(row=row, column=0, sticky='nw', pady=8)
        symptoms_frame = ttk.Frame(scrollable_frame)
        symptoms_frame.grid(row=row, column=1, sticky='ew', pady=8)
        self.symptoms_text = tk.Text(symptoms_frame, height=4, width=50, wrap='word', font=('Segoe UI', 10))
        self.symptoms_text.pack(side='left', fill='both', expand=True)
        symptoms_scroll = ttk.Scrollbar(symptoms_frame, command=self.symptoms_text.yview)
        symptoms_scroll.pack(side='right', fill='y')
        self.symptoms_text.config(yscrollcommand=symptoms_scroll.set)
        ttk.Label(scrollable_frame, text="(Descrivere i sintomi attuali del paziente)", font=('Segoe UI', 8), foreground='gray').grid(row=row+1, column=1, sticky='w')
        row += 2
        
        # Separator
        ttk.Separator(scrollable_frame, orient='horizontal').grid(row=row, column=0, columnspan=2, sticky='ew', pady=15)
        row += 1
        
        # ==== PARAMETRI VITALI ====
        vital_header = ttk.Label(
            scrollable_frame,
            text="🩺 PARAMETRI VITALI",
            font=('Segoe UI', 11, 'bold')
        )
        vital_header.grid(row=row, column=0, columnspan=2, sticky='w', pady=(0, 10))
        row += 1
        
        # Pressione Arteriosa
        ttk.Label(scrollable_frame, text="Pressione Arteriosa (es: 120/80):", font=('Segoe UI', 10)).grid(row=row, column=0, sticky='w', pady=5)
        self.bp_var = tk.StringVar()
        bp_entry = tk.Entry(scrollable_frame, textvariable=self.bp_var, width=50, font=('Segoe UI', 10), exportselection=0)
        bp_entry.grid(row=row, column=1, sticky='ew', pady=5)
        row += 1
        
        # Frequenza Cardiaca
        ttk.Label(scrollable_frame, text="Frequenza Cardiaca (bpm):", font=('Segoe UI', 10)).grid(row=row, column=0, sticky='w', pady=5)
        self.hr_var = tk.StringVar()
        hr_entry = tk.Entry(scrollable_frame, textvariable=self.hr_var, width=50, font=('Segoe UI', 10), exportselection=0)
        hr_entry.grid(row=row, column=1, sticky='ew', pady=5)
        row += 1
        
        # Temperatura
        ttk.Label(scrollable_frame, text="Temperatura (°C):", font=('Segoe UI', 10)).grid(row=row, column=0, sticky='w', pady=5)
        self.temp_var = tk.StringVar()
        temp_entry = tk.Entry(scrollable_frame, textvariable=self.temp_var, width=50, font=('Segoe UI', 10), exportselection=0)
        temp_entry.grid(row=row, column=1, sticky='ew', pady=5)
        row += 1
        
        # Frequenza Respiratoria
        ttk.Label(scrollable_frame, text="Frequenza Respiratoria (atti/min):", font=('Segoe UI', 10)).grid(row=row, column=0, sticky='w', pady=5)
        self.rr_var = tk.StringVar()
        rr_entry = tk.Entry(scrollable_frame, textvariable=self.rr_var, width=50, font=('Segoe UI', 10), exportselection=0)
        rr_entry.grid(row=row, column=1, sticky='ew', pady=5)
        row += 1
        
        # SpO2
        ttk.Label(scrollable_frame, text="Saturazione O2 (%):", font=('Segoe UI', 10)).grid(row=row, column=0, sticky='w', pady=5)
        self.spo2_var = tk.StringVar()
        spo2_entry = tk.Entry(scrollable_frame, textvariable=self.spo2_var, width=50, font=('Segoe UI', 10), exportselection=0)
        spo2_entry.grid(row=row, column=1, sticky='ew', pady=5)
        row += 1
        
        # Separator
        ttk.Separator(scrollable_frame, orient='horizontal').grid(row=row, column=0, columnspan=2, sticky='ew', pady=15)
        row += 1
        
        # ==== ESAME CLINICO ====
        exam_header = ttk.Label(
            scrollable_frame,
            text="🔬 ESAME CLINICO",
            font=('Segoe UI', 11, 'bold')
        )
        exam_header.grid(row=row, column=0, columnspan=2, sticky='w', pady=(0, 10))
        row += 1
        
        # Esame obiettivo
        ttk.Label(scrollable_frame, text="Esame Obiettivo:", font=('Segoe UI', 10)).grid(row=row, column=0, sticky='nw', pady=8)
        exam_frame = ttk.Frame(scrollable_frame)
        exam_frame.grid(row=row, column=1, sticky='ew', pady=8)
        self.exam_text = tk.Text(exam_frame, height=4, width=50, wrap='word', font=('Segoe UI', 10))
        self.exam_text.pack(side='left', fill='both', expand=True)
        exam_scroll = ttk.Scrollbar(exam_frame, command=self.exam_text.yview)
        exam_scroll.pack(side='right', fill='y')
        self.exam_text.config(yscrollcommand=exam_scroll.set)
        ttk.Label(scrollable_frame, text="(Risultati dell'esame fisico)", font=('Segoe UI', 8), foreground='gray').grid(row=row+1, column=1, sticky='w')
        row += 2
        
        # Separator
        ttk.Separator(scrollable_frame, orient='horizontal').grid(row=row, column=0, columnspan=2, sticky='ew', pady=15)
        row += 1
        
        # ==== DIAGNOSI E TRATTAMENTO ====
        diag_header = ttk.Label(
            scrollable_frame,
            text="💊 DIAGNOSI E TRATTAMENTO",
            font=('Segoe UI', 11, 'bold')
        )
        diag_header.grid(row=row, column=0, columnspan=2, sticky='w', pady=(0, 10))
        row += 1
        
        # Diagnosi
        ttk.Label(scrollable_frame, text="Diagnosi:", font=('Segoe UI', 10)).grid(row=row, column=0, sticky='nw', pady=8)
        diagnosis_frame = ttk.Frame(scrollable_frame)
        diagnosis_frame.grid(row=row, column=1, sticky='ew', pady=8)
        self.diagnosis_text = tk.Text(diagnosis_frame, height=3, width=50, wrap='word', font=('Segoe UI', 10))
        self.diagnosis_text.pack(side='left', fill='both', expand=True)
        diagnosis_scroll = ttk.Scrollbar(diagnosis_frame, command=self.diagnosis_text.yview)
        diagnosis_scroll.pack(side='right', fill='y')
        self.diagnosis_text.config(yscrollcommand=diagnosis_scroll.set)
        row += 1
        
        # Piano terapeutico
        ttk.Label(scrollable_frame, text="Piano Terapeutico:", font=('Segoe UI', 10)).grid(row=row, column=0, sticky='nw', pady=8)
        treatment_frame = ttk.Frame(scrollable_frame)
        treatment_frame.grid(row=row, column=1, sticky='ew', pady=8)
        self.treatment_text = tk.Text(treatment_frame, height=4, width=50, wrap='word', font=('Segoe UI', 10))
        self.treatment_text.pack(side='left', fill='both', expand=True)
        treatment_scroll = ttk.Scrollbar(treatment_frame, command=self.treatment_text.yview)
        treatment_scroll.pack(side='right', fill='y')
        self.treatment_text.config(yscrollcommand=treatment_scroll.set)
        ttk.Label(scrollable_frame, text="(Farmaci prescritti, raccomandazioni, follow-up)", font=('Segoe UI', 8), foreground='gray').grid(row=row+1, column=1, sticky='w')
        row += 2
        
        # Note aggiuntive
        ttk.Label(scrollable_frame, text="Note Aggiuntive:", font=('Segoe UI', 10)).grid(row=row, column=0, sticky='nw', pady=8)
        notes_frame = ttk.Frame(scrollable_frame)
        notes_frame.grid(row=row, column=1, sticky='ew', pady=8)
        self.notes_text = tk.Text(notes_frame, height=3, width=50, wrap='word', font=('Segoe UI', 10))
        self.notes_text.pack(side='left', fill='both', expand=True)
        notes_scroll = ttk.Scrollbar(notes_frame, command=self.notes_text.yview)
        notes_scroll.pack(side='right', fill='y')
        self.notes_text.config(yscrollcommand=notes_scroll.set)
        row += 1
        
        # Separator
        ttk.Separator(scrollable_frame, orient='horizontal').grid(row=row, column=0, columnspan=2, sticky='ew', pady=15)
        row += 1
        
        # Priority
        ttk.Label(scrollable_frame, text="Priorità:", font=('Segoe UI', 10)).grid(row=row, column=0, sticky='w', pady=8)
        self.priority_var = tk.StringVar(value="routine")
        priority_frame = ttk.Frame(scrollable_frame)
        priority_frame.grid(row=row, column=1, sticky='w', pady=8)
        ttk.Radiobutton(priority_frame, text="Routine", variable=self.priority_var, value="routine").pack(side='left', padx=(0, 10))
        ttk.Radiobutton(priority_frame, text="Presto", variable=self.priority_var, value="soon").pack(side='left', padx=(0, 10))
        ttk.Radiobutton(priority_frame, text="Urgente", variable=self.priority_var, value="urgent").pack(side='left', padx=(0, 10))
        ttk.Radiobutton(priority_frame, text="Emergenza", variable=self.priority_var, value="emergency").pack(side='left')
        row += 1
        
        # Configure grid column weights
        scrollable_frame.columnconfigure(1, weight=1)
        
        # Buttons frame
        button_frame = ttk.Frame(self.dialog)
        button_frame.pack(fill='x', padx=20, pady=(10, 20))
        
        # Required fields note
        note_label = ttk.Label(
            button_frame,
            text="* Campi obbligatori",
            font=('Segoe UI', 9, 'bold'),
            foreground='red'
        )
        note_label.pack(side='left', padx=5)
        
        # Cancel button
        cancel_btn = ttk.Button(
            button_frame,
            text="❌ Annulla",
            command=self.cancel
        )
        cancel_btn.pack(side='right', padx=5)
        
        # Save button
        save_btn = ttk.Button(
            button_frame,
            text="✅ Salva Scheda Clinica",
            command=self.save
        )
        save_btn.pack(side='right', padx=5)
    
    def validate_required_fields(self):
        """Validate required fields."""
        if not self.chief_complaint_var.get().strip():
            messagebox.showerror("Errore", "Motivo Principale della Visita è obbligatorio")
            return False
        
        symptoms = self.symptoms_text.get(1.0, tk.END).strip()
        if not symptoms:
            messagebox.showerror("Errore", "Sintomi Attuali sono obbligatori")
            return False
        
        return True
    
    def get_record_data(self):
        """Get clinical record data from form."""
        data = {
            "chief_complaint": self.chief_complaint_var.get().strip(),
            "symptoms": self.symptoms_text.get(1.0, tk.END).strip(),
            "vital_signs": {
                "blood_pressure": self.bp_var.get().strip() or None,
                "heart_rate": self.hr_var.get().strip() or None,
                "temperature": self.temp_var.get().strip() or None,
                "respiratory_rate": self.rr_var.get().strip() or None,
                "spo2": self.spo2_var.get().strip() or None
            },
            "physical_exam": self.exam_text.get(1.0, tk.END).strip(),
            "diagnosis": self.diagnosis_text.get(1.0, tk.END).strip(),
            "treatment_plan": self.treatment_text.get(1.0, tk.END).strip(),
            "notes": self.notes_text.get(1.0, tk.END).strip(),
            "priority": self.priority_var.get(),
            "encounter_timestamp": datetime.now().isoformat()
        }
        
        if self.patient_data:
            data["patient_id"] = self.patient_data.get("patient_id") or self.patient_data.get("codice_fiscale")
            data["patient"] = {
                "patient_id": self.patient_data.get("patient_id") or self.patient_data.get("codice_fiscale"),
                "nome": self.patient_data.get("nome"),
                "cognome": self.patient_data.get("cognome"),
                "codice_fiscale": self.patient_data.get("codice_fiscale")
            }
        
        return data
    
    def save(self):
        """Save clinical record."""
        if not self.validate_required_fields():
            return
        
        self.result = self.get_record_data()
        
        # Call callback if provided
        if self.callback:
            self.callback(self.result)
        
        self.dialog.destroy()
    
    def cancel(self):
        """Cancel form."""
        self.result = None
        self.dialog.destroy()
    
    def show(self):
        """Show dialog and wait for result."""
        self.dialog.wait_window()
        return self.result
