import json
import os
from datetime import datetime
from data_processor import (
    process_driver_standings,
    process_constructor_standings,
    process_race_schedule
)

def save_to_json(file_name, data):
    """Speichert Daten in einer JSON-Datei im angegebenen Pfad."""
    try:
        os.makedirs(os.path.dirname(file_name), exist_ok=True)  # Stelle sicher, dass der Ordner existiert
        
        with open(file_name, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
        print(f"Data successfully saved to {file_name}")
    except Exception as e:
        print(f"Error saving data to {file_name}: {e}")

def main():
    current_year = datetime.now().year

    # Fetch und Process: Rennkalender
    print("Fetching and processing race schedule...")
    race_schedule = process_race_schedule(current_year)
    if race_schedule:
        print(f"Race schedule processed: {len(race_schedule)} races found.")
        # Dynamische Saisonbestimmung aus dem Jahr des ersten Rennens
        first_race_date = race_schedule[0]['Date']  # Das Datum des ersten Rennens
        current_season = first_race_date.split(".")[-1]  # Saison als Jahr extrahieren
        season_folder = os.path.join("cache", current_season)
        os.makedirs(season_folder, exist_ok=True)  # Saison-Ordner erstellen
        print(f"Created folder {current_season}")
        
        results_folder = os.path.join(season_folder, "results")
        os.makedirs(results_folder, exist_ok=True)  # Results-Ordner erstellen
        print(f"Created results folder in {current_season}")
        
        drivers_folder = os.path.join("cache", "drivers")
        os.makedirs(drivers_folder, exist_ok=True)  # Drivers-Ordner erstellen
        print(f"Created drivers folder in cache")

        # Speichern der kombinierten Daten
        save_to_json(os.path.join(season_folder, "race_schedule.json"), race_schedule)
        print(f"Saved combined race schedule for {len(race_schedule)} races.")
    else:
        print("Error: Race schedule could not be processed.")

    # Fetch und Process: Fahrerwertung
    print("Fetching and processing driver standings...")
    driver_standings = process_driver_standings(current_year)
    if driver_standings:
        print(f"Driver standings processed: {len(driver_standings)} entries found.")
        save_to_json(os.path.join(season_folder, "driver_standings.json"), driver_standings)
    else:
        print("Error: Driver standings could not be processed.")

    # Fetch und Process: Teamwertung
    print("Fetching and processing constructor standings...")
    constructor_standings = process_constructor_standings(current_year)
    if constructor_standings:
        print(f"Constructor standings processed: {len(constructor_standings)} entries found.")
        save_to_json(os.path.join(season_folder, "constructor_standings.json"), constructor_standings)
    else:
        print("Error: Constructor standings could not be processed.")

if __name__ == "__main__":
    main()
