import requests

BASE_URL = "https://api.jolpi.ca/ergast/f1" #the base URL is used to save some lines of code, as it is the same for every request!

# Main Page Data Fetcher
#I will one explain one API request, as these are all programmed very similar
def fetch_driver_information(year): #the year gets forwarded when calling the function. This ensures that I can get the data from any season I want.
    url = f"{BASE_URL}/{year}/drivers/" #this is the API endpoint, which I use to retrieve the respective data
    response = requests.get(url) #the request gets saved as a response in this variable
    
    if response.status_code == 200: #this code is mostly just for debugging purposes.
        return response.json() #if the status code is 200, then everything is fine and it returns the API response
    else:
        print(f"Failed to fetch driver information for {year}")  #if I get an error, it will give me an error message in my terminal
        return None

def fetch_constructor_information(year):
    url = f"{BASE_URL}/{year}/constructors/"
    response = requests.get(url)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch driver information for {year}")
        return None

def fetch_driver_standings(year, race="last"):
    url = f"{BASE_URL}/{year}/{race}/driverstandings/"
    response = requests.get(url)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch driver standings in {year}")
        return None

def fetch_constructor_standings(year, race="last"):
    url = f"{BASE_URL}/{year}/{race}/constructorstandings/"
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
    
def fetch_seasonal_standings(year, race, driver_id):
    url = f"{BASE_URL}/{year}/{race}/drivers/{driver_id}/results/"
    response = requests.get(url)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch seasonal standings for {driver_id} for {race} in {year}")
        return None
    
def fetch_race_results(year, race):
    url = f"{BASE_URL}/{year}/{race}/results/"
    response = requests.get(url)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch race results for round {race} in {year}")
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
    
    
    
    
    
    
    
    
    
