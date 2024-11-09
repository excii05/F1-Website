# app.py
from flask import Flask, render_template, request
from data_fetcher import fetch_driver_standings
from data_processor import process_driver_standings

app = Flask(__name__)

@app.route('/')
def driver_standings():
    # Daten von der API holen und verarbeiten
    data = fetch_driver_standings()
    standings = process_driver_standings(data)

    # Sortierparameter von der URL abfragen
    sort_by = request.args.get('sort_by')
    order = request.args.get('order', 'desc')

    # Daten sortieren, je nach sort_by und order
    if sort_by == 'points':
        standings = sorted(standings, key=lambda x: int(x['points']), reverse=(order == 'desc'))
    elif sort_by == 'wins':
        standings = sorted(standings, key=lambda x: int(x['wins']), reverse=(order == 'desc'))

    return render_template("driver_stats.html", standings=standings, sort_by=sort_by, order=order)

if __name__ == '__main__':
    app.run(debug=True)
