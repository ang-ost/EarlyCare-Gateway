"""
Patient Search Form - Form per cercare e accedere alla cartella clinica del paziente
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, Callable, Dict, Any


class PatientSearchDialog:
    """Dialog per cercare un paziente e accedere alla sua cartella clinica."""
    
    def __init__(self, parent, callback=None):
        """
        Initialize patient search dialog.
        
        Args:
            parent: Parent window
            callback: Function to call when patient is found (receives patient data)
        """
        self.parent = parent
        self.callback = callback
        self.result = None
        
        # Create dialog window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("🔍 Ricerca Paziente")
        self.dialog.geometry("600x400")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (600 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (400 // 2)
        self.dialog.geometry(f"+{x}+{y}")
        
        # Create form
        self.create_form()
    
    def create_form(self):
        """Create the patient search form."""
        # Main container
        main_frame = ttk.Frame(self.dialog, padding=30)
        main_frame.pack(fill='both', expand=True)
        
        # Form title
        title_label = ttk.Label(
            main_frame,
            text="🔍 Ricerca Paziente",
            font=('Segoe UI', 18, 'bold')
        )
        title_label.pack(pady=(0, 20))
        
        subtitle_label = ttk.Label(
            main_frame,
            text="Inserisci il Codice Fiscale oppure Nome e Cognome",
            font=('Segoe UI', 10),
            foreground='gray'
        )
        subtitle_label.pack(pady=(0, 30))
        
        # Search fields frame
        search_frame = ttk.Frame(main_frame)
        search_frame.pack(fill='x', pady=10)
        
        # Codice Fiscale
        cf_frame = ttk.Frame(search_frame)
        cf_frame.pack(fill='x', pady=10)
        
        ttk.Label(
            cf_frame,
            text="Codice Fiscale:",
            font=('Segoe UI', 11, 'bold')
        ).pack(side='left', padx=(0, 10))
        
        self.codice_fiscale_var = tk.StringVar()
        cf_entry = ttk.Entry(
            cf_frame,
            textvariable=self.codice_fiscale_var,
            width=30,
            font=('Segoe UI', 11)
        )
        cf_entry.pack(side='left', fill='x', expand=True)
        cf_entry.bind('<Return>', lambda e: self.search_patient())
        
        # Separator
        separator_frame = ttk.Frame(search_frame)
        separator_frame.pack(fill='x', pady=15)
        
        ttk.Separator(separator_frame, orient='horizontal').pack(side='left', fill='x', expand=True, padx=(0, 10))
        ttk.Label(separator_frame, text="OPPURE", font=('Segoe UI', 9), foreground='gray').pack(side='left')
        ttk.Separator(separator_frame, orient='horizontal').pack(side='left', fill='x', expand=True, padx=(10, 0))
        
        # Nome
        nome_frame = ttk.Frame(search_frame)
        nome_frame.pack(fill='x', pady=10)
        
        ttk.Label(
            nome_frame,
            text="Nome:",
            font=('Segoe UI', 11, 'bold'),
            width=15
        ).pack(side='left', padx=(0, 10))
        
        self.nome_var = tk.StringVar()
        ttk.Entry(
            nome_frame,
            textvariable=self.nome_var,
            width=30,
            font=('Segoe UI', 11)
        ).pack(side='left', fill='x', expand=True)
        
        # Cognome
        cognome_frame = ttk.Frame(search_frame)
        cognome_frame.pack(fill='x', pady=10)
        
        ttk.Label(
            cognome_frame,
            text="Cognome:",
            font=('Segoe UI', 11, 'bold'),
            width=15
        ).pack(side='left', padx=(0, 10))
        
        self.cognome_var = tk.StringVar()
        cognome_entry = ttk.Entry(
            cognome_frame,
            textvariable=self.cognome_var,
            width=30,
            font=('Segoe UI', 11)
        )
        cognome_entry.pack(side='left', fill='x', expand=True)
        cognome_entry.bind('<Return>', lambda e: self.search_patient())
        
        # Message label
        self.message_var = tk.StringVar()
        self.message_label = ttk.Label(
            main_frame,
            textvariable=self.message_var,
            font=('Segoe UI', 10),
            foreground='red'
        )
        self.message_label.pack(pady=20)
        
        # Buttons frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(side='bottom', fill='x', pady=(20, 0))
        
        # Search button
        search_btn = ttk.Button(
            button_frame,
            text="🔍 Cerca Paziente",
            command=self.search_patient,
            style='Primary.TButton'
        )
        search_btn.pack(side='left', padx=5, ipadx=20, ipady=5)
        
        # Cancel button
        cancel_btn = ttk.Button(
            button_frame,
            text="❌ Annulla",
            command=self.cancel
        )
        cancel_btn.pack(side='right', padx=5, ipadx=20, ipady=5)
    
    def search_patient(self):
        """Execute patient search."""
        codice_fiscale = self.codice_fiscale_var.get().strip().upper()
        nome = self.nome_var.get().strip()
        cognome = self.cognome_var.get().strip()
        
        # Validate input
        if not codice_fiscale and not (nome and cognome):
            self.message_var.set("⚠️ Inserire il Codice Fiscale oppure Nome e Cognome")
            return
        
        # Build search criteria
        search_criteria = {}
        if codice_fiscale:
            search_criteria['codice_fiscale'] = codice_fiscale
        if nome:
            search_criteria['nome'] = nome
        if cognome:
            search_criteria['cognome'] = cognome
        
        self.result = search_criteria
        
        # Call callback if provided
        if self.callback:
            self.callback(search_criteria)
        
        # Close dialog
        self.dialog.destroy()
    
    def cancel(self):
        """Cancel search."""
        self.result = None
        self.dialog.destroy()
    
    def show(self):
        """Show dialog and wait for result."""
        self.dialog.wait_window()
        return self.result
