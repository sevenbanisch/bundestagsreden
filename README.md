# bundestagsreden
Mal schauen, was man mit den Bundestagsreden machen kann.

<!-- TODO: Julian: Add documentation here -->

# Vorbedingungen
## Installierte Software(-pakete)
* python >=3.8 (https://www.python.org/downloads/)

Benötigte python-packages können via `pip install <package-name>` installiert werden.

## Heruntergeladene Dateien
Daten von https://www.bundestag.de/services/opendata herunterladen und in `data/` speichern.
Im Folgenden ein Beispiel, wie die Inhalte von `data/` aussehen, mit den MdB-Stammdaten, und den Reden der Legislaturperioden 19 & 20. 
```bash
data
├── MdB-Stammdaten-data
│   ├── MDB_STAMMDATEN.DTD
│   └── MDB_STAMMDATEN.XML
├── data_19
│   └── speeches
│       ├── 1900001.xml
│       ├── 1900002.xml
│       ├── 1900003.xml
│       ├── 1900004.xml
│       ├── 1900005.xml
│       ├── 1900006.xml
│       └── BUNDESTAGSDOKUMENTE.dtd
└── data_20
  └── speeches
      ├── 20001-data.xml
      ├── 20002-data.xml
      ├── 20003-data.xml
      ├── 20004-data.xml
      ├── 20005-data.xml
      └── 20042-data.xml
```

# Parsen
`run.py` script in `bundestagsreden parser`-Ordner ausführen.
Ein Terminal (cmd, powershell, bash, iterm, etc.) in `bundestagsreden/bundestagsreden parser/` öffnen und `python run.py` eingeben.
Dadurch werden zuerst die MdB-Stammdaten und anschließend alle Reden einer angegebenen Wahlperiode ins json-Format importiert und vorverarbeitet.

# Report Erstellung
Wie die .html Datei(en) erstellt wird/werden.