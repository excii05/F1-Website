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

def process_race_schedule(data):
    schedule_list = []

    if data and "MRData" in data and "RaceTable" in data["MRData"]:
        for race in data["MRData"]["RaceTable"]["Races"]:
            schedule_list.append({
                "round": race["round"],
                "location": f"{race['Circuit']['Location']['locality']}, {race['Circuit']['Location']['country']}",
                "date": race["date"]
            })

    return schedule_list