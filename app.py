import atexit
import os
import json
from datetime import datetime
from flask import Flask, render_template, request
from data_fetcher import (
    fetch_driver_information,
    fetch_constructor_information,
    fetch_driver_standings, 
    fetch_constructor_standings, 
    fetch_race_schedule,
    fetch_driver_info
)
from driver_data_fetcher import store_driver_data
from team_data_fetcher import store_team_data
from seasonal_data_fetcher import get_seasonal_stats
from matplotlib_data_fetcher import fetch_season_standings
from matplotlib_graphic_generator import (
    plot_driver_championship,
    plot_constructor_championship,
    plot_driver_results
)
from apscheduler.schedulers.background import BackgroundScheduler

app = Flask(__name__)

current_year = 2024
years = [str(y) for y in range(2020, current_year + 1)]

# ---------------------------
# Scheduler-Konfiguration
# ---------------------------
# Konfiguriere hier den Wochentag und die Uhrzeit, an der die Jobs ausgeführt werden sollen.
WEEKLY_JOB_DAY = 'tue'    # Beispiel: jeden Montag
WEEKLY_JOB_HOUR = 15       # Beispiel: 03:00 Uhr
WEEKLY_JOB_MINUTE = 14     # Beispiel: 03:00 Uhr

# ---------------------------
# Datenabruf-Funktionen für die Web-App
# ---------------------------
def get_year():
    return request.args.get("year", current_year)

def get_driver_details(driver_id):
    year = get_year()
    data = fetch_driver_information(year)
    if data:
        drivers = data['MRData']['DriverTable']['Drivers']
        for driver in drivers:
            if driver['driverId'] == driver_id:
                return driver
    return None

def get_driver_age(driver_id):
    data = fetch_driver_info(driver_id)
    if data:
        drivers = data['MRData']['DriverTable']['Drivers']
        if drivers:
            birth_date = drivers[0].get("dateOfBirth", "0000-00-00")
            birth_datetime = datetime.strptime(birth_date, "%Y-%m-%d")
            today = datetime.today()
            age = today.year - birth_datetime.year - ((today.month, today.day) < (birth_datetime.month, birth_datetime.day))
            return age
    return None

def get_driver_standings():
    year = get_year()
    data = fetch_driver_standings(year)
    if data:
        return data['MRData']['StandingsTable']['StandingsLists'][0]['DriverStandings']
    return []

def get_constructor_standings():
    year = get_year()
    data = fetch_constructor_standings(year)
    if data:
        return data['MRData']['StandingsTable']['StandingsLists'][0]['ConstructorStandings']
    return []

def get_race_schedule():
    year = get_year()
    data = fetch_race_schedule(year)
    if data:
        return data['MRData']['RaceTable']['Races']
    return []

# Custom Jinja-Filter zum Extrahieren des Namens nach dem Unterstrich
def extract_lastname(driver_id):
    return driver_id.split('_')[-1]  # Nimmt nur den Teil nach dem "_"

app.jinja_env.filters['lastname'] = extract_lastname  # Filter registrieren

def format_team_id(team_id):
    return team_id.replace('_', ' ')  # Ersetzt Unterstrich durch Leerzeichen

app.jinja_env.filters['format_team'] = format_team_id  # Filter registrieren


# ---------------------------
# Routen
# ---------------------------
@app.route('/')
def home():
    year = request.args.get("year", current_year)
    
    driver_standings = get_driver_standings()
    constructor_standings = get_constructor_standings()
    race_schedule = get_race_schedule()

    return render_template(
        'index.html',
        driver_standings=driver_standings,
        constructor_standings=constructor_standings,
        race_schedule=race_schedule,
        year=year,
        years=years
    )

@app.route('/driver/<driver_id>')
def driver_profile(driver_id):
    year = request.args.get("year", current_year)
    
    # Pfade zu den JSON-Dateien zusammenbauen
    career_stats_path = os.path.join('cache', 'driver_carrier_stats', f'{driver_id}.json')
    seasonal_stats_path = os.path.join('cache', 'driver_seasonal_stats', f'{driver_id}_{year}.json')

    # Initialisierung der Daten
    driver_info = {}
    career_stats = {}
    seasonal_stats = {}

    age = get_driver_age(driver_id)
    
    # Fahrerkarrieredaten einlesen
    if os.path.exists(career_stats_path):
        try:
            with open(career_stats_path, 'r', encoding='utf-8') as file:
                career_data = json.load(file)
            driver_info = career_data.get("driver_info", {})
            career_stats = career_data.get("career_stats", {})
        except Exception as e:
            return f"Fehler beim Laden der Karriere-Daten: {e}", 500

    # Saisonstatistiken einlesen
    if os.path.exists(seasonal_stats_path):
        try:
            with open(seasonal_stats_path, 'r', encoding='utf-8') as file:
                seasonal_stats = json.load(file)
        except Exception as e:
            return f"Fehler beim Laden der Saison-Daten: {e}", 500

    return render_template(
        'driver_profile.html',
        driver=driver_info,
        career_stats=career_stats,
        seasonal_stats=seasonal_stats,
        driver_id=driver_id,
        age=age,
        year=year,
        years=years
    )

