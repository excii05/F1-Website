import math
import json
import os
import time
from data_fetcher import fetch_team_info, fetch_team_results, fetch_wcc_standings, fetch_wdc_standings

def get_team_info(team_id):
    data = fetch_team_info(team_id)
    team = data.get("MRData", {}).get("ConstructorTable", {}).get("Constructors", [])[0] if data else {}
    
    return {
        "name": team.get("name", ""),
        "nationality": team.get("nationality", "")
    }

def get_team_results(team_id):
    limit = 100
    offset = 0
    results = []
    
    while True:
        data = fetch_team_results(team_id, limit, offset)
        races = data.get("MRData", {}).get("RaceTable", {}).get("Races", [])
        
        if not races:
            break
        
        results.extend(races)
        offset += limit
    
    return results

def analyze_team_results(team_id):
    results = get_team_results(team_id)
    stats = {
        "total_races": len(results),
        "wins": 0,
        "first_season": None,
        "seasons": set(),
        "WCC_titles": 0,
        "WDC_titles": 0,
        "WDC_drivers": {}
    }
    
    for race in results:
        season = race["season"]
        result = race["Results"][0]
        position = result.get("position", "99")
        
        stats["seasons"].add(season)
        if not stats["first_season"] or int(season) < int(stats["first_season"]):
            stats["first_season"] = season
        
        if position == "1":
            stats["wins"] += 1
    
    for year in range(int(stats["first_season"] or 1950), 2025):
        for standing_type, key in [(fetch_wcc_standings, "WCC_titles"), (fetch_wdc_standings, "WDC_titles")]:
            standings_data = standing_type(year)
            if standings_data:
                for season in standings_data.get("MRData", {}).get("StandingsTable", {}).get("StandingsLists", []):
                    if key == "WCC_titles":
                        entities = season.get("ConstructorStandings", [])
                        for entity in entities:
                            if entity.get("Constructor", {}).get("constructorId") == team_id:
                                stats[key] += 1
                    else:
                        entities = season.get("DriverStandings", [])
                        for entity in entities:
                            # Hier gehen wir davon aus, dass das erste Element in "Constructors" den gesuchten Constructor enthält.
                            constructor_info = entity.get("Constructors", [{}])[0]
                            if constructor_info.get("constructorId") == team_id:
                                stats[key] += 1
                                driver_name = entity["Driver"]["givenName"] + " " + entity["Driver"]["familyName"]
                                stats["WDC_drivers"][driver_name] = stats["WDC_drivers"].get(driver_name, 0) + 1
    
    active_seasons = sorted(list(stats["seasons"]))
    gaps = [f"{active_seasons[i-1]}-{active_seasons[i]}" for i in range(1, len(active_seasons)) if int(active_seasons[i]) - int(active_seasons[i-1]) > 1]
    
    return stats, gaps

def run_full_query(team_id):
    """Führt die komplette Abfrage durch und gibt die ermittelten Daten als Dictionary zurück."""
    team_info = get_team_info(team_id)
    stats, gaps = analyze_team_results(team_id)
    
    output_data = {
        "team_info": team_info,
        "career_stats": {
            "first_season": stats["first_season"],
            "total_races": stats["total_races"],
            "wins": stats["wins"],
            "WCC_titles": stats["WCC_titles"],
            "WDC_titles": stats["WDC_titles"],
            "WDC_drivers": stats["WDC_drivers"],
            "season_gaps": gaps
        }
    }
    
    return output_data

def store_team_data(team_id, max_retries=3):
    """
    Ruft die vollständigen Team-Daten ab und speichert diese in einer JSON-Datei.
    Bei Fehlern wird bis zu `max_retries` mal versucht, die Daten abzurufen.
    """
    attempt = 0

    while attempt < max_retries:
        try:
            output_data = run_full_query(team_id)
            
            # Sicherstellen, dass das Zielverzeichnis existiert
            output_dir = os.path.join("cache", "team_carrier_stats")
            os.makedirs(output_dir, exist_ok=True)
            output_file = os.path.join(output_dir, f"{team_id}.json")
            
            with open(output_file, "w", encoding="utf-8") as json_file:
                json.dump(output_data, json_file, indent=4, ensure_ascii=False)
            
            print(f"Team-Daten erfolgreich in '{output_file}' gespeichert.")
            return  # Erfolgreicher Durchlauf -> Funktion verlassen
        
        except Exception as e:
            attempt += 1
            print(f"Fehler beim Abrufen der Team-Daten für {team_id} (Versuch {attempt}/{max_retries}): {e}")
            if attempt >= max_retries:
                print("Maximale Anzahl an Versuchen erreicht. Es konnten keine Team-Daten gespeichert werden.")
                raise e
            else:
                print("Starte die Abfrage neu...")
                time.sleep(1)  # Kurze Wartezeit vor dem erneuten Versuch

def main():
    team_id = "mercedes"
    store_team_data(team_id)

if __name__ == "__main__":
    main()