import json
import os
import matplotlib.pyplot as plt

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
    
    # Fahrer nach ihrer letzten bekannten Position sortieren
    sorted_drivers = sorted(driver_positions.keys(), key=lambda d: driver_positions[d][-1] if driver_positions[d][-1] is not None else float('inf'))
    
    plt.figure(figsize=(12, 6))
    
    for driver in sorted_drivers:
        positions = [pos if pos is not None else float('nan') for pos in driver_positions[driver]]
        short_driver = driver.split("_")[-1][:3].upper()  # Nur die ersten drei Buchstaben des Nachnamens in Großbuchstaben
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
    
    plt.show()

if __name__ == "__main__":
    year = 2024  # Ersetze mit dem gewünschten Jahr
    plot_driver_championship(year)