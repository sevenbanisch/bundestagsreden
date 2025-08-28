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
    #legislatur = 20
    alleReden = []
    with jsonlines.open(f'../../data/speeches_{legislatur}.jsonl') as f:
        for line in f.iter():
            #for line in list(f):
            alleReden.append(line)
    alleReden.sort(key = lambda x:x['date'])
    return alleReden

alleReden = load_data(20)
st.write("Anzahl Reden:", len(alleReden))

# Load the topic annotations
with open("../WoerkingWithLLMTopics/topic_annotations_WP20.json", "r", encoding="utf-8") as f:
    themen_annot = json.load(f)

########################################################

########################################################

min_weight = st.slider("Minimum topic weight to include", 0.0, 1.0, 0.5, 0.05)
unique_topics = set()
topic_doc_count = Counter()
topic_weight_sum = defaultdict(float)

for doc_id, topic_map in themen_annot.items():
    for topic, weight in topic_map.items():
        topic_norm = topic.strip()
        w = float(weight)
        if w >= min_weight:
            unique_topics.add(topic_norm)
            topic_doc_count[topic_norm] += 1
            topic_weight_sum[topic_norm] += w

unique_topics = sorted(
    unique_topics,
    key=lambda t: topic_doc_count[t],
    reverse=True
)

# Summarize
df = pd.DataFrame({
    "topic": list(unique_topics),
    "documents_with_topic": [topic_doc_count[t] for t in unique_topics],
    "mean_score": [topic_weight_sum[t]/topic_doc_count[t] for t in unique_topics],
}).sort_values(["documents_with_topic", "mean_score", "topic"], ascending=[False, False, True])

st.metric("Unique topics", len(unique_topics))
st.dataframe(df, use_container_width=True)

# Optional: quick search/filter
q = st.text_input("Filter topics")
if q:
    st.dataframe(df[df["topic"].str.contains(q, case=False, na=False)], use_container_width=True)

#
# selected_topics = st.multiselect(
#     "Select topics for further analysis",
#     options=df["topic"].tolist(),
#     default=[]
# )


########################################################

########################################################


selected_topic = st.selectbox(
    "Wähle ein Thema:",
    options=unique_topics,
    index=6
)
count = topic_doc_count.get(selected_topic, 0)
st.subheader(f"📄 Dein Thema: {selected_topic} ({count} Reden)")

# selected_speeches = [
#     rede for rede in alleReden
#     if selected_topic in themen_annot[rede['id']]
# ]

selected_speeches = [
    rede for rede in alleReden
    if themen_annot[rede['id']].get(selected_topic, 0.0) >= min_weight
]

# zufällige Reden aus deinen gefilterten
subset_size = min(20, len(selected_speeches))
random_subset = random.sample(selected_speeches, subset_size)

st.write(len(selected_speeches))
#subset = random.sample(submissions, sample_size)

# daraus eine auswählen
speech = st.selectbox(
    "Wähle eine Rede aus einer Zufallsauswahl",
    options=random_subset,
    format_func=lambda r: f"{r['name']} ({r['party']})"
)

# Text anzeigen
st.subheader("Rede")
st.write(speech["text"])