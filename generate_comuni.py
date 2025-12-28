"""
Script per generare il dizionario completo dei codici catastali italiani
Fonte: comuni-json package NPM
"""

import json
import requests

# Scarica il file comuni.json dal repository GitHub di comuni-json
url = "https://raw.githubusercontent.com/matteocontrini/comuni-json/master/comuni.json"

print("Scaricamento dati comuni italiani...")
response = requests.get(url)
comuni = response.json()

print(f"Trovati {len(comuni)} comuni")

# Crea il dizionario Python
codici_catastali = {}
for comune in comuni:
    nome = comune['nome'].upper()
    codice = comune.get('codiceCatastale', '')
    if codice:
        codici_catastali[nome] = codice

print(f"\nGenerazione dizionario Python con {len(codici_catastali)} comuni...")

# Genera il codice Python
output = "# Codici catastali dei comuni italiani\n"
output += "# Generato automaticamente da comuni-json\n"
output += "COMMON_MUNICIPALITY_CODES = {\n"

for nome, codice in sorted(codici_catastali.items()):
    output += f"    '{nome}': '{codice}',\n"

output += "}\n"

# Salva in un file
with open('codici_catastali_completi.py', 'w', encoding='utf-8') as f:
    f.write(output)

print(f"File generato: codici_catastali_completi.py")
print(f"Totale comuni: {len(codici_catastali)}")
