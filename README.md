# EarlyCare Gateway - Early Disease Diagnosis System

![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![HIPAA Compliant](https://img.shields.io/badge/HIPAA-Compliant-brightgreen)

## Overview

EarlyCare Gateway is an intelligent clinical data routing system designed for early disease diagnosis. It routes clinical data (text, signals, images) through configurable checks and enrichments before providing AI-powered decision support. The system emphasizes **privacy**, **traceability**, and **configurable response times** while keeping AI models swappable by pathology, device, or domain.

## 🎯 Key Features

- **Multi-Modal Data Support**: Handles text (clinical notes), signals (ECG, EEG), and images (CT, MRI, X-rays)
- **Intelligent Routing**: Chain of Responsibility pattern for flexible data processing pipelines
- **Swappable AI Models**: Strategy pattern allows models to be changed by pathology, device, or clinical domain
- **Real-Time Monitoring**: Observer pattern for metrics, audit trails, and performance tracking
- **Clinical System Integration**: Facade pattern for seamless HL7, FHIR, and DICOM integration
- **HIPAA Compliant**: Built-in anonymization, encryption, and comprehensive audit logging
- **Configurable Triage**: Automatic patient prioritization with configurable response times

## 🏗️ Architecture

### Design Patterns

1. **Chain of Responsibility**: Data flows through validation → enrichment → triage → processing
2. **Strategy**: AI models are swappable based on pathology, device type, or clinical domain
3. **Observer**: Real-time monitoring of system performance, metrics, and audit events
4. **Facade**: Unified interface for HL7, FHIR, and DICOM clinical systems

### System Components

```
EarlyCare-Gateway/
├── src/
│   ├── models/           # Domain models (Patient, ClinicalData, DecisionSupport)
│   ├── gateway/          # Core gateway and chain handlers
│   ├── strategy/         # AI model strategies (pathology, device, domain)
│   ├── observer/         # Monitoring and audit observers
│   ├── facade/           # Clinical system adapters (HL7, FHIR, DICOM)
│   └── privacy/          # Security (anonymization, encryption, audit)
├── config/               # Configuration files
├── examples/             # Usage examples
└── tests/                # Unit and integration tests
```

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/your-org/earlycare-gateway.git
cd earlycare-gateway

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Basic Usage

```python
from src.gateway.clinical_gateway import ClinicalGateway
from src.models.patient import Patient, PatientRecord
from src.models.clinical_data import TextData, DataSource
from src.strategy.strategy_selector import StrategySelector
from src.observer.metrics_observer import MetricsObserver, AuditObserver
from datetime import datetime

# Initialize gateway
gateway = ClinicalGateway()

# Set up monitoring
metrics = MetricsObserver()
audit = AuditObserver()
gateway.attach_observer(metrics)
gateway.attach_observer(audit)

# Configure model strategy
strategy_selector = StrategySelector.create_default_selector()
gateway.set_strategy_selector(strategy_selector)

# Create patient record
patient = Patient(
    patient_id="P12345",
    date_of_birth=datetime(1975, 6, 15),
    gender=Gender.MALE,
    medical_record_number="MRN-12345",
    chief_complaint="Chest pain and shortness of breath"
)

record = PatientRecord(patient=patient, priority="urgent")

# Add clinical data
clinical_note = TextData(
    data_id="NOTE-001",
    patient_id="P12345",
    timestamp=datetime.now(),
    source=DataSource.EHR,
    text_content="Patient presents with chest pain radiating to left arm...",
    document_type="emergency_note"
)
record.add_clinical_data(clinical_note)

# Process through gateway
decision_support = gateway.process_request(record)

# View results
print(f"Urgency: {decision_support.urgency_level.value}")
print(f"Top Diagnosis: {decision_support.get_top_diagnosis().condition}")
print(f"Processing Time: {decision_support.processing_time_ms:.2f}ms")
```

## 📊 Processing Pipeline

The gateway routes clinical data through a configurable chain:

1. **ValidationHandler**: Validates data quality and completeness
2. **EnrichmentHandler**: Adds context and metadata
3. **TriageHandler**: Calculates urgency scores
4. **PrivacyCheckHandler**: Ensures compliance and anonymization
5. **Strategy Execution**: AI models analyze data and generate diagnosis

## 🔒 Security & Privacy

### HIPAA Compliance

- **Data Anonymization**: Automatic PII removal and pseudonymization
- **Encryption**: AES-256 encryption for data at rest and in transit
- **Audit Logging**: Comprehensive, tamper-evident audit trails
- **Access Control**: Role-based access with full audit

### Example: Anonymizing Patient Data

```python
from src.privacy.anonymizer import DataAnonymizer

anonymizer = DataAnonymizer()

# Anonymize text
anonymized_text = anonymizer.anonymize_text(
    "Patient John Doe, SSN 123-45-6789, called from 555-123-4567"
)
# Result: "Patient [NAME], SSN [SSN-REDACTED], called from [PHONE-REDACTED]"

# Generate pseudonym
pseudonym = anonymizer.generate_pseudonym("P12345", "patient")
# Result: "ANON_PATIENT_a3f2c1b..."
```

## 🔌 Clinical System Integration

### Connecting to FHIR Server

```python
from src.facade.clinical_facade import ClinicalSystemFacade

facade = ClinicalSystemFacade()

# Connect to FHIR server
facade.connect_to_system('fhir', {
    'base_url': 'https://fhir.hospital.org/api',
    'api_key': 'your-api-key'
})

# Import patient data
record = facade.import_patient_data('fhir', 'Patient/12345')

# Process through gateway
decision_support = gateway.process_request(record)

# Export results back to EHR
facade.export_decision_support('fhir', decision_support, 'Patient/12345')
```

## 📈 Monitoring & Observability

### Real-Time Metrics

```python
from src.observer.metrics_observer import MetricsObserver, PerformanceObserver

# Attach observers
metrics = MetricsObserver()
performance = PerformanceObserver(alert_threshold_ms=5000)

gateway.attach_observer(metrics)
gateway.attach_observer(performance)

# Get metrics after processing
stats = metrics.get_metrics()
print(f"Total Requests: {stats['requests_total']}")
print(f"Avg Processing Time: {stats['avg_processing_time_ms']:.2f}ms")
print(f"Success Rate: {stats['success_rate']:.2%}")
```

## 🧠 AI Model Strategies

### Swappable Models by Domain

```python
from src.strategy.model_strategy import DomainStrategy, PathologyStrategy
from src.strategy.strategy_selector import StrategySelector

# Create custom strategy selector
selector = StrategySelector()

# Register domain-specific strategies
selector.register_strategy(DomainStrategy("cardiology"))
selector.register_strategy(DomainStrategy("neurology"))
selector.register_strategy(PathologyStrategy("cancer"))

# Enable ensemble mode for multiple models
selector.enable_ensemble(True)

gateway.set_strategy_selector(selector)
```

## 🧪 Testing

```bash
# Run unit tests
pytest tests/unit

# Run integration tests
pytest tests/integration

# Run with coverage
pytest --cov=src tests/
```

## 📝 Configuration

Configuration files are located in `config/`:

- `gateway_config.yaml`: Gateway and chain settings
- `models_config.yaml`: AI model configurations
- `privacy_config.yaml`: Security and privacy settings
- `integrations_config.yaml`: Clinical system connections

## 🔧 Advanced Features

### Custom Chain Handlers

```python
from src.gateway.chain_handler import ChainHandler

class CustomValidationHandler(ChainHandler):
    def _process(self, record, context):
        # Custom validation logic
        return record

# Add to gateway
gateway.set_processing_chain([
    CustomValidationHandler(),
    EnrichmentHandler(),
    TriageHandler()
])
```

### Performance Tuning

- Configure response time thresholds
- Enable/disable specific validators
- Adjust triage scoring weights
- Control model ensemble behavior

## 📄 License

This project is licensed under the MIT License - see LICENSE file for details.

## 🤝 Contributing

Contributions are welcome! Please read CONTRIBUTING.md for guidelines.

## 📞 Support

For questions and support, please open an issue on GitHub or contact the development team.

## ⚠️ Disclaimer

This system is designed for clinical decision support and should not replace professional medical judgment. All diagnoses should be reviewed by qualified healthcare professionals.

## 🗺️ Roadmap

- [ ] Real-time signal processing for wearable devices
- [ ] Multi-language NLP support
- [ ] Federated learning capabilities
- [ ] Mobile application integration
- [ ] Cloud deployment templates (AWS, Azure, GCP)
- [ ] Advanced explainability features (SHAP, LIME)

---

**Built with ❤️ for better healthcare outcomes**
