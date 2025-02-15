f1_dashboard/
│
├── app.py                              # Hauptdatei zum Starten der Flask-App
├── data_fetcher.py                     # Modul für die Datenabfrage über Jolpica One API
├── driver_data_fetcher.py              # Modul für die Datenabfrage der allzeit Konstrukteurstatistiken
├── team_data_fetcher.py                # Modul für die Datenabfrage der allzeit Fahrerstatistiken
├── seasonal_data_fetcher.py            # Modul für die Datenabfrage der saisonalen Fahrerstatistiken
├── matplotlib_data_fetcher.py          # Modul für die Datenabfrage für die Grafiken
├── matplotlib_graphic_generator.py     # Modul für die Generierung von Grafiken
│
├── old_data_fetcher.py                 # Datei um die Daten für alle älteren Seasons abzufragen und abzuspeichern
│
├── templates/
│   ├── base.html                       # Haupt-HTML-Datei, welcher den Code für den Kopf- und Fußzeile enthält
│   ├── index.html                      # HTML Vorlage für die Startseite
│   ├── driver_profile.html             # HTML Vorlage für den Fahrersteckbrief
│   └── constructor_profile.html        # HTML Vorlage für den Konstrukteurssteckbrief
│
├── static/
│   ├── css/
│   │   ├── base_styles.css             # Haupt-CSS-Datei für die HTML Templates
│   │   ├── index_styles.css            # CSS-Datei für die Haupt-HTML Seite
│   │   ├── driver_styles.css           # CSS-Datei für die Fahrer-HTML Seite
│   │   └── team_styles.css             # CSS-Datei für die Konstrukteur-HTML Seite
│   │ 
│   ├── js/
│   │   └── script.js                   # JavaScript für Interaktivität
│   │
│   ├── svg/
│   ├── championship/
│   │   ├── constructor_championships_{year}.png
│   │   └── driver_championships_{year}.png
│   │
│   ├── circuits/
│   │   └── source.txt
│   │
│   ├── drivers/
│   │   └── {driver_id}_{year}.png
│   │
│   ├── icons/
│   │   └── icon.svg
│   │
│   └── f1.png
│
├── cache/
│   ├── driver_carrier_stats/
│   │   └── {driver_id}.json
│   │
│   ├── driver_seasonal_stats/
│   │   └── {driver_id}_{year}.json
│   │
│   ├── matplotlib/
│   │   ├── constructor_standings_{year}.png
│   │   ├── driver_standings_{year}.png
│   │   └── race_results_{year}.png
│   │
│   ├── team_carrier_stats/
│   │   └── {team_id}.json
│   │
└   └── team_colors.json
