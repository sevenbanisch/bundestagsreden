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
<!-- TODO: Julian: Add documentation here -->
Wie die .html Datei(en) erstellt wird/werden.