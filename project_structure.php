f1_dashboard/
│
├── app.py                     # Hauptdatei zum Starten der Flask-App
├── data_fetcher.py            # Modul für die Datenabfrage über Formula One API
├── data_processor.py          # Modul für die Datenverarbeitung
├── data_cache.py              # Modul für die Datenspeicherung
│
├── templates/
│   ├── index.html             # Haupt-HTML-Datei für die Startseite
│   ├── driver_profile.html    # HTML Vorlage für Fahrersteckbrief
│   └── racetrack.html         # HTML Vorlage für die Rennstrecke
│
├── static/
│   ├── css/
│   │   └── styles.css         # CSS-Datei für Styles
│   ├── js/
│   │   └── script.js          # JavaScript für Interaktivität
│
└── cache/
    ├── driver_standings.json
    ├── constructor_standings.json
    ├── race_schedule.json
    ├── {driver_id}_results.json
    └── {constructor}_results.json