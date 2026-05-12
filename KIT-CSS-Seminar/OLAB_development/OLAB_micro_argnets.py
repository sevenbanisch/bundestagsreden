import streamlit as st
from streamlit.components.v1 import html
import jsonlines
import json
import pandas as pd
from collections import Counter, defaultdict
from langchain_openai import ChatOpenAI
import networkx as nx
from pyvis.network import Network

from transformers import AutoTokenizer
tokenizer = AutoTokenizer.from_pretrained("bert-base-german-cased")
import re
import ast
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
from spacy.lang.de.stop_words import STOP_WORDS as DE_STOPWORDS
from sklearn.decomposition import PCA
import sys
import os
import plotly.graph_objects as go
import plotly.express as px
import random


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

@st.cache_data
def parse_json_safely(response: str) -> dict:
    """Tries to parse JSON, strips junk if necessary."""
    try:
        return json.loads(response)
    except json.JSONDecodeError:
        try:
            start, end = response.find("{"), response.rfind("}") + 1
            return json.loads(response[start:end])
        except Exception:
            return {"error": "Invalid JSON", "raw_response": response}



st.set_page_config(page_title="Open Lab Bundestag (micro prototype)", layout="wide")

st.title("Open Lab Bundestag (micro prototype)")

legislatur = 20
alleReden = load_data(legislatur)
st.write("Anzahl Reden:", len(alleReden))

# Load the topic annotations
with open(f"../WoerkingWithLLMTopics/topic_annotations_WP{legislatur}.json", "r", encoding="utf-8") as f:
    themen_annot = json.load(f)

########################################################

########################################################

min_weight = st.slider("Minimum topic weight to include", 0.0, 1.0, 0.66, 0.05)
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
st.write(len(selected_speeches))

# zufällige Reden aus deinen gefilterten
#subset_size = min(20, len(selected_speeches))
#random_subset = random.sample(selected_speeches, subset_size)
selected_top_title = selected_speeches[20]['discussion_title']

selected_speeches = [
    rede for rede in alleReden
    if rede['discussion_title'] == selected_top_title
]
st.write(len(selected_speeches))
#subset = random.sample(submissions, sample_size)

# daraus eine auswählen
speech = st.selectbox(
    "Wähle eine Rede aus einer Zufallsauswahl",
    options=selected_speeches,
    format_func=lambda r: f"{r['name']} ({r['party']})"
)

# Text anzeigen
st.subheader("Rede")
st.write(speech["text"])

#############################################

#############################################

base_url = 'http://thages.philosophie.kit.edu:8080/v1'
thages_key = os.environ['THAGES_API_KEY']

llm = ChatOpenAI(
    model = "meta-llama/Llama-3.1-8B-Instruct",
    base_url=base_url,
    openai_api_key=thages_key,
    max_tokens=2048,
    temperature=0.1,
    top_p=0.9
)

def prompt_associations(rede: str) -> str:
    SCHEMA = {
        "language": "de",
        "associations": [
            {
                "source_concept": "<string>",
                "target_concept": "<string>",
                "source_valence":"<float in [-1.0, 1.0]>",
                "target_valence":"<float in [-1.0, 1.0]>",
                "source_target_logical_coherence": "consistent|inconsistent|neutral",
                "association_type": "claim|data|warrant|backing|qualifier|rebuttal|",
                "association_valence":"<float in [-1.0, 1.0]>",
                "epistemic_frame": "belief|knowledge|uncertainty|inquiry",
                "explicitness_level": "explicit|implicit|fragmentary",
                "evaluation_terms": ["<Wertungen/Adjektive>"],
                "certainty_score": "<float in [0.0, 1.0]>",
                "evidence": ["<exakte Zitatphrase>", "..."],
                "justification": "string"
            }
        ]
    }

    sys_msg = f"""Du bist Expert:in für Diskursanalyse und Argument-Mining und Teil einer Computational Social Science Pipeline für Datenanalyse."""

    N = 8
    user_msg = f"""
    Analysiere die untenstehende REDE. Ziel: Extrahiere die {N-2} - {N+2} wichtigsten Assoziationen und semantischen Verknüpfungen im Text.
    
    Gib AUSSCHLIESSLICH ein JSON-Objekt zurück, das diesem SCHEMA strikt entspricht:
    
    {SCHEMA}
    
    Regeln:
    - Verwende ausschließlich die REDE.
    - Wähle sinntragende Konzepte (keine Funktionswörter), ggf. Konzepte zusammenfassen (Singular, konsistente Benennung).
    - Likert und float Scores müssen Wertebereiche einhalten (certainty_score ∈ [0..1], valence ∈ [-1.0..1.0]).
    - Verwende wenn möglich nur exakte Zitate aus der REDE.
    - Sei konsistent, knapp, logisch.
    - Gib keine Erklärungen oder Hinweise außerhalb des SCHEMAs!
    - Nur das SCHEMA zur weiteren Analyse.
    
    ---
    
    REDE:
    \"\"\"{speech["text"]}\"\"\"
    
    """

    messages=[
        {
            "role": "system",
            "content": sys_msg
        },
        {
            "role": "user",
            "content": user_msg
        }
    ]
    return messages

