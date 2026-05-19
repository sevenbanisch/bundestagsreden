import streamlit as st
import jsonlines
import pandas as pd
from collections import Counter, defaultdict
import plotly.express as px
import re
import spacy
from wordcloud import WordCloud
import io

st.set_page_config(page_title="Die Umweltdebatte - Themen und Positionen im Bundestag", layout="wide")

#Daten laden
@st.cache_data
def load_data(legislaturen):
    alleReden = []
    for legislatur in legislaturen:
        with jsonlines.open(f'../../data/speeches_{legislatur}.jsonl') as f:
            for line in f.iter():
                line["legislatur"] = legislatur
                alleReden.append(line)
    alleReden.sort(key = lambda x:x['date'])
    return alleReden

alleReden = load_data([19, 20])


#Funktion: Reden in einzelne Sätze splitten
def split_into_sentences(text):
    sentences = re.split(r'(?<=[.!?]) +', text)
    return sentences

#Keywords in Sätzen markieren
def highlight_keywords(text, keywords):
    for kw in sorted(keywords, key=len, reverse=True):
        pattern = re.compile(rf'\b({re.escape(kw)}[a-zA-ZäöüÄÖÜß]*)', flags=re.IGNORECASE)
        text = pattern.sub(r'<mark>\1</mark>', text)
    return text

#Keywords + 1 Satz davor + 1 Satz danach
def extract_keyword_context(text, keywords):
    sentences = split_into_sentences(text)
    contexts = []
    keywords_lower = [kw.lower() for kw in keywords]
    for i, sentence in enumerate(sentences):
        sentence_lower = sentence.lower()
        if any(kw in sentence_lower for kw in keywords_lower):
            prev_sent = sentences[i-1] if i > 0 else ""
            next_sent = sentences[i+1] if i < len(sentences)-1 else ""
            context = "\n".join([prev_sent, sentence, next_sent]).strip()
            contexts.append(context)
    return contexts


# Seitendesign
#st.set_page_config(page_title="Die Umweltdebatte - Themen und Positionen im Bundestag", layout="wide")

# Hintergrundfarbe
st.markdown("""
    <style>
        div[class^="stApp"] {
            background-color: #E9ECEF;
        }
    </style>
""", unsafe_allow_html=True)

#Schriftart
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700;900&display=swap');

        html, body, div, p, span, h1, h2, h3, h4, h5, h6, button, input, textarea, label, {
            font-family: 'Roboto', sans-serif !important;
        }
    </style>
""", unsafe_allow_html=True)

# Überschrift, Unterüberschrift & Einleitung
st.markdown("""
    <div style="Text-align: center;">
        <h1 style="font-size: 140px; color: #343a40; font-weight: 900; margin-top: 0px;">
            Die Umweltdebatte
        </h1>
        <h2 style="font-size: 55px; color: #343a40; font-weight: 500; margin-top: 0px;">
            Themen und Positionen im Bundestag<br>während der 19. und 20. Legislaturperiode
        </h2>
        <h3 style="font-size: 18px; color: #6C757D; font-weight: 350; margin-top: 25px; margin-bottom: 60px; line-height: 1.4;">
            Im Rahmen des Seminars <em>Computational Social Science: Themen und Positionen im Deutschen Bundestag</em> 
            wurden Tools für die sozial-semantische Analyse von Reden, die während der letzten beiden Legislaturperioden 
            im Bundestag gehalten wurden, entwickelt.<br>Ziel dieses Projektes war die Analyse der Reden mit Fokus auf 
            den Themenschwepunkt <strong>Umweltdebatte</strong>. Dabei soll zunächst ein allgemeiner Überblick über das 
            Thema gegeben werden, bevor verschiedene Analysen einen genaueren Einblick in das Thema erlauben. Es 
            werden folgende Fragen beantwortet: <strong>Welche Partei spricht über welche Themen im Kontext der 
            Umweltdebatte?</strong>, <strong>Wie oft kommt das vor?</strong> und <strong>Welcher Politiker/ Welche 
            Politikerin benutzt, wann welche Keywords?</strong> Zuletzt soll außerdem der Einfluss der Gruppierung <em>Die 
            Letzte Generation</em> auf die Umweltdebatte im Bundestag betrachtet werden indem die Fragestellungen 
            <strong>Welche Parteien sprechen häufig über <em>Die Letzte Generation</em>?</strong> und <strong>In welchem Kontext sprechen 
            die Parteien über <em>Die Letzte Generation</em>?</strong> genauer betrachtet werden.<br>Mit Hilfe dieser 
            Analysen sollen Aussagen über die verschiedenen Akteure der Umweltdebatte im Deutschen Bundestag getroffen 
            und visualisiert werden.
    </div>
