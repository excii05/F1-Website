document.addEventListener("DOMContentLoaded", function () {
    const languageDropdown = document.getElementById("language-dropdown");
    const elements = document.querySelectorAll("[data-key]");

    // Lädt die Übersetzungen aus der JSON-Datei
    function loadTranslations(lang) {
        fetch("../translations.json")
            .then(response => {
                if (!response.ok) {
                    throw new Error("Fehler beim Laden der Übersetzungen.");
                }
                return response.json();
            })
            .then(data => applyTranslations(data[lang]))
            .catch(error => console.error("Fehler beim Laden der Übersetzungen:", error));
    }

    // Wendet die Übersetzungen auf die entsprechenden Elemente an
    function applyTranslations(translations) {
        elements.forEach(element => {
            const key = element.getAttribute("data-key");
            if (translations[key]) {
                element.innerHTML = translations[key];
            }
        });
    }

    // Event-Listener für Dropdown, um die Sprache zu ändern
    languageDropdown.addEventListener("change", (event) => {
        const selectedLang = event.target.value;
        loadTranslations(selectedLang);
    });

    // Standardmäßig auf Deutsch setzen
    loadTranslations("de");

    // Funktion zum Laden der Fahrerwertung
    function loadDriverStandings() {
        fetch('/api/driver-standings')
            .then(response => {
                if (!response.ok) {
                    throw new Error("Fehler beim Laden der Fahrerwertung.");
                }
                return response.json();
            })
            .then(data => {
                let driverTable = `<table class="table">
                    <thead>
                        <tr>
                            <th>Position</th>
                            <th>Voller Name</th>
                            <th>Punkte</th>
                            <th>Siege</th>
                            <th>Konstrukteur</th>
                        </tr>
                    </thead>
                    <tbody>`;
                data.forEach(driver => {
                    driverTable += `<tr>
                        <td>${driver.position}</td>
                        <td>${driver.name}</td>
                        <td>${driver.points}</td>
                        <td>${driver.wins}</td>
                        <td>${driver.constructor}</td>
                    </tr>`;
                });
                driverTable += `</tbody></table>`;
                document.getElementById("driver-standings").innerHTML = driverTable;
            })
            .catch(error => console.error('Error loading driver standings:', error));
    }

    // Funktion zum Laden der Konstrukteurswertung
    function loadConstructorStandings() {
        fetch('/api/constructor-standings')
            .then(response => {
                if (!response.ok) {
                    throw new Error("Fehler beim Laden der Konstrukteurswertung.");
                }
                return response.json();
            })
            .then(data => {
                let constructorTable = `<table class="table">
                    <thead>
                        <tr>
                            <th>Position</th>
                            <th>Konstrukteur</th>
                            <th>Punkte</th>
                            <th>Siege</th>
                        </tr>
                    </thead>
                    <tbody>`;
                data.forEach(constructor => {
                    constructorTable += `<tr>
                        <td>${constructor.position}</td>
                        <td>${constructor.name}</td>
                        <td>${constructor.points}</td>
                        <td>${constructor.wins}</td>
                    </tr>`;
                });
                constructorTable += `</tbody></table>`;
                document.getElementById("constructor-standings").innerHTML = constructorTable;
            })
            .catch(error => console.error('Error loading constructor standings:', error));
    }

    // Aufrufen der Funktionen zum Laden der Daten
    loadDriverStandings();
    loadConstructorStandings();
});
