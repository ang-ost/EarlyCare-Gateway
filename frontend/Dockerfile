# Frontend Dockerfile per EarlyCare Gateway
FROM node:18-alpine as build

# Imposta la directory di lavoro
WORKDIR /app

# Copia i file di configurazione del package
COPY package*.json ./

# Installa le dipendenze
RUN npm install

# Copia il codice sorgente
COPY . .

# Build dell'applicazione
RUN npm run build

# Stage di produzione con Nginx
FROM nginx:alpine

# Copia i file buildati da stage precedente
COPY --from=build /app/dist /usr/share/nginx/html

# Copia configurazione Nginx personalizzata
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Espone la porta 80
EXPOSE 80

# Avvia Nginx
CMD ["nginx", "-g", "daemon off;"]
