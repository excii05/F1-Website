import json
from data_fetcher import (
    fetch_driver_standings,
    fetch_constructor_standings,
    fetch_race_schedule,
    fetch_driver_results
)
from data_processor import (
    process_driver_standings,
    process_constructor_standings,
    process_race_schedule,
    process_driver_results
)

def save_to_json(file_name, data):
    """Speichert Daten in einer JSON-Datei."""
    try:
        with open(file_name, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
        print(f"Data successfully saved to {file_name}")
    except Exception as e:
        print(f"Error saving data to {file_name}: {e}")

def main():
    # Fahrerstände verarbeiten und speichern
    driver_standings_data = fetch_driver_standings()
    if driver_standings_data:
        driver_standings = process_driver_standings(driver_standings_data)
        save_to_json("driver_standings.json", driver_standings)
    else:
        print("Driver standings data could not be fetched or is empty.")

    # Konstrukteursstände verarbeiten und speichern
    constructor_standings_data = fetch_constructor_standings()
    if constructor_standings_data:
        constructor_standings = process_constructor_standings(constructor_standings_data)
        save_to_json("constructor_standings.json", constructor_standings)
    else:
        print("Constructor standings data could not be fetched or is empty.")

    # Rennkalender verarbeiten und speichern
    race_schedule_data = fetch_race_schedule()
    if race_schedule_data:
        race_schedule = process_race_schedule(race_schedule_data)
        save_to_json("race_schedule.json", race_schedule)
    else:
        print("Race schedule data could not be fetched or is empty.")

    # Fahrerresultate verarbeiten und speichern
    driver_standings_data = fetch_driver_standings()
    if driver_standings_data:
        driver_standings = process_driver_standings(driver_standings_data)
        driver_results_data = {driver['driver_id']: fetch_driver_results(driver['driver_id']) for driver in driver_standings}

        driver_results = process_driver_results(driver_results_data, driver_standings)
        for driver_id, result in driver_results.items():
            save_to_json(f"{driver_id}_results.json", result)
    else:
        print("Driver results data could not be fetched or is empty.")

if __name__ == "__main__":
    main()