@app.route('/team/<team_id>')
def team_profile(team_id):
    year = request.args.get("year", current_year)
    
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
            career_stats = career_stats,
            team_id=team_id,
            year=year,
            years=years
        )
    else:
        # Falls keine JSON-Datei gefunden wurde, gib den Fehlercode 404 zurück.
        return "Konstrukteurdaten nicht gefunden", 404

# ---------------------------
# Scheduler-Funktionen: Wöchentliche Datenaktualisierung
# ---------------------------
def weekly_driver_update():
    year = get_year()
    """Ruft einmal wöchentlich für alle Fahrer die Daten ab und speichert sie."""
    driver_list_data = fetch_driver_information(year)
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
    year = get_year()
    """Ruft einmal wöchentlich für alle aktuellen Teams die Daten ab und speichert sie."""
    team_list_data = fetch_constructor_information(year)
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
        
def weekly_seasonal_stats_update():
    year = get_year()
    """Ruft einmal wöchentlich die saisonalen Statistiken für alle Fahrer ab und speichert sie."""
    driver_list_data = fetch_driver_information(year)
    if driver_list_data:
        drivers = driver_list_data.get('MRData', {}).get('DriverTable', {}).get('Drivers', [])
        print(f"Starte wöchentlichen saisonalen Statistik-Abruf für {len(drivers)} Fahrer...")
        for driver in drivers:
            driver_id = driver.get("driverId")
            if driver_id:
                try:
                    print(f"Starte Abfrage der saisonalen Statistiken für Fahrer: {driver_id}")
                    get_seasonal_stats(year, driver_id)
                except Exception as e:
                    print(f"Fehler bei saisonalen Statistiken für Fahrer {driver_id}: {e}")
    else:
        print("Keine Fahrerliste verfügbar. Saisonaler Statistik-Job wird abgebrochen.")

def weekly_graphics_data_update():
    year = get_year()
    fetch_season_standings(year)

def weekly_championship_graphics_update():
    year = get_year()
    plot_driver_championship(year)
    plot_constructor_championship(year)
    
def weekly_race_graphics_update():
    year = get_year()
    """Ruft einmal wöchentlich die saisonalen Statistiken für alle Fahrer ab und speichert sie."""
    driver_list_data = fetch_driver_information(year)
    if driver_list_data:
        drivers = driver_list_data.get('MRData', {}).get('DriverTable', {}).get('Drivers', [])
        print(f"Starte wöchentliche Grafikgenerierung für {len(drivers)} Fahrer...")
        for driver in drivers:
            driver_id = driver.get("driverId")
            if driver_id:
                try:
                    print(f"Starte Generierung der wöchtentlichen Grafik für Fahrer: {driver_id}")
                    plot_driver_results(year, driver_id)
                except Exception as e:
                    print(f"Fehler bei der Generierung der wöchtentlichen Grafik für Fahrer: {driver_id}: {e}")
    else:
        print("Keine Fahrerliste verfügbar. Generierung der wöchtentlichen Grafik-Job wird abgebrochen.")

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
scheduler.add_job(
    func=weekly_seasonal_stats_update,
    trigger='cron',
    day_of_week=WEEKLY_JOB_DAY,
    hour=WEEKLY_JOB_HOUR + 1,
    minute=WEEKLY_JOB_MINUTE,
    id='weekly_seasonal_stats_update_job'
)
scheduler.add_job(
    func=weekly_graphics_data_update,
    trigger='cron',
    day_of_week=WEEKLY_JOB_DAY,
    hour=WEEKLY_JOB_HOUR + 1,
    minute=WEEKLY_JOB_MINUTE + 30,
    id='weekly_graphics_data_update_job'
)
scheduler.add_job(
    func=weekly_championship_graphics_update,
    trigger='cron',
    day_of_week=WEEKLY_JOB_DAY,
    hour=WEEKLY_JOB_HOUR + 2,
    minute=WEEKLY_JOB_MINUTE,
    id='weekly_championship_graphics_update_job'
)
scheduler.add_job(
    func=weekly_race_graphics_update,
    trigger='cron',
    day_of_week=WEEKLY_JOB_DAY,
    hour=WEEKLY_JOB_HOUR + 2,
    minute=WEEKLY_JOB_MINUTE,
    id='weekly_race_graphics_update_job'
)
scheduler.start()
print(f"Scheduler gestartet: Wöchentliche Jobs jeden {WEEKLY_JOB_DAY} um {WEEKLY_JOB_HOUR:02d}:{WEEKLY_JOB_MINUTE:02d} Uhr.")

# Sicherstellen, dass der Scheduler beim Beenden der App ordentlich heruntergefahren wird.
atexit.register(lambda: scheduler.shutdown())

if __name__ == '__main__':
    app.run(debug=True)
