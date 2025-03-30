import atexit #importing modules
import os
import json
from flask import has_request_context
from datetime import datetime
from flask import Flask, render_template, request
from data_fetcher import ( #importing functions from different files
    fetch_driver_information,
    fetch_constructor_information,
    fetch_driver_standings, 
    fetch_constructor_standings, 
    fetch_race_schedule,
    fetch_driver_info
)
from driver_data_fetcher import store_driver_data
from team_data_fetcher import store_team_data
from seasonal_data_fetcher import get_seasonal_stats
from matplotlib_data_fetcher import fetch_season_standings
from matplotlib_graphic_generator import (
    plot_driver_championship,
    plot_constructor_championship,
    plot_driver_results
)
from apscheduler.schedulers.background import BackgroundScheduler

# Note: I will not explain every single line of code, as many of it is very identical to another.
# If you have questions, please feel free to contact me on my portfolio page: tim.fuhrmann-leo.de

app = Flask(__name__) #created Flask application

current_year = 2025 #fallback if API request breaks
years = [str(y) for y in range(2020, current_year + 1)] #sets the available seasons for which I have data

# ---------------------------
# Scheduler configuration
# ---------------------------
WEEKLY_JOB_DAY = 'mon' #sets the week day for the scheduler
WEEKLY_JOB_HOUR = 1 #sets the hour for the scheduler
WEEKLY_JOB_MINUTE = 0 #sets the minute day for the scheduler

# ---------------------------
# Data calling function
# ---------------------------
def get_year():
    if has_request_context():
        return request.args.get("year", current_year)
    return current_year  # Default to current year if no request context

def get_driver_details(driver_id):
    year = get_year()
    data = fetch_driver_information(year) #calls function from data_fetcher.py file
    if data: #checks if data received
        drivers = data['MRData']['DriverTable']['Drivers'] #loads the driver list
        for driver in drivers: #checks if driver with a specific driver_id is in that list
            if driver['driverId'] == driver_id:
                return driver #returns the driver if true
    return None #returns nothing if false

def get_driver_age(driver_id):
    data = fetch_driver_info(driver_id)
    if data:
        drivers = data['MRData']['DriverTable']['Drivers']
        if drivers:
            birth_date = drivers[0].get("dateOfBirth", "0000-00-00") #requests date of birth. If nothing is returned it will use 0000-00-00 instead
            birth_datetime = datetime.strptime(birth_date, "%Y-%m-%d")
            today = datetime.today() #gets current date
            age = today.year - birth_datetime.year - ((today.month, today.day) < (birth_datetime.month, birth_datetime.day)) #calculated the age
            return age
    return None

def get_driver_standings():
    year = get_year()
    data = fetch_driver_standings(year)
    if data:
        return data['MRData']['StandingsTable']['StandingsLists'][0]['DriverStandings']
    return []

def get_constructor_standings():
    year = get_year()
    data = fetch_constructor_standings(year)
    if data:
        return data['MRData']['StandingsTable']['StandingsLists'][0]['ConstructorStandings']
    return []

def get_race_schedule():
    year = get_year()
    data = fetch_race_schedule(year)
    if data:
        races = data['MRData']['RaceTable']['Races']
        for race in races:
            date_parts = race['date'].split('-')
            race['date'] = f"{date_parts[2]}.{date_parts[1]}.{date_parts[0]}"
        return races
    return []

def count_f1_teams(career_stats):
    former_teams = career_stats.get("former_teams", [])
    return len(former_teams)

# Custom Jinja-Filter to extract the last name (important for the pictures I get from the official F1 website!)
def extract_lastname(driver_id):
    return driver_id.split('_')[-1]  #only takes the name after the _
app.jinja_env.filters['lastname'] = extract_lastname  #registers filter

# Custom Jinja-Filter to replace the _ with a space (important for the pictures I get from the official F1 website!)
def format_team_id(team_id):
    return team_id.replace('_', ' ')  #replaces the _ with a space
app.jinja_env.filters['format_team'] = format_team_id


