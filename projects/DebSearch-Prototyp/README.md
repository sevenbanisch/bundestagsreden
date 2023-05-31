# DebSearch Prototyp

## Vorbedingungen
### Installierte Software(-pakete)
* python >=3.8 (https://www.python.org/downloads/)

Benötigte python-packages können via `pip install <package-name>` installiert werden.

## Report Erstellung
Unter `projects/DebSearch-Prototyp/` befinden sich python-scripte zur Generierung von `.html`-Dateien, welche die Analyse-Ergebnisse zu den Bundestagsreden grafisch darstellen.
Die Datei `main.py` integriert dabei sämtliche Funktionen zur Generierung des Reports.
Dafür muss man das Script via `python main.py` im Verzeichnis `projects/DebSearch-Prototyp/` ausführen.
Nach erfolgreicher Ausführung findet man die Datei `topic_network.html` als Einstiegspunkt, sowie unter `/TOPnets/` entsprechende "Unterseiten" zur Navigation.
Des Weiteren liegen in `/imgs/wordclouds/` noch generierte Wordcloud-Bilder, welche aber noch keine Verwendung in den `.html`-Dateien finden.

### groups.pickle
Da die Vorverarbeitung des TopicModels mit Spacy lange dauert werden die erzeugten Gruppen in der `groups.pickle` Datei gespeichert.
Auf diese Datei wird bei folgenden Report-Erzeugungen zurückgegriffen. Wenn die Rohdaten und geparsten Daten der Bundestagsreden aktualisiert wurden muss diese Datei gelöscht und erneut erzeugt werden.