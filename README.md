# 🎬 Cinema Pegasus - Backend

Questo repository contiene il backend dell'applicazione, responsabile della gestione dell' autenticazione, delle prenotazioni, del mostrare i dati dei film e della generazione dei biglietti in formato PDF.

## 📌 Tecnologie Utilizzate

- **Framework**: Flask
- **Database**: PostgreSQL
- **Gestione delle migrazioni**: Alembic
- **Autenticazione**: Flask-Login
- **ORM**: SQLAlchemy
- **Gestione file**: Cloudinary
- **Generazione PDF**: ReportLab

## 📁 Struttura del Progetto

```bash
├── dto                 # Data Transfer Objects per la gestione dei dati
│   ├── biglietto_dto.py
│   ├── film_dto.py
│   ├── ordini_dto.py
│   ├── posto_dto.py
│   ├── proiezione_dto.py
├── models.py           # Definizione dei modelli del database
├── routes              # Gestione delle API
│   ├── autenticazione.py
│   ├── biglietti.py
│   ├── film.py
│   ├── ordini.py
│   ├── posti.py
│   ├── proiezioni.py
├── services            # Logica applicativa
│   ├── biglietti_service.py
│   ├── film_service.py
│   ├── ordini_service.py
│   ├── posto_service.py
│   ├── proiezione_service.py
├── utils               # Utility generali
│   ├── cloudinary_utils.py
│   ├── pdf_utils.py
└── app.py              # Entry point dell'applicazione
```

## 🚀 Installazione

1. **Clona il repository**
   ```bash
   git clone https://github.com/emanuelep57/projectwork-backend.git
   cd projectwork-backend
   ```

2. **Crea un ambiente virtuale e attivalo**
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```

3. **Installa le dipendenze**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configura le variabili d'ambiente**  
   Crea un file `.env` e aggiungi le seguenti variabili:
   ```env
   DATABASE_URL=postgresql://user:password@localhost:5432/cinema_pegasus
   SECRET_KEY=your_secret_key
   CLOUDINARY_API_SECRET=your_api_secret
   CLOUDINARY_CLOUD_NAME=your_cloudinary_url
   CLOUDINARY_API_KEY=cloudinary_api_key
   ```

5. **Esegui le migrazioni del database**
   ```bash
   flask db upgrade
   ```

6. **Avvia il server**
   ```bash
   flask run
   ```

## 📌 Funzionalità

✅ **Autenticazione degli utenti**  
✅ **Gestione dei film e delle proiezioni**  
✅ **Creazione degli ordini e dei biglietti**  
✅ **Generazione del biglietto in PDF**  
✅ **Gestione dei posti disponibili**

## 📜 Documentazione API
La documentazione è reperibile online, all'URL: https://projectwork-backend.onrender.com/

![documentazione delle api](documentazione-api.png)