""", unsafe_allow_html=True)


#Tabs Design
st.markdown("""
    <style>
        button[data-baseweb="tab"] {
            padding: 30px 30px !important;
            background-color: #CED4DA !important;
            border-radius: 12px !important;
            margin-right: 10px !important;
        }

        button[data-baseweb="tab"] div[data-testid="stMarkdownContainer"] p {
            font-size: 30px !important;
            font-weight: 500 !important;
            margin: 0;
            color: #343A40 !important;
        }
        
        button[data-baseweb="tab"][aria-selected="true"] {
            background-color: #F8F9FA !important;
        }
        
        button[data-baseweb="tab"][aria-selected="true"] div[data-testid="stMarkdownContainer"] p {
            font-size: 35px !important;
            font-weight: 550 !important;
            color: #212529 !important;
        }
        
        div[data-baseweb="tab-highlight"] {
            display: none !important;
            width: 0px !important;
            height: 0px !important;
            position: absolute !important;
            left: -9999px !important;
            overflow: hidden !important;
        }
        
        div[role="tablist"] {
            display:flex;
            justify-content: center !important;
            margin-bottom: 30px;
        }

        div[role="tablist"] > button[data-baseweb="tab"]:nth-child(3) div[data-testid="stMarkdownContainer"] p {
            font-style: italic !important;
        }
    </style>
