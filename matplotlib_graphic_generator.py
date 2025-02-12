import os
import json
import numpy as np
import matplotlib.pyplot as plt

def plot_driver_results(year, driver_id):
    file_path = f"cache/matplotlib/race_results_{year}.json"
    save_path = f"static/svg/drivers/{driver_id}_{year}.png"
    
    if not os.path.exists(file_path):
        print(f"Die Datei {file_path} existiert nicht.")
        return
    
    with open(file_path, "r", encoding="utf-8") as f:
        race_results_data = json.load(f)
    
    total_races = len(race_results_data)
    rounds = list(range(1, total_races + 1))
    positions = [np.nan] * total_races
    qualifying_positions = [np.nan] * total_races
    
    for round_num, race_data in race_results_data.items():
        for result in race_data["race"]:
            if result["driver"] == driver_id:
                index = int(round_num) - 1
                if result["status"] == "DNF":
                    positions[index] = 21
                else:
                    positions[index] = int(result["position"])
                break
        
        for result in race_data.get("qualifying", []):
            if result["driver"] == driver_id:
                index = int(round_num) - 1
                grid_position = int(result["grid"])
                if grid_position > 0:
                    qualifying_positions[index] = grid_position
                break
    
    if all(np.isnan(positions)) and all(np.isnan(qualifying_positions)):
        print(f"Keine Rennergebnisse oder Qualifying-Ergebnisse für Fahrer {driver_id} in {year} gefunden.")
        return
    
    plt.figure(figsize=(10, 5))
    
    plt.figure(figsize=(10, 5), facecolor="#f8f9fa")  
    ax = plt.gca()
    ax.set_facecolor("#f8f9fa")  
    
    # Linien zeichnen, ohne zusätzliche Marker
    plt.plot(rounds, positions, linestyle="-", color="b", label="Rennen")
    plt.plot(rounds, qualifying_positions, linestyle="-", color="r", label="Qualifying")
    
    # Einzelne Punkte nur dort setzen, wo keine Verbindung besteht
    for i in range(total_races):
        if not np.isnan(positions[i]):
            if (i == 0 or np.isnan(positions[i - 1])) and (i == total_races - 1 or np.isnan(positions[i + 1])):
                plt.scatter(rounds[i], positions[i], color='b', s=30)
        
        if not np.isnan(qualifying_positions[i]):
            if (i == 0 or np.isnan(qualifying_positions[i - 1])) and (i == total_races - 1 or np.isnan(qualifying_positions[i + 1])):
                plt.scatter(rounds[i], qualifying_positions[i], color='r')
    
    plt.gca().invert_yaxis()
    plt.xlabel("Rennrunde")
    plt.ylabel("Position")
    plt.title(f"Performance von {driver_id.split('_')[-1].capitalize()} in {year}")
    plt.legend()
    plt.grid(alpha=0.1)
    
    plt.xticks(range(1, total_races + 1, 1))
    plt.yticks(list(range(20, 0, -1)) + [21], labels=[str(i) for i in range(20, 0, -1)] + ["DNF"])
    
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    plt.savefig(save_path, format="png", dpi=300)
    print(f"Grafik gespeichert unter {save_path}")
    
    # plt.show()

