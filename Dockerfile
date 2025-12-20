# Backend Dockerfile per EarlyCare Gateway
FROM python:3.11-slim

# Imposta la directory di lavoro
WORKDIR /app

# Installa le dipendenze di sistema necessarie
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copia i file dei requisiti
COPY requirements.txt .

# Installa le dipendenze Python
RUN pip install --no-cache-dir -r requirements.txt

# Installa dipendenze aggiuntive per Flask e MongoDB
RUN pip install --no-cache-dir \
    flask>=3.0.0 \
    pymongo>=4.6.0 \
    google-generativeai>=0.3.0

# Copia il codice sorgente
COPY . .

# Crea le directory necessarie
RUN mkdir -p webapp/uploads/exports cartelle_cliniche/template

# Espone la porta dell'applicazione
EXPOSE 5000

# Variabili d'ambiente di default
ENV FLASK_APP=webapp/app.py
ENV FLASK_ENV=production
ENV PYTHONUNBUFFERED=1

# Comando per avviare l'applicazione
CMD ["python", "-m", "flask", "run", "--host=0.0.0.0", "--port=5000"]