""", unsafe_allow_html=True)

#Tabs Inhalt
tabs = st.tabs(["Die Umweltdebatte im Bundestag", "Politiker*innen & Keywords", "Die Letzte Generation"])


#Keywords in Kategorien
keyword_kategorien = {
    "Klimaschutz": [
        'Klimawandel','Klimaschutz','Klimaziele','Klimaneutralität','Klimapaket','Klimafonds',
        'Pariser Abkommen','Klimakrise','Klimanotstand','Klimasteuer','CO2-Neutralität','CO2-Bepreisung',
        'Emissionshandel'
    ],
    "Energie": [
        'Energiewende','Energiekrise','erneuerbare Energien','Zwang zur Solar- und Windenergie',
        'Energieeffizienz','Energiespeicherung','Windkraft','Photovoltaik','Solarpflicht',
        'Atomkraftausstieg','Kohleausstieg','Wasserstoffstrategie','Stromnetztausbau'
    ],
    "Mobilität": [
        'Verkehrswende','emissionsfreie Mobilität','E-Mobilität','Verbrennerverbot','Tempolimit',
        'ÖPNV-Ausbau','Radverkehrsförderung','Bahnreform','Autofeindlichkeit'
    ],
    "Aktivismus & Protest": [
        'Klimaproteste','Klimastreik','Klimaaktivisten','Klimaterroristen','Radikalisierung der Klimabewegung',
        'Fridays for Future','Letzte Generation','Neue Generation','Greta Thunberg','Widerstandskollektiv'
    ],
    "Umwelt & Landwirtschaft": [
        'Umwelt','Umweltschutz','Umweltpolitik','Umweltaktivismus','Umweltrecht','Förderprogramme',
        'Ökodiktatur','Agrarwende','Agrar-Ideologie','Artensterben','Massentierhaltung','Biodiversität',
        'Ressourcenschonung','Kreislaufwirtschaft','Nachhaltigkeit','Nachhaltigkeitsstrategie','nachhaltige Entwicklung'
    ]
}


#Sidebar für Keywords
with st.sidebar:
    st.markdown("## 🔍 Keyword-Auswahl")
    suchbegriff = st.text_input("Nach Keyword suchen:").lower()

    selected_keywords = []

    for kategorie, keywords in keyword_kategorien.items():
        gefiltert = [kw for kw in keywords if suchbegriff in kw.lower()]

        if gefiltert:
            default_keywords = ["Klimawandel"]
            ausgewählt = st.multiselect(
                label=kategorie,
                options=gefiltert,
                default=[kw for kw in gefiltert if kw in default_keywords],
                key=f"multiselect_{kategorie}"
            )
            selected_keywords.extend(ausgewählt)

#Warnung: Kein Keyword ausgewählt (für Sidebar)
    if not selected_keywords:
        st.markdown("""<div style="background-color:#F8D7DA; padding: 15px; border-radius: 8px; color: #721C24; border-left: 6px solid #F5C6CB; border-right: 6px solid #F5C6CB; font-size: 14px;">
            Es muss mindestens ein Keyword ausgewählt werden!
        </div>""", unsafe_allow_html=True)
    else:
        untermenge = [
            rede for rede in alleReden
            if all(kw.lower() in rede['text'].lower() for kw in selected_keywords)
        ]


#Warnung: Keine Reden mit Keyword gefunden (für Tab 2)
    def zeige_warnung_box(text: str):
        st.markdown(f"""
            <div style="background-color:#F8D7DA; padding: 15px; border-radius: 8px;
                        color: #721C24; border-left: 6px solid #F5C6CB;
                        border-right: 6px solid #F5C6CB; font-size: 14px;">
                {text}
            </div>
        """, unsafe_allow_html=True)


#Infobox: Wie viele Reden werden untersucht (für Tab 1 & 2)
    def zeige_info_box(text: str):
        st.markdown(f"""
            <div style="background-color:#D1ECF1; padding: 15px; border-radius: 8px;
                        color: #0C5460; border-left: 6px solid #BEE5EB;
                        border-right: 6px solid #BEE5EB; font-size: 14px;">
                {text}
            </div>
        """, unsafe_allow_html=True)


# Infobox: Anzahl gefundener Reden (Tab 2)
    def zeige_anzahl_box(text: str):
        st.markdown(f"""
            <div style="background-color:#E2E3E5; padding: 15px; border-radius: 8px;
                        color: #383D41; border-left: 6px solid #D6D8DB;
                        border-right: 6px solid #D6D8DB; font-size: 14px;">
                {text}
            </div>
        """, unsafe_allow_html=True)


#Tab 1 Die Umweltdebatte im Bundestag
with tabs[0]:
    st.markdown("""
    <h1 style="font-size: 30px; color: #343A40; font-weight: 600; margin-top: 0px;">
        Welche Partei spricht über welche Themen im Kontext der Umweltdebatte?<br>In wie vielen Reden der Parteien werden 
        die Keywords thematisiert?
    </h1>
    <h2 style="font-size: 15px; color: #212529; font-weight: 350; margin-top: 0px;">
        Die Auswahl der Keywords erfolgt über die Sidebar links.<br>Hier wird zunächst eine Kategorie ausgesucht, in der 
        dann geziehlt mindestens ein Keyword gewählt wird. Es können auch Keywords aus verschiedenen Kategorien gleichzeitig
        ausgewählt und verglichen werden. Optional können Keywords auch über die Suchfunktion gefunden werden.
    </h2>
    <h3 style="font-size: 20px; color: #212529; font-weight: 500; margin-top: 25px;">
        Verteilung der Häufigkeiten nach Partei und Keyword:
    </h3>
    """, unsafe_allow_html=True)

#Analyse Tab 1
    party_names = set()
    for rede in alleReden:
        party_names.add(rede['party'])

    parteien = list(party_names)

    if selected_keywords:
        rows = []
        for kw in selected_keywords:
            untermengeKW = [rede for rede in alleReden if kw.lower() in rede["text"].lower()]
            for partei in parteien:
                count = sum(1 for r in untermengeKW if r["party"] == partei)
                rows.append({"partei": partei, "keyword": kw, "anzahl": count})

        df_freq = pd.DataFrame(rows)

        fig = px.bar(
            df_freq,
            x="partei",
            y="anzahl",
            color="keyword",
            barmode="group",
            text="anzahl",
            title=""
        )


#Schaubild Design
        fig.update_traces(
            textposition="outside",
            textfont=dict(
                family="Roboto, sans-serif",
                size=12,
                color="#212529"
            )
        )

        fig.update_layout(
            xaxis_title="Parteien",
            yaxis_title="Anzahl der Reden mit Keyword",
            xaxis=dict(
                title_font=dict(
                    family="Roboto, sans-serif",
                    size=18,
                    color="#212529"
                ),
                title_standoff=30,
                tickfont=dict(
                    family="Roboto, sans-serif",
                    size=12,
                    color="#495057"
                )
            ),
            yaxis=dict(
                title_font=dict(
                    family="Roboto, sans-serif",
                    size=18,
                    color="#212529"
                ),
                title_standoff=30,
                tickfont=dict(
                    family="Roboto, sans-serif",
                    size=12,
                    color="#495057"
                )
            ),
            legend_title_text="",
            legend_title_font=dict(
                family="Roboto, sans-serif",
                size=18,
                color="#212529"
            ),
            legend=dict(
                font=dict(
                    family="Roboto, sans-serif",
                    size=12,
                    color="#212529"
                )
            ),
            plot_bgcolor="#F8F9FA",
            paper_bgcolor="#F8F9FA",

            margin=dict(
                l=100,
                r=100,
                t=40,
                b=80,
            )
        )

        st.plotly_chart(fig, use_container_width=False)

    st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)

    zeige_info_box(f"Anzahl aller Reden, die durchsucht werden: {len(alleReden)}")


#Tab 2 Politiker*innen & Keywords
with tabs[1]:
    st.markdown("""
        <h1 style="font-size: 30px; color: #343A40; font-weight: 600; margin-top: 0px;">
            Welcher Politiker/ Welche Politikerin benutzt, wann welches Keyword im Kontext der Umweltdebatte?
        </h1>
        <h2 style="font-size: 15px; color: #212529; font-weight: 350; margin-top: 0px;">
            Die Auswahl der Keywords erfolgt über die Sidebar links.<br>Hier wird zunächst eine Kategorie ausgesucht, in
            der dann geziehlt mindestens ein Keyword gewählt wird. Es können auch Keywords aus verschiedenen Kategorien 
            gleichzeitig ausgewählt und verglichen werden. Optional können Keywords auch über die Suchfunktion gefunden 
            werden.
        </h2>
        <h3 style="font-size: 20px; color: #212529; font-weight: 500; margin-top: 25px;">
            Verteilung der Häufigkeiten nach Politiker*in und Keyword:
        </h3>
        """, unsafe_allow_html=True)


#Analyse Tab 2
    if selected_keywords:
        untermenge = [rede for rede in alleReden if all(kw.lower() in rede['text'].lower() for kw in selected_keywords)]

        zeige_anzahl_box(f'Die Suche nach den Keywords {selected_keywords} ergab {len(untermenge)} Reden.')

        st.markdown("<div style='margin-top: 30px;'></div>", unsafe_allow_html=True)

        person_partei = {}
        redner_liste = []
        reden_pro_person = defaultdict(list)

        for rede in untermenge:
            person = rede['name']
            partei = rede.get('party', 'unbekannt')
            redner_liste.append(person)
            if person not in person_partei:
                person_partei[person] = partei
            reden_pro_person[person].append(rede)

        redner_zaehlung = Counter(redner_liste)
        redner_sortiert = redner_zaehlung.most_common()

        if len(redner_sortiert) == 0:
            zeige_warnung_box("Keine Rede mit den ausgewählten Keywords gefunden.")
        else:
            st.markdown("""
                <h3 style='font-size: 18px; font-weight: 400; text-decoration: underline; color: #212529;'>
                    Politiker*innen, die die ausgewählten Keywords erwähnt haben:
                </h3>
            """, unsafe_allow_html=True)

# Top 10 anzeigen
            top_anzahl = 10
            for idx, (person, anzahl) in enumerate(redner_sortiert[:top_anzahl], start=1):
                partei = person_partei.get(person, 'unbekannt')
                with st.expander(f"{idx}. {person} ({partei}): {anzahl} Reden"):
                    for rede in reden_pro_person[person]:
                        datum = rede.get('date', 'unbekannt')
                        rede_id = rede.get('id', 'unbekannte ID')
                        kontexte = extract_keyword_context(rede['text'], selected_keywords)
                        st.markdown(f"---\n**Datum:** {datum} | **Rede-ID:** {rede_id}")
                        if kontexte:
                            for i, context in enumerate(kontexte, start=1):
                                highlighted_context = highlight_keywords(context, selected_keywords)
                                st.markdown(f"""
                                    <div style="margin-bottom: 30px;">
                                        <div style="font-weight: 600; font-size: 16px; color: #212529; margin-bottom: 5px;">
                                            Kontext {i}:
                                        </div>
                                        <blockquote style="margin-top: 0; margin-bottom: 10px;">
                                            {highlighted_context.replace(chr(10), "<br>")}
                                        </blockquote>
                                    </div>
                                """, unsafe_allow_html=True)

                        else:
                            st.markdown("_Kein passender Kontext gefunden._")

# Zusätzliche anzeigen
            if len(redner_sortiert) > top_anzahl:
                st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)
                if st.toggle("Vollständige Liste anzeigen"):
                    st.markdown("""
                        <h4 style='font-size: 18px; font-weight: 400; text-decoration: underline; color: #212529;'>
                            Alle weiteren Politiker*innen, die die ausgewählten Keywords erwähnt haben:
                        </h4>
                    """, unsafe_allow_html=True)

                    for idx, (person, anzahl) in enumerate(redner_sortiert[top_anzahl:], start=top_anzahl + 1):
                        partei = person_partei.get(person, 'unbekannt')
                        with st.expander(f"{idx}. {person} ({partei}): {anzahl} Reden"):
                            for rede in reden_pro_person[person]:
                                datum = rede.get('date', 'unbekannt')
                                rede_id = rede.get('id', 'unbekannte ID')
                                kontexte = extract_keyword_context(rede['text'], selected_keywords)
                                st.markdown(f"---\n**Datum:** {datum} | **Rede-ID:** {rede_id}")
                                if kontexte:
                                    for i, context in enumerate(kontexte, start=1):
                                        highlighted_context = highlight_keywords(context, selected_keywords)
                                        st.markdown(f"""
                                            <div style="margin-bottom: 30px;">
                                                <div style="font-weight: 600; font-size: 16px; color: #212529; margin-bottom: 5px;">
                                                    Kontext {i}:
                                                </div>
                                                <blockquote style="margin-top: 0; margin-bottom: 10px;">
                                                    {highlighted_context.replace(chr(10), "<br>")}
                                                </blockquote>
                                            </div>
                                        """, unsafe_allow_html=True)


                                else:
                                    st.markdown("Kein passender Kontext gefunden.")

    st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)

    zeige_info_box(f"Anzahl aller Reden, die durchsucht werden: {len(alleReden)}")


#Tab 3 Die Letzte Generation
with tabs[2]:
    st.markdown("""
        <h1 style="font-size: 30px; color: #343A40; font-weight: 600; margin-top: 0px;">
            Nimmt <em>Die Letzte Generation</em> Einfluss auf die Umweltdebatte im deutschen Bundestag?
        </h1>
        <h2 style="font-size: 20px; color: #212529; font-weight: 500; margin-top: 25px;">
            Welche Parteien sprechen häufig über <em>Die Letzte Generation</em>?
        </h2>
        """, unsafe_allow_html=True)

#Analyse Tab 3
    lg_keyword = "Letzte Generation"
    reden_mit_lg = [rede for rede in alleReden if lg_keyword.lower() in rede["text"].lower()]

    parteien = sorted(set(rede["party"] for rede in reden_mit_lg))

#Keywordhäufigkeit: Welche Partei spricht über 'Die Letzte Generation'?
    rows = []
    for partei in parteien:
        for legislatur in [19, 20]:
            anzahl = sum(
                1 for rede in reden_mit_lg
                if rede["party"] == partei and rede["legislatur"] == legislatur
            )
            rows.append({
                "Partei": partei,
                "Legislaturperiode": f"{legislatur}. Legislaturperiode ",
                "Anzahl": anzahl
            })

    df_lg = pd.DataFrame(rows)

#Schaubild Design
    fig_lg = px.bar(
        df_lg,
        x="Partei",
        y="Anzahl",
        color="Legislaturperiode",
        barmode="group",
        text="Anzahl",
    )

    fig_lg.update_traces(
        textposition="outside",
        textfont=dict(
            family="Roboto, sans-serif",
            size=12,
            color="#212529"
        )
    )

    fig_lg.update_layout(
        xaxis_title="Parteien",
        yaxis_title="Anzahl der Reden über 'Die Letzte Generation'",
        xaxis=dict(
            title_font=dict(
                family="Roboto, sans-serif",
                size=18,
                color="#212529"
            ),
            title_standoff=30,
            tickfont=dict(
                family="Roboto, sans-serif",
                size=12,
                color="#495057"
            )
        ),
        yaxis=dict(
            title_font=dict(
                family="Roboto, sans-serif",
                size=18,
                color="#212529"
            ),
            title_standoff=30,
            tickfont=dict(
                family="Roboto, sans-serif",
                size=12,
                color="#495057"
            )
        ),
        legend_title_text="",
        legend=dict(
            font=dict(
                family="Roboto, sans-serif",
                size=12,
                color="#212529"
            )
        ),
        plot_bgcolor="#F8F9FA",
        paper_bgcolor="#F8F9FA",
        margin=dict(l=100, r=100, t=40, b=80)
    )

    st.plotly_chart(fig_lg, use_container_width=False)

    st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)

    zeige_info_box(f"Anzahl aller Reden, die durchsucht werden: {len(alleReden)}")

    st.markdown("<hr style='margin-top:50px; margin-bottom:30px;'>", unsafe_allow_html=True)

#Wortfrequenzanalyse: In welchem Kontext sprechen die Parteien über Die Letzte Generation?
    st.markdown("""
    <h2 style="font-size: 20px; color: #212529; font-weight: 500; margin-top: 25px;">
    In welchem Kontext sprechen die Parteien über <em>Die Letzte Generation</em>?
    </h2>
    <p style="font-size: 15px; color: #212529; font-weight: 350; margin-bottom: 5px">
    Die Auswahl der Parteien, um eine Wortfrequenzanalyse für diese durchzuführen, erfolgt über die Dropbox unten. 
    Untersucht werden alle Reden der ausgewählten Parteien, in denen <em>Die Letzte Generation</em> erwähnt wird. Die 
    Darstellung zwei unterschiedlicher Parteien nebeneinander dient dem Vergleich.
    </p>
    """, unsafe_allow_html=True)

    parteien_mit_lg = sorted(set([rede["party"] for rede in reden_mit_lg]))

    col1, col2 = st.columns(2)
    standard_partei_1 = "AfD"
    standard_partei_2 = "BÜNDNIS 90/DIE GRÜNEN"
    with col1:
        partei_1 = st.selectbox("", parteien_mit_lg, key="partei_1")
    with col2:
        partei_2 = st.selectbox("", parteien_mit_lg, key="partei_2")

# spaCy laden
    nlp = spacy.load("de_core_news_sm")

#Wordcloud
    def erstelle_wordcloud(partei):
        reden_partei = [rede["text"] for rede in reden_mit_lg if rede["party"] == partei]

        if not reden_partei:
            return None

        gesamter_text = " ".join(reden_partei)
        doc = nlp(gesamter_text)

        bedeutungswörter = [
            token.lemma_.lower()
            for token in doc
            if not token.is_stop and not token.is_punct and token.pos_ in {"NOUN", "VERB", "ADJ"}
        ]

        eigene_stopwörter = {
            "generation", "letzte", "deutschland", "deutsch", "bundestag", "regierung", "partei",
            "herr", "frau", "dame", "kollege", "kollegin", "geehrt", "geehrte", "liebe",
            "präsidentin", "letzter", "mensch"
        }

        filtered_words = [w for w in bedeutungswörter if w not in eigene_stopwörter and len(w) > 2]
        wort_haeufigkeit = Counter(filtered_words)

        wordcloud = WordCloud(
            width=1600,
            height=800,
            background_color="#F8F9FA",
            colormap="tab10",
            max_words=20
        ).generate_from_frequencies(wort_haeufigkeit)

        img_buffer = io.BytesIO()
        wordcloud.to_image().save(img_buffer, format='PNG')
        img_buffer.seek(0)
        return img_buffer

    col1, col2 = st.columns(2)

    with col1:
        if wc_img := erstelle_wordcloud(partei_1):
            st.image(wc_img, use_container_width=True)
        else:
            zeige_warnung_box(f"Keine Reden mit Bezug zur 'Letzten Generation' von {partei_1} gefunden.")

    with col2:
        if wc_img := erstelle_wordcloud(partei_2):
            st.image(wc_img, use_container_width=True)
        else:
            zeige_warnung_box(f"Keine Reden mit Bezug zur 'Letzten Generation' von {partei_2} gefunden.")

#Kontextanalyse: Welche Begriffe stehen in direkter Nähe zu der 'Letzten Generation'?
    st.markdown("<hr style='margin-top:50px; margin-bottom:30px;'>", unsafe_allow_html=True)

    st.markdown("""
    <h2 style="font-size: 20px; color: #212529; font-weight: 500; margin-top: 25px;">
    Redebeiträge der Parteien über <em>Die Letzte Generation</em>
    </h2>
    <p style="font-size: 15px; color: #212529; font-weight: 350; margin-bottom: 5px">
    Die Auswahl der Parteien erfolgt über die Dropbox unten. Hier werden dann die entsprechenden Redebeiträge mit den 
    konkreten Abschnitten, in denen <em>Die Letzte Generation</em> erwähnt wird, angezeigt.
    </p>
    """, unsafe_allow_html=True)

    partei_auswahl = st.selectbox("", parteien_mit_lg, key="kontext_partei")

#Reden filtern
    reden_partei_lg = [
        rede for rede in reden_mit_lg
        if rede["party"] == partei_auswahl
    ]

    if not reden_partei_lg:
        zeige_warnung_box(f"Keine Reden von {partei_auswahl}, in denen 'Letzte Generation' erwähnt wird.")
    else:
        def extract_extended_context(text, keywords, window=2):
            sentences = split_into_sentences(text)
            contexts = []
            keywords_lower = [kw.lower() for kw in keywords]

            for i, sentence in enumerate(sentences):
                sentence_lower = sentence.lower()
                if any(kw in sentence_lower for kw in keywords_lower):
                    start = max(0, i - window)
                    end = min(len(sentences), i + window + 1)
                    context = " ".join(sentences[start:end])
                    contexts.append(context.strip())

            return contexts

        keyword_lg = ["Letzte Generation"]
        for rede in reden_partei_lg:
            redner = rede.get("name", "Unbekannt")
            datum = rede.get("date", "Unbekanntes Datum")
            rede_id = rede.get("id", "Unbekannte ID")
            kontexte = extract_extended_context(rede["text"], keyword_lg, window=2)

#Expander Design
            with st.expander(f"**{redner}** – {datum}"):
                st.markdown(
                    f"<div style='font-weight:600; font-size:16px; margin-bottom:10px;'>Rede-ID: {rede_id}</div>",
                    unsafe_allow_html=True)

                if kontexte:
                    for i, abschnitt in enumerate(kontexte, start=1):
                        highlighted = highlight_keywords(abschnitt, keyword_lg)
                        st.markdown(f"""
                            <div style="margin-bottom: 25px;">
                                <blockquote style="margin-top: 0; margin-bottom: 10px;">
                                    {highlighted.replace(chr(10), "<br>")}
                                </blockquote>
                            </div>
                        """, unsafe_allow_html=True)
                else:
                    st.markdown("_Kein Kontext gefunden._")
