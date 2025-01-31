import math
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
                    entities = season.get("ConstructorStandings", []) if key == "WCC_titles" else season.get("DriverStandings", [])
                    for entity in entities:
                        if key == "WCC_titles":
                            if entity.get("Constructor", {}).get("constructorId") == team_id:
                                stats[key] += 1
                        else:
                            constructor_info = entity.get("Constructors", [{}])[0]
                            if constructor_info.get("constructorId") == team_id:
                                stats[key] += 1
                                driver_name = entity["Driver"]["givenName"] + " " + entity["Driver"]["familyName"]
                                stats["WDC_drivers"][driver_name] = stats["WDC_drivers"].get(driver_name, 0) + 1
    
    active_seasons = sorted(list(stats["seasons"]))
    gaps = [f"{active_seasons[i-1]}-{active_seasons[i]}" for i in range(1, len(active_seasons)) if int(active_seasons[i]) - int(active_seasons[i-1]) > 1]
    
    return stats, gaps

def main():
    team_id = "mercedes"
    team_info = get_team_info(team_id)
    stats, gaps = analyze_team_results(team_id)
    
    print(f"Statistiken für {team_info['name']}: ")
    print(f"Heimatland: {team_info['nationality']}")
    print(f"Erste Saison: {stats['first_season']}")
    print(f"Gesamtzahl an Rennen: {stats['total_races']}")
    print(f"Siege: {stats['wins']}")
    print(f"Konstrukteurstitel (WCC): {stats['WCC_titles']}")
    print(f"Fahrer-Weltmeisterschaften (WDC): {stats['WDC_titles']}")
    wdc_drivers_str = ", ".join([f"{driver} ({count})" for driver, count in stats['WDC_drivers'].items()]) if stats['WDC_drivers'] else '---'
    print(f"Weltmeister mit diesem Team: {wdc_drivers_str}")
    print(f"Pause gemacht in: {', '.join(gaps) if gaps else 'Keine Pausen'}")

if __name__ == "__main__":
    main()