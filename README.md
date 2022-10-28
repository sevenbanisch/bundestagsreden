# bundestagsreden

## Vorbedingungen
### Installierte Software(-pakete)
* python >=3.8 (https://www.python.org/downloads/)

Benötigte python-packages können via `pip install <package-name>` installiert werden.

## Rohdaten
Die Rohdaten, die als Grundlage für die weiteren Auswertungen dienen liegen jeweils unter `bundestagsreden_parser/data_19/`, `bundestagsreden_parser/data_20/` und `bundestagsreden_parser/MdB-Stammdaten-data/`.
Sie enthalten die `.xml`-Dateien aller bisherigen Reden der Legislaturperioden 19 & 20 sowie die Stammdaten aller Bundestagsabgeordneten.
Diese und weitere Dateien stammen von https://www.bundestag.de/services/opendata.

## Vorverarbeitung (Parsen)
Ein Terminal (cmd, powershell, bash, iterm, etc.) in `bundestagsreden/bundestagsreden_parser/` öffnen und `python run.py` eingeben.
Dadurch werden zuerst die MdB-Stammdaten und anschließend alle Reden einer angegebenen Wahlperiode ins json-Format importiert und vorverarbeitet.
Die Ergebnisse dieser Vorverarbeitung werden unter `data/` je nach Option `speeches_19.jsonl`, `speeches_19_with_comments.jsonl`, `speeches_20.jsonl`, `speeches_20_with_comments.jsonl` und `parsed_mdbs.json` gespeichert.
Dieser Ordner (`data/`) wird nicht unter `git` verwaltet.

## Report Erstellung
Unter `pipelines_SS22/integration/` befinden sich python-scripte zur Generierung von `.html`-Dateien, welche die Analyse-Ergebnisse zu den Bundestagsreden grafisch darstellen.
Die Datei `main.py` integriert dabei sämtliche Funktionen zur Generierung des Reports.
Dafür muss man das Script via `python main.py` im Verzeichnis `pipelines_SS22/integration/` ausführen.
Nach erfolgreicher Ausführung findet man die Datei `topic_network.html` als Einstiegspunkt, sowie unter `/TOPnets/` entsprechende "Unterseiten" zur Navigation.
Des Weiteren liegen in `/imgs/wordclouds/` noch generierte Wordcloud-Bilder, welche aber noch keine Verwendung in den `.html`-Dateien finden.

### groups.pickle
Da die Vorverarbeitung des TopicModels mit Spacy lange dauert werden die erzeugten Gruppen in der `groups.pickle` Datei gespeichert.
Auf diese Datei wird bei folgenden Report-Erzeugungen zurückgegriffen. Wenn die Rohdaten und geparsten Daten der Bundestagsreden aktualisiert wurden muss diese Datei gelöscht und erneut erzeugt werden.