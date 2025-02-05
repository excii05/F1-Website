import json
import os
import matplotlib.pyplot as plt
import numpy as np

def plot_driver_results(year, driver_id):
    file_path = f"cache/matplotlib/race_results_{year}.json"
    
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
                qualifying_positions[index] = int(result["grid"])
                break
    
    if all(np.isnan(positions)) and all(np.isnan(qualifying_positions)):
        print(f"Keine Rennergebnisse oder Qualifying-Ergebnisse für Fahrer {driver_id} in {year} gefunden.")
        return
    
    plt.figure(figsize=(10, 5))
    plt.plot(rounds, positions, marker="o", linestyle="-", color="b", label="Rennen")
    plt.plot(rounds, qualifying_positions, marker="s", linestyle="--", color="r", label="Qualifying")
    plt.gca().invert_yaxis()
    plt.xlabel("Rennrunde")
    plt.ylabel("Position")
    plt.title(f"Performance von {driver_id.split('_')[-1].capitalize()} in {year}")
    plt.legend()
    plt.grid()
    
    # Achsen anpassen
    plt.xticks(range(1, total_races + 1, 1))
    plt.yticks(list(range(20, 0, -1)) + [21], labels=[str(i) for i in range(20, 0, -1)] + ["DNF"])
    
    plt.show()

if __name__ == "__main__":
    year = 2024  # Ersetze mit dem gewünschten Jahr
    driver_id = "max_verstappen"  # Ersetze mit der gewünschten Fahrer-ID
    plot_driver_results(year, driver_id)