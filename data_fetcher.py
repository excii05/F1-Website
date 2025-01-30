import requests
import math
from datetime import datetime

BASE_URL = "https://api.jolpi.ca/ergast/f1"

def fetch_driver_standings(year):
    url = f"{BASE_URL}/{year}/driverstandings/?format=json"
    response = requests.get(url)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch driver standings in {year}")
        return None

def fetch_constructor_standings(year):
    url = f"{BASE_URL}/{year}/constructorstandings/?format=json"
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

def driver_information(year):
    url = f"{BASE_URL}/{year}/drivers/?format=json"
    response = requests.get(url)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch driver information for {year}")
        return None
    
    
    
def fetch_driver_info(driver_id):
    url = f"{BASE_URL}/drivers/{driver_id}"
    response = requests.get(url).json()
    driver = response.get("MRData", {}).get("DriverTable", {}).get("Drivers", [])[0]
    
    birth_date = driver.get("dateOfBirth", "0000-00-00")
    birth_datetime = datetime.strptime(birth_date, "%Y-%m-%d")
    today = datetime.today()
    age = today.year - birth_datetime.year - ((today.month, today.day) < (birth_datetime.month, birth_datetime.day))
    
    return {
        "full_name": f"{driver.get('givenName', '')} {driver.get('familyName', '')}",
        "nationality": driver.get("nationality", ""),
        "age": age
    }

def fetch_driver_results(driver_id):
    results = []
    limit = 100
    offset = 0
    while True:
        url = f"{BASE_URL}/drivers/{driver_id}/results?limit={limit}&offset={offset}"
        response = requests.get(url).json()
        races = response.get("MRData", {}).get("RaceTable", {}).get("Races", [])
        if not races:
            break
        results.extend(races)
        offset += limit
    return results

def fetch_driver_championships(driver_id):
    championships = 0
    runner_up = 0
    
    for year in range(1950, 2025):
        url = f"{BASE_URL}/{year}/driverStandings?limit=100"
        response = requests.get(url).json()
        standings = response.get("MRData", {}).get("StandingsTable", {}).get("StandingsLists", [])
        
        for season in standings:
            for driver in season.get("DriverStandings", []):
                if driver.get("Driver", {}).get("driverId") == driver_id:
                    position = driver.get("position")
                    if position == "1":
                        championships += 1
                    elif position == "2":
                        runner_up += 1
    
    return championships, runner_up