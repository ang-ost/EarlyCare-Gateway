"""
Patient Form Dialog - Form for patient demographic data entry
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from pathlib import Path
import json
import re


class PatientFormDialog:
    """Dialog for entering patient demographic data only."""
    
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
        self.dialog.title("👤 Dati Anagrafici Paziente")
        self.dialog.geometry("700x650")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (700 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (650 // 2)
        self.dialog.geometry(f"+{x}+{y}")
        
        # Create form
        self.create_form()
    
    def create_form(self):
        """Create the patient demographic data entry form."""
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
            text="Dati Anagrafici Paziente",
            font=('Segoe UI', 14, 'bold')
        )
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # ==== DATI ANAGRAFICI ====
        row = 1
        
        # Name
        ttk.Label(scrollable_frame, text="Nome *:", font=('Segoe UI', 10)).grid(row=row, column=0, sticky='w', pady=8)
        self.name_var = tk.StringVar()
        name_entry = ttk.Entry(scrollable_frame, textvariable=self.name_var, width=40, font=('Segoe UI', 10))
        name_entry.grid(row=row, column=1, sticky='ew', pady=8)
        row += 1
        
        # Surname
        ttk.Label(scrollable_frame, text="Cognome *:", font=('Segoe UI', 10)).grid(row=row, column=0, sticky='w', pady=8)
        self.surname_var = tk.StringVar()
        surname_entry = ttk.Entry(scrollable_frame, textvariable=self.surname_var, width=40, font=('Segoe UI', 10))
        surname_entry.grid(row=row, column=1, sticky='ew', pady=8)
        row += 1
        
        # Date of Birth
        ttk.Label(scrollable_frame, text="Data di Nascita (GG/MM/AAAA) *:", font=('Segoe UI', 10)).grid(row=row, column=0, sticky='w', pady=8)
        self.dob_var = tk.StringVar()
        dob_entry = ttk.Entry(scrollable_frame, textvariable=self.dob_var, width=40, font=('Segoe UI', 10))
        dob_entry.grid(row=row, column=1, sticky='ew', pady=8)
        row += 1
        
        # Date of Death (optional)
        ttk.Label(scrollable_frame, text="Data del Decesso (GG/MM/AAAA):", font=('Segoe UI', 10)).grid(row=row, column=0, sticky='w', pady=8)
        self.dod_var = tk.StringVar()
        dod_entry = ttk.Entry(scrollable_frame, textvariable=self.dod_var, width=40, font=('Segoe UI', 10))
        dod_entry.grid(row=row, column=1, sticky='ew', pady=8)
        row += 1
        
        # Birth Place
        ttk.Label(scrollable_frame, text="Comune di Nascita *:", font=('Segoe UI', 10)).grid(row=row, column=0, sticky='w', pady=8)
        self.birthplace_var = tk.StringVar()
        birthplace_entry = ttk.Entry(scrollable_frame, textvariable=self.birthplace_var, width=40, font=('Segoe UI', 10))
        birthplace_entry.grid(row=row, column=1, sticky='ew', pady=8)
        row += 1
        
        # Gender
        ttk.Label(scrollable_frame, text="Sesso:", font=('Segoe UI', 10)).grid(row=row, column=0, sticky='w', pady=8)
        self.gender_var = tk.StringVar(value="M")
        gender_frame = ttk.Frame(scrollable_frame)
        gender_frame.grid(row=row, column=1, sticky='w', pady=8)
        ttk.Radiobutton(gender_frame, text="Maschio", variable=self.gender_var, value="M").pack(side='left', padx=(0, 15))
        ttk.Radiobutton(gender_frame, text="Femmina", variable=self.gender_var, value="F").pack(side='left')
        row += 1
        
        # Fiscal Code (manual or calculated)
        ttk.Label(scrollable_frame, text="Codice Fiscale *:", font=('Segoe UI', 10)).grid(row=row, column=0, sticky='w', pady=8)
        self.fiscal_code_var = tk.StringVar()
        fiscal_code_entry = ttk.Entry(scrollable_frame, textvariable=self.fiscal_code_var, width=40, font=('Segoe UI', 10))
        fiscal_code_entry.grid(row=row, column=1, sticky='ew', pady=8)
        row += 1
        
        # Calculate button
        calc_btn = ttk.Button(
            scrollable_frame,
            text="🔢 Calcola Codice Fiscale",
            command=self.calculate_fiscal_code
        )
        calc_btn.grid(row=row, column=1, sticky='w', pady=5)
        row += 1
        
        # Separator
        ttk.Separator(scrollable_frame, orient='horizontal').grid(row=row, column=0, columnspan=2, sticky='ew', pady=15)
        row += 1
        
        # Allergies
        ttk.Label(scrollable_frame, text="Allergie:", font=('Segoe UI', 10)).grid(row=row, column=0, sticky='nw', pady=8)
        allergies_frame = ttk.Frame(scrollable_frame)
        allergies_frame.grid(row=row, column=1, sticky='ew', pady=8)
        self.allergies_text = tk.Text(allergies_frame, height=3, width=40, wrap='word', font=('Segoe UI', 10))
        self.allergies_text.pack(side='left', fill='both', expand=True)
        allergies_scroll = ttk.Scrollbar(allergies_frame, command=self.allergies_text.yview)
        allergies_scroll.pack(side='right', fill='y')
        self.allergies_text.config(yscrollcommand=allergies_scroll.set)
        ttk.Label(scrollable_frame, text="(Una per riga)", font=('Segoe UI', 8), foreground='gray').grid(row=row+1, column=1, sticky='w')
        row += 2
        
        # Malattie Permanenti
        ttk.Label(scrollable_frame, text="Malattie Permanenti:", font=('Segoe UI', 10)).grid(row=row, column=0, sticky='nw', pady=8)
        diseases_frame = ttk.Frame(scrollable_frame)
        diseases_frame.grid(row=row, column=1, sticky='ew', pady=8)
        self.diseases_text = tk.Text(diseases_frame, height=4, width=40, wrap='word', font=('Segoe UI', 10))
        self.diseases_text.pack(side='left', fill='both', expand=True)
        diseases_scroll = ttk.Scrollbar(diseases_frame, command=self.diseases_text.yview)
        diseases_scroll.pack(side='right', fill='y')
        self.diseases_text.config(yscrollcommand=diseases_scroll.set)
        ttk.Label(scrollable_frame, text="(es: diabete, celiachia, malattie cardiovascolari, neurodegenerative - Una per riga)", font=('Segoe UI', 8), foreground='gray').grid(row=row+1, column=1, sticky='w')
        row += 2
        
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
            text="✅ Salva Paziente",
            command=self.save
        )
        save_btn.pack(side='right', padx=5)
    
    def calculate_fiscal_code(self):
        """Calculate Italian fiscal code following official rules."""
        name = self.name_var.get().strip().upper()
        surname = self.surname_var.get().strip().upper()
        dob = self.dob_var.get().strip()
        birthplace = self.birthplace_var.get().strip().upper()
        
        # Validate inputs
        if not name or not surname or not dob or not birthplace:
            messagebox.showwarning("Attenzione", "Compilare Nome, Cognome, Data di Nascita e Comune di Nascita prima di calcolare il codice fiscale")
            return
        
        # Get gender from radio button
        gender = self.gender_var.get()
        
        # Parse date (GG/MM/AAAA)
        try:
            day, month, year = [x.strip() for x in dob.split('/')]
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
        
        if not self.fiscal_code_var.get().strip():
            messagebox.showerror("Errore", "Codice Fiscale è obbligatorio")
            return False
        
        # Validate date format (GG/MM/AAAA) for birth date
        try:
            day, month, year = [x.strip() for x in self.dob_var.get().strip().split('/')]
            datetime(int(year), int(month), int(day))
        except:
            messagebox.showerror("Errore", "Formato Data di Nascita non valido (usa GG/MM/AAAA, es: 15/06/1975)")
            return False
        
        # Validate date of death if provided
        if self.dod_var.get().strip():
            try:
                day, month, year = [x.strip() for x in self.dod_var.get().strip().split('/')]
                datetime(int(year), int(month), int(day))
            except:
                messagebox.showerror("Errore", "Formato Data del Decesso non valido (usa GG/MM/AAAA)")
                return False
        
        return True
    
    def get_patient_data(self):
        """Get patient demographic data from form."""
        # Parse text fields
        allergies = [line.strip() for line in self.allergies_text.get(1.0, tk.END).split('\n') if line.strip()]
        diseases = [line.strip() for line in self.diseases_text.get(1.0, tk.END).split('\n') if line.strip()]
        
        # Convert date format from GG/MM/AAAA to AAAA-MM-GG for internal use
        dob_input = self.dob_var.get().strip()
        try:
            day, month, year = [x.strip() for x in dob_input.split('/')]
            dob_formatted = f"{year}-{month.zfill(2)}-{day.zfill(2)}"
        except:
            dob_formatted = dob_input
        
        # Convert date of death if provided
        dod_formatted = None
        dod_input = self.dod_var.get().strip()
        if dod_input:
            try:
                day, month, year = [x.strip() for x in dod_input.split('/')]
                dod_formatted = f"{year}-{month.zfill(2)}-{day.zfill(2)}"
            except:
                dod_formatted = dod_input
        
        fiscal_code = self.fiscal_code_var.get().strip()
        
        data = {
            "patient_id": fiscal_code,  # Use fiscal code as patient ID
            "nome": self.name_var.get().strip(),
            "cognome": self.surname_var.get().strip(),
            "data_nascita": dob_formatted,
            "data_decesso": dod_formatted,
            "comune_nascita": self.birthplace_var.get().strip(),
            "codice_fiscale": fiscal_code,
            "gender": self.gender_var.get(),  # M or F
            "allergie": allergies if allergies else [],
            "malattie_permanenti": diseases if diseases else []
        }
        
        return data
    
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
