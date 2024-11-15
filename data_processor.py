from datetime import datetime

def process_driver_standings(data):
    """Verarbeitet Fahrerstände."""
    standings = []
    for driver in data['MRData']['StandingsTable']['StandingsLists'][0]['DriverStandings']:
        standings.append({
            "driver_id": driver['Driver']['driverId'],
            "position": driver['position'],
            "name": f"{driver['Driver']['givenName']} {driver['Driver']['familyName']}",
            "points": driver['points'],
            "wins": driver['wins'],
            "constructor": driver['Constructors'][0]['name']
        })
    return standings

def process_constructor_standings(data):
    """Verarbeitet Konstrukteursstände."""
    standings = []
    for constructor in data['MRData']['StandingsTable']['StandingsLists'][0]['ConstructorStandings']:
        standings.append({
            "position": constructor['position'],
            "name": constructor['Constructor']['name'],
            "points": constructor['points'],
            "wins": constructor['wins']
        })
    return standings

def process_race_schedule(data):
    """Verarbeitet den Rennkalender."""
    schedule = []
    for race in data['MRData']['RaceTable']['Races']:
        schedule.append({
            "round": race['round'],
            "location": {
                "country": race['Circuit']['Location']['country'],
                "city": race['Circuit']['Location']['locality']
            },
            "circuit_name": race['Circuit']['circuitName'],
            "date": datetime.strptime(race['date'], '%Y-%m-%d').strftime('%d.%m.%Y')
        })
    return schedule

def process_driver_results(driver_data, driver_standings):
    """Verarbeitet Fahrerresultate."""
    results = {}
    for driver in driver_standings:
        driver_id = driver['driver_id']
        data = driver_data.get(driver_id, None)
        if not data:
            continue

        driver_info = data['MRData']['StandingsTable']['StandingsLists']
        if not driver_info:
            continue

        driver_info = driver_info[0]['DriverStandings'][0]['Driver']

        # Berechne Alter
        birthday = datetime.strptime(driver_info['dateOfBirth'], '%Y-%m-%d')
        age = (datetime.now() - birthday).days // 365

        # Ermittle erstes Rennen und Nationalität
        races = data['MRData']['RaceTable']['Races']
        first_race_date = min(race['date'] for race in races) if races else None

        # Rennstarts zählen
        total_races = len(races)

        # Siege summieren und Weltmeisterschaften zählen
        wins = sum(int(season['DriverStandings'][0]['wins']) for season in driver_info)
        championships = sum(1 for season in driver_info if season['DriverStandings'][0]['position'] == "1")

        results[driver_id] = {
            "name": f"{driver_info['givenName']} {driver_info['familyName']}",
            "birthday": driver_info['dateOfBirth'],
            "age": age,
            "nationality": driver_info['nationality'],
            "first_race": first_race_date,
            "total_races": total_races,
            "wins": wins,
            "championships": championships
        }
    return results
