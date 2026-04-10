import streamlit as st
import jsonlines
import ast
from openai import OpenAI
from langchain_openai import ChatOpenAI
#from langchain.chat_models import ChatOpenAI
#from langchain.prompts import ChatPromptTemplate
import os
from collections import Counter
from itertools import chain
import json

#thages_key = os.environ['THAGES_API_KEY']
#base_url = 'http://thages.philosophie.kit.edu:8080/v1'

llm_base_url = "https://ki-toolbox.scc.kit.edu/api/v1"
llm_model = "kit.gpt-oss-120b"

try:
    llm_api_key = os.environ["KIT_AI_API_KEY"]
except KeyError as exc:
    raise RuntimeError("Umgebungs‑Variable KIT_AI_API_KEY fehlt") from exc


def call_llm(messages, temperature: float = 0.0) -> str:
    client = OpenAI(api_key=llm_api_key, base_url=llm_base_url)
    try:
        # Send chat request
        resp = client.chat.completions.create(
            model=llm_model,
            messages=messages,
            temperature=temperature)
    except KeyError as exc:
        raise RuntimeError("Error") from exc


    return resp.choices[0].message.content.strip()


alleReden = st.session_state.alleReden
themen_annot = st.session_state.themen_annot
legislatur = st.session_state.legislatur

st.title("Themenklassifikation der Reden mit LLMs")

st.subheader("Das ist eine Rede:")
rede = alleReden[20000]
st.write(rede)

st.subheader("Das sind die vordefinierten Themen:")

topics = ['Zuwanderung und Flucht', 'Energiepolitik und Energiemanagement', 'Wirtschaftslage', 'Inflation', 'Gesundheitswesen', 'Bildung', 'Wohnen und Mieten', 'Verkehr und Mobilität', 'Soziale Ungleichheit', 'Digitalisierung', 'Rente und Altersvorsorge', 'Sicherheit und Terrorismus', 'Künstliche Intelligenz', 'Cybersicherheit', 'Globalisierung', 'Europäische Union', 'Forschung und Innovation', 'Klimaschutz', 'Arbeitsmarkt', 'Integration', 'Außenpolitik', 'Kultur und Kunst', 'Familienpolitik', 'Geschlechtergerechtigkeit', 'Sport und Freizeit', 'Konsumverhalten', 'Medien und Kommunikation', 'Rechtsextremismus', 'Demokratie und Partizipation', 'Jugendpolitik', 'Städteentwicklung', 'Landwirtschaft', 'Infrastrukturprojekte', 'Finanzpolitik', 'Krise und Katastrophenmanagement', 'Friedenspolitik', 'Tierschutz', 'Mittelstand und KMU', 'Bildungsgerechtigkeit', 'Tourismus', 'Kommunalpolitik', 'Ehrenamt und Zivilgesellschaft', 'Verteidigung', 'Sonstige Themen']

descriptions = ['Der Umgang mit Migration, Asyl und Integration ', 'Die Aufrechterhaltung und Ausbau von Erneuerbaren Energien sowie fossiler Energieträger', 'Die wirtschaftliche Stabilität ist zentrales Anliegen.', 'Bekämpfung und Steuerung der Inflation sind zentrale Anliegen ', 'Verbesserungen im Gesundheitssystem und die Bewältigung der Folgen der Pandemie stehen im Fokus.', 'Reformen und Investitionen im Bildungssektor, Förderung von Chancengleichheit und Erhöhung der Bildungsqualität', 'Wohnungsnot, Bauvorhaben und steigende Mietpreise stehen im Fokus', 'Der Ausbau nachhaltiger Verkehrsnetze und die Förderung von E-Mobilität sind wichtige Themen.', 'Maßnahmen zur Bekämpfung der sozialen Ungleichheit und zur Förderung der sozialen Gerechtigkeit.', 'Fortschritte in der Digitalisierung und die Förderung von digitaler Infrastruktur.', 'Sicherung der Renten und Anpassungen an demografische Veränderungen.', 'Innere Sicherheit und Maßnahmen gegen Terrorismus.', 'Regulierung und Integration von KI in den Alltag und die Arbeitswelt.', 'Schutz vor Cyberangriffen und Datenschutz.', 'Auswirkungen der Globalisierung auf die deutsche Wirtschaft und Gesellschaft.', 'Die Rolle Deutschlands in der EU und die Europawahlen.', 'Förderung von Wissenschaft und technologischen Innovationen.', 'Maßnahmen zum Schutz der Klima, Natur, Umwelt und  Biodiversität für eine nachhaltige Umwelt', 'Herausforderungen und Chancen im Arbeitsmarkt, insbesondere durch Automatisierung und KI.', 'Erfolgreiche Integration von Geflüchteten und Minderheiten in die Gesellschaft und den Arbeitsmarkt.', 'Deutschlands Rolle in der internationalen Politik und Beziehungen zu anderen Ländern.', 'Förderung von Kultur und Kunst sowie deren Zugang für alle Bevölkerungsschichten.', 'Unterstützung von Familien und Kinderbetreuung.', 'Förderung der Gleichstellung der Geschlechter.', 'Organisation und Förderung von Sportereignissen', 'Veränderungen im Konsumverhalten und deren Auswirkungen.', 'Veränderungen in der Medienlandschaft und die Rolle der sozialen Medien.', 'Bekämpfung von Rechtsextremismus und Rassismus.', 'Stärkung der demokratischen Strukturen und Bürgerbeteiligung.', 'Förderung von Jugendprojekten und Partizipationsmöglichkeiten für junge Menschen.', 'Nachhaltige Entwicklung und Planung von Städten.', 'Zukunft der Landwirtschaft und nachhaltige Agrarwirtschaft.', 'Ausbau und Modernisierung der deutschen Infrastruktur.', 'Maßnahmen zur Haushaltskonsolidierung und Steuerpolitik sowie Regulierung der Finanzmärkte', 'Vorbereitungen und Maßnahmen zur Bewältigung von Krisen.', 'Einsatz für internationale Friedensbemühungen.', 'Maßnahmen zum Schutz von Tieren und Tierrechten.', 'Unterstützung für kleine und mittlere Unternehmen.', 'Maßnahmen zur Förderung der Chancengleichheit im Bildungsbereich.', 'Förderung und nachhaltige Entwicklung des Tourismus.', 'Herausforderungen und Chancen auf kommunaler Ebene.', 'Unterstützung und Förderung des ehrenamtlichen Engagements.', 'Gewährleistung der nationale Sicherheit durch eine Kombination aus diplomatischen, militärischen und zivilen Maßnahmen sowie durch die Zusammenarbeit mit internationalen Partnern.', 'bspw. Geschäftsordnung etc. also alles was den oberen Themen nicht zuordnungsbar ist.']

