import json
import os
import time
from data_fetcher import fetch_driver_info, fetch_driver_results, fetch_driver_championship

def get_driver_info(driver_id):
    data = fetch_driver_info(driver_id)
    driver = data.get("MRData", {}).get("DriverTable", {}).get("Drivers", [])[0] if data else {}
    
    return {
        "full_name": driver.get("givenName", "") + " " + driver.get("familyName", ""),
        "nationality": driver.get("nationality", "")
    }

def get_driver_results(driver_id):
    limit = 100
    offset = 0
    results = []
    
    while True:
        data = fetch_driver_results(driver_id, limit, offset)
        races = data.get("MRData", {}).get("RaceTable", {}).get("Races", [])
        
        if not races:
            break
        
        results.extend(races)
        offset += limit
    
    return results

def analyze_driver_results(driver_id):
    results = get_driver_results(driver_id)
    stats = {
        "total_races": len(results),
        "wins": 0,
        "podiums": 0,
        "p2_finishes": 0,
        "p3_finishes": 0,
        "pole_positions": 0,
        "fastest_laps": 0,
        "outside_top10": 0,
        "DNF": 0,
        "DSQ": 0,
        "teams": set(),
        "first_season": None,
        "championships": 0,
        "runner_up": 0,
        "current_team": None
    }
    
    for race in results:
        season = race["season"]
        result = race["Results"][0]
        position = result.get("position", "99")
        grid = result.get("grid", "-1")
        status = result.get("status", "").lower()
        constructor = result["Constructor"]["name"]
        fastest_lap = result.get("FastestLap", {}).get("rank", "") == "1"
        
        if not stats["first_season"] or int(season) < int(stats["first_season"]):
            stats["first_season"] = season
        
        stats["teams"].add(constructor)
        stats["current_team"] = constructor
        
        if position == "1":
            stats["wins"] += 1
        if position in ["1", "2", "3"]:
            stats["podiums"] += 1
        if position == "2":
            stats["p2_finishes"] += 1
        if position == "3":
            stats["p3_finishes"] += 1
        if grid == "1":
            stats["pole_positions"] += 1
        if fastest_lap:
            stats["fastest_laps"] += 1
        
        if status != "finished" and not status.startswith("+"):
            if "disqualified" in status:
                stats["DSQ"] += 1
            else:
                stats["DNF"] += 1
        
        if position.isdigit() and int(position) > 10:
            stats["outside_top10"] += 1
    
    stats["teams"].discard(stats["current_team"])
    
    start_year = int(stats["first_season"] or 1950)
    for year in range(start_year, 2025):
        for standing_position in [1, 2]:
            standings_data = fetch_driver_championship(year, standing_position)
            if standings_data:
                for season in standings_data.get("MRData", {}).get("StandingsTable", {}).get("StandingsLists", []):
                    for driver in season.get("DriverStandings", []):
                        if driver["Driver"]["driverId"] == driver_id:
                            if standing_position == 1:
                                stats["championships"] += 1
                            else:
                                stats["runner_up"] += 1
    return stats

def run_full_query(driver_id):
    driver_info = get_driver_info(driver_id)
    stats = analyze_driver_results(driver_id)
    
    former_teams = list(stats['teams']) if stats['teams'] else []
    
    output_data = {
        "driver_info": driver_info,
        "career_stats": {
            "total_races": stats["total_races"],
            "wins": stats["wins"],
            "podiums": stats["podiums"],
            "p2_finishes": stats["p2_finishes"],
            "p3_finishes": stats["p3_finishes"],
            "pole_positions": stats["pole_positions"],
            "fastest_laps": stats["fastest_laps"],
            "DNF": stats["DNF"],
            "DSQ": stats["DSQ"],
            "outside_top10": stats["outside_top10"],
            "first_season": stats["first_season"],
            "former_teams": former_teams,
            "current_team": stats["current_team"],
            "championships": stats["championships"],
            "runner_up": stats["runner_up"]
        }
    }
    return output_data

def store_driver_data(driver_id, max_retries=3):
    attempt = 0

    while attempt < max_retries:
        try:
            output_data = run_full_query(driver_id)
            
            output_dir = os.path.join("cache", "driver_carreer_stats")
            os.makedirs(output_dir, exist_ok=True)
            output_file = os.path.join(output_dir, f"{driver_id}.json")
            
            with open(output_file, "w", encoding="utf-8") as json_file:
                json.dump(output_data, json_file, indent=4, ensure_ascii=False)
            
            print(f"Die Daten wurden erfolgreich in '{output_file}' gespeichert.")
            return
        
        except Exception as e:
            attempt += 1
            print(f"Fehler beim Abrufen der Daten für {driver_id} (Versuch {attempt}/{max_retries}): {e}")
            if attempt >= max_retries:
                print("Maximale Anzahl an Versuchen erreicht. Es konnten keine Daten gespeichert werden.")
                raise e
            else:
                print("Starte die Abfrage neu...")
                time.sleep(1)

def main():
    driver_id = "hamilton"
    store_driver_data(driver_id)

if __name__ == "__main__":
    main()