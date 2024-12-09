from datetime import datetime
from data_fetcher import (
    fetch_driver_standings,
    fetch_constructor_standings,
    fetch_race_schedule,
    fetch_race_results,
    fetch_session_schedule
)

# Driver Standings
def process_driver_standings(year):
    """Holt und verarbeitet die Fahrerwertung."""
    print(f"Fetching driver standings for {year}...")
    raw_data = fetch_driver_standings(year)
    if not raw_data:
        print(f"Error: No driver standings data fetched for {year}.")
        return []

    driver_standings = []
    try:
        standings_list = raw_data['MRData']['StandingsTable']['StandingsLists'][0]['DriverStandings']
        for entry in standings_list:
            try:
                driver = entry['Driver']
                constructors = entry['Constructors']

                driver_standings.append({
                    'ID': driver.get('driverId', 'Unknown ID'),
                    'Position': entry.get('position', 'Unknown Position'),
                    'Name': f"{driver.get('givenName', 'Unknown')} {driver.get('familyName', 'Unknown')}",
                    'Points': entry.get('points', '0'),
                    'Wins': entry.get('wins', '0'),
                    'Team': constructors[0].get('name', 'Unknown Team') if constructors else 'No Team'
                })
            except KeyError as e:
                print(f"Error processing driver standings entry: {entry}. Missing key: {e}")
    except KeyError as e:
        print(f"Error processing driver standings data. Missing key: {e}")
    return driver_standings


def process_constructor_standings(year):
    """Holt und verarbeitet die Teamwertung."""
    print(f"Fetching constructor standings for {year}...")
    raw_data = fetch_constructor_standings(year)
    if not raw_data:
        print(f"Error: No constructor standings data fetched for {year}.")
        return []

    constructor_standings = []
    try:
        standings_list = raw_data['MRData']['StandingsTable']['StandingsLists'][0]['ConstructorStandings']
        for entry in standings_list:
            try:
                constructor = entry['Constructor']

                constructor_standings.append({
                    'ID': constructor.get('constructorId', 'Unknown ID'),
                    'Position': entry.get('position', 'Unknown Position'),
                    'Name': constructor.get('name', 'Unknown Name'),
                    'Points': entry.get('points', '0'),
                    'Wins': entry.get('wins', '0')
                })
            except KeyError as e:
                print(f"Error processing constructor standings entry: {entry}. Missing key: {e}")
    except KeyError as e:
        print(f"Error processing constructor standings data. Missing key: {e}")
    return constructor_standings


def process_race_schedule(year):
    """Holt und verarbeitet den Rennkalender, inkl. Sessions."""
    print(f"Fetching race schedule for {year}...")
    raw_data = fetch_race_schedule(year)
    if not raw_data:
        print(f"Error: No race schedule data fetched for {year}.")
        return []

    race_schedule = []
    try:
        races = raw_data['MRData']['RaceTable']['Races']
        for race in races:
            try:
                circuit = race['Circuit']
                country = circuit['Location'].get('country', 'Unknown Country')

                # API-Abfrage für Sessions
                print(f"Fetching session schedule for {country} in {year}...")
                session_data = fetch_session_schedule(country, year)

                # Sitzungen verarbeiten
                sessions = []
                for session in session_data:
                    sessions.append({
                        "Session Key": session.get("session_key", "Unknown"),
                        "Session Type": session.get("session_type", "Unknown"),
                        "Session Name": session.get("session_name", "Unknown"),
                        "Date Start": session.get("date_start", "Unknown"),
                        "Date End": session.get("date_end", "Unknown")
                    })

                # Rennkalender-Eintrag mit Sitzungen erstellen
                race_schedule.append({
                    'ID': circuit.get('circuitId', 'Unknown Circuit ID'),
                    'Round': race.get('round', 'Unknown Round'),
                    'Location': {
                        'Country': circuit['Location'].get('country', 'Unknown Country'),
                        'Locality': circuit['Location'].get('locality', 'Unknown Locality')
                    },
                    'Circuit Name': circuit.get('circuitName', 'Unknown Circuit Name'),
                    'Date': datetime.strptime(race['date'], '%Y-%m-%d').strftime('%d.%m.%Y'),
                    'Sessions': sessions  # Sitzungen hinzufügen
                })
            except KeyError as e:
                print(f"Error processing race schedule entry: {race}. Missing key: {e}")
    except KeyError as e:
        print(f"Error processing race schedule data. Missing key: {e}")
    return race_schedule


def process_race_results(year, race_schedule):
    """Holt und verarbeitet die Rennergebnisse."""
    print(f"Fetching race results for the {year} season...")
    results = []
    for race in race_schedule:
        round_number = race['Round']
        circuit_id = race['ID']
        raw_data = fetch_race_results(year, round_number)
        if not raw_data:
            print(f"Error: No data fetched for race round {round_number}.")
            continue

        try:
            races = raw_data['MRData']['RaceTable']['Races']
            if not races:
                print(f"Warning: No races found for round {round_number}.")
                continue

            for result in races[0]['Results']:
                try:
                    fastest_lap = result.get('FastestLap', {})
                    average_speed = fastest_lap.get('AverageSpeed', {})

                    results.append({
                        'Circuit ID': circuit_id,
                        'Driver ID': result['Driver'].get('driverId', 'Unknown Driver ID'),
                        'Start Position': result.get('grid', 'Unknown Grid'),
                        'End Position': result.get('position', 'Unknown Position'),
                        'Points': result.get('points', '0'),
                        'Fastest Lap': {
                            'Time': fastest_lap.get('Time', {}).get('time', None),
                            'Lap': fastest_lap.get('lap', None),
                        },
                        'DNF': result.get('status') if result.get('status') != 'Finished' else None
                    })
                except KeyError as e:
                    print(f"Error processing race result: {result}. Missing key: {e}")

        except KeyError as e:
            print(f"Error processing race data for round {round_number}. Missing key: {e}")

    return results