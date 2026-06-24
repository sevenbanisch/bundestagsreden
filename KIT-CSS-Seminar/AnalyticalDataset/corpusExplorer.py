import streamlit as st
import jsonlines
import json
import matplotlib.pyplot as plt     # Für Visualisierung

#####################

DATA_PATH = "../../data/"

@st.cache_data
def laden(legislatur):
    # Wir generieren eine leere Liste:
    alleReden = []

    # Wir öffnen den entsprechende File (Dateipfad anpassen!):
    with jsonlines.open(f'{DATA_PATH}speeches_{legislatur}.jsonl') as f:
        for line in f.iter():
            # Wir packen alles Zeile für Zeile zu unserer Liste:
            alleReden.append(line)

    # Wir sortieren nach Datum:
    alleReden.sort(key = lambda x:x['date'])
    return alleReden

#####################





st.title("Exploration der Daten nach Themengebieten")
st.subheader("Dies ist ein einfaches Beispiel für eine interaktive App, die im Browser läuft.")
st.markdown("""<hr style="height:10px;border:none;color:#333;background-color:#333;" /> """, unsafe_allow_html=True)

WP = st.sidebar.selectbox(
    "Wahlperiode auswählen",
    options=[19, 20, 21],
    index=2,  # default = 21
)

alleReden = laden(WP)
# Load the topic annotations
with open(f"../../annotations/topics/topic_annotations_WP{WP}.json", "r", encoding="utf-8") as f:
    themen_annot = json.load(f)

st.info(f"Anzahl Reden: {len(alleReden)}")

##########################################
## Topics
##########################################

st.sidebar.subheader("Wonach willst du suchen?")

topics = ['Zuwanderung und Flucht', 'Energiepolitik und Energiemanagement', 'Wirtschaftslage', 'Inflation', 'Gesundheitswesen', 'Bildung', 'Wohnen und Mieten', 'Verkehr und Mobilität', 'Soziale Ungleichheit', 'Digitalisierung', 'Rente und Altersvorsorge', 'Sicherheit und Terrorismus', 'Künstliche Intelligenz', 'Cybersicherheit', 'Globalisierung', 'Europäische Union', 'Forschung und Innovation', 'Klimaschutz', 'Arbeitsmarkt', 'Integration', 'Außenpolitik', 'Kultur und Kunst', 'Familienpolitik', 'Geschlechtergerechtigkeit', 'Sport und Freizeit', 'Konsumverhalten', 'Medien und Kommunikation', 'Rechtsextremismus', 'Demokratie und Partizipation', 'Jugendpolitik', 'Städteentwicklung', 'Landwirtschaft', 'Infrastrukturprojekte', 'Finanzpolitik', 'Krise und Katastrophenmanagement', 'Friedenspolitik', 'Tierschutz', 'Mittelstand und KMU', 'Bildungsgerechtigkeit', 'Tourismus', 'Kommunalpolitik', 'Ehrenamt und Zivilgesellschaft', 'Verteidigung', 'Sonstige Themen']

selected_topics = st.sidebar.multiselect(
    "Themen auswählen",
    options=topics,
    default=[]
)

threshold = st.sidebar.slider(
    "Mindestgewicht",
    min_value=0.0,
    max_value=1.0,
    value=0.6,
    step=0.1
)

st.write("Ausgewählte Themen:", selected_topics)

if selected_topics:
    gefilterte_reden = []

    for rede in alleReden:
        rede_id = rede["id"]  # ggf. anpassen

        annot = themen_annot.get(rede_id, {})

        if any(
            annot.get(topic, 0) >= threshold
            for topic in selected_topics
        ):
            gefilterte_reden.append(rede)
else:
    gefilterte_reden = alleReden

st.info(f"Anzahl gefilterte Reden: {len(gefilterte_reden)}")


##########################################
## Keywords
##########################################


keywords_raw = st.sidebar.text_input(
    "Keywords suchen",
    placeholder="z.B. Migration Klima Haushalt"
)

keywords = [
    kw.strip().lower()
    for kw in keywords_raw.split()
    if kw.strip()
]

keyword_logik = st.sidebar.radio(
    "Keyword-Verknüpfung",
    ["Mindestens ein Keyword", "Alle Keywords"]
)

if keywords:
    reden_nach_keywords = []

    for rede in gefilterte_reden:
        text = rede["text"].lower()

        if keyword_logik == "Mindestens ein Keyword":
            keep = any(kw in text for kw in keywords)
        else:
            keep = all(kw in text for kw in keywords)

        if keep:
            reden_nach_keywords.append(rede)

    gefilterte_reden = reden_nach_keywords

st.info(f"Anzahl gefilterte Reden: {len(gefilterte_reden)}")

st.title("Hausaufgabe")

st.write("""
Verschaffen Sie sich einen Überblick über die Reden in Ihrem Themenbereich.
Erstellen Sie mindestens fünf aussagekräftige Statistiken oder Visualisierungen.
""")

st.markdown("""
### Mögliche Analysen

- Verteilung der Redeanzahl pro Partei zur Auswahl
- Verhältnis zur Gesamtanzahl im Datensatz (Wichtig zur Normalisierung)
- Redner:innen mit den meisten Beiträgen oder Keywords
- Entwicklung des Themas über die Wahlperioden
- Häufigste Wörter im Themenbereich
- Vergleich zweier Parteien hinsichtlich des Themas
- Anteil des Themas an allen Reden einer Wahlperiode
- Welche weiteren Themen treten häufig gemeinsam auf?
- Anzahl der Reden zum Thema über die Zeit
- Zeitliche Entwicklung einzelner Schlüsselbegriffe
- Unterschiede zwischen Regierungs- und Oppositionsparteien
- Parteien, die das Thema besonders früh oder spät aufgegriffen haben
- Wie ist das Geschlechterverhältnis? 
- **Gerne auch eigene Analysen mit Bezug zur Forschungsfrage!**
""")