import json
import os
import matplotlib.pyplot as plt
import numpy as np

def plot_driver_results(year, driver_id):
    file_path = f"cache/matplotlib/race_results_{year}.json"
    save_path = f"static/svg/drivers/{driver_id}.png"
    
    if not os.path.exists(file_path):
        print(f"Die Datei {file_path} existiert nicht.")
        return
    
    with open(file_path, "r", encoding="utf-8") as f:
        race_results_data = json.load(f)
    
    total_races = len(race_results_data)
    rounds = list(range(1, total_races + 1))
    positions = [np.nan] * total_races  # Initialisiere alle Werte mit NaN
    qualifying_positions = [np.nan] * total_races  # Initialisiere alle Werte für das Qualifying mit NaN
    
    for round_num, race_data in race_results_data.items():
        for result in race_data["race"]:
            if result["driver"] == driver_id:
                index = int(round_num) - 1  # Index anpassen
                if result["status"] == "DNF":
                    positions[index] = 21  # DNF wird als Position 21 dargestellt
                else:
                    positions[index] = int(result["position"])
                break
        
        for result in race_data.get("qualifying", []):
            if result["driver"] == driver_id:
                index = int(round_num) - 1  # Index anpassen
                grid_position = int(result["grid"])
                
                # Filter: Falls Gridposition 0 ist, ignoriere das Qualifying-Ergebnis
                if grid_position > 0:
                    qualifying_positions[index] = grid_position
                break
    
    if all(np.isnan(positions)) and all(np.isnan(qualifying_positions)):
        print(f"Keine Rennergebnisse oder Qualifying-Ergebnisse für Fahrer {driver_id} in {year} gefunden.")
        return
    
    plt.figure(figsize=(10, 5))
    plt.plot(rounds, positions, linestyle="-", color="b", label="Rennen")
    plt.plot(rounds, qualifying_positions, linestyle="-", color="r", label="Qualifying")
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
    
    plt.show()

def plot_driver_championship(year):
    file_path = f"cache/matplotlib/driver_standings_{year}.json"
    save_path = f"static/svg/championship/championship_{year}.svg"
    
    if not os.path.exists(file_path):
        print(f"Die Datei {file_path} existiert nicht.")
        return
    
    with open(file_path, "r", encoding="utf-8") as f:
        standings_data = json.load(f)
    
    total_rounds = len(standings_data)
    rounds = list(range(1, total_rounds + 1))
    drivers = set()
    
    for round_data in standings_data.values():
        for entry in round_data:
            drivers.add(entry["driver"])
    
    driver_positions = {driver: [None] * total_rounds for driver in drivers}
    
    for round_num, round_data in standings_data.items():
        for entry in round_data:
            driver = entry["driver"]
            position = int(entry["position"])
            driver_positions[driver][int(round_num) - 1] = position
    
    sorted_drivers = sorted(driver_positions.keys(), key=lambda d: driver_positions[d][-1] if driver_positions[d][-1] is not None else float('inf'))
    
    plt.figure(figsize=(12, 6))
    
    for driver in sorted_drivers:
        positions = [pos if pos is not None else float('nan') for pos in driver_positions[driver]]
        short_driver = driver.split("_")[-1][:3].upper()
        plt.plot(rounds, positions, linestyle="-", label=short_driver)
    
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

if __name__ == "__main__":
    year = 2024
    driver_id = "zhou"
    plot_driver_results(year, driver_id)
    # plot_driver_championship(year)