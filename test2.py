import requests
import math

def get_team_info(team_id):
    url = f"https://api.jolpi.ca/ergast/f1/constructors/{team_id}"
    response = requests.get(url).json()
    team = response.get("MRData", {}).get("ConstructorTable", {}).get("Constructors", [])[0]
    
    return {
        "name": team.get("name", ""),
        "nationality": team.get("nationality", "")
    }

def get_total_races(team_id):
    url = f"https://api.jolpi.ca/ergast/f1/constructors/{team_id}/results?limit=1"
    response = requests.get(url).json()
    return int(response.get("MRData", {}).get("total", 0))

def get_team_results(team_id):
    total_races = get_total_races(team_id)
    limit = 100
    num_requests = math.ceil(total_races / limit)
    
    results = []
    for i in range(num_requests):
        offset = i * limit
        url = f"https://api.jolpi.ca/ergast/f1/constructors/{team_id}/results?limit={limit}&offset={offset}"
        response = requests.get(url).json()
        results.extend(response.get("MRData", {}).get("RaceTable", {}).get("Races", []))
    
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
        wcc_url = f"https://api.jolpi.ca/ergast/f1/{year}/constructorStandings/1?limit=100"
        wcc_response = requests.get(wcc_url).json()
        standings_lists = wcc_response.get("MRData", {}).get("StandingsTable", {}).get("StandingsLists", [])
        
        for season in standings_lists:
            for constructor in season.get("ConstructorStandings", []):
                if constructor["Constructor"]["constructorId"] == team_id:
                    stats["WCC_titles"] += 1
    
        wdc_url = f"https://api.jolpi.ca/ergast/f1/{year}/driverStandings/1?limit=100"
        wdc_response = requests.get(wdc_url).json()
        standings_lists_wdc = wdc_response.get("MRData", {}).get("StandingsTable", {}).get("StandingsLists", [])
        
        for season in standings_lists_wdc:
            for driver in season.get("DriverStandings", []):
                constructor_name = driver["Constructors"][0]["constructorId"]
                if constructor_name == team_id:
                    stats["WDC_titles"] += 1
                    driver_name = driver["Driver"]["givenName"] + " " + driver["Driver"]["familyName"]
                    stats["WDC_drivers"][driver_name] = stats["WDC_drivers"].get(driver_name, 0) + 1
    
    active_seasons = sorted(list(stats["seasons"]))
    gaps = []
    for i in range(1, len(active_seasons)):
        if int(active_seasons[i]) - int(active_seasons[i - 1]) > 1:
            gaps.append(f"{active_seasons[i-1]}-{active_seasons[i]}")
    
    return stats, gaps

def main():
    team_id = "mercedes"
    team_info = get_team_info(team_id)
    stats, gaps = analyze_team_results(team_id)
    
    wdc_drivers_str = ", ".join([f"{driver} ({count})" for driver, count in stats['WDC_drivers'].items()]) if stats['WDC_drivers'] else '---'
    
    print(f"Statistiken für {team_info['name']}:")
    print(f"Heimatland: {team_info['nationality']}")
    print(f"Erste Saison: {stats['first_season']}")
    print(f"Gesamtzahl an Rennen: {stats['total_races']}")
    print(f"Siege: {stats['wins']}")
    print(f"Konstrukteurstitel (WCC): {stats['WCC_titles']}")
    print(f"Fahrer-Weltmeisterschaften (WDC): {stats['WDC_titles']}")
    print(f"Weltmeister mit diesem Team: {wdc_drivers_str}")
    print(f"Pause gemacht in: {', '.join(gaps) if gaps else 'Keine Pausen'}")

if __name__ == "__main__":
    main()