import requests

def fetch_driver_standings(year):
    url = f"https://api.jolpi.ca/ergast/f1/{year}/driverstandings/?format=json"
    response = requests.get(url)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch driver standings in {year}")
        return None

def fetch_constructor_standings(year):
    url = f"https://api.jolpi.ca/ergast/f1/{year}/constructorstandings/?format=json"
    response = requests.get(url)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch constructor standings in {year}")
        return None

def fetch_race_schedule(year):
    url = f"https://api.jolpi.ca/ergast/f1/{year}/races/?format=json"
    response = requests.get(url)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch race schedule in {year}")
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
    url = f"https://api.jolpi.ca/ergast/f1/{year}/{round}/results/?format=json"
    response = requests.get(url)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch race results for round {round} in {year}")
        return None

def fetch_lap_times(year, round, driver_id):
    url = f"https://api.jolpi.ca/ergast/f1/{year}/{round}/drivers/{driver_id}/laps/?format=json&limit=8000"
    response = requests.get(url)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch lap times for {driver_id} in round {round} in {year}")
        return None