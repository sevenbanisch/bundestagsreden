# AnalyticalDataset

### Kurzzusammenfassung
Durch corpusExplorer.py wird eine Streamlit-App zur Verfügung gestellt, mit der es möglich ist, die Reden nach Themen und/oder Keywords zu filtern.

### Vorbereitung
Die Annotationen zu jeder Rede sind in dem Ordner "annotations/topics" zu finden.
Es gibt 2 Optionen:
1) Falls ihr das Repository gecloned habt, müsst ihr nichts weiter tun und könnt direkt mit dem minimalen Beispiel starten.
2) Falls nicht, erstellt euch einen Ordner "annotations" und in diesem Ordner einen Ordner "topics". Ladet die .json Dateien hier herunter (Link: https://github.com/sevenbanisch/bundestagsreden/tree/master/annotations/topics) und verschiebt die heruntergeladenen Dateien in den erstellten Ordner "topics".

### Erste Schritte
Starte die Streamlit-App, indem du im ersten Schritt Streamlit im Terminal installierst (pip install streamlit) und anschließend die App mit streamlit run corpusExplorer.py startest.
Im Terminal muss man darauf achten, dass man in dem Ordner ist, in dem corpusExplorer.py liegt.