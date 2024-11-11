def process_driver_standings(data):
    standings_list = []

    if data and "MRData" in data and "StandingsTable" in data["MRData"]:
        for standing in data["MRData"]["StandingsTable"]["StandingsLists"][0]["DriverStandings"]:
            driver = standing["Driver"]
            standings_list.append({
                'id': driver['driverId'],
                "position": standing["position"],
                "name": f"{driver['givenName']} {driver['familyName']}",
                "points": standing["points"],
                "wins": standing["wins"],
                "constructor": standing["Constructors"][0]["name"]
            })

    return standings_list

def process_constructor_standings(data):
    standings_list = []

    if data and "MRData" in data and "StandingsTable" in data["MRData"]:
        for standing in data["MRData"]["StandingsTable"]["StandingsLists"][0]["ConstructorStandings"]:
            constructor = standing["Constructor"]
            standings_list.append({
                "position": standing["position"],
                "name": constructor["name"],
                "points": standing["points"],
                "wins": standing["wins"]
            })

    return standings_list

from datetime import datetime

def process_race_schedule(data):
    schedule_list = []

    if data and "MRData" in data and "RaceTable" in data["MRData"]:
        for race in data["MRData"]["RaceTable"]["Races"]:
            # Datum in das gewünschte Format umwandeln
            date_obj = datetime.strptime(race["date"], "%Y-%m-%d")
            formatted_date = date_obj.strftime("%d.%m.%Y")

            schedule_list.append({
                "round": race["round"],
                "location": f"{race['Circuit']['Location']['country']}, {race['Circuit']['Location']['locality']}",
                "circuit_name": race["Circuit"]["circuitName"],
                "date": formatted_date
            })

    return schedule_list

def process_driver_profile(data):
    # Holen der relevanten Fahrer-Daten aus der API
    driver = data['MRData']['DriverTable']['Drivers'][0]

    # Berechnung des Alters aus dem Geburtsdatum
    from datetime import datetime
    dob = driver['dateOfBirth']
    birth_year = int(dob.split('-')[0])  # Jahr des Geburtsdatums extrahieren
    current_year = datetime.now().year
    age = current_year - birth_year

    # Zurückgegebene Daten
    return {
        'id': driver['driverId'],
        'name': f"{driver['givenName']} {driver['familyName']}",
        'date_of_birth': driver['dateOfBirth'],
        'age': age,
        'nationality': driver['nationality'],
        'permanent_number': driver.get('permanentNumber', 'N/A'),
        'code': driver.get('code', 'N/A'),
        'first_race': driver.get('firstRace', 'N/A'),  # Erster Rennstart
        'race_starts': driver.get('careerStats', {}).get('raceStarts', 'N/A'),  # Rennstarts
        'pole_positions': driver.get('careerStats', {}).get('polePositions', 'N/A'),  # Pole Positions
        'wins': driver.get('careerStats', {}).get('wins', 'N/A'),  # Siege
        'fastest_laps': driver.get('careerStats', {}).get('fastestLaps', 'N/A'),  # Schnellste Runden
        'championship_wins': driver.get('careerStats', {}).get('championshipWins', 'N/A')  # Meisterschaftsgewinne
    }



# Neue Funktion zur Verarbeitung der Saisonergebnisse eines Fahrers
def process_driver_results(data):
    race_results = []
    for race in data['MRData']['RaceTable']['Races']:
        race_results.append({
            'round': race['round'],
            'race_name': race['raceName'],
            'date': race['date'],
            'position': race['Results'][0].get('position', 'N/A'),
            'grid': race['Results'][0].get('grid', 'N/A'),
            'points': race['Results'][0].get('points', '0')
        })
    return race_results