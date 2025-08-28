import streamlit as st
import jsonlines
import json
import pandas as pd
from collections import Counter, defaultdict
import numpy as np
from sklearn.decomposition import PCA
import sys
import os
import plotly.graph_objects as go
import plotly.express as px
import random


st.set_page_config(page_title="Open Lab Bundestag (micro prototype)", layout="wide")

st.title("Open Lab Bundestag (micro prototype)")
@st.cache_data
def load_data(legislatur):
    alleReden = []
    with jsonlines.open(f'../../data/speeches_{legislatur}.jsonl') as f:
        for line in f.iter():
            #for line in list(f):
            alleReden.append(line)
    alleReden.sort(key = lambda x:x['date'])
    return alleReden

alleReden = load_data(20)
st.write("Anzahl Reden:", len(alleReden))

default_keywords = ['Umweltschutz','Klimawandel','Klimakrise','Klimahysterie']

selected_keywords = st.multiselect(
    "Wähle Parteien aus",
    options=default_keywords,
    default=default_keywords[0]
)


untermenge = [rede for rede in alleReden if all(kw in rede['text'] for kw in selected_keywords)]

st.write(f'Die Suche nach "{selected_keywords}" ergab {len(untermenge)} Reden')

person_partei = {}
redner_liste = []
for rede in untermenge:
    person = rede['name']
    partei = rede.get('party', 'unbekannt')
    redner_liste.append(person)
    if person not in person_partei:
        person_partei[person] = partei

redner_zaehlung = Counter(redner_liste)
top_10_redner = redner_zaehlung.most_common(10)
st.write(f"10 Politiker*innen, die '{selected_keywords}' am häufigsten erwähnt haben:")
for person, anzahl in top_10_redner:
    partei = person_partei.get(person, 'unbekannt')
    st.write(f"{person} ({partei}): {anzahl} Reden")


st.title("Häufigkeitsverteilung")
party_names = set()
for rede in alleReden:
    party_names.add(rede['party'])


parteien = list(party_names)


# angenommen: selected_keywords ist eine Liste von Suchwörtern
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
    barmode="group",   # gruppierte Balken pro Partei
    text="anzahl",
    title="Verteilung der Häufigkeiten nach Partei und Keyword"
)
fig.update_traces(textposition="outside")
st.plotly_chart(fig, use_container_width=True)
