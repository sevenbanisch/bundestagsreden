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

WP = 20
alleReden = load_data(WP)
st.write("Anzahl Reden:", len(alleReden))

# Load the topic annotations
with open(f"../../annotations/topics/topic_annotations_WP{WP}.json", "r", encoding="utf-8") as f:
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

st.title("Themen Netzwerke")
party_names = set()
for rede in alleReden:
    party_names.add(rede['party'])



selected_parties = st.multiselect(
    "Wähle Parteien aus",
    options=party_names,
    default=party_names
)

unique_topics_pca = unique_topics#[0:50]

doc_ids_all = list(themen_annot.keys())

doc_ids = []
for rede in alleReden:
    if rede['party'] in selected_parties:
        doc_ids.append(rede['id'])

# Mapping von Topic → Spaltenindex
topic_to_idx = {t: i for i, t in enumerate(unique_topics_pca)}

# Array initialisieren (Reden x Topics)
X = np.zeros((len(doc_ids), len(unique_topics_pca)))

# Füllen
for i, doc_id in enumerate(doc_ids):
    for topic, score in themen_annot[doc_id].items():
        if topic in topic_to_idx:   # falls gefiltert
            j = topic_to_idx[topic]
            X[i, j] = score

# Jetzt: X ist deine Matrix
st.write(X.shape)   # (n_docs, n_topics)

# PCA über die Topics
pca = PCA(n_components=2, random_state=0)
Z = pca.fit_transform(X.T)  # jetzt: Topics × PCs

df_plot = pd.DataFrame({
    "topic": list(unique_topics_pca),
    "PC1": Z[:, 0],
    "PC2": Z[:, 1],
}).head(50)

# erklärter Varianzanteil
var_txt = f"PC1: {pca.explained_variance_ratio_[0]:.1%}, PC2: {pca.explained_variance_ratio_[1]:.1%}"
st.caption(f"Erklärte Varianz — {var_txt}")

# Scatter-Plot mit Topic-Labels
fig = px.scatter(
    df_plot,
    x="PC1", y="PC2",
    hover_name="topic",
    text="topic",
    title="PCA der Topics (2D)"
)

st.plotly_chart(fig, use_container_width=True)






selected_topic = st.selectbox(
    "Wähle ein Thema:",
    options=unique_topics
)
count = topic_doc_count.get(selected_topic, 0)
st.subheader(f"📄 Dein Thema: {selected_topic} ({count} Reden)")


