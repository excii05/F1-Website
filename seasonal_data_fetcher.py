import json
import os
from data_fetcher import fetch_seasonal_standings, fetch_driver_standings

def get_seasonal_stats(year, driver_id):
    standings_data = fetch_driver_standings(year)
    
    if not standings_data:
        return
    
    total_races = int(standings_data['MRData']['total'])
    
    podiums = 0
    pole_positions = 0
    fastest_laps = 0
    dnfs = 0
    wins = 0
    points = 0
    races_participated = 0
    championship_position = 0
    
    for race in range(1, total_races + 1):
        race_result = fetch_seasonal_standings(year, race, driver_id)
        if race_result:
            try:
                race_info = race_result['MRData']['RaceTable']['Races'][0]['Results'][0]
                races_participated += 1
                
                position = int(race_info['position'])
                
                if position == 1:
                    wins += 1
                if position <= 3:
                    podiums += 1
                if 'FastestLap' in race_info and race_info['FastestLap'].get('rank') == '1':
                    fastest_laps += 1
                if race_info['grid'] == '1':
                    pole_positions += 1
                if race_info["status"] != "Finished" and not race_info["status"].startswith("+"):
                    dnfs += 1
            except (KeyError, IndexError):
                print(f"Could not retrieve data for race {race}")
    
    driver_standings = fetch_driver_standings(year)
    for entry in driver_standings['MRData']['StandingsTable']['StandingsLists']:
        for driver in entry['DriverStandings']:
            if driver['Driver']['driverId'] == driver_id:
                championship_position = int(driver['position'])
                points = int(float(driver['points']))
    
    driver_data = {
        'races_participated': races_participated,
        'championship_position': championship_position,
        'podiums': podiums,
        'pole_positions': pole_positions,
        'fastest_laps': fastest_laps,
        'dnfs': dnfs,
        'wins': wins,
        'points': points
    }
    
    cache_dir = 'cache/driver_seasonal_stats'
    os.makedirs(cache_dir, exist_ok=True)
    file_path = os.path.join(cache_dir, f"{driver_id}_{year}.json")
    
    with open(file_path, 'w') as json_file:
        json.dump(driver_data, json_file, indent=4)
    
    print(f"Data saved to {file_path}")

def main():
    year = "2020"
    driver_id = "raikkonen"
    get_seasonal_stats(year, driver_id)

if __name__ == "__main__":
    main()