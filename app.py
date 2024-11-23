import json
import subprocess
import os
import time
from flask import Flask, render_template, request

app = Flask(__name__)

CACHE_TIMESTAMP_FILE = "cache_timestamp.txt"
CACHE_FOLDER = "cache"
SEASON_FOLDER = "cache"  # Cache-Ordner bleibt gleich, da die Saison als Unterordner nicht mehr benötigt wird.

# Dynamisch die Saison anhand des Datums im cache/ordner
def get_current_season():
    try:
        race_schedule = load_json(os.path.join(CACHE_FOLDER, "race_schedule.json"))
        if race_schedule:
            first_race_date = race_schedule[0]['Date']  # Das Datum des ersten Rennens (im Format Day.Month.Year)
            current_season = first_race_date.split(".")[-1]  # Saison als Jahr extrahieren (letztes Element)
            return current_season
        else:
            return None
    except Exception as e:
        print(f"Error fetching the current season: {e}")
        return None


def load_json(file_name):
    """Lädt Daten aus einer JSON-Datei und prüft, ob sie valide ist."""
    try:
        with open(file_name, 'r', encoding='utf-8') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        print(f"Error loading {file_name}.")
        return None

def run_data_cache():
    """Führt die data_cache.py Datei aus."""
    try:
        print("Running data_cache.py to update JSON files...")
        subprocess.run(["python", "data_cache.py"], check=True)
    except Exception as e:
        print(f"Error running data_cache.py: {e}")

def validate_and_repair_cache():
    """Validiert die JSON-Dateien und führt data_cache.py aus, falls nötig."""
    needs_repair = False
    for file_name in [
        "cache/driver_standings.json",
        "cache/constructor_standings.json",
        "cache/race_schedule.json",
        "cache/2024/race_results_by_driver.json",
        "cache/2024/race_results_by_circuit.json"
    ]:
        if load_json(file_name) is None:  # Datei fehlt oder ist beschädigt
            print(f"File {file_name} is missing or corrupted. Repair needed.")
            needs_repair = True
    
    if needs_repair:
        run_data_cache()

def needs_update():
    """Prüft, ob seit der letzten Aktualisierung 24 Stunden vergangen sind."""
    try:
        if not os.path.exists(CACHE_TIMESTAMP_FILE):
            return True
        
        with open(CACHE_TIMESTAMP_FILE, 'r') as file:
            last_update = float(file.read().strip())
            return (time.time() - last_update) > 24 * 60 * 60
    except Exception as e:
        print(f"Error checking cache timestamp: {e}")
        return True

def update_cache_if_needed():
    """Aktualisiert den Cache, falls nötig."""
    if needs_update():
        run_data_cache()
        try:
            with open(CACHE_TIMESTAMP_FILE, 'w') as file:
                file.write(str(time.time()))
        except Exception as e:
            print(f"Error updating cache timestamp: {e}")


@app.route('/')
def standings():
    # Daten-Cache validieren und aktualisieren, falls nötig
    validate_and_repair_cache()
    update_cache_if_needed()

    # Daten aus JSON-Dateien laden
    driver_standings = load_json("cache/driver_standings.json") or []
    constructor_standings = load_json("cache/constructor_standings.json") or []
    race_schedule = load_json("cache/race_schedule.json") or []

    # Sortierparameter von der URL abfragen
    driver_sort_by = request.args.get('driver_sort_by')
    driver_order = request.args.get('driver_order', 'desc')
    constructor_sort_by = request.args.get('constructor_sort_by')
    constructor_order = request.args.get('constructor_order', 'desc')

    # Fahrer-Wertung sortieren
    if driver_sort_by == 'points':
        driver_standings = sorted(driver_standings, key=lambda x: int(x['points']), reverse=(driver_order == 'desc'))
    elif driver_sort_by == 'wins':
        driver_standings = sorted(driver_standings, key=lambda x: int(x['wins']), reverse=(driver_order == 'desc'))

    # Konstrukteurs-Wertung sortieren
    if constructor_sort_by == 'points':
        constructor_standings = sorted(constructor_standings, key=lambda x: int(x['points']), reverse=(constructor_order == 'desc'))
    elif constructor_sort_by == 'wins':
        constructor_standings = sorted(constructor_standings, key=lambda x: int(x['wins']), reverse=(constructor_order == 'desc'))

    return render_template(
        "index.html",
        driver_standings=driver_standings,
        constructor_standings=constructor_standings,
        driver_sort_by=driver_sort_by,
        driver_order=driver_order,
        constructor_sort_by=constructor_sort_by,
        constructor_order=constructor_order,
        race_schedule=race_schedule
    )


@app.route('/driver/<driver_id>')
def driver_profile(driver_id):
    # Fahrerprofil- und Ergebnisdaten aus JSON laden
    driver_results = load_json(f"cache/{driver_id}_results.json")

    if not driver_results:
        return f"Driver data for {driver_id} not found.", 404

    return render_template('driver_profile.html', driver=driver_results)


@app.route('/constructor/<constructor_id>')
def constructor_profile(constructor_id):
    # Teamprofil-Daten aus JSON laden
    constructor_data = load_json(f"cache/{constructor_id}_profile.json")

    if not constructor_data:
        return f"Constructor data for {constructor_id} not found.", 404

    return render_template('constructor_profile.html', constructor=constructor_data)


@app.route('/circuit/<circuit_id>')
def circuit_profile(circuit_id):
    # Rennstrecken-Daten aus JSON laden
    circuit_data = load_json(f"cache/{circuit_id}_profile.json")

    if not circuit_data:
        return f"Circuit data for {circuit_id} not found.", 404

    return render_template('circuit_profile.html', circuit=circuit_data)


if __name__ == '__main__':
    app.run(debug=True)
