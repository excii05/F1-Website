# data_fetcher.py
import requests

def fetch_driver_standings():
    url = "http://ergast.com/api/f1/current/driverStandings.json"
    response = requests.get(url)
    
    if response.status_code == 200:
        return response.json()  # JSON-Daten zurückgeben
    else:
        print("Failed to fetch data")
        return None
