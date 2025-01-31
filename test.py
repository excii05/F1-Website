import requests
import math
from datetime import datetime

def get_driver_info(driver_id):
    url = f"https://api.jolpi.ca/ergast/f1/drivers/{driver_id}"
    response = requests.get(url).json()
    driver = response.get("MRData", {}).get("DriverTable", {}).get("Drivers", [])[0]
    
    birth_date = driver.get("dateOfBirth", "0000-00-00")
    birth_datetime = datetime.strptime(birth_date, "%Y-%m-%d")
    today = datetime.today()
    age = today.year - birth_datetime.year - ((today.month, today.day) < (birth_datetime.month, birth_datetime.day))
    
    return {
        "full_name": driver.get("givenName", "") + " " + driver.get("familyName", ""),
        "nationality": driver.get("nationality", ""),
        "age": age
    }

def get_total_races(driver_id):
    url = f"https://api.jolpi.ca/ergast/f1/drivers/{driver_id}/results?limit=1"
    response = requests.get(url).json()
    return int(response.get("MRData", {}).get("total", 0))

def get_driver_results(driver_id):
    total_races = get_total_races(driver_id)
    limit = 100
    num_requests = math.ceil(total_races / limit)
    
    results = []
    for i in range(num_requests):
        offset = i * limit
        url = f"https://api.jolpi.ca/ergast/f1/drivers/{driver_id}/results?limit={limit}&offset={offset}"
        response = requests.get(url).json()
        results.extend(response.get("MRData", {}).get("RaceTable", {}).get("Races", []))
    
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
        "DNQ": 0,
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
                stats["DNQ"] += 1
            else:
                stats["DNF"] += 1
        
        if position.isdigit() and int(position) > 10:
            stats["outside_top10"] += 1
    
    stats["teams"].discard(stats["current_team"])
    
    for year in range(int(stats["first_season"] or 1950), 2025):
        standings_url = f"https://api.jolpi.ca/ergast/f1/{year}/driverStandings/1?limit=100"
        standings_response = requests.get(standings_url).json()
        standings_lists = standings_response.get("MRData", {}).get("StandingsTable", {}).get("StandingsLists", [])
        
        for season in standings_lists:
            for driver in season.get("DriverStandings", []):
                if driver["Driver"]["driverId"] == driver_id:
                    stats["championships"] += 1
    
        standings_url_p2 = f"https://api.jolpi.ca/ergast/f1/{year}/driverStandings/2?limit=100"
        standings_response_p2 = requests.get(standings_url_p2).json()
        standings_lists_p2 = standings_response_p2.get("MRData", {}).get("StandingsTable", {}).get("StandingsLists", [])
        
        for season in standings_lists_p2:
            for driver in season.get("DriverStandings", []):
                if driver["Driver"]["driverId"] == driver_id:
                    stats["runner_up"] += 1
    
    return stats

def main():
    driver_id = "alonso"
    driver_info = get_driver_info(driver_id)
    stats = analyze_driver_results(driver_id)
    
    former_teams = ', '.join(stats['teams']) if stats['teams'] else "---"
    
    print(f"Karriere-Statistiken für {driver_info['full_name']}:")
    print(f"Alter: {driver_info['age']}")
    print(f"Nationalität: {driver_info['nationality']}")
    print(f"Rennen: {stats['total_races']}")
    print(f"Siege: {stats['wins']}")
    print(f"Podien: {stats['podiums']} (P2: {stats['p2_finishes']}, P3: {stats['p3_finishes']})")
    print(f"Pole Positions: {stats['pole_positions']}")
    print(f"Schnellste Runden: {stats['fastest_laps']}")
    print(f"DNFs: {stats['DNF']}, DNQs: {stats['DNQ']}")
    print(f"Rennen außerhalb der Top 10: {stats['outside_top10']}")
    print(f"Erste Saison: {stats['first_season']}")
    print(f"Ehemalige Teams: {former_teams}")
    print(f"Aktuelles Team: {stats['current_team']}")
    print(f"Meisterschaften: {stats['championships']}")
    print(f"Vize-Weltmeisterschaften: {stats['runner_up']}")

if __name__ == "__main__":
    main()