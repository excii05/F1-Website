import json
import os
import requests  # API-Zugriff hinzufügen
from data_fetcher import (
    fetch_driver_standings,
    fetch_constructor_standings,
    fetch_race_schedule,
    fetch_race_results
)
from data_processor import (
    process_driver_standings,
    process_constructor_standings,
    process_race_schedule,
    process_race_results
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

def fetch_lap_times(year, round_number):
    """Holt die Rundenzeiten für ein bestimmtes Rennen über die Ergast API."""
    try:
        url = f"http://ergast.com/api/f1/{year}/{round_number}/laps.json?limit=2000"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        lap_times = data.get('MRData', {}).get('RaceTable', {}).get('Races', [])
        return lap_times
    except requests.RequestException as e:
        print(f"Error fetching lap times for {year} Round {round_number}: {e}")
        return None

def main():
    # Fetch und Process: Rennkalender
    print("Fetching race schedule...")
    race_schedule_data = fetch_race_schedule()
    if race_schedule_data:
        print("Processing race schedule...")
        race_schedule = process_race_schedule(race_schedule_data)
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

            # Speichern der Renntermine in einer Datei
            save_to_json(os.path.join(season_folder, "race_schedule.json"), race_schedule)
        else:
            print("Warning: Race schedule processing returned no data.")
            return  # Wenn keine Rennkalender-Daten vorhanden sind, abgebrochen.
    else:
        print("Error: Race schedule data could not be fetched or is empty.")
        return  # Wenn keine Rennkalender-Daten abgerufen wurden, abgebrochen.

    # Debugging: Initialisierung
    print("Starting data caching process...")

    # Fetch und Process: Fahrerwertung
    print("Fetching driver standings...")
    driver_standings_data = fetch_driver_standings()
    if driver_standings_data:
        print("Processing driver standings...")
        driver_standings = process_driver_standings(driver_standings_data)
        if driver_standings:
            print(f"Driver standings processed: {len(driver_standings)} entries found.")
            save_to_json(os.path.join(season_folder, "driver_standings.json"), driver_standings)
        else:
            print("Warning: Driver standings processing returned no data.")
    else:
        print("Error: Driver standings data could not be fetched or is empty.")

    # Fetch und Process: Teamwertung
    print("Fetching constructor standings...")
    constructor_standings_data = fetch_constructor_standings()
    if constructor_standings_data:
        print("Processing constructor standings...")
        constructor_standings = process_constructor_standings(constructor_standings_data)
        if constructor_standings:
            print(f"Constructor standings processed: {len(constructor_standings)} entries found.")
            save_to_json(os.path.join(season_folder, "constructor_standings.json"), constructor_standings)
        else:
            print("Warning: Constructor standings processing returned no data.")
    else:
        print("Error: Constructor standings data could not be fetched or is empty.")

    # Fetch und Process: Rennergebnisse
    print("Fetching and processing race results...")
    if 'driver_standings' in locals() and 'race_schedule' in locals():
        race_results = process_race_results(driver_standings, race_schedule)
        if race_results:
            print(f"Race results processed: {len(race_results)} entries found.")
            # Speichern der Ergebnisse nach Fahrer
            save_to_json(os.path.join(results_folder, "race_results_by_driver.json"), race_results)

            # Speichern der Ergebnisse nach Rennen
            for race in race_schedule:
                race_id = race['ID']
                race_round = race['Round']
                race_year = current_season
                race_results_for_circuit = [
                    result for result in race_results if result['Circuit ID'] == race_id
                ]
                race_folder = os.path.join(results_folder, race_id)
                os.makedirs(race_folder, exist_ok=True)
                save_to_json(os.path.join(race_folder, f"race_results.json"), race_results_for_circuit)
                print(f"Saved race results for circuit: {race_id}")

                # Rundenzeiten für jedes Rennen abrufen und speichern
                print(f"Fetching lap times for race {race_id}...")
                lap_times = fetch_lap_times(race_year, race_round)
                if lap_times:
                    save_to_json(os.path.join(race_folder, "lap_times.json"), lap_times)
                    print(f"Saved lap times for race {race_id}")

            # Zusätzliche Datei: Fahrer mit allen Rennen und Positionen
            print("Compiling driver race positions...")
            driver_race_positions = {}
            for result in race_results:
                driver_id = result['Driver ID']
                if driver_id not in driver_race_positions:
                    driver_race_positions[driver_id] = []

                driver_race_positions[driver_id].append({
                    'Round': race['Round'],
                    'Race': result['Circuit ID'],
                    'Start Position': result.get('Start Position', 'Unknown'),
                    'End Position': result.get('End Position', 'Unknown')
                })
            save_to_json(os.path.join(season_folder, "driver_race_positions.json"), driver_race_positions)
            print("Driver race positions saved successfully.")

        else:
            print("Warning: Race results processing returned no data.")
    else:
        print("Error: Cannot process race results as driver standings or race schedule is missing.")

if __name__ == "__main__":
    main()