# ---------------------------
# Routes
# ---------------------------
@app.route('/') #standard app route --> this is the main page
def home():
    year = request.args.get("year", str(current_year))
    
    driver_standings = get_driver_standings() #gets the current driver WDC standings
    constructor_standings = get_constructor_standings() #gets the current driver WCC standings
    race_schedule = get_race_schedule() #gets all the race weeksends for the current season

    return render_template( #forwards all the data to the HTML template
        'index.html',
        driver_standings=driver_standings,
        constructor_standings=constructor_standings,
        race_schedule=race_schedule,
        year=year,
        years=years
    )

@app.route('/driver/<driver_id>')
def driver_profile(driver_id):
    year = request.args.get("year", str(current_year))
    
    #constructs the file path where the data is stored
    career_stats_path = os.path.join('cache', 'driver_carreer_stats', f'{driver_id}.json')
    seasonal_stats_path = os.path.join('cache', 'driver_seasonal_stats', f'{driver_id}_{year}.json')

    #initializes the data from the .json files
    driver_info = {}
    career_stats = {}
    seasonal_stats = {}
    
    #reads in all the data from the .json files
    if os.path.exists(career_stats_path):
        try:
            with open(career_stats_path, 'r', encoding='utf-8') as file:
                career_data = json.load(file)
            driver_info = career_data.get("driver_info", {})
            career_stats = career_data.get("career_stats", {})
        except Exception as e:
            return f"Error when loading the driver data: {e}", 500

    if os.path.exists(seasonal_stats_path):
        try:
            with open(seasonal_stats_path, 'r', encoding='utf-8') as file:
                seasonal_stats = json.load(file)
        except Exception as e:
            return f"Error when loading the season data: {e}", 500
    
    age = get_driver_age(driver_id) #gets the drivers age
    total_teams = count_f1_teams(career_stats) #gets the amount of former teams of the driver

    return render_template(
        'driver_profile.html',
        driver=driver_info,
        career_stats=career_stats,
        seasonal_stats=seasonal_stats,
        driver_id=driver_id,
        total_teams=total_teams,
        age=age,
        year=year,
        years=years
    )

@app.route('/team/<team_id>')
def team_profile(team_id):
    year = request.args.get("year", str(current_year))
    
    json_path = os.path.join('cache', 'team_carrier_stats', f'{team_id}.json')
    
    if os.path.exists(json_path):
        try:
            with open(json_path, 'r', encoding='utf-8') as file:
                team_data = json.load(file)
        except Exception as e:
            return f"Error when loading the constructor data: {e}", 500

        team_info = team_data.get("team_info", {})
        career_stats = team_data.get("career_stats", {})

        return render_template(
            'constructor_profile.html',
            team = team_info,
            career_stats = career_stats,
            team_id=team_id,
            year=year,
            years=years
        )

# ---------------------------
# Scheduler function: Weekly data update from the API!
# ---------------------------
def weekly_driver_update():
    year = current_year
    driver_list_data = fetch_driver_information(year) #gets the entire driver list for the current season
    if driver_list_data:
        drivers = driver_list_data.get('MRData', {}).get('DriverTable', {}).get('Drivers', [])
        print(f"Starting weekly driver data update for {len(drivers)}...") #debugging logs
        for driver in drivers:
            driver_id = driver.get("driverId")
            if driver_id:
                try:
                    print(f"Starting to update data for: {driver_id}")
                    store_driver_data(driver_id)
                    print(f"Data for driver {driver_id} succesfully saved.")
                except Exception as e:
                    print(f"Error for driver {driver_id}: {e}")
    else:
        print("Couldn't find driver data. Job was aborded.")

def weekly_team_update():
    year = current_year
    team_list_data = fetch_constructor_information(year)
    if team_list_data:
        teams = team_list_data.get('MRData', {}).get('ConstructorTable', {}).get('Constructors', [])
        print(f"Starting weekly driver data update for {len(teams)}...")
        for team in teams:
            team_id = team.get("constructorId")
            if team_id:
                try:
                    print(f"Starting to update data for: {team_id}")
                    store_team_data(team_id)
                    print(f"Data for driver {team_id} succesfully saved.")
                except Exception as e:
                    print(f"Error for driver {team_id}: {e}")
    else:
        print("Couldn't find constructor data. Job was aborded.")
        
