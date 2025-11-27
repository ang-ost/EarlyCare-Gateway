"""
Clinical Folder Processor - Command Line Tool

Process a complete clinical folder through the EarlyCare Gateway.

Usage:
    python process_clinical_folder.py <folder_path>
    python process_clinical_folder.py --create-template <output_path>

Examples:
    # Process an existing folder
    python process_clinical_folder.py clinical_data/patient_001
    
    # Create a template folder
    python process_clinical_folder.py --create-template clinical_data/template
"""

import sys
import argparse
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.gateway.clinical_gateway import ClinicalGateway
from src.gateway.folder_processor import ClinicalFolderProcessor
from src.strategy.strategy_selector import StrategySelector
from src.observer.metrics_observer import MetricsObserver, AuditObserver


def print_header(text: str):
    """Print formatted header."""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70)


def print_results(decision_support):
    """Print decision support results."""
    print_header("📊 RISULTATI DIAGNOSI")
    
    print(f"\n🆔 Request ID: {decision_support.request_id}")
    print(f"👤 Paziente: {decision_support.patient_id}")
    print(f"⏱️  Tempo di elaborazione: {decision_support.processing_time_ms:.2f}ms")
    print(f"🚨 Livello di urgenza: {decision_support.urgency_level.value.upper()}")
    print(f"📈 Punteggio triage: {decision_support.triage_score:.1f}/100")
    
    if decision_support.diagnoses:
        print(f"\n💊 DIAGNOSI ({len(decision_support.diagnoses)}):")
        for i, diagnosis in enumerate(decision_support.diagnoses, 1):
            print(f"\n  {i}. {diagnosis.condition}")
            print(f"     Confidenza: {diagnosis.confidence_score:.1%} ({diagnosis.confidence_level.value})")
            
            if diagnosis.evidence:
                print(f"     Evidenze: {', '.join(diagnosis.evidence[:3])}")
            
            if diagnosis.recommended_tests:
                print(f"     Test raccomandati: {', '.join(diagnosis.recommended_tests[:3])}")
            
            if diagnosis.recommended_specialists:
                print(f"     Specialisti: {', '.join(diagnosis.recommended_specialists[:2])}")
    
    if decision_support.alerts:
        print(f"\n⚠️  ALERT:")
        for alert in decision_support.alerts:
            print(f"     • {alert}")
    
    if decision_support.warnings:
        print(f"\n⚡ AVVISI:")
        for warning in decision_support.warnings:
            print(f"     • {warning}")
    
    if decision_support.clinical_notes:
        print(f"\n📝 NOTE CLINICHE:")
        for note in decision_support.clinical_notes:
            print(f"     • {note}")
    
    print(f"\n🤖 Modelli utilizzati: {', '.join(decision_support.models_used)}")
    
    if decision_support.explanation:
        print(f"\n💡 Spiegazione:")
        print(f"   {decision_support.explanation}")


def process_file_or_folder(path: str, gateway: ClinicalGateway):
    """Process a clinical file or folder."""
    processor = ClinicalFolderProcessor(gateway)
    
    try:
        path_obj = Path(path)
        
        # Check if it's a file or folder
        if path_obj.is_file():
            # Process single file
            decision_support = processor.process_single_file(path)
        elif path_obj.is_dir():
            # Process folder
            decision_support = processor.process_folder(path)
        else:
            raise ValueError(f"Path not found or invalid: {path}")
        
        # Print results
        print_results(decision_support)
        
        # Save results to file
        if path_obj.is_file():
            output_file = path_obj.parent / f"results_{path_obj.stem}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        else:
            output_file = path_obj / f"results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            import json
            json.dump(decision_support.to_dict(), f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Risultati salvati in: {output_file}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Errore durante l'elaborazione: {e}")
        import traceback
        traceback.print_exc()
        return False


def create_template(output_path: str):
    """Create a template clinical folder."""
    processor = ClinicalFolderProcessor()
    
    try:
        processor.create_folder_template(output_path)
        print(f"\n✅ Template creato con successo!")
        print(f"\nPer utilizzarlo:")
        print(f"  1. Modifica patient_info.json con i dati del paziente")
        print(f"  2. Aggiungi note cliniche in notes/")
        print(f"  3. Aggiungi dati segnale in signals/")
        print(f"  4. Aggiungi immagini in images/")
        print(f"  5. Esegui: python process_clinical_folder.py {output_path}")
        return True
        
    except Exception as e:
        print(f"\n❌ Errore nella creazione del template: {e}")
        return False


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description='Process clinical folder through EarlyCare Gateway',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Esempi:
  # Elabora una cartella clinica
  python process_clinical_folder.py clinical_data/patient_001
  
  # Elabora un singolo file
  python process_clinical_folder.py clinical_data/patient_001/notes/admission.txt
  
  # Crea un template di cartella
  python process_clinical_folder.py --create-template clinical_data/template
        """
    )
    
    parser.add_argument(
        'path',
        nargs='?',
        help='Path del file o cartella clinica da elaborare'
    )
    
    parser.add_argument(
        '--create-template',
        dest='template_path',
        help='Crea una cartella template nel path specificato'
    )
    
    parser.add_argument(
        '--no-monitoring',
        action='store_true',
        help='Disabilita monitoring e metriche'
    )
    
    args = parser.parse_args()
    
    # Print banner
    print_header("🏥 EarlyCare Gateway - Clinical Folder Processor")
    
    # Create template mode
    if args.template_path:
        return 0 if create_template(args.template_path) else 1
    
    # Process mode
    if not args.path:
        parser.print_help()
        return 1
    
    # Initialize gateway
    print("\n⚙️  Inizializzazione gateway...")
    gateway = ClinicalGateway()
    
    # Setup monitoring
    if not args.no_monitoring:
        metrics = MetricsObserver()
        audit = AuditObserver(log_file="logs/folder_processor_audit.log")
        gateway.attach_observer(metrics)
        gateway.attach_observer(audit)
        print("   ✓ Monitoring attivato")
    
    # Setup AI strategies
    strategy_selector = StrategySelector.create_default_selector()
    strategy_selector.enable_ensemble(True)
    gateway.set_strategy_selector(strategy_selector)
    print("   ✓ Strategie AI configurate")
    
    # Process file or folder
    success = process_file_or_folder(args.path, gateway)
    
    # Show metrics
    if not args.no_monitoring and success:
        print_header("📊 METRICHE DI SISTEMA")
        stats = metrics.get_metrics()
        print(f"\nRichieste elaborate: {stats['requests_completed']}")
        print(f"Tempo medio elaborazione: {stats['avg_processing_time_ms']:.2f}ms")
        print(f"Success rate: {stats['success_rate']:.1%}")
    
    print("\n" + "=" * 70)
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
