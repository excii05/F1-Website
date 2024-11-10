def process_driver_standings(data):
    standings_list = []

    if data and "MRData" in data and "StandingsTable" in data["MRData"]:
        for standing in data["MRData"]["StandingsTable"]["StandingsLists"][0]["DriverStandings"]:
            driver = standing["Driver"]
            standings_list.append({
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