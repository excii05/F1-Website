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

def fetch_driver_results(driver_id):
    url = f"http://ergast.com/api/f1/drivers/{driver_id}/driverStandings.json"
    response = requests.get(url)
    
    if response.status_code == 200:
        return response.json()
    else:
        print("Failed to fetch driver results")
        return None

def fetch_total_races(driver_id):
    url = f"https://ergast.com/api/f1/drivers/{driver_id}/results.json"
    response = requests.get(url)
    
    if response.status_code == 200:
        return response.json()
    else:
        print("Failed to fetch driver results")
        return None