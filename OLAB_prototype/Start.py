import streamlit as st
import pandas as pd
import jsonlines
import json


#st.set_page_config(page_title="Bundestag Analysis", layout="wide")
st.set_page_config(
    page_title="Offenes Labor Bundestag – Start",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

@st.cache_data
def load_data(legislatur):
    #legislatur = 20
    alleReden = []
    with jsonlines.open(f'../data/speeches_{legislatur}.jsonl') as f:
        for line in f.iter():
            #for line in list(f):
            alleReden.append(line)
    alleReden.sort(key = lambda x:x['date'])
    return alleReden





@st.cache_data
def load_topic_annotations(legislatur):
    with open(f"../annotations/topics/topic_annotations_WP{legislatur}.json", "r", encoding="utf-8") as f:
        themen_annot = json.load(f)

    erlaubte_themen = ['Zuwanderung und Flucht', 'Energiepolitik und Energiemanagement', 'Wirtschaftslage', 'Inflation', 'Gesundheitswesen', 'Bildung', 'Wohnen und Mieten', 'Verkehr und Mobilität', 'Soziale Ungleichheit', 'Digitalisierung', 'Rente und Altersvorsorge', 'Sicherheit und Terrorismus', 'Künstliche Intelligenz', 'Cybersicherheit', 'Globalisierung', 'Europäische Union', 'Forschung und Innovation', 'Klimaschutz', 'Arbeitsmarkt', 'Integration', 'Außenpolitik', 'Kultur und Kunst', 'Familienpolitik', 'Geschlechtergerechtigkeit', 'Sport und Freizeit', 'Konsumverhalten', 'Medien und Kommunikation', 'Rechtsextremismus', 'Demokratie und Partizipation', 'Jugendpolitik', 'Städteentwicklung', 'Landwirtschaft', 'Infrastrukturprojekte', 'Finanzpolitik', 'Krise und Katastrophenmanagement', 'Friedenspolitik', 'Tierschutz', 'Mittelstand und KMU', 'Bildungsgerechtigkeit', 'Tourismus', 'Kommunalpolitik', 'Ehrenamt und Zivilgesellschaft', 'Verteidigung', 'Sonstige Themen']

    # Gefiltertes themen_annot
    themen_annot_clean = {}
    for speech_id, themes in themen_annot.items():
        neue_themen = {k: v for k, v in themes.items() if k in erlaubte_themen}
        if neue_themen:
            themen_annot_clean[speech_id] = neue_themen

    return themen_annot_clean

# Set default legislative period
legislatur = 20

# Load data only once
if "alleReden" not in st.session_state:
    with st.spinner(f"Lade Daten für Legislaturperiode {legislatur}..."):
        st.session_state.alleReden = load_data(legislatur)
        st.session_state.themen_annot = load_topic_annotations(legislatur)
        st.session_state.legislatur = legislatur



# st.title("📊 Bundestag Speech Analysis")
# st.markdown("""
# Welcome to the **Bundestag Debate Explorer**.
#
# Use the sidebar to navigate:
# - 🧠 PCA of Topics and Debates
# - 🕸️ Topic Similarity Networks
# - 💬 Speech & Theme Exploration
#
# Start exploring!
# """)

import streamlit as st

def main():

    # Styles / CSS (optional, dezent)
    st.markdown(
        """
        <style>
        .big-title {
            font-size: 2.5rem;
            font-weight: bold;
        }
        .subtitle {
            font-size: 1.3rem;
            color: #666666;
        }
        .section-heading {
            margin-top: 2rem;
            margin-bottom: 1rem;
            font-size: 1.7rem;
            font-weight: bold;
        }
        .highlight {
            color: #0052cc;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # --- Header / Hero Section ---
    st.markdown('<div class="big-title">Offenes Labor Bundestag (OLaB)</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Diskursive Strukturen sichtbar machen – mit offenen Parlamentsdaten & KI</div>', unsafe_allow_html=True)

    # Optional: Logo oder Bild einfügen
    # st.image("logo.png", width=150)

    st.write("---")
    st.markdown(
        """
        Willkommen bei OLaB, einem experimentellen Projekt an der Schnittstelle von *Computational Social Science*, *digitaler Öffentlichkeit* und *Wissenschaftskommunikation*.

        In dieser Anwendung kannst du interaktive Analysewerkzeuge nutzen, um:
        - **semantische Netzwerke** zu Themen und Begriffen zu erkunden,  
        - **interaktionale Netzwerke** (Zustimmung, Widerspruch) zu visualisieren,  
        - **LLM-gestützte Klassifizierung und Argumentanalyse** auf Bundestagsreden anzuwenden.
        """
    )

    # --- Abstract / Motivation ---
    st.markdown('<div class="section-heading">Motivation & Idee</div>', unsafe_allow_html=True)
    st.markdown(
        """
        Die parlamentarische Debatte im Deutschen Bundestag ist ein hochstrukturiertes Feld politischer Kommunikation — zugleich jedoch für viele Bürger:innen schwer zugänglich.

        Mit OLaB möchten wir diesen Diskursraum öffnen:
        - Transparenz und Nachvollziehbarkeit politischer Kommunikation  
        - Visualisierung komplexer Netzwerke und Zusammenhänge  
        - Einsatz moderner KI/LLM-Verfahren zur Themenanalyse  
        - Ein Angebot für Forschung, Lehre und Zivilgesellschaft  
        """
    )

    # # --- Navigation / Einstieg ---
    # st.markdown('<div class="section-heading">Loslegen</div>', unsafe_allow_html=True)
    # col1, col2, col3 = st.columns([1, 1, 1])
    # with col2:
    #     if st.button("🔎 Zu den Analysen", type="primary"):
    #         # Hier weiterleiten zur Analyse-Seite
    #         st.experimental_set_query_params(page="analyses")
    # st.markdown("— oder verwende die Navigation in der Seitenleiste")

    # --- Footer / Kontakt & Call to Action ---
    st.write("---")
    st.markdown(
        """
        ### Partner:innen & Zusammenarbeit
        Wir freuen uns über Partner*innen aus Wissenschaft, Administration und Zivilgesellschaft.  
        Wenn du Interesse hast, die Plattform mitzugestalten oder Daten beizusteuern, kontaktiere uns!

        **Kontakt:** sven.banisch@kit.edu  
        """
    )

#**Website:** [www.olab-bundestag.de](https://www.olab-bundestag.de)


if __name__ == "__main__":
    main()

