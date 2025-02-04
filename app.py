from flask import Flask, render_template
from data_fetcher import (
    fetch_driver_information,
    fetch_constructor_information,
    fetch_driver_standings, 
    fetch_constructor_standings, 
    fetch_race_schedule,
)
from driver_data_fetcher import store_driver_data
from team_data_fetcher import store_team_data
from seasonal_data_fetcher import get_driver_season_stats
from apscheduler.schedulers.background import BackgroundScheduler
import atexit
import os
import json

app = Flask(__name__)

# ---------------------------
# Scheduler-Konfiguration
# ---------------------------
# Konfiguriere hier den Wochentag und die Uhrzeit, an der die Jobs ausgeführt werden sollen.
WEEKLY_JOB_DAY = 'sun'    # Beispiel: jeden Montag
WEEKLY_JOB_HOUR = 14       # Beispiel: 03:00 Uhr
WEEKLY_JOB_MINUTE = 32     # Beispiel: 03:00 Uhr

# ---------------------------
# Datenabruf-Funktionen für die Web-App
# ---------------------------
def get_driver_details(driver_id):
    data = fetch_driver_information(2024)
    if data:
        drivers = data['MRData']['DriverTable']['Drivers']
        for driver in drivers:
            if driver['driverId'] == driver_id:
                return driver
    return None

def get_driver_standings():
    data = fetch_driver_standings(2024)
    if data:
        return data['MRData']['StandingsTable']['StandingsLists'][0]['DriverStandings']
    return []

def get_constructor_standings():
    data = fetch_constructor_standings(2024)
    if data:
        return data['MRData']['StandingsTable']['StandingsLists'][0]['ConstructorStandings']
    return []

def get_race_schedule():
    data = fetch_race_schedule(2024)
    if data:
        return data['MRData']['RaceTable']['Races']
    return []

# Custom Jinja-Filter zum Extrahieren des Namens nach dem Unterstrich
def extract_lastname(driver_id):
    return driver_id.split('_')[-1]  # Nimmt nur den Teil nach dem "_"

app.jinja_env.filters['lastname'] = extract_lastname  # Filter registrieren

# ---------------------------
# Routen
# ---------------------------
@app.route('/')
def home():
    driver_standings = get_driver_standings()
    constructor_standings = get_constructor_standings()
    race_schedule = get_race_schedule()

    return render_template(
        'index.html',
        driver_standings=driver_standings,
        constructor_standings=constructor_standings,
        race_schedule=race_schedule
    )

@app.route('/driver/<driver_id>')
def driver_profile(driver_id):
    year = 2024  # Aktuelles Jahr

    # Pfad zur JSON-Datei zusammenbauen
    json_path = os.path.join('cache', 'driver_carrier_stats', f'{driver_id}.json')

    # Prüfen, ob die Datei existiert
    if os.path.exists(json_path):
        try:
            with open(json_path, 'r', encoding='utf-8') as file:
                driver_data = json.load(file)
        except Exception as e:
            return f"Fehler beim Laden der Fahrerdaten: {e}", 500

        driver_info = driver_data.get("driver_info", {})
        career_stats = driver_data.get("career_stats", {})

    else:
        driver_info = {}
        career_stats = {}

    # Saison-Statistiken abrufen
    seasonal_stats = get_driver_season_stats(year, driver_id)

    if not driver_info and not career_stats and not seasonal_stats:
        return "Fahrerdaten nicht gefunden", 404

    return render_template(
        'driver_profile.html',
        driver=driver_info,
        career_stats=career_stats,
        seasonal_stats=seasonal_stats,  # Saison-Statistiken separat übergeben
        driver_id=driver_id
    )