#messages = prompt_associations(speech)
#response = llm.invoke(messages)
#st.write(response.content)
#raw_response = response.content
#result = parse_json_safely(raw_response)
#all_assocs = result.get("associations", [])

def get_coherence(a: dict) -> str:
    return a.get("source_target_logical_coherence") or "unknown"

if st.button("🚀 Annotiere alle Reden dieses TOP"):
    all_assocs = []
    for sx,speech in enumerate(selected_speeches):
        text = speech['text']
        tokens = tokenizer.encode(text)
        st.write("Token count:", len(tokens))

        if len(tokens) < 1129:
            messages = prompt_associations(speech)
            response = llm.invoke(messages)
            st.write(f"{sx}. speech processed...")
            raw_response = response.content
            result = parse_json_safely(raw_response)
            assocs = result.get("associations", [])
            all_assocs = all_assocs + assocs
        else:
            st.write(f"{sx}. speech too long...")

# ---- Controls (optional) ----
min_certainty = 0 # st.slider("Min. certainty to include", 0.0, 1.0, 0.0, 0.05)
min_strength  = 0 # st.slider("Min. association valence to include", 0.0, 1.0, 0.0, 0.05)

# ---- Build signed, directed graph ----
G = nx.DiGraph()

# helper: read either 'source_target_logical_coherence' or 'source_target_cognitive_coherence'


# accumulate node valences for coloring later
node_vals = {}  # concept -> [vals]
node_degree = {}  # concept -> degree count for sizing

for a in all_assocs:
    src = a.get("source_concept")
    tgt = a.get("target_concept")
    if not src or not tgt:
        continue

    coh = get_coherence(a).lower()
    certainty = float(a.get("certainty_score", 0) or 0)
    strength = float(a.get("association_valence", 0) or 0)

    if certainty < min_certainty: #or strength < min_strength:
        continue

    # signed link
    if coh == "consistent":
        sign = +1
        color = "#1f9d55"  # green
    elif coh == "inconsistent":
        sign = -1
        color = "#e3342f"  # red
    else:
        sign = 0
        color = "#6c757d"  # gray

    # edge width: scale by certainty * strength (keep it visible)
    width = 1 + 6 * (certainty * abs(strength))

    # add nodes (track valence)
    sv = float(a.get("source_valence", 0) or 0)
    tv = float(a.get("target_valence", 0) or 0)
    node_vals.setdefault(src, []).append(sv)
    node_vals.setdefault(tgt, []).append(tv)

    node_degree[src] = node_degree.get(src, 0) + 1
    node_degree[tgt] = node_degree.get(tgt, 0) + 1

    # tooltip
    evidence = " | ".join(a.get("evidence", [])[:2]) if a.get("evidence") else ""
    assoc_type = a.get("association_type", "")
    epistemic = a.get("epistemic_frame", "")
    title = (
        f"<b>{src}</b> → <b>{tgt}</b><br>"
        f"coherence: <b>{coh}</b> (sign={sign})<br>"
        f"type: {assoc_type}, epistemic: {epistemic}<br>"
        f"certainty: {certainty:.2f}, strength: {strength:.2f}<br>"
        f"evidence: {evidence}"
    )

    # store edge attrs
    G.add_edge(
        src, tgt,
        sign=sign,
        color=color,
        width=width,
        title=title,
        arrows="to"
    )

