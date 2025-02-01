import requests
import math
from datetime import datetime

BASE_URL = "https://api.jolpi.ca/ergast/f1"

# Main Page Data Fetcher
def driver_information(year):
    url = f"{BASE_URL}/{year}/drivers/"
    response = requests.get(url)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch driver information for {year}")
        return None

def fetch_driver_standings(year):
    url = f"{BASE_URL}/{year}/driverstandings/"
    response = requests.get(url)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch driver standings in {year}")
        return None

def fetch_constructor_standings(year):
    url = f"{BASE_URL}/{year}/constructorstandings/"
    response = requests.get(url)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch constructor standings in {year}")
        return None

def fetch_race_schedule(year):
    url = f"https://api.jolpi.ca/ergast/f1/{year}/races/"
    response = requests.get(url)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch race schedule in {year}")
        return None

# Driver Data Fetcher    
def fetch_driver_info(driver_id):
    url = f"{BASE_URL}/drivers/{driver_id}"
    response = requests.get(url)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch driver information for {driver_id}")
        return None

def fetch_driver_results(driver_id, limit=100, offset=0):
    url = f"{BASE_URL}/drivers/{driver_id}/results?limit={limit}&offset={offset}"
    response = requests.get(url)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch driver results for {driver_id}")
        return None

def fetch_driver_championship(year, position):
    url = f"{BASE_URL}/{year}/driverStandings/{position}?limit=100"
    response = requests.get(url)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch driver standings for {year}")
        return None   

# Team Data Fetcher   
def fetch_team_info(team_id):
    url = f"{BASE_URL}/constructors/{team_id}"
    response = requests.get(url)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch team information for {team_id}")
        return None

def fetch_team_results(team_id, limit=100, offset=0):
    url = f"{BASE_URL}/constructors/{team_id}/results?limit={limit}&offset={offset}"
    response = requests.get(url)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch team results for {team_id}")
        return None

def fetch_wcc_standings(year):
    url = f"{BASE_URL}/{year}/constructorStandings/1?limit=100"
    response = requests.get(url)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch WCC standings for {year}")
        return None

def fetch_wdc_standings(year):
    url = f"{BASE_URL}/{year}/driverStandings/1?limit=100"
    response = requests.get(url)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch WDC standings for {year}")
        return None
    
    
    
    
    
    
    
    
    