with st.expander("Anzeigen!"):
    # Create two columns
    col1, col2 = st.columns([1, 3])  # You can tweak the ratio for better spacing

    # Header
    col1.subheader("Topic")
    col2.subheader("Description")

    # Content
    for topic, desc in zip(topics, descriptions):
        col1.write(topic)
        col2.write(desc)

st.subheader("Das ist die Anfrage an das LLM (Prompt):")

num_topics = 3
topic_descriptions = "\n".join(
    [f"[{topic}]: {desc}" for topic, desc in zip(topics, descriptions)]
)

topics_prompt = "\n".join(
    [f"{tx+1}. {topic}" for tx,topic in enumerate(topics)]
)

#rede=alleReden[21000]['text']

system_msg = f"""Du bist ein politischer Themenanalyst.
Du bist darauf spezialisiert, Bundestagsreden präzise nach vordefinierten Themen zu klassifizieren.
Die vordefinierten Themen mit einer kurzen Beschreibung findest du hier:

{topic_descriptions}.

Bitte wähle nur aus diesen vordefinierten Themen. Keine Beschreibungen!"""

user_msg = f"""Ordne eine Rede aus dem deutschen Bundestag thematisch einer Kategorie zu. Hier sind die Kategorien als python-Liste

{topics}. 

Gib ausschließlich die {num_topics} relevantesten Kategorien in dieser Liste zurück. Bitte als Output nur eine python-Liste. Keine Beschreibungen oder Erläuterungen!

Rede:
{rede['text']}
"""

with st.expander("System Message Anzeigen!"):
    st.write(system_msg)
with st.expander("User Message Anzeigen!"):
    st.write(user_msg)

# Eingabe von Anzahl der Samples
num_samples = st.number_input(
    label="Anzahl der Wiederholungen",
    min_value=1,
    max_value=10,
    value=3,  # Default-Wert
    step=1
)

if st.button("Frage nun das LLM!"):
    messages=[
        {
            "role": "system",
            "content": system_msg
        },
        {
            "role": "user",
            "content": user_msg
        }
    ]
    #num_samples = 5
    all_cats = []
    failed = 0
    for sample in range(num_samples):
        try:
            # llm = ChatOpenAI(
            #     model_name=llm_model,
            #     base_url=llm_base_url,
            #     openai_api_key=llm_api_key
            #     #openai_api_base=base_url,
            #     #openai_api_key=api_key,
            #     #max_tokens=2096
            # )
            # response = llm.invoke(messages)
            response = call_llm(messages,temperature=0.9)
            cats = ast.literal_eval(response)
            if isinstance(cats, list):
                all_cats.append(cats)
            else:
                failed += 1
                continue
        except Exception as e:
            print(f"[Sample {sample+1}] Error: {e}")
            failed += 1
            continue
        st.write(f"{sample+1}. Trail: {cats}")
    # Flatten and count
    flat = list(chain.from_iterable(all_cats))
    st.write(flat)
    counter = Counter(flat)
    total = sum(counter.values())
    counter = {k: v * num_topics / total for k, v in counter.items()}
    sorted_topics = dict(sorted(counter.items(), key=lambda x: x[1], reverse=True))

    st.subheader("Hier ist das finale Ergebnis (topic scores):")
    st.write(sorted_topics)
    #st.write(failed)