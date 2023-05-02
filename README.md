# bundestagsreden

## Vorbedingungen
### Installierte Software(-pakete)
* python >=3.8 (https://www.python.org/downloads/)

Benötigte python-packages können via `pip install <package-name>` installiert werden.

## Parser (`parser/`)

Der parser ist eine Weiterentwicklung von https://github.com/pournaki/bundestag-parser. 

### Rohdaten

Die Rohdaten, die als Grundlage für die weiteren Auswertungen dienen liegen jeweils unter `parser/data_19/`, `parser/data_20/` und `parser/MdB-Stammdaten-data/`.
Sie enthalten die `.xml`-Dateien aller bisherigen Reden der Legislaturperioden 19 & 20 sowie die Stammdaten aller Bundestagsabgeordneten.
Diese und weitere Dateien stammen von https://www.bundestag.de/services/opendata.

### Ausführung

Ein Terminal (cmd, powershell, bash, iterm, etc.) in `bundestagsreden/parser/` öffnen und `python run.py` eingeben.
Dadurch werden zuerst die MdB-Stammdaten und anschließend alle Reden einer angegebenen Wahlperiode ins json-Format importiert und vorverarbeitet.

Man kann zwischen der 19. und der 20. Legislaturperiode wählen, sowie, ob Kommentare (Zurufe, Beifallsbekundungen, etc.) integriert werden sollen.

Die Ergebnisse dieser Vorverarbeitung werden im Ordner `data/` je nach Option `speeches_19.jsonl`, `speeches_19_with_comments.jsonl`, `speeches_20.jsonl`, `speeches_20_with_comments.jsonl` und `parsed_mdbs.json` gespeichert.

## Datenordner (`data/`)

Dieser Ordner (`data/`) wird nicht unter `git` verwaltet. Das heißt, dass man zunächst den Parser ausführen muss, der lokal die entsprechenden `JSONL`-Dateien ablegt. Darauf greifen die Analyseskripte zu.

## Projekte (`projects/`)

Im Ordner `project/` befinden sich einige Beispielanalysen in der Regel als jupyter notebook abgelegt.

## Utilities (`utilities/`)

Hier werden in Zukunft stabile Versionen wichtiger Funktionen als "proper python" zur Verfügung gestellt.