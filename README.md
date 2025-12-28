# EarlyCare Gateway - Intelligent Clinical Decision Support System

![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)
![React Version](https://img.shields.io/badge/react-18%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![HIPAA Compliant](https://img.shields.io/badge/HIPAA-Compliant-brightgreen)
![Docker Supported](https://img.shields.io/badge/docker-supported-blue)

## � Introduction & Vision

**EarlyCare Gateway** is an advanced, production-ready software solution designed to bridge the gap between raw clinical data and modern Artificial Intelligence.
It is not just a simple medical record system; it is an intelligent **routing and processing engine** that ingests multi-modal data (text, vital signs, images), validates it, enriches it, and uses state-of-the-art AI to assist healthcare professionals in early disease diagnosis.

The system is built to solve specific challenges in modern healthcare:
1.  **Fragmentation**: Unifying diverse data sources (patient history, current symptoms, imaging).
2.  **Latency**: Providing real-time decision support for triage.
3.  **Privacy**: Ensuring strict HIPAA/GDPR compliance while leveraging cloud AI.
4.  **Reliability**: Handling failure gracefully with fallback mechanisms.

---

## 📋 Table of Contents

1.  [Technical Architecture (Deep Dive)](#-technical-architecture-deep-dive)
2.  [Design Patterns Implemented](#-design-patterns-implemented)
3.  [Technology Stack](#-technology-stack)
4.  [Core Features Detailed](#-core-features-detailed)
5.  [AI & Diagnostics Engine](#-ai--diagnostics-engine)
6.  [Security & Privacy](#-security--privacy)
7.  [Database Schema](#-database-schema)
8.  [Web Application Flow](#-web-application-flow)
9.  [Installation & Setup](#-installation--setup)
10. [Deployment Guide](#-deployment-guide)

---

## 🏗️ Technical Architecture (Deep Dive)

The system follows a **Layered Architecture** with a central **Gateway** component handling the orchestration of data flow.

### The "Gateway" Concept
The core of the backend is the `ClinicalGateway`. Unlike a standard CRUD controller, the Gateway treats every incoming clinical request as a payload that must pass through a strict pipeline of handlers. This ensures no data is ever processed without validation, anonymization, and auditing.

### Data Flow Pipeline
1.  **Ingestion**: Frontend sends a Patient Record (Symptoms + Attachments).
2.  **Gateway Entry**: The request enters the `ClinicalGateway`.
3.  **Processing Chain**:
    *   `ValidationHandler`: Checks data integrity (e.g., valid Fiscal Code, realistic vital signs).
    *   `EnrichmentHandler`: Adds calculated metadata (e.g., Age from DOB, BMI from weight/height).
    *   `PrivacyHandler`: Anonymizes sensitive fields before external processing.
    *   `TriageHandler`: Calculates an initial urgency score based on configured rules.
4.  **Strategy Execution**: The system selects the best AI strategy (e.g., `GeminiStrategy`) to analyze the data.
5.  **Observer Notification**: Auditing and Metrics systems record the transaction result.
6.  **Persistence**: Data is stored in MongoDB.
7.  **Response**: The enriched, analyzed result is returned to the Frontend.

---

## 🧩 Design Patterns Implemented

The robustness of EarlyCare Gateway comes from the strict application of GoF design patterns:

*   **Chain of Responsibility Pattern**: Used in the processing pipeline. Each handler (`Validation`, `Privacy`, `Triage`) decides whether to process the request or pass it along, making the workflow highly extensible.
*   **Strategy Pattern**: Used for AI Models. The system allows hot-swapping the intelligence engine (e.g., distinct strategies for Neurology vs. Cardiology, or Google Gemini vs. OpenAI) without changing the core code.
*   **Observer Pattern**: Used for monitoring. `AuditObserver` and `MetricsObserver` subscribe to gateway events to log activities and track performance metric decoupled from business logic.
*   **Facade Pattern**: (In `src/facade`) Used to standardize interactions with external clinical systems (like potential future HL7/FHIR integrations), providing a simplified interface to the rest of the app.

---

## � Technology Stack

### Backend
*   **Framework**: Python Flask (Micro-framework approach).
*   **Gateway Logic**: Pure Python implementing design patterns.
*   **AI Integration**: Google Generative AI SDK (`google-generativeai`) for reliable multimodal analysis.
*   **PDF Generation**: `ReportLab` for generating professional clinical reports.
*   **Data Validation**: Pydantic models for strict typing.

### Frontend
*   **Framework**: React 18 (Vite).
*   **Styling**: Vanilla modern CSS (Glassmorphism design language).
*   **State Management**: React Hooks & Context API.
*   **Visuals**: Responsive layout with dark/light mode optimization.

### Data & Infrastructure
*   **Database**: MongoDB (NoSQL) for flexible schema (Polymorphic Clinical Data).
*   **Deployment**: Docker & Docker Compose; configured for Render.com (PaaS).

---

## 🌟 Core Features Detailed

### 1. Advanced Patient Management
*   **Dual Identity System**: 
    *   **Italian Citizens**: Validated via strict **Fiscal Code** algorithms (OMOCODA support included).
    *   **Foreign Citizens**: Automatic generation of a unique internal ID (e.g., `FR-XXXX`) to handle tourists or undocumented patients seamlessly.
*   **Persistence**: Full editing capabilities for patient demographics.

### 2. Clinical Records & Triage
*   **Vital Signs Tracking**: Records BP, HR, Temp, Saturation with automatic "Out of Range" highlighting.
*   **Context Awareness**: The system remembers previous visits to provide historical context.

### 3. Professional Reporting
*   **PDF Export**: Generates a header-to-footer professional PDF of the diagnosis.
*   **Smart Pagination**: Ensures clinical notes aren't cut off mid-sentence across pages.

---

## 🧠 AI & Diagnostics Engine

The AI module is not a simple chatbot. It is a **Structured Clinical Analyst**.

*   **Multimodal Input**: It accepts the JSON of the clinical visit **AND** base64-encoded images (X-rays, ECGs, Skin photos) simultaneously.
*   **Structured Output**: The prompt engineering forces the AI to return a specific JSON structure:
    *   *Analysis of Clinical Data* (Symptoms consistency).
    *   *Image Interpretation* (What is seen in the X-ray?).
    *   *Presumptive Diagnosis* (Ranked by probability).
    *   *Suggested Tests* (Next steps).
*   **Retry Logic**: Implements exponential backoff to handle API saturation/timeouts gracefully.

---

## � Security & Privacy

*   **Doctor Authentication**: 
    *   Custom registration flow generating a mnemonic **Doctor ID** (e.g., `MR7X9Z`).
    *   SHA-256 password hashing.
    *   Session-based auth with secure HttpOnly cookies.
*   **Data Protection**:
    *   **At Rest**: MongoDB data is structured to separate PII (Patient Info) from Clinical Data where possible.
    *   **In Transit**: Forced HTTPS on production.
    *   **Audit**: Every "View", "Create", or "Export" action is logged in the `audit_logs` collection for accountability.

---

## 💾 Database Schema

The MongoDB instance uses these primary collections:

1.  `users`: Doctor credentials and specialized profiles.
2.  `patients`: Demographics, indexed by `fiscal_code` or `internal_id`.
3.  `clinical_records`: The central "Episode of Care" linking a patient to a doctor and a date.
4.  `clinical_data`: Polymorphic collection storing the *contents* of a record:
    *   `type: text` (Notes)
    *   `type: image` (Base64 blobs or S3 references)
    *   `type: signal` (Vital signs array)
5.  `audit_logs`: Immutable history of system actions.

---

## 🚀 Installation & Setup

### Option A: Docker (Recommended)
Spin up the full stack (Frontend + Backend + DB) in one command:
```bash
docker-compose up -d --build
```
Access at `http://localhost:80`.

### Option B: Manual Setup

**Backend**:
```bash
cd backend
python -m venv venv
# Activate venv...
pip install -r requirements.txt
# Create .env file with GEMINI_API_KEY
python webapp/app.py
```

**Frontend**:
```bash
cd frontend
npm install
npm run dev
```

---

## 🌐 Deployment Guide (Render)

The repo includes configuration files (`render.yaml` implicit logic) for PaaS deployment.

*   **Environment Variables needed**:
    *   `GEMINI_API_KEY`: For AI.
    *   `MONGODB_URI`: Connection string (Atlas).
    *   `FLASK_SECRET_KEY`: For sessions.
    *   `FRONTEND_URL` / `VITE_API_URL`: For CORS/API linking.

---

## 🔧 Troubleshooting

*   **CORS Errors**: Usually a mismatch between the HTTPS/HTTP protocol or trailing slashes in `VITE_API_URL`.
*   **AI Errors**: If images are too large (>4MB) or non-standard formats, Gemini may reject them. The backend handles resizing automatically in most cases.
*   **Database**: Ensure IP Whitelist on MongoDB Atlas allows the Render server IP.

---

*EarlyCare Gateway: Where Code meets Cure.*
