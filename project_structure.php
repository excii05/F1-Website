f1_dashboard/
│
├── app.py                     # Hauptdatei zum Starten der Flask-App
├── data_fetcher.py            # Modul für die Datenabfrage über Formula One API
├── data_processor.py          # Modul für die Datenverarbeitung
├── data_cache.py              # Modul für die Datenspeicherung
│
├── templates/
│   ├── index.html             # Haupt-HTML-Datei für die Startseite
│   ├── driver_profile.html    # HTML Vorlage für den Fahrersteckbrief
│   ├── constructor_profile.html    # HTML Vorlage für den Konstrukteurssteckbrief
│   └── racetrack.html         # HTML Vorlage für die Rennstrecke
│
├── static/
│   ├── css/
│   │   └── styles.css         # CSS-Datei für Styles
│   ├── js/
│   │   └── script.js          # JavaScript für Interaktivität
│
├── cache/
│   ├── season_folder/
│   │   ├── results_folder/
│   │   │   └── race_id_folder/
│   │   │       ├── lap_times.json
│   │   │       └──race_results.json
│   │   ├── driver_standings.json
│   │   ├── constructor_standings.json
│   │   └── race_schedule.json
│   ├── drivers_folder/
│   └── translations.json