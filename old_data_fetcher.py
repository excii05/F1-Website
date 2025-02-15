import logging
from data_fetcher import (
    fetch_driver_information,
    fetch_constructor_information,
)
from driver_data_fetcher import store_driver_data
from team_data_fetcher import store_team_data
from seasonal_data_fetcher import get_seasonal_stats
from matplotlib_data_fetcher import fetch_season_standings
from matplotlib_graphic_generator import (
    plot_driver_championship, 
    plot_constructor_championship, 
    plot_driver_results
)

year = "2020"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def weekly_driver_update():
    driver_list_data = fetch_driver_information(year)
    if driver_list_data:
        drivers = driver_list_data.get('MRData', {}).get('DriverTable', {}).get('Drivers', [])
        print(f"Starte wöchentlichen Fahrer-Datenabruf für {len(drivers)} Fahrer...")
        for driver in drivers:
            driver_id = driver.get("driverId")
            if driver_id:
                try:
                    print(f"Starte Abfrage für Fahrer: {driver_id}")
                    store_driver_data(driver_id)
                    print(f"Daten für Fahrer {driver_id} erfolgreich aktualisiert.")
                except Exception as e:
                    print(f"Fehler bei Fahrer {driver_id}: {e}")
    else:
        print("Keine Fahrerliste verfügbar. Fahrer-Job wird abgebrochen.")

def weekly_team_update():
    team_list_data = fetch_constructor_information(year)
    if team_list_data:
        teams = team_list_data.get('MRData', {}).get('ConstructorTable', {}).get('Constructors', [])
        print(f"Starte wöchentlichen Team-Datenabruf für {len(teams)} Teams...")
        for team in teams:
            team_id = team.get("constructorId")
            if team_id:
                try:
                    print(f"Starte Abfrage für Team: {team_id}")
                    store_team_data(team_id)
                    print(f"Daten für Team {team_id} erfolgreich aktualisiert.")
                except Exception as e:
                    print(f"Fehler bei Team {team_id}: {e}")
    else:
        print("Keine Team-Liste verfügbar. Team-Job wird abgebrochen.")
        
def weekly_seasonal_stats_update():
    driver_list_data = fetch_driver_information(year)
    if driver_list_data:
        drivers = driver_list_data.get('MRData', {}).get('DriverTable', {}).get('Drivers', [])
        print(f"Starte wöchentlichen saisonalen Statistik-Abruf für {len(drivers)} Fahrer...")
        for driver in drivers:
            driver_id = driver.get("driverId")
            if driver_id:
                try:
                    print(f"Starte Abfrage der saisonalen Statistiken für Fahrer: {driver_id}")
                    get_seasonal_stats(year, driver_id)
                except Exception as e:
                    print(f"Fehler bei saisonalen Statistiken für Fahrer {driver_id}: {e}")
    else:
        print("Keine Fahrerliste verfügbar. Saisonaler Statistik-Job wird abgebrochen.")

def weekly_graphics_data_update():
    fetch_season_standings(year)

def weekly_championship_graphics_update():
    plot_driver_championship(year)
    plot_constructor_championship(year)
    
def weekly_race_graphics_update():
    driver_list_data = fetch_driver_information(year)
    if driver_list_data:
        drivers = driver_list_data.get('MRData', {}).get('DriverTable', {}).get('Drivers', [])
        print(f"Starte wöchentliche Grafikgenerierung für {len(drivers)} Fahrer...")
        for driver in drivers:
            driver_id = driver.get("driverId")
            if driver_id:
                try:
                    print(f"Starte Generierung der wöchtentlichen Grafik für Fahrer: {driver_id}")
                    plot_driver_results(year, driver_id)
                except Exception as e:
                    print(f"Fehler bei der Generierung der wöchtentlichen Grafik für Fahrer: {driver_id}: {e}")
    else:
        print("Keine Fahrerliste verfügbar. Generierung der wöchtentlichen Grafik-Job wird abgebrochen.")

def main():
    # weekly_driver_update()
    # weekly_team_update()
    # weekly_seasonal_stats_update()
    # weekly_graphics_data_update()
    weekly_championship_graphics_update()
    weekly_race_graphics_update()

if __name__ == "__main__":
    main()