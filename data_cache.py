import json
import os
from data_fetcher import (
    fetch_driver_standings,
    fetch_constructor_standings,
    fetch_race_schedule
)
from data_processor import (
    process_driver_standings,
    process_constructor_standings,
    process_race_schedule
)

def save_to_json(file_name, data):
    """Speichert Daten in einer JSON-Datei im Ordner cache/."""
    try:
        os.makedirs("cache", exist_ok=True)
        
        file_path = os.path.join("cache", file_name)

        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
        print(f"Data successfully saved to {file_path}")
    except Exception as e:
        print(f"Error saving data to {file_name}: {e}")

def main():
    driver_standings_data = fetch_driver_standings()
    if driver_standings_data:
        driver_standings = process_driver_standings(driver_standings_data)
        save_to_json("driver_standings.json", driver_standings)
    else:
        print("Driver standings data could not be fetched or is empty.")

    constructor_standings_data = fetch_constructor_standings()
    if constructor_standings_data:
        constructor_standings = process_constructor_standings(constructor_standings_data)
        save_to_json("constructor_standings.json", constructor_standings)
    else:
        print("Constructor standings data could not be fetched or is empty.")

    race_schedule_data = fetch_race_schedule()
    if race_schedule_data:
        race_schedule = process_race_schedule(race_schedule_data)
        save_to_json("race_schedule.json", race_schedule)
    else:
        print("Race schedule data could not be fetched or is empty.")

if __name__ == "__main__":
    main()