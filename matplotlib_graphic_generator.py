import json
import os
import matplotlib.pyplot as plt

def plot_driver_results(year, driver_id):
    file_path = f"cache/matplotlib/race_results_{year}.json"
    
    if not os.path.exists(file_path):
        print(f"Die Datei {file_path} existiert nicht.")
        return
    
    with open(file_path, "r", encoding="utf-8") as f:
        race_results_data = json.load(f)
    
    rounds = []
    positions = []
    
    for round_num, race_data in race_results_data.items():
        for result in race_data["race"]:
            if result["driver"] == driver_id:
                rounds.append(int(round_num))
                if result["status"] == "DNF":
                    positions.append(21)  # DNF wird als Position 21 dargestellt
                else:
                    positions.append(int(result["position"]))
                break
    
    if not rounds:
        print(f"Keine Rennergebnisse für Fahrer {driver_id} in {year} gefunden.")
        return
    
    # Sortieren nach Rennrunde
    rounds, positions = zip(*sorted(zip(rounds, positions)))
    
    plt.figure(figsize=(10, 5))
    plt.plot(rounds, positions, marker="o", linestyle="-", color="b", label=f"{driver_id}")
    plt.gca().invert_yaxis()
    plt.xlabel("Rennrunde")
    plt.ylabel("Position")
    plt.title(f"Rennergebnisse von {driver_id} in {year}")
    plt.grid()
    
    # Achsen anpassen
    plt.xticks(range(1, max(rounds) + 1, 1))
    plt.yticks(list(range(20, 0, -1)) + [21], labels=[str(i) for i in range(20, 0, -1)] + ["DNF"])
    
    plt.show()

if __name__ == "__main__":
    year = 2024  # Ersetze mit dem gewünschten Jahr
    driver_id = "sainz"  # Ersetze mit der gewünschten Fahrer-ID
    plot_driver_results(year, driver_id)