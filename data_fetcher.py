import requests

def fetch_driver_standings():
    url = "http://ergast.com/api/f1/current/driverStandings.json"
    response = requests.get(url)
    
    if response.status_code == 200:
        return response.json()
    else:
        print("Failed to fetch driver standings")
        return None

def fetch_constructor_standings():
    url = "http://ergast.com/api/f1/current/constructorStandings.json"
    response = requests.get(url)
    
    if response.status_code == 200:
        return response.json()
    else:
        print("Failed to fetch constructor standings")
        return None

def fetch_race_schedule():
    url = "http://ergast.com/api/f1/current.json"
    response = requests.get(url)
    
    if response.status_code == 200:
        return response.json()
    else:
        print("Failed to fetch race schedule")
        return None

def fetch_race_results(year, round):
    url = f"http://ergast.com/api/f1/{year}/{round}/results.json"
    response = requests.get(url)
    
    if response.status_code == 200:
        return response.json()
    else:
        print("Failed to fetch race results")
        return None

def fetch_lap_times(year, round):
    url = f"http://ergast.com/api/f1/{year}/{round}/laps.json"
    response = requests.get(url)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch lap times for year {year} round {round}")
        return None