def weekly_seasonal_stats_update():
    year = current_year
    """Ruft einmal wöchentlich die saisonalen Statistiken für alle Fahrer ab und speichert sie."""
    driver_list_data = fetch_driver_information(year)
    if driver_list_data:
        drivers = driver_list_data.get('MRData', {}).get('DriverTable', {}).get('Drivers', [])
        print(f"Starting weekly seasonal data update for {len(drivers)}...")
        for driver in drivers:
            driver_id = driver.get("driverId")
            if driver_id:
                try:
                    print(f"Starting to update data for: {driver_id}")
                    get_seasonal_stats(year, driver_id)
                except Exception as e:
                    print(f"Error for driver {driver_id}: {e}")
    else:
        print("Couldn't find driver data. Job was aborded.")

def weekly_graphics_data_update():
    year = current_year
    fetch_season_standings(year)

def weekly_championship_graphics_update():
    year = current_year
    plot_driver_championship(year)
    plot_constructor_championship(year)
    
def weekly_race_graphics_update():
    year = current_year
    driver_list_data = fetch_driver_information(year)
    if driver_list_data:
        drivers = driver_list_data.get('MRData', {}).get('DriverTable', {}).get('Drivers', [])
        print(f"Starting weekly graphics update for {len(drivers)} Fahrer...")
        for driver in drivers:
            driver_id = driver.get("driverId")
            if driver_id:
                try:
                    print(f"Starting to generate graphics for: {driver_id}")
                    plot_driver_results(year, driver_id)
                except Exception as e:
                    print(f"Error for driver: {driver_id}: {e}")
    else:
        print("Couldn't find driver data. Job was aborded.")

# ---------------------------
# Scheduler initialisation
# ---------------------------
scheduler = BackgroundScheduler()
scheduler.add_job( #adding scheduler jobs
    func=weekly_driver_update,
    trigger='cron',
    day_of_week=WEEKLY_JOB_DAY,
    hour=WEEKLY_JOB_HOUR,
    minute=WEEKLY_JOB_MINUTE,
    id='weekly_driver_update_job'
)
scheduler.add_job(
    func=weekly_team_update,
    trigger='cron',
    day_of_week=WEEKLY_JOB_DAY,
    hour=WEEKLY_JOB_HOUR,
    minute=WEEKLY_JOB_MINUTE,
    id='weekly_team_update_job'
)
scheduler.add_job(
    func=weekly_seasonal_stats_update,
    trigger='cron',
    day_of_week=WEEKLY_JOB_DAY,
    hour=WEEKLY_JOB_HOUR + 1, #stacking jobs to avoid running into API rate limits!
    minute=WEEKLY_JOB_MINUTE,
    id='weekly_seasonal_stats_update_job'
)
scheduler.add_job(
    func=weekly_graphics_data_update,
    trigger='cron',
    day_of_week=WEEKLY_JOB_DAY,
    hour=WEEKLY_JOB_HOUR + 1,
    minute=WEEKLY_JOB_MINUTE + 30,
    id='weekly_graphics_data_update_job'
)
scheduler.add_job(
    func=weekly_championship_graphics_update,
    trigger='cron',
    day_of_week=WEEKLY_JOB_DAY,
    hour=WEEKLY_JOB_HOUR + 2,
    minute=WEEKLY_JOB_MINUTE,
    id='weekly_championship_graphics_update_job'
)
scheduler.add_job(
    func=weekly_race_graphics_update,
    trigger='cron',
    day_of_week=WEEKLY_JOB_DAY,
    hour=WEEKLY_JOB_HOUR + 2,
    minute=WEEKLY_JOB_MINUTE,
    id='weekly_race_graphics_update_job'
)

scheduler.start()
print(f"Scheduler started: Starting to update data each {WEEKLY_JOB_DAY} at {WEEKLY_JOB_HOUR:02d}:{WEEKLY_JOB_MINUTE:02d} o'clock.")

#makes sure that the scheduler is properly shut down before exiting the program
atexit.register(lambda: scheduler.shutdown())

if __name__ == '__main__': #calling the app (starting the app!)
    app.run(debug=True)