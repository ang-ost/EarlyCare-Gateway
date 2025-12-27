"""
Medical Diagnostics AI Module
Provides AI-powered medical diagnostics based on patient clinical records
Powered by Google Gemini
"""

import google.generativeai as genai
from typing import Dict, Optional, List
import json
from datetime import datetime
import time


class MedicalDiagnosticsAI:
    """
    AI-powered medical diagnostics assistant using Google Gemini.
    Analyzes patient clinical data and provides diagnostic insights.
    """
    
    def __init__(self, api_key: str):
        """
        Initialize the Medical Diagnostics AI.
        
        Args:
            api_key: Google Gemini API key
        """
        self.api_key = api_key
        
        # Configure Gemini
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-3-flash-preview')
        self.model_name = 'gemini-3-flash-preview'
        
        # System prompt for medical diagnostics
        self.system_prompt = """Sei un assistente medico AI per diagnostica clinica e supporto decisionale.

REGOLE:
- Scrivi in testo semplice, NO Markdown (no *, #, -)
- Analisi completa e dettagliata
- Considera tutti i dati clinici disponibili
- Terminologia medica italiana professionale
- NOTA: Supporto decisionale - diagnosi finale spetta al medico

STRUTTURA RISPOSTA:

ANALISI DATI CLINICI:
Esamina anamnesi, sintomi, segni vitali, esami. Interpretazione clinica.

QUADRO CLINICO:
Descrizione complessiva e fisiopatologia dei sintomi.

DIAGNOSI PRESUNTIVA:
Diagnosi principale più probabile con ragionamento clinico.

DIAGNOSI DIFFERENZIALI:
Altre possibili diagnosi con elementi pro/contro.

ESAMI CONSIGLIATI:
Quali esami fare, perché e risultati attesi.

PIANO TERAPEUTICO:
Farmaci (dosaggi, vie, durata), terapie non farmacologiche, stile di vita.

MONITORAGGIO:
Parametri da monitorare, frequenza, controlli successivi.

URGENZA:
Livello di urgenza e priorità intervento.

PRECAUZIONI:
Controindicazioni, allergie, interazioni farmacologiche.

PROGNOSI:
Tempi recupero, possibili complicanze.
"""
    
    def generate_diagnosis(self, patient_data: Dict) -> Dict:
        """
        Generate a medical diagnosis based on patient clinical data.
        Implements retry logic with exponential backoff.
        
        Args:
            patient_data: Dictionary containing patient information and clinical data
            
        Returns:
            Dictionary with diagnosis, confidence, and recommendations
        """
        max_retries = 3
        retry_delay = 1  # seconds
        
        for attempt in range(max_retries):
            try:
                return self._generate_with_gemini(patient_data)
            except Exception as e:
                print(f"[AI] Tentativo Gemini {attempt + 1}/{max_retries} fallito: {e}")
                
                # If last attempt, raise error
                if attempt == max_retries - 1:
                    raise
                
                # Wait before retry with exponential backoff
                wait_time = retry_delay * (2 ** attempt)
                print(f"[AI] Attendo {wait_time}s prima di riprovare...")
                time.sleep(wait_time)
        
        raise Exception("Tutti i tentativi falliti")
    
    def _generate_with_gemini(self, patient_data: Dict) -> Dict:
        """Generate diagnosis using Google Gemini API with multimodal support."""
        # Format patient data for analysis
        print(f"[AI] Formatting patient data...")
        formatted_data = self._format_patient_data(patient_data)
        print(f"[AI] Patient data formatted, length: {len(formatted_data)} chars")
        
        # Check for attachments (images, documents)
        attachments = patient_data.get('allegati', [])
        has_multimodal_content = False
        image_parts = []
        
        if attachments and isinstance(attachments, list):
            print(f"[AI] Processing {len(attachments)} attachments...")
            import base64
            from PIL import Image
            import io
            
            for att in attachments:
                if isinstance(att, dict) and 'content' in att and 'type' in att:
                    file_type = att['type']
                    file_name = att.get('name', 'unknown')
                    
                    # Process images
                    if file_type.startswith('image/'):
                        try:
                            # Decode base64 image
                            image_data = base64.b64decode(att['content'])
                            image = Image.open(io.BytesIO(image_data))
                            
                            # Convert to RGB if necessary (Gemini requires RGB)
                            if image.mode != 'RGB':
                                image = image.convert('RGB')
                            
                            image_parts.append({
                                'name': file_name,
                                'image': image
                            })
                            has_multimodal_content = True
                            print(f"[AI] Added image: {file_name} ({image.size})")
                        except Exception as e:
                            print(f"[AI] Error processing image {file_name}: {e}")
                    
                    # TODO: Process PDF documents (extract text)
                    elif file_type == 'application/pdf':
                        try:
                            # For now, just note that PDF is attached
                            print(f"[AI] PDF attachment detected: {file_name} (text extraction not yet implemented)")
                        except Exception as e:
                            print(f"[AI] Error processing PDF {file_name}: {e}")
        
        # Create the prompt
        prompt_text = f"""{self.system_prompt}

DATI CLINICI DEL PAZIENTE:

{formatted_data}

Fornisci ora una valutazione diagnostica completa e strutturata."""

        # Add note about attachments if present
        if has_multimodal_content:
            prompt_text += f"\n\nNOTA: Sono presenti {len(image_parts)} immagini allegate. Analizza attentamente le immagini fornite insieme ai dati clinici per una diagnosi più accurata."

        print(f"[AI] Calling Gemini API...")
        
        # Build content parts for multimodal request
        if has_multimodal_content:
            # Multimodal request with images
            content_parts = [prompt_text]
            for img_part in image_parts:
                content_parts.append(img_part['image'])
                content_parts.append(f"\n[Immagine allegata: {img_part['name']}]\n")
            
            response = self.model.generate_content(
                content_parts,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.3,
                    top_p=0.95,
                    top_k=40,
                    max_output_tokens=2048,
                    candidate_count=1,
                )
            )
        else:
            # Text-only request
            response = self.model.generate_content(
                prompt_text,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.3,
                    top_p=0.95,
                    top_k=40,
                    max_output_tokens=2048,
                    candidate_count=1,
                )
            )
        
        print(f"[AI] Response received from Gemini")
        
        # Extract the diagnosis text
        if not response or not hasattr(response, 'text'):
            print(f"[AI] ERROR: Invalid response from Gemini")
            raise Exception("Risposta non valida dall'API Gemini")
        
        diagnosis_text = response.text
        print(f"[AI] Diagnosis text extracted, length: {len(diagnosis_text)} chars")
        
        # Check if response was truncated
        finish_reason = None
        if hasattr(response, 'candidates') and len(response.candidates) > 0:
            candidate = response.candidates[0]
            if hasattr(candidate, 'finish_reason'):
                finish_reason = candidate.finish_reason
        
        # Parse and structure the response
        result = {
            'success': True,
            'diagnosis': diagnosis_text,
            'timestamp': datetime.now().isoformat(),
            'patient_id': patient_data.get('patient_id', 'N/A'),
            'model': self.model_name,
            'metadata': {
                'analysis_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'data_points_analyzed': self._count_data_points(patient_data),
                'attachments_analyzed': len(image_parts) if has_multimodal_content else 0,
                'finish_reason': str(finish_reason) if finish_reason else 'COMPLETE'
            }
        }
        
        return result
    
    def _format_patient_data(self, data: Dict) -> str:
        """Format patient data into a readable text for AI analysis."""
        formatted = []
        
        # Patient Demographics
        if 'patient_id' in data:
            formatted.append(f"ID PAZIENTE: {data['patient_id']}")
        if 'nome' in data:
            formatted.append(f"NOME: {data['nome']}")
        if 'cognome' in data:
            formatted.append(f"COGNOME: {data['cognome']}")
        if 'data_nascita' in data:
            formatted.append(f"DATA DI NASCITA: {data['data_nascita']}")
        if 'eta' in data:
            formatted.append(f"ETÀ: {data['eta']} anni")
        if 'sesso' in data:
            formatted.append(f"SESSO: {data['sesso']}")
        
        formatted.append("")
        
        # Contact Information
        if 'contatto' in data:
            formatted.append("CONTATTI:")
            contatto = data['contatto']
            if isinstance(contatto, dict):
                if 'telefono' in contatto:
                    formatted.append(f"  Telefono: {contatto['telefono']}")
                if 'email' in contatto:
                    formatted.append(f"  Email: {contatto['email']}")
            formatted.append("")
        
        # Medical History
        if 'storia_clinica' in data:
            formatted.append("STORIA CLINICA:")
            storia = data['storia_clinica']
            if isinstance(storia, dict):
                if 'condizioni_preesistenti' in storia:
                    formatted.append("  Condizioni preesistenti:")
                    for cond in storia['condizioni_preesistenti']:
                        formatted.append(f"    - {cond}")
                if 'allergie' in storia:
                    formatted.append("  Allergie:")
                    for all in storia['allergie']:
                        formatted.append(f"    - {all}")
                if 'farmaci_correnti' in storia:
                    formatted.append("  Farmaci correnti:")
                    for farm in storia['farmaci_correnti']:
                        formatted.append(f"    - {farm}")
            formatted.append("")
        
        # Clinical Data
        if 'dati_clinici' in data:
            formatted.append("DATI CLINICI:")
            clinici = data['dati_clinici']
            if isinstance(clinici, dict):
                for key, value in clinici.items():
                    formatted.append(f"  {key}: {value}")
            formatted.append("")
        
        # Vital Signs
        if 'segni_vitali' in data:
            formatted.append("SEGNI VITALI:")
            vitali = data['segni_vitali']
            if isinstance(vitali, dict):
                for key, value in vitali.items():
                    formatted.append(f"  {key}: {value}")
            formatted.append("")
        
        # Symptoms
        if 'sintomi' in data:
            formatted.append("SINTOMI:")
            sintomi = data['sintomi']
            if isinstance(sintomi, list):
                for sint in sintomi:
                    formatted.append(f"  - {sint}")
            else:
                formatted.append(f"  {sintomi}")
            formatted.append("")
        
        # Test Results
        if 'risultati_esami' in data:
            formatted.append("RISULTATI ESAMI:")
            esami = data['risultati_esami']
            if isinstance(esami, dict):
                for esame, risultato in esami.items():
                    formatted.append(f"  {esame}: {risultato}")
            elif isinstance(esami, list):
                for esame in esami:
                    formatted.append(f"  - {esame}")
            formatted.append("")
        
        # Notes
        if 'note' in data:
            formatted.append("NOTE CLINICHE:")
            formatted.append(f"  {data['note']}")
            formatted.append("")
        
        # Admission Note
        if 'nota_ammissione' in data:
            formatted.append("NOTA DI AMMISSIONE:")
            formatted.append(f"  {data['nota_ammissione']}")
            formatted.append("")
        
        # Additional fields - catch all remaining
        excluded_keys = {
            'patient_id', 'nome', 'cognome', 'data_nascita', 'eta', 'sesso',
            'contatto', 'storia_clinica', 'dati_clinici', 'segni_vitali',
            'sintomi', 'risultati_esami', 'note', 'nota_ammissione',
            '_id', 'created_at', 'updated_at', 'doctor_id'
        }
        
        other_data = {k: v for k, v in data.items() if k not in excluded_keys}
        if other_data:
            formatted.append("ALTRI DATI:")
            for key, value in other_data.items():
                if isinstance(value, (dict, list)):
                    formatted.append(f"  {key}: {json.dumps(value, indent=2, ensure_ascii=False)}")
                else:
                    formatted.append(f"  {key}: {value}")
        
        return "\n".join(formatted)
    
    def _count_data_points(self, data: Dict) -> int:
        """Count the number of data points in patient data."""
        count = 0
        
        def count_recursive(obj):
            nonlocal count
            if isinstance(obj, dict):
                count += len(obj)
                for value in obj.values():
                    count_recursive(value)
            elif isinstance(obj, list):
                count += len(obj)
                for item in obj:
                    count_recursive(item)
        
        count_recursive(data)
        return count
    
    def batch_diagnosis(self, patients_data: List[Dict]) -> List[Dict]:
        """
        Generate diagnoses for multiple patients.
        
        Args:
            patients_data: List of patient data dictionaries
            
        Returns:
            List of diagnosis results
        """
        results = []
        for patient_data in patients_data:
            result = self.generate_diagnosis(patient_data)
            results.append(result)
        return results