def plot_driver_championship(year):
    file_path = f"cache/matplotlib/driver_standings_{year}.json"
    color_file = "cache/team_colors.json"
    save_path = f"static/svg/championship/driver_championship_{year}.svg"
    
    if not os.path.exists(file_path):
        print(f"Die Datei {file_path} existiert nicht.")
        return
    
    if not os.path.exists(color_file):
        print(f"Die Datei {color_file} mit den Teamfarben existiert nicht.")
        return
    
    with open(file_path, "r", encoding="utf-8") as f:
        standings_data = json.load(f)
    
    with open(color_file, "r", encoding="utf-8") as f:
        color_data = json.load(f)
        team_colors = {team["name"]: team["color"] for team in color_data["teams"]}  # Umwandlung in Dictionary
    
    total_rounds = len(standings_data)
    rounds = list(range(1, total_rounds + 1))
    drivers = set()
    driver_teams = {}

    for round_data in standings_data.values():
        for entry in round_data:
            driver = entry["driver"]
            team = entry["team"]
            drivers.add(driver)
            driver_teams[driver] = team  # Speichert das Team des Fahrers
    
    driver_positions = {driver: [None] * total_rounds for driver in drivers}
    
    for round_num, round_data in standings_data.items():
        for entry in round_data:
            driver = entry["driver"]
            position = int(entry["position"]) if entry["position"] is not None else float('nan') # Änderung
            driver_positions[driver][int(round_num) - 1] = position
    
    sorted_drivers = sorted(driver_positions.keys(), key=lambda d: driver_positions[d][-1] if driver_positions[d][-1] is not None else float('inf'))
    
    plt.figure(figsize=(12, 6), facecolor="#f8f9fa")
    ax = plt.gca()
    ax.set_facecolor("#f8f9fa") 
    
    for driver in sorted_drivers:
        positions = [pos if pos is not None else float('nan') for pos in driver_positions[driver]]
        short_driver = driver.split("_")[-1][:3].upper()
        
        team = driver_teams.get(driver, "default")
        color = team_colors.get(team, "#000000")  # Standardfarbe schwarz, falls Team nicht gefunden
        
        plt.plot(rounds, positions, linestyle="-", label=short_driver, color=color, linewidth=2)
    
    plt.gca().invert_yaxis()
    plt.xticks(rounds, range(1, total_rounds + 1))
    plt.yticks(range(1, len(drivers) + 1))
    plt.xlabel("Runde")
    plt.ylabel("Meisterschaftsposition")
    plt.title(f"{year} Championship Standings")
    plt.legend(loc="upper left", bbox_to_anchor=(1, 1))
    plt.grid(alpha=0.1)
    
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    plt.savefig(save_path, format="svg", bbox_inches='tight')
    print(f"Grafik gespeichert unter {save_path}")
    
    # plt.show()

def plot_constructor_championship(year):
    file_path = f"cache/matplotlib/constructor_standings_{year}.json"
    color_file = "cache/team_colors.json"
    save_path = f"static/svg/championship/constructor_championship_{year}.svg"
    
    if not os.path.exists(file_path):
        print(f"Die Datei {file_path} existiert nicht.")
        return
    
    if not os.path.exists(color_file):
        print(f"Die Datei {color_file} mit den Teamfarben existiert nicht.")
        return
    
    with open(file_path, "r", encoding="utf-8") as f:
        standings_data = json.load(f)
    
    with open(color_file, "r", encoding="utf-8") as f:
        color_data = json.load(f)
        team_colors = {team["name"]: team["color"] for team in color_data["teams"]}
    
    total_rounds = len(standings_data)
    rounds = list(range(1, total_rounds + 1))
    constructors = set()
    original_names = {}
    
    constructor_positions = {}
    
    for round_data in standings_data.values():
        for entry in round_data:
            original_name = entry["name"]
            constructor = original_name.replace(" F1 Team", "")
            constructors.add(constructor)
            original_names[constructor] = original_name
    
    constructor_positions = {constructor: [None] * total_rounds for constructor in constructors}
    
    for round_num, round_data in standings_data.items():
        for entry in round_data:
            original_name = entry["name"]
            constructor = original_name.replace(" F1 Team", "")
            position = int(entry["position"]) if entry["position"] is not None else float('nan')
            constructor_positions[constructor][int(round_num) - 1] = position
    
    sorted_constructors = sorted(constructor_positions.keys(), key=lambda c: constructor_positions[c][-1] if constructor_positions[c][-1] is not None else float('inf'))
    
    plt.figure(figsize=(12, 6), facecolor="#f8f9fa")
    ax = plt.gca()
    ax.set_facecolor("#f8f9fa")
    
    for constructor in sorted_constructors:
        positions = [pos if pos is not None else float('nan') for pos in constructor_positions[constructor]]
        original_name = original_names.get(constructor, constructor)
        color = team_colors.get(original_name, "#000000")
        
        plt.plot(rounds, positions, linestyle="-", label=constructor, color=color, linewidth=2)
    
    plt.gca().invert_yaxis()
    plt.xticks(rounds, range(1, total_rounds + 1))
    plt.yticks(range(1, len(constructors) + 1))
    plt.xlabel("Runde")
    plt.ylabel("Meisterschaftsposition")
    plt.title(f"{year} Constructor Championship Standings")
    plt.legend(loc="upper left", bbox_to_anchor=(1, 1))
    plt.grid(alpha=0.1)
    
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    plt.savefig(save_path, format="svg", bbox_inches='tight')
    print(f"Grafik gespeichert unter {save_path}")
    
    plt.show()

if __name__ == "__main__":
    year = 2024
    driver_id = "sainz"
    # plot_driver_results(year, driver_id)
    plot_driver_championship(year)
    # plot_constructor_championship(year)