@app.route('/team/<team_id>')
def team_profile(team_id):
    # Pfad zur JSON-Datei zusammenbauen
    json_path = os.path.join('cache', 'team_carrier_stats', f'{team_id}.json')
    
    # Prüfen, ob die Datei existiert
    if os.path.exists(json_path):
        try:
            with open(json_path, 'r', encoding='utf-8') as file:
                team_data = json.load(file)
        except Exception as e:
            # Falls ein Fehler beim Laden auftritt, wird ein 500-Fehler zurückgegeben
            return f"Fehler beim Laden der Konstrukteurdaten: {e}", 500

        # Extrahiere die einzelnen Daten, sodass das Template wie gewohnt
        # mit "driver" und "career_stats" arbeiten kann
        team_info = team_data.get("team_info", {})
        career_stats = team_data.get("career_stats", {})

        return render_template(
            'constructor_profile.html',
            team = team_info,
            career_stats = career_stats
        )
    else:
        # Falls keine JSON-Datei gefunden wurde, gib den Fehlercode 404 zurück.
        return "Konstrukteurdaten nicht gefunden", 404

@app.route('/race/<race_id>')
def race_details(race_id):
    # Beispielhafte Implementierung
    return f"Race details for {race_id}"

# ---------------------------
# Scheduler-Funktionen: Wöchentliche Datenaktualisierung
# ---------------------------
def weekly_driver_update():
    """Ruft einmal wöchentlich für alle Fahrer die Daten ab und speichert sie."""
    driver_list_data = fetch_driver_information(2024)
    if driver_list_data:
        drivers = driver_list_data.get('MRData', {}).get('DriverTable', {}).get('Drivers', [])
        print(f"Starte wöchentlichen Fahrer-Datenabruf für {len(drivers)} Fahrer...")
        for driver in drivers:
            driver_id = driver.get("driverId")
            if driver_id:
                try:
                    print(f"Starte Abfrage für Fahrer: {driver_id}")
                    store_driver_data(driver_id)
                    print(f"Daten für Fahrer {driver_id} erfolgreich aktualisiert.")
                except Exception as e:
                    print(f"Fehler bei Fahrer {driver_id}: {e}")
    else:
        print("Keine Fahrerliste verfügbar. Fahrer-Job wird abgebrochen.")

def weekly_team_update():
    """Ruft einmal wöchentlich für alle aktuellen Teams die Daten ab und speichert sie."""
    team_list_data = fetch_constructor_information(2024)
    if team_list_data:
        teams = team_list_data.get('MRData', {}).get('ConstructorTable', {}).get('Constructors', [])
        print(f"Starte wöchentlichen Team-Datenabruf für {len(teams)} Teams...")
        for team in teams:
            team_id = team.get("constructorId")
            if team_id:
                try:
                    print(f"Starte Abfrage für Team: {team_id}")
                    store_team_data(team_id)
                    print(f"Daten für Team {team_id} erfolgreich aktualisiert.")
                except Exception as e:
                    print(f"Fehler bei Team {team_id}: {e}")
    else:
        print("Keine Team-Liste verfügbar. Team-Job wird abgebrochen.")

# ---------------------------
# Scheduler initialisieren
# ---------------------------
scheduler = BackgroundScheduler()
scheduler.add_job(
    func=weekly_driver_update,
    trigger='cron',
    day_of_week=WEEKLY_JOB_DAY,
    hour=WEEKLY_JOB_HOUR,
    minute=WEEKLY_JOB_MINUTE,
    id='weekly_driver_update_job'
)
scheduler.add_job(
    func=weekly_team_update,
    trigger='cron',
    day_of_week=WEEKLY_JOB_DAY,
    hour=WEEKLY_JOB_HOUR,
    minute=WEEKLY_JOB_MINUTE,
    id='weekly_team_update_job'
)
scheduler.start()
print(f"Scheduler gestartet: Wöchentliche Jobs jeden {WEEKLY_JOB_DAY} um {WEEKLY_JOB_HOUR:02d}:{WEEKLY_JOB_MINUTE:02d} Uhr.")

# Sicherstellen, dass der Scheduler beim Beenden der App ordentlich heruntergefahren wird.
atexit.register(lambda: scheduler.shutdown())

if __name__ == '__main__':
    app.run(debug=True)
