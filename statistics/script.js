document.addEventListener("DOMContentLoaded", function () {
    const languageDropdown = document.getElementById("language-dropdown");
    const elements = document.querySelectorAll("[data-key]");

    // Lädt die Übersetzungen aus der JSON-Datei
    function loadTranslations(lang) {
        fetch("../translations.json")
            .then(response => response.json())
            .then(data => applyTranslations(data[lang]));
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
});
