import requests

# ! API von Ergast auf Jolpi umbauen!!!!!

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
    
def fetch_session_schedule(country, year):
    url = f"https://api.openf1.org/v1/sessions?country_name={country}&year={year}"
    response = requests.get(url)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch sessions for country {country} in year {year}")
        return None

def fetch_race_results(year, round):
    url = f"http://ergast.com/api/f1/{year}/{round}/results.json"
    response = requests.get(url)
    
    if response.status_code == 200:
        return response.json()
    else:
        print("Failed to fetch race results")
        return None

def fetch_lap_times(year, round, driver_id):
    url = f"https://api.jolpi.ca/ergast/f1/{year}/{round}/drivers/{driver_id}/laps/?format=json&limit=8000"
    response = requests.get(url)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch lap times for year {year} round {round}")
        return None