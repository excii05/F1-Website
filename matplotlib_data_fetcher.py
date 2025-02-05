import json
import os
from data_fetcher import fetch_driver_standings, fetch_race_results

def fetch_season_driver_standings(year):
    standings_data = {}
    race_results_data = {}
    save_path = "cache/matplotlib/"
    os.makedirs(save_path, exist_ok=True)
    
    # Anzahl der Rennen ermitteln
    initial_data = fetch_driver_standings(year)
    if not initial_data:
        print("Fehler beim Abrufen der Anzahl der Rennen.")
        return
    
    total_rounds = int(initial_data['MRData']['total'])
    
    for round in range(1, total_rounds + 1):
        # Fahrer-WM-Stände abrufen
        data = fetch_driver_standings(year, round)
        if data:
            standings = data['MRData']['StandingsTable']['StandingsLists'][0]['DriverStandings']
            standings_data[round] = [
                {
                    "position": driver["position"],
                    "driver": driver["Driver"]["driverId"]
                }
                for driver in standings
            ]
        
        # Renn- und Qualifying-Ergebnisse abrufen
        race_data = fetch_race_results(year, round)
        if race_data:
            results = race_data["MRData"]["RaceTable"]["Races"][0]["Results"]
            
            # Qualifying-Ergebnisse nach Grid-Position sortieren
            qualifying_results = sorted(
                [
                    {
                        "grid": result["grid"],
                        "driver": result["Driver"]["driverId"]
                    }
                    for result in results
                ],
                key=lambda x: int(x["grid"]) if x["grid"].isdigit() else float('inf')
            )
            
            # Statusbereinigung für das Rennen
            race_results = []
            for result in results:
                status = result["status"]
                if status == "Finished" or "+" in status:
                    status = "Finished"
                elif status == "DNQ" or status not in ["Finished", "DNQ"]:
                    status = "DNF"
                
                race_results.append({
                    "position": result["position"],
                    "driver": result["Driver"]["driverId"],
                    "status": status
                })
            
            race_results_data[round] = {
                "qualifying": qualifying_results,
                "race": race_results
            }
    
    # Daten speichern
    standings_file = os.path.join(save_path, f"driver_standings_{year}.json")
    with open(standings_file, "w", encoding="utf-8") as f:
        json.dump(standings_data, f, indent=4)
    
    results_file = os.path.join(save_path, f"race_results_{year}.json")
    with open(results_file, "w", encoding="utf-8") as f:
        json.dump(race_results_data, f, indent=4)
    
    print(f"Daten für {total_rounds} Rennen in {year} gespeichert unter {standings_file} und {results_file}.")

if __name__ == "__main__":
    year = 2024  # Ersetze mit dem gewünschten Jahr
    fetch_season_driver_standings(year)