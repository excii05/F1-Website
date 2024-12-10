import logging
from datetime import datetime
from collections import deque
from data_fetcher import (
    fetch_driver_standings,
    fetch_constructor_standings,
    fetch_race_schedule,
    fetch_race_results,
    fetch_session_schedule,
    fetch_lap_times
)

# Logging konfigurieren
logging.basicConfig(
    filename='error_log.log',
    level=logging.ERROR,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Fehlerhafte Abfragen queue
failed_queries = deque()

# Helper-Funktion für Debug-Meldungen
def debug_message(message):
    print(message)
    logging.debug(message)

# Helper-Funktion für das Verarbeiten von Fehlern
def handle_error(context, error, keep_data=None):
    error_message = f"Error in {context}: {error}"
    debug_message(error_message)
    if keep_data:
        debug_message("Retaining existing data due to error.")
    failed_queries.append(context)

# Fallback-Mechanismus ausführen
def process_failed_queries():
    while failed_queries:
        context = failed_queries.popleft()
        debug_message(f"Retrying failed query: {context}...")
        try:
            # Wiederholung der entsprechenden Funktion
            context()
        except Exception as e:
            logging.error(f"Final failure in {context}: {e}")

# Driver Standings
def process_driver_standings(year):
    """Holt und verarbeitet die Fahrerwertung."""
    debug_message(f"Fetching driver standings for {year}...")
    raw_data = fetch_driver_standings(year)
    if not raw_data:
        handle_error(lambda: process_driver_standings(year), "No data fetched", keep_data=None)
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
                handle_error("processing driver standings entry", e)
    except KeyError as e:
        handle_error("processing driver standings data", e)
    return driver_standings

# Constructor Standings
def process_constructor_standings(year):
    """Holt und verarbeitet die Teamwertung."""
    debug_message(f"Fetching constructor standings for {year}...")
    raw_data = fetch_constructor_standings(year)
    if not raw_data:
        handle_error(lambda: process_constructor_standings(year), "No data fetched", keep_data=None)
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
                handle_error("processing constructor standings entry", e)
    except KeyError as e:
        handle_error("processing constructor standings data", e)
    return constructor_standings

# Race Schedule
def process_race_schedule(year):
    """Holt und verarbeitet den Rennkalender, inkl. Sessions."""
    debug_message(f"Fetching race schedule for {year}...")
    raw_data = fetch_race_schedule(year)
    if not raw_data:
        handle_error(lambda: process_race_schedule(year), "No data fetched", keep_data=None)
        return []

    race_schedule = []
    try:
        races = raw_data['MRData']['RaceTable']['Races']
        for race in races:
            try:
                circuit = race['Circuit']
                country = circuit['Location'].get('country', 'Unknown Country')

                # API-Abfrage für Sessions
                debug_message(f"Fetching session schedule for {country} in {year}...")
                session_data = fetch_session_schedule(country, year)

                # Sitzungen verarbeiten
                sessions = []
                for session in session_data:
                    date_start = session.get("date_start", "Unknown")
                    date_end = session.get("date_end", "Unknown")

                    formatted_date_start = (
                        datetime.strptime(date_start.split("+")[0], '%Y-%m-%dT%H:%M:%S').strftime('%d.%m.%Y %H:%M')
                        if date_start != "Unknown" else "Unknown"
                    )
                    formatted_date_end = (
                        datetime.strptime(date_end.split("+")[0], '%Y-%m-%dT%H:%M:%S').strftime('%d.%m.%Y %H:%M')
                        if date_end != "Unknown" else "Unknown"
                    )

                    sessions.append({
                        "Session Key": session.get("session_key", "Unknown"),
                        "Session Type": session.get("session_type", "Unknown"),
                        "Session Name": session.get("session_name", "Unknown"),
                        "Date Start": formatted_date_start,
                        "Date End": formatted_date_end
                    })

                race_schedule.append({
                    'ID': circuit.get('circuitId', 'Unknown Circuit ID'),
                    'Round': race.get('round', 'Unknown Round'),
                    'Location': {
                        'Country': circuit['Location'].get('country', 'Unknown Country'),
                        'Locality': circuit['Location'].get('locality', 'Unknown Locality')
                    },
                    'Circuit Name': circuit.get('circuitName', 'Unknown Circuit Name'),
                    'Date': datetime.strptime(race['date'], '%Y-%m-%d').strftime('%d.%m.%Y'),
                    'Sessions': sessions
                })
            except KeyError as e:
                handle_error("processing race schedule entry", e)
    except KeyError as e:
        handle_error("processing race schedule data", e)
    return race_schedule

# Race Results
def process_race_results(year, race_schedule):
    """Holt und verarbeitet die Rennergebnisse."""
    debug_message(f"Fetching race results for the {year} season...")
    results = []
    for race in race_schedule:
        round_number = race['Round']
        circuit_id = race['ID']
        debug_message(f"Fetching results for round {round_number} ({circuit_id})...")
        raw_data = fetch_race_results(year, round_number)
        if not raw_data:
            handle_error(lambda: process_race_results(year, race_schedule), f"No data fetched for round {round_number}", keep_data=results)
            continue

        try:
            races = raw_data['MRData']['RaceTable']['Races']
            if not races:
                debug_message(f"Warning: No races found for round {round_number}.")
                continue

            for result in races[0]['Results']:
                try:
                    fastest_lap = result.get('FastestLap', {})

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
                    handle_error(f"processing race result for round {round_number}", e, keep_data=results)

        except KeyError as e:
            handle_error(f"processing race data for round {round_number}", e, keep_data=results)

    return results

def process_lap_times(year, race_schedule):
    """Holt und verarbeitet die Rundenzeiten."""
    debug_message(f"Fetching lap times for the {year} season...")
    results = []

    for race in race_schedule:
        round_number = race['Round']
        circuit_id = race['ID']
        debug_message(f"Fetching lap times for round {round_number} ({circuit_id})...")

        raw_data = fetch_race_results(year, round_number)
        if not raw_data:
            handle_error(lambda: process_lap_times(year, race_schedule), f"No data fetched for lap times in round {round_number}", keep_data=results)
            continue

        try:
            races = raw_data['MRData']['RaceTable']['Races']
            if not races:
                debug_message(f"Warning: No race data found for round {round_number}.")
                continue

            results_for_race = races[0].get('Results', [])
            if not results_for_race:
                debug_message(f"Warning: No results found for round {round_number}.")
                continue

            for result in results_for_race:
                driver_id = result['Driver']['driverId']
                lap_data = fetch_lap_times(year, round_number, driver_id)
                if not lap_data:
                    handle_error(f"Fetching lap times for driver {driver_id} in round {round_number}", "No data fetched", keep_data=results)
                    continue

                laps = lap_data['MRData']['RaceTable']['Races'][0].get('Laps', [])
                if not laps:
                    debug_message(f"Warning: No lap data found for driver {driver_id} in round {round_number}.")
                    continue

                for lap in laps:
                    lap_number = lap.get("number")
                    for timing in lap.get("Timings", []):
                        lap_time = {
                            "Lap": lap_number,
                            "Driver ID": driver_id,
                            "Time": timing.get("time"),
                            "Position": timing.get("position"),
                        }

                        results.append({
                            "Circuit ID": circuit_id,
                            "Round": round_number,
                            "Lap Number": lap_time["Lap"],
                            "Driver ID": lap_time["Driver ID"],
                            "Time": lap_time["Time"],
                            "Position": lap_time["Position"],
                        })

        except KeyError as e:
            handle_error(f"processing lap times for round {round_number}", e, keep_data=results)
        except IndexError as e:
            handle_error(f"processing lap times for round {round_number}", e, keep_data=results)

    return results

# Fallback-Prozesse ausführen, falls Fehler aufgetreten sind
process_failed_queries()
