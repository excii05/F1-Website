import json
import os
from data_fetcher import (
    fetch_driver_standings,
    fetch_constructor_standings,
    fetch_race_schedule,
    fetch_race_results,
    fetch_lap_times,
    fetch_session_schedule
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
            
            combined_data = []  # Kombinierte Daten für Rennen und Sessions
            
            # Sitzungsdaten für jedes Rennen abrufen und hinzufügen
            for race in race_schedule:
                race_id = race.get("ID")
                round_number = race.get("Round")
                country = race.get("Location", {}).get("Country")
                year = current_season

                # API-Abfrage für Sessions
                session_data = fetch_session_schedule(country, year)
                print(f"Fetching session schedule for {country} in {year}")

                sessions = []

                # Prüfen, ob Daten zurückgegeben wurden und ob die Antwort eine Liste ist
                if session_data and isinstance(session_data, list):
                    print("Raw session data received:")
                    print(json.dumps(session_data, indent=4))
                    
                    # Iteriere durch die Liste und extrahiere die relevanten Daten
                    for session in session_data:
                        sessions.append({
                            "Session Type": session.get("session_type", "Unknown"),
                            "Session Name": session.get("session_name", "Unknown"),
                            "Date Start": session.get("date_start", "Unknown"),
                            "Date End": session.get("date_end", "Unknown")
                        })

                    # Debug: Zeige die extrahierten Sessions
                    print("Extracted sessions:")
                    print(json.dumps(sessions, indent=4))
                else:
                    print(f"No valid session data found for {country}, year: {year}.")

                # Die Sessions unter dem entsprechenden Race speichern
                race["Sessions"] = sessions

                # Debug: Zeige das aktualisierte Race-Objekt mit Sessions
                print("Updated race object with sessions:")
                print(json.dumps(race, indent=4))

                # Kombinierte Datenstruktur für Rennen und zugehörige Sitzungen
                combined_race_data = {
                    "ID": race_id,
                    "Round": round_number,
                    "Location": {
                        "Country": race.get("Location", {}).get("Country"),
                        "Locality": race.get("Location", {}).get("Locality")
                    },
                    "Circuit Name": race.get("Circuit Name"),
                    "Date": race.get("Date"),
                    "Sessions": sessions
                }
                combined_data.append(combined_race_data)
            
            # Speichern der kombinierten Daten
            save_to_json(os.path.join(season_folder, "race_schedule_combined.json"), combined_data)
            print(f"Saved combined race schedule and session data for {len(combined_data)} races.")
        else:
            print("Warning: Race schedule processing returned no data.")
            return
    else:
        print("Error: Race schedule data could not be fetched or is empty.")
        return

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

if __name__ == "__main__":
    main()
