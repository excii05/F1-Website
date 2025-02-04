import json
import os
from data_fetcher import fetch_driver_standings

def fetch_season_driver_standings(year):
    standings_data = {}
    save_path = "cache/matplotlib/"
    os.makedirs(save_path, exist_ok=True)
    
    # Anzahl der Rennen ermitteln
    initial_data = fetch_driver_standings(year)
    if not initial_data:
        print("Fehler beim Abrufen der Anzahl der Rennen.")
        return
    
    total_rounds = int(initial_data['MRData']['total'])
    
    for round_num in range(1, total_rounds + 1):
        data = fetch_driver_standings(year, round_num)
        if data:
            standings = data['MRData']['StandingsTable']['StandingsLists'][0]['DriverStandings']
            standings_data[round_num] = [
                {
                    "position": driver["position"],
                    "driver": driver["Driver"]["driverId"]
                }
                for driver in standings
            ]
    
    file_path = os.path.join(save_path, f"driver_standings_{year}.json")
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(standings_data, f, indent=4)
    
    print(f"Daten für {total_rounds} Rennen in {year} gespeichert unter {file_path}.")

if __name__ == "__main__":
    year = 2024  # Ersetze mit dem gewünschten Jahr
    fetch_season_driver_standings(year)