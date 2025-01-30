from data_fetcher import fetch_driver_results, fetch_driver_championships

def analyze_driver_results(driver_id):
    results = fetch_driver_results(driver_id)  # Kein unnötiges Limit setzen, API erlaubt max. 100
    total_races = len(results)
    stats = {
        "total_races": total_races,
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
        stats["current_team"] = constructor  # Annahme: letztes Team ist aktuelles Team
        
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
    
    # Optimierte Meisterschaftsabfrage mit einer einzigen API-Anfrage für alle Jahre
    stats["championships"], stats["runner_up"] = fetch_driver_championships(driver_id)
    
    # Entferne das aktuelle Team aus der Liste vorheriger Teams
    previous_teams = stats["teams"] - {stats["current_team"]}
    stats["teams"] = ", ".join(previous_teams) if previous_teams else "---"
    
    return stats