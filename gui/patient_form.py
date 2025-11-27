"""
Patient Form Dialog - Form for patient data entry
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from pathlib import Path
import json
import re


class PatientFormDialog:
    """Dialog for entering patient data manually."""
    
    def __init__(self, parent, callback=None):
        """
        Initialize patient form dialog.
        
        Args:
            parent: Parent window
            callback: Function to call with patient data when saved
        """
        self.parent = parent
        self.callback = callback
        self.result = None
        
        # Create dialog window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("📝 Inserimento Dati Paziente")
        self.dialog.geometry("700x800")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (700 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (800 // 2)
        self.dialog.geometry(f"+{x}+{y}")
        
        # Create form
        self.create_form()
    
    def create_form(self):
        """Create the patient data entry form."""
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
            text="Inserimento Dati Paziente",
            font=('Segoe UI', 14, 'bold')
        )
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # ==== DATI ANAGRAFICI ====
        row = 1
        
        # Section header
        demo_header = ttk.Label(
            scrollable_frame,
            text="👤 DATI ANAGRAFICI",
            font=('Segoe UI', 11, 'bold')
        )
        demo_header.grid(row=row, column=0, columnspan=2, sticky='w', pady=(10, 10))
        row += 1
        
        # Name
        ttk.Label(scrollable_frame, text="Nome *:").grid(row=row, column=0, sticky='w', pady=5)
        self.name_var = tk.StringVar()
        ttk.Entry(scrollable_frame, textvariable=self.name_var, width=40).grid(row=row, column=1, sticky='ew', pady=5)
        row += 1
        
        # Surname
        ttk.Label(scrollable_frame, text="Cognome *:").grid(row=row, column=0, sticky='w', pady=5)
        self.surname_var = tk.StringVar()
        ttk.Entry(scrollable_frame, textvariable=self.surname_var, width=40).grid(row=row, column=1, sticky='ew', pady=5)
        row += 1
        
        # Date of Birth
        ttk.Label(scrollable_frame, text="Data di Nascita (GG/MM/AAAA) *:").grid(row=row, column=0, sticky='w', pady=5)
        self.dob_var = tk.StringVar()
        ttk.Entry(scrollable_frame, textvariable=self.dob_var, width=40).grid(row=row, column=1, sticky='ew', pady=5)
        row += 1
        
        # Birth Place
        ttk.Label(scrollable_frame, text="Comune di Nascita *:").grid(row=row, column=0, sticky='w', pady=5)
        self.birthplace_var = tk.StringVar()
        ttk.Entry(scrollable_frame, textvariable=self.birthplace_var, width=40).grid(row=row, column=1, sticky='ew', pady=5)
        row += 1
        
        # Gender
        ttk.Label(scrollable_frame, text="Sesso *:").grid(row=row, column=0, sticky='w', pady=5)
        self.gender_var = tk.StringVar(value="M")
        gender_frame = ttk.Frame(scrollable_frame)
        gender_frame.grid(row=row, column=1, sticky='w', pady=5)
        ttk.Radiobutton(gender_frame, text="Maschio", variable=self.gender_var, value="M").pack(side='left', padx=5)
        ttk.Radiobutton(gender_frame, text="Femmina", variable=self.gender_var, value="F").pack(side='left', padx=5)
        row += 1
        
        # Calculated Fiscal Code (read-only)
        ttk.Label(scrollable_frame, text="Codice Fiscale (calcolato):").grid(row=row, column=0, sticky='w', pady=5)
        self.fiscal_code_var = tk.StringVar(value="Inserire i dati sopra")
        fiscal_entry = ttk.Entry(scrollable_frame, textvariable=self.fiscal_code_var, width=40, state='readonly')
        fiscal_entry.grid(row=row, column=1, sticky='ew', pady=5)
        row += 1
        
        # Calculate button
        calc_btn = ttk.Button(
            scrollable_frame,
            text="🔢 Calcola Codice Fiscale",
            command=self.calculate_fiscal_code
        )
        calc_btn.grid(row=row, column=1, sticky='w', pady=5)
        row += 1
        
        # ==== DATI CLINICI ====
        
        # Section header
        clinical_header = ttk.Label(
            scrollable_frame,
            text="🏥 DATI CLINICI",
            font=('Segoe UI', 11, 'bold')
        )
        clinical_header.grid(row=row, column=0, columnspan=2, sticky='w', pady=(20, 10))
        row += 1
        
        # Chief Complaint
        ttk.Label(scrollable_frame, text="Sintomo/Motivo Principale *:").grid(row=row, column=0, sticky='nw', pady=5)
        self.chief_complaint_var = tk.StringVar()
        ttk.Entry(scrollable_frame, textvariable=self.chief_complaint_var, width=40).grid(row=row, column=1, sticky='ew', pady=5)
        row += 1
        
        # Medical History
        ttk.Label(scrollable_frame, text="Storia Clinica:").grid(row=row, column=0, sticky='nw', pady=5)
        history_frame = ttk.Frame(scrollable_frame)
        history_frame.grid(row=row, column=1, sticky='ew', pady=5)
        self.history_text = tk.Text(history_frame, height=4, width=40, wrap='word')
        self.history_text.pack(side='left', fill='both', expand=True)
        history_scroll = ttk.Scrollbar(history_frame, command=self.history_text.yview)
        history_scroll.pack(side='right', fill='y')
        self.history_text.config(yscrollcommand=history_scroll.set)
        ttk.Label(scrollable_frame, text="(Una per riga)", font=('Segoe UI', 8), foreground='gray').grid(row=row+1, column=1, sticky='w')
        row += 2
        
        # Current Medications
        ttk.Label(scrollable_frame, text="Farmaci Attuali:").grid(row=row, column=0, sticky='nw', pady=5)
        meds_frame = ttk.Frame(scrollable_frame)
        meds_frame.grid(row=row, column=1, sticky='ew', pady=5)
        self.medications_text = tk.Text(meds_frame, height=4, width=40, wrap='word')
        self.medications_text.pack(side='left', fill='both', expand=True)
        meds_scroll = ttk.Scrollbar(meds_frame, command=self.medications_text.yview)
        meds_scroll.pack(side='right', fill='y')
        self.medications_text.config(yscrollcommand=meds_scroll.set)
        ttk.Label(scrollable_frame, text="(Una per riga)", font=('Segoe UI', 8), foreground='gray').grid(row=row+1, column=1, sticky='w')
        row += 2
        
        # Allergies
        ttk.Label(scrollable_frame, text="Allergie:").grid(row=row, column=0, sticky='nw', pady=5)
        allergies_frame = ttk.Frame(scrollable_frame)
        allergies_frame.grid(row=row, column=1, sticky='ew', pady=5)
        self.allergies_text = tk.Text(allergies_frame, height=3, width=40, wrap='word')
        self.allergies_text.pack(side='left', fill='both', expand=True)
        allergies_scroll = ttk.Scrollbar(allergies_frame, command=self.allergies_text.yview)
        allergies_scroll.pack(side='right', fill='y')
        self.allergies_text.config(yscrollcommand=allergies_scroll.set)
        ttk.Label(scrollable_frame, text="(Una per riga)", font=('Segoe UI', 8), foreground='gray').grid(row=row+1, column=1, sticky='w')
        row += 2
        
        # ==== PARAMETRI VITALI ====
        
        # Section header
        vitals_header = ttk.Label(
            scrollable_frame,
            text="🩺 PARAMETRI VITALI (Opzionali)",
            font=('Segoe UI', 11, 'bold')
        )
        vitals_header.grid(row=row, column=0, columnspan=2, sticky='w', pady=(20, 10))
        row += 1
        
        # Blood Pressure
        ttk.Label(scrollable_frame, text="Pressione Arteriosa (es: 120/80):").grid(row=row, column=0, sticky='w', pady=5)
        self.bp_var = tk.StringVar()
        ttk.Entry(scrollable_frame, textvariable=self.bp_var, width=40).grid(row=row, column=1, sticky='ew', pady=5)
        row += 1
        
        # Heart Rate
        ttk.Label(scrollable_frame, text="Frequenza Cardiaca (bpm):").grid(row=row, column=0, sticky='w', pady=5)
        self.hr_var = tk.StringVar()
        ttk.Entry(scrollable_frame, textvariable=self.hr_var, width=40).grid(row=row, column=1, sticky='ew', pady=5)
        row += 1
        
        # Temperature
        ttk.Label(scrollable_frame, text="Temperatura (°C):").grid(row=row, column=0, sticky='w', pady=5)
        self.temp_var = tk.StringVar()
        ttk.Entry(scrollable_frame, textvariable=self.temp_var, width=40).grid(row=row, column=1, sticky='ew', pady=5)
        row += 1
        
        # Respiratory Rate
        ttk.Label(scrollable_frame, text="Frequenza Respiratoria (atti/min):").grid(row=row, column=0, sticky='w', pady=5)
        self.rr_var = tk.StringVar()
        ttk.Entry(scrollable_frame, textvariable=self.rr_var, width=40).grid(row=row, column=1, sticky='ew', pady=5)
        row += 1
        
        # SpO2
        ttk.Label(scrollable_frame, text="Saturazione O2 (%):").grid(row=row, column=0, sticky='w', pady=5)
        self.spo2_var = tk.StringVar()
        ttk.Entry(scrollable_frame, textvariable=self.spo2_var, width=40).grid(row=row, column=1, sticky='ew', pady=5)
        row += 1
        
        # Configure grid column weights
        scrollable_frame.columnconfigure(1, weight=1)
        
        # Buttons frame
        button_frame = ttk.Frame(self.dialog)
        button_frame.pack(fill='x', padx=20, pady=(10, 20))
        
        # Save and Export button
        save_export_btn = ttk.Button(
            button_frame,
            text="💾 Salva ed Esporta JSON",
            command=self.save_and_export,
            style='Success.TButton'
        )
        save_export_btn.pack(side='left', padx=5)
        
        # Save button
        save_btn = ttk.Button(
            button_frame,
            text="✅ Salva e Usa",
            command=self.save,
            style='Primary.TButton'
        )
        save_btn.pack(side='left', padx=5)
        
        # Cancel button
        cancel_btn = ttk.Button(
            button_frame,
            text="❌ Annulla",
            command=self.cancel
        )
        cancel_btn.pack(side='right', padx=5)
        
        # Required fields note
        note_label = ttk.Label(
            button_frame,
            text="* Campi obbligatori",
            font=('Segoe UI', 8),
            foreground='red'
        )
        note_label.pack(side='right', padx=20)
    
    def calculate_fiscal_code(self):
        """Calculate Italian fiscal code following official rules."""
        name = self.name_var.get().strip().upper()
        surname = self.surname_var.get().strip().upper()
        dob = self.dob_var.get().strip()
        birthplace = self.birthplace_var.get().strip().upper()
        gender = self.gender_var.get()
        
        # Validate inputs
        if not name or not surname or not dob or not birthplace:
            messagebox.showwarning("Attenzione", "Compilare tutti i campi anagrafici prima di calcolare il codice fiscale")
            return
        
        # Parse date (GG/MM/AAAA)
        try:
            day, month, year = dob.split('/')
            day = int(day)
            month = int(month)
            year = int(year)
        except:
            messagebox.showerror("Errore", "Formato data non valido. Usa GG/MM/AAAA (es: 15/06/1975)")
            return
        
        # Calculate fiscal code components
        try:
            # Step 1: Surname code (3 letters)
            surname_code = self._encode_surname(surname)
            
            # Step 2: Name code (3 letters)
            name_code = self._encode_name(name)
            
            # Step 3: Year code (last 2 digits)
            year_code = f"{year % 100:02d}"
            
            # Step 4: Month code (official letter mapping)
            month_codes = ['A', 'B', 'C', 'D', 'E', 'H', 'L', 'M', 'P', 'R', 'S', 'T']
            month_code = month_codes[month - 1]
            
            # Step 5: Day code (add 40 for females)
            day_code = day + (40 if gender == 'F' else 0)
            day_code = f"{day_code:02d}"
            
            # Step 6: Birthplace cadastral code (simplified)
            # In production, use official ISTAT table
            birthplace_code = self._get_cadastral_code(birthplace)
            
            # Combine first 15 characters
            partial_code = f"{surname_code}{name_code}{year_code}{month_code}{day_code}{birthplace_code}"
            
            # Step 7: Calculate check character (16th character)
            check_char = self._calculate_check_character(partial_code)
            
            # Final fiscal code
            fiscal_code = partial_code + check_char
            
            self.fiscal_code_var.set(fiscal_code)
            
        except Exception as e:
            messagebox.showerror("Errore", f"Impossibile calcolare il codice fiscale: {e}")
    
    def _encode_surname(self, surname):
        """
        Encode surname following official rules:
        - Take first 3 consonants in order
        - If less than 3 consonants, add vowels
        - Pad with X if needed to reach 3 characters
        
        Example: OSTELLO → consonants: STLL → first 3: STL
        """
        # Remove spaces and special characters, keep only letters
        surname = re.sub(r'[^A-Z]', '', surname.upper())
        
        # Extract consonants and vowels in order
        consonants = ''.join([c for c in surname if c not in 'AEIOU'])
        vowels = ''.join([c for c in surname if c in 'AEIOU'])
        
        # Take first 3 consonants, then vowels if needed, pad with X
        code = (consonants + vowels + 'XXX')[:3]
        
        return code
    
    def _encode_name(self, name):
        """
        Encode name following official rules:
        - If 4+ consonants: take 1st, 3rd, 4th consonant (skip 2nd)
        - If less than 4 consonants: take all consonants, then vowels
        - Pad with X if needed to reach 3 characters
        
        Example: ANGELO → consonants: NGL (3) → all 3: NGL
        """
        # Remove spaces and special characters, keep only letters
        name = re.sub(r'[^A-Z]', '', name.upper())
        
        # Extract consonants and vowels in order
        consonants = ''.join([c for c in name if c not in 'AEIOU'])
        vowels = ''.join([c for c in name if c in 'AEIOU'])
        
        if len(consonants) >= 4:
            # Special rule: take 1st, 3rd, 4th consonant (indices 0, 2, 3)
            # Skip the 2nd consonant (index 1)
            code = consonants[0] + consonants[2] + consonants[3]
        else:
            # Take all consonants (first 3), then vowels if needed, pad with X
            code = (consonants + vowels + 'XXX')[:3]
        
        return code
    
    def _get_cadastral_code(self, birthplace):
        """
        Get cadastral code for birthplace.
        Uses a dictionary of major Italian cities.
        For unknown cities, generates a simplified code.
        
        Example: BARI → A662 (official code)
        """
        # Dictionary of major Italian cities with official cadastral codes
        cadastral_codes = {
            'ROMA': 'H501',
            'MILANO': 'F205',
            'NAPOLI': 'F839',
            'TORINO': 'L219',
            'PALERMO': 'G273',
            'GENOVA': 'D969',
            'BOLOGNA': 'A944',
            'FIRENZE': 'D612',
            'BARI': 'A662',
            'CATANIA': 'C351',
            'VENEZIA': 'L736',
            'VERONA': 'L781',
            'MESSINA': 'F158',
            'PADOVA': 'G224',
            'TRIESTE': 'L424',
            'BRESCIA': 'B157',
            'PARMA': 'G337',
            'TARANTO': 'L049',
            'PRATO': 'G999',
            'MODENA': 'F257',
            'REGGIO CALABRIA': 'H224',
            'REGGIO EMILIA': 'H223',
            'PERUGIA': 'G478',
            'LIVORNO': 'E625',
            'RAVENNA': 'H199',
            'CAGLIARI': 'B354',
            'FOGGIA': 'D643',
            'RIMINI': 'H294',
            'SALERNO': 'H703',
            'FERRARA': 'D548',
            'SASSARI': 'I452',
            'MONZA': 'F704',
            'SIRACUSA': 'I754',
            'PESCARA': 'G482',
            'BERGAMO': 'A794',
            'TRENTO': 'L378',
            'FORLI': 'D704',
            'VICENZA': 'L840',
            'TERNI': 'L117',
            'BOLZANO': 'A952',
            'NOVARA': 'F952',
            'PIACENZA': 'G535',
            'ANCONA': 'A271',
            'ANDRIA': 'A285',
            'AREZZO': 'A390',
            'UDINE': 'L483',
            'CESENA': 'C573',
            'LECCE': 'E506',
            'PESARO': 'G479',
            'BARLETTA': 'A669',
            'ALESSANDRIA': 'A182',
            'LA SPEZIA': 'E463',
            'PISA': 'G702',
            'CATANZARO': 'C352',
            'PISTOIA': 'G713',
            'GUIDONIA MONTECELIO': 'E263',
            'LUCCA': 'E715',
            'BRINDISI': 'B180',
            'COMO': 'C933',
            'BUSTO ARSIZIO': 'B300',
            'VARESE': 'L682',
        }
        
        # Normalize birthplace
        birthplace_clean = re.sub(r'[^A-Z ]', '', birthplace.upper()).strip()
        
        # Check if it's in our dictionary
        if birthplace_clean in cadastral_codes:
            return cadastral_codes[birthplace_clean]
        
        # If not found, generate a simplified code
        # Remove spaces and take first letter + 3 digits based on name
        birthplace_compact = birthplace_clean.replace(' ', '')
        if birthplace_compact:
            # First letter + pseudo-numeric code
            first_letter = birthplace_compact[0]
            # Generate 3 digits based on string hash (simplified)
            digits = f"{abs(hash(birthplace_compact)) % 1000:03d}"
            return first_letter + digits
        
        return 'Z999'  # Default for unknown
    
    def _calculate_check_character(self, code):
        """
        Calculate check character (16th character) using official algorithm.
        Uses different value tables for odd and even positions, then modulo 26.
        """
        # Official values for ODD positions (1st, 3rd, 5th, ... = index 0, 2, 4, ...)
        odd_values = {
            '0': 1, '1': 0, '2': 5, '3': 7, '4': 9, '5': 13, '6': 15, '7': 17, '8': 19, '9': 21,
            'A': 1, 'B': 0, 'C': 5, 'D': 7, 'E': 9, 'F': 13, 'G': 15, 'H': 17, 'I': 19, 'J': 21,
            'K': 2, 'L': 4, 'M': 18, 'N': 20, 'O': 11, 'P': 3, 'Q': 6, 'R': 8, 'S': 12, 'T': 14,
            'U': 16, 'V': 10, 'W': 22, 'X': 25, 'Y': 24, 'Z': 23
        }
        
        # Official values for EVEN positions (2nd, 4th, 6th, ... = index 1, 3, 5, ...)
        even_values = {
            '0': 0, '1': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9,
            'A': 0, 'B': 1, 'C': 2, 'D': 3, 'E': 4, 'F': 5, 'G': 6, 'H': 7, 'I': 8, 'J': 9,
            'K': 10, 'L': 11, 'M': 12, 'N': 13, 'O': 14, 'P': 15, 'Q': 16, 'R': 17, 'S': 18, 'T': 19,
            'U': 20, 'V': 21, 'W': 22, 'X': 23, 'Y': 24, 'Z': 25
        }
        
        # Check character letters (result of modulo 26)
        check_letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        
        # Calculate sum
        total = 0
        for i, char in enumerate(code):
            if i % 2 == 0:
                # Odd position (1-based) = even index (0-based)
                total += odd_values.get(char, 0)
            else:
                # Even position (1-based) = odd index (0-based)
                total += even_values.get(char, 0)
        
        # Return letter corresponding to (total modulo 26)
        return check_letters[total % 26]
    
    def validate_required_fields(self):
        """Validate required fields."""
        if not self.name_var.get().strip():
            messagebox.showerror("Errore", "Nome è obbligatorio")
            return False
        
        if not self.surname_var.get().strip():
            messagebox.showerror("Errore", "Cognome è obbligatorio")
            return False
        
        if not self.dob_var.get().strip():
            messagebox.showerror("Errore", "Data di Nascita è obbligatoria")
            return False
        
        if not self.birthplace_var.get().strip():
            messagebox.showerror("Errore", "Comune di Nascita è obbligatorio")
            return False
        
        # Validate date format (GG/MM/AAAA)
        try:
            day, month, year = self.dob_var.get().strip().split('/')
            datetime(int(year), int(month), int(day))
        except:
            messagebox.showerror("Errore", "Formato Data di Nascita non valido (usa GG/MM/AAAA, es: 15/06/1975)")
            return False
        
        if not self.chief_complaint_var.get().strip():
            messagebox.showerror("Errore", "Sintomo/Motivo Principale è obbligatorio")
            return False
        
        # Check if fiscal code is calculated
        if self.fiscal_code_var.get() == "Inserire i dati sopra" or not self.fiscal_code_var.get().strip():
            messagebox.showerror("Errore", "Calcolare il Codice Fiscale prima di salvare")
            return False
        
        return True
    
    def get_patient_data(self):
        """Get patient data from form."""
        # Parse text fields
        history = [line.strip() for line in self.history_text.get(1.0, tk.END).split('\n') if line.strip()]
        medications = [line.strip() for line in self.medications_text.get(1.0, tk.END).split('\n') if line.strip()]
        allergies = [line.strip() for line in self.allergies_text.get(1.0, tk.END).split('\n') if line.strip()]
        
        # Convert date format from GG/MM/AAAA to AAAA-MM-GG for internal use
        dob_input = self.dob_var.get().strip()
        try:
            day, month, year = dob_input.split('/')
            dob_formatted = f"{year}-{month.zfill(2)}-{day.zfill(2)}"
        except:
            dob_formatted = dob_input
        
        fiscal_code = self.fiscal_code_var.get().strip()
        
        data = {
            "patient_id": fiscal_code,  # Use fiscal code as patient ID
            "medical_record_number": fiscal_code,  # Use fiscal code as MRN
            "name": self.name_var.get().strip(),
            "surname": self.surname_var.get().strip(),
            "date_of_birth": dob_formatted,
            "birthplace": self.birthplace_var.get().strip(),
            "gender": self.gender_var.get(),
            "fiscal_code": fiscal_code,
            "chief_complaint": self.chief_complaint_var.get().strip(),
            "medical_history": history,
            "medications": medications,
            "allergies": allergies,
            "vital_signs": {
                "blood_pressure": self.bp_var.get().strip() or None,
                "heart_rate": self.hr_var.get().strip() or None,
                "temperature": self.temp_var.get().strip() or None,
                "respiratory_rate": self.rr_var.get().strip() or None,
                "spo2": self.spo2_var.get().strip() or None
            }
        }
        
        return data
    
    def save_and_export(self):
        """Save and export patient data to JSON file."""
        if not self.validate_required_fields():
            return
        
        data = self.get_patient_data()
        
        # Ask where to save
        from tkinter import filedialog
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            initialfile=f"patient_{data['patient_id']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                
                messagebox.showinfo("Successo", f"Dati paziente salvati in:\n{file_path}")
                self.result = data
                
                # Call callback if provided
                if self.callback:
                    self.callback(data, file_path)
                
                self.dialog.destroy()
            except Exception as e:
                messagebox.showerror("Errore", f"Impossibile salvare il file:\n{e}")
    
    def save(self):
        """Save patient data without exporting."""
        if not self.validate_required_fields():
            return
        
        self.result = self.get_patient_data()
        
        # Call callback if provided
        if self.callback:
            self.callback(self.result, None)
        
        self.dialog.destroy()
    
    def cancel(self):
        """Cancel form."""
        self.result = None
        self.dialog.destroy()
    
    def show(self):
        """Show dialog and wait for result."""
        self.dialog.wait_window()
        return self.result
