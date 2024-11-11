from flask import Flask, render_template, request
from data_fetcher import fetch_driver_standings, fetch_constructor_standings, fetch_race_schedule, fetch_driver_profile, fetch_driver_results
from data_processor import process_driver_standings, process_constructor_standings, process_race_schedule, process_driver_profile, process_driver_results

app = Flask(__name__)

@app.route('/')
def standings():
    # Daten von der API holen und verarbeiten
    driver_data = fetch_driver_standings()
    constructor_data = fetch_constructor_standings()
    race_schedule_data = fetch_race_schedule()

    driver_standings = process_driver_standings(driver_data)
    constructor_standings = process_constructor_standings(constructor_data)
    race_schedule = process_race_schedule(race_schedule_data)
    
    for driver in driver_standings:
        print(driver)  # Debug-Ausgabe

    # Sortierparameter von der URL abfragen
    driver_sort_by = request.args.get('driver_sort_by')
    driver_order = request.args.get('driver_order', 'desc')
    constructor_sort_by = request.args.get('constructor_sort_by')
    constructor_order = request.args.get('constructor_order', 'desc')

    # Fahrer-Wertung sortieren
    if driver_sort_by == 'points':
        driver_standings = sorted(driver_standings, key=lambda x: int(x['points']), reverse=(driver_order == 'desc'))
    elif driver_sort_by == 'wins':
        driver_standings = sorted(driver_standings, key=lambda x: int(x['wins']), reverse=(driver_order == 'desc'))

    # Konstrukteurs-Wertung sortieren
    if constructor_sort_by == 'points':
        constructor_standings = sorted(constructor_standings, key=lambda x: int(x['points']), reverse=(constructor_order == 'desc'))
    elif constructor_sort_by == 'wins':
        constructor_standings = sorted(constructor_standings, key=lambda x: int(x['wins']), reverse=(constructor_order == 'desc'))

    return render_template("index.html", 
                           driver_standings=driver_standings, 
                           constructor_standings=constructor_standings, 
                           driver_sort_by=driver_sort_by, 
                           driver_order=driver_order, 
                           constructor_sort_by=constructor_sort_by, 
                           constructor_order=constructor_order,
                           race_schedule=race_schedule
                           )

# Route für die Fahrerprofilseite
@app.route('/driver/<driver_id>')
def driver_profile(driver_id):
    # Fahrerprofil- und Ergebnisdaten von der API holen
    profile_data = fetch_driver_profile(driver_id)
    results_data = fetch_driver_results(driver_id)

    # Daten verarbeiten
    driver_info = process_driver_profile(profile_data)
    race_results = process_driver_results(results_data)

    return render_template('driver_profile.html', driver=driver_info, race_results=race_results)

if __name__ == '__main__':
    app.run(debug=True)
