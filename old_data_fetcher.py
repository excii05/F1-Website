import logging
import time
from apscheduler.schedulers.background import BackgroundScheduler
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

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

year = "2023"

# ---------------------------
# Scheduler-Konfiguration
# ---------------------------
WEEKLY_JOB_DAY = 'wed'    # Beispiel: jeden Mittwoch
WEEKLY_JOB_HOUR = 15      # 15:28 Uhr
WEEKLY_JOB_MINUTE = 38

# ---------------------------
# Scheduler-Funktionen: Wöchentliche Datenaktualisierung
# ---------------------------

def weekly_driver_update():
    """Ruft einmal wöchentlich für alle Fahrer die Daten ab und speichert sie."""
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
    """Ruft einmal wöchentlich für alle aktuellen Teams die Daten ab und speichert sie."""
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
    """Ruft einmal wöchentlich die saisonalen Statistiken für alle Fahrer ab und speichert sie."""
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
    """Ruft einmal wöchentlich die saisonalen Statistiken für alle Fahrer ab und speichert sie."""
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

# ---------------------------
# Scheduler initialisieren
# ---------------------------
scheduler = BackgroundScheduler()
scheduler.add_job(
    func=weekly_driver_update,
    trigger='cron',
    day_of_week=WEEKLY_JOB_DAY,
    hour=WEEKLY_JOB_HOUR,
    minute=WEEKLY_JOB_MINUTE,
    id='weekly_driver_update_job'
)
scheduler.add_job(
    func=weekly_team_update,
    trigger='cron',
    day_of_week=WEEKLY_JOB_DAY,
    hour=WEEKLY_JOB_HOUR,
    minute=WEEKLY_JOB_MINUTE,
    id='weekly_team_update_job'
)

if __name__ == '__main__':
    try:
        scheduler.start()
        logger.info(f"Scheduler gestartet: Wöchentliche Jobs jeden {WEEKLY_JOB_DAY} um {WEEKLY_JOB_HOUR:02d}:{WEEKLY_JOB_MINUTE:02d} Uhr.")
        
        # Blockiere das Hauptprogramm, damit es nicht sofort beendet wird
        while True:
            time.sleep(60)  # Sleep für 60 Sekunden, damit das Programm weiterläuft
    except (KeyboardInterrupt, SystemExit):
        logger.info("Scheduler wird gestoppt...")
        scheduler.shutdown()