# ---- Node visuals: color by avg valence, size by degree ----
def val_to_color(v: float) -> str:
    """
    Map [-1..1] valence to color (red -> gray -> green)
    """
    v = max(-1.0, min(1.0, v))
    if v >= 0:
        # gray -> green
        g = int(128 + v * (255-128))
        r = int(128 - v * 64)
        b = int(128 - v * 64)
    else:
        # red -> gray
        v = abs(v)
        r = int(128 + v * (255-128))
        g = int(128 - v * 64)
        b = int(128 - v * 64)
    return f"rgb({r},{g},{b})"

avg_val = {n: (sum(vs)/len(vs) if vs else 0.0) for n, vs in node_vals.items()}
max_deg = max(node_degree.values()) if node_degree else 1

# ---- Build PyVis network ----
net = Network(height="680px", width="100%", bgcolor="#ffffff", directed=True, notebook=False)
net.barnes_hut(gravity=-20000, central_gravity=0.2, spring_length=160, spring_strength=0.03, damping=0.8)

for n in G.nodes():
    v = avg_val.get(n, 0.0)
    col = val_to_color(v)
    deg = node_degree.get(n, 1)
    size = 10 + 20 * (deg / max_deg)  # 10..30
    net.add_node(
        n,
        label=n,
        color=col,
        value=deg,
        title=f"{n}<br>avg valence: {v:.2f}<br>degree: {deg}",
        size=size
    )

for u, v, d in G.edges(data=True):
    net.add_edge(u, v, color=d.get("color", "#999"), width=d.get("width", 1.0), title=d.get("title",""), arrows="to")

# small legend
legend_html = """
<div style="font-family:system-ui,Segoe UI,Arial; font-size:13px;">
  <b>Legend</b>:
  <span style="color:#1f9d55;">&nbsp;●&nbsp;consistent (positive)</span>&nbsp;&nbsp;
  <span style="color:#e3342f;">&nbsp;●&nbsp;inconsistent (negative)</span>&nbsp;&nbsp;
  <span style="color:#6c757d;">&nbsp;●&nbsp;unknown/neutral</span><br>
  Node color = avg valence (red→gray→green), size = degree
</div>
"""

# ---- Render in Streamlit ----

net_html = net.generate_html()
html(legend_html + net_html, height=720, scrolling=True)













# - Wähle nur handlungs-/positionsfähige Konzepte (z. B. Maßnahmen, Forderungen, normative Claims).
# - Reine Themen/Entitäten sind zu präzisieren (z. B. "Corona" → "Corona-Schutzmaßnahmen",
#   "Wirtschaft" → "Wirtschaftsentlastung").

#
# # 1) Texte der gefilterten Reden
# texts = [r["text"] for r in selected_speeches]
#
# # 2) TF-IDF auf Deutsch, nur sinnvolle N-Gramme
#
# stop_list = list(DE_STOPWORDS)
# stop_list.extend(['liebe','kolleginnen','kollegen','herren','damen','herr','frau'])
#
# vectorizer = TfidfVectorizer(
#     stop_words=stop_list,
#     lowercase=True,
#     ngram_range=(1, 3),   # 1- bis 3-Wort-Phrasen
#     min_df=1,             # erscheint in mind. 2 Reden der Auswahl
#     max_df=0.8,           # zu generische Terme raus
#     max_features=5000
# )
# X = vectorizer.fit_transform(texts)
#
# # 3) Globale Wichtigkeit je Term (Summe über alle Reden)
# scores = np.asarray(X.sum(axis=0)).ravel()
# terms  = vectorizer.get_feature_names_out()
#
# # 4) Top-K Terme nehmen (ggf. simpel filtern)
# order = scores.argsort()[::-1]
# top_k = 30
# keyterms = [t for t in terms[order] if len(t) >= 3][:top_k]
#
# # 5) Für den Prompt (JSON-Array)
# CONCEPT_LIST_JSON_ARRAY = json.dumps(keyterms, ensure_ascii=False)
#
# # Optional anzeigen / editierbar machen:
# st.write(keyterms)
# # selected_keyterms = st.multiselect("Kernkonzepte prüfen/anpassen", options=keyterms, default=keyterms)
# # CONCEPT_LIST_JSON_ARRAY = json.dumps(selected_keyterms, ensure_ascii=False)