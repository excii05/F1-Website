# data_processor.py

def process_driver_standings(data):
    standings_list = []

    # Die Datenstruktur durchlaufen und relevante Informationen extrahieren
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
