from flask import Flask, render_template
from data_fetcher import (
    fetch_driver_standings, 
    fetch_constructor_standings, 
    fetch_race_schedule, 
    driver_information,
    fetch_driver_info
)
from driver_stats import analyze_driver_results

app = Flask(__name__)

# Datenabruf-Funktionen
def get_driver_standings():
    data = fetch_driver_standings(2024)
    if data:
        return data['MRData']['StandingsTable']['StandingsLists'][0]['DriverStandings']
    return []

def get_constructor_standings():
    data = fetch_constructor_standings(2024)
    if data:
        return data['MRData']['StandingsTable']['StandingsLists'][0]['ConstructorStandings']
    return []

def get_race_schedule():
    data = fetch_race_schedule(2024)
    if data:
        return data['MRData']['RaceTable']['Races']
    return []

def get_driver_details(driver_id):
    data = driver_information(2024)
    if data:
        drivers = data['MRData']['DriverTable']['Drivers']
        for driver in drivers:
            if driver['driverId'] == driver_id:
                return driver
    return None

def get_team_details(team_id):
    data = get_constructor_standings()
    for team in data:
        if team['Constructor']['constructorId'] == team_id:
            return team['Constructor']
    return None

def get_race_details(race_id):
    data = get_race_schedule()
    for race in data:
        if race['round'] == race_id:  # Annahme: 'round' wird als race_id verwendet
            return race
    return None

# Routen
@app.route('/')
def home():
    driver_standings = get_driver_standings()
    constructor_standings = get_constructor_standings()
    race_schedule = get_race_schedule()

    return render_template(
        'index.html',
        driver_standings=driver_standings,
        constructor_standings=constructor_standings,
        race_schedule=race_schedule
    )

@app.route('/driver/<driver_id>')
def driver_profile(driver_id):
    driver = fetch_driver_info(driver_id)
    stats = analyze_driver_results(driver_id)
    
    if driver:
        return render_template('driver_profile.html', driver=driver, stats=stats)
    else:
        return "Driver not found", 404

@app.route('/team/<team_id>')
def team_profile(team_id):
    team = get_team_details(team_id)
    if team:
        return render_template('constructor_profile.html', team=team)
    else:
        return "Team not found", 404

@app.route('/race/<race_id>')
def race_details(race_id):
    race = get_race_details(race_id)
    if race:
        return render_template('circuit_profile.html', race=race)
    else:
        return "Race not found", 404

if __name__ == '__main__':
    app.run(debug=True)