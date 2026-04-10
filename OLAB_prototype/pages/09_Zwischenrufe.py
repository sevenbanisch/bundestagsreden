import json
import streamlit as st
import re
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from collections import Counter
import pandas as pd
from pyvis.network import Network
from streamlit.components.v1 import html
from matplotlib.ticker import MaxNLocator

#Falls eine andere Regierungperiode analysiert werden soll, hier anderen Datensatz einfügen, des weiteren muss weiter unten die Definition von Regierung und Oppossition angepasst werden
@st.cache_data
def load_data_with_comments(legislatur):
    with open(f'../data/speeches_{legislatur}_with_comments.jsonl', 'r', encoding = 'utf8') as fp:
        data = list(fp)
    speeches = []
    for line in data:
        speeches.append(json.loads(line))
    speeches.sort(key = lambda x:x['date'])
    return speeches

st.title("Analyse der Zwischenrufe")


alleReden_wc = load_data_with_comments(20)
#st.write(len(alleReden_wc))

######################################################
# Beispiel
######################################################
st.subheader("Zunächst ein Beispiel:")
rede = alleReden_wc[20000]
st.write(f"**{rede["name"]}** ({rede["party"]}):")
st.write(rede["text"])

rede = alleReden_wc[20001]
st.write(f"**{rede["name"]}** ({rede["party"]}):")
st.write(rede["text"])

rede = alleReden_wc[20002]
st.write(f"**{rede["name"]}** ({rede["party"]}):")
st.write(rede["text"])

######################################################
# Global
######################################################

st.subheader("Globaler Überblick: Häufigkeit der Zwischenrufe über alle Reden")

if st.button("Berechne die globale Statistik!",type="primary"):
    nodes_all = {}
    for redner in alleReden_wc:
        name = redner["name"]
        # If the speaker is already in the dictionary, increment the count
        if name in nodes_all:
            nodes_all[name]["speech_count"] += 1
            # Otherwise, add the speaker to the dictionary with speech count 1
        else:
            nodes_all[name] = {
                "name": redner["name"],
                "party": redner["party"],
                "speech_count": 1,
                "Regierung/Opposition": "unk" if redner["party"] == "unknown" else "Regierung" if redner["party"] == "FDP" or redner["party"] == "BÜNDNIS 90/DIE GRÜNEN" or redner["party"] == "SPD" else "Opposition"#Wenn eine andere Regierungsperiode analysiert werden soll, muss hier die Definition von Regierung und Opposition angepasst werden
            }

    nodelist_all = list(nodes_all.values())
    uniquenames_all = [d["name"] for d in nodelist_all]

    n = len(uniquenames_all)
    matrix = np.zeros((n, n), dtype=int)
    # Create a mapping from name to index
    name_to_index = {name: i for i, name in enumerate(uniquenames_all)}
    # This is how comment are coded
    Kommentar = r"\{\(.*?\)\}"

    # Populate the matrix
    for speech in alleReden_wc:
        speaker_name = speech["name"]
        speaker_index = name_to_index[speaker_name]
        Kommentarcontent = re.findall(Kommentar, speech["text"])
        # Join all text found inside curly brackets into a single string for easier name search
        inside_text = " ".join(Kommentarcontent)
        for name in uniquenames_all:
            if name != speaker_name:  # Avoid counting the speaker's own name
                if name in inside_text:
                    target_index = name_to_index[name]
                    matrix[speaker_index][target_index] += 1
                    # Break the loop or conditionally skip if already counted in this speech

    TransponierteMatrix = matrix.T
    TMatrix = TransponierteMatrix.tolist()

    # Calculate the weighted out-degree for each speaker (sum of rows in the matrix)
    wout_degrees = np.sum(TMatrix, axis=1)
    degree_distribution = Counter(wout_degrees)
    sorted_degrees = sorted(degree_distribution.items())
    # Unpack the degrees and counts for plotting
    wout_degree_values, counts = zip(*sorted_degrees)

    # Create the dot plot
    fig=plt.figure(figsize=(16, 6))
    plt.scatter(wout_degree_values, counts, color="blue")
    #plt.xscale('log')  # Set x-axis to logarithmic scale
    plt.title('Anzahl der Zwischenrufe pro Redner*in')
    plt.xlabel('Anzahl Zwischenrufe')
    plt.ylabel('Anzahl Redner*innen')
    plt.grid(True)
    st.pyplot(fig)
    plt.close(fig)

    with st.expander("Bitte zeige die 10 Aktivsten!"):
        # Create a table with speakers and their respective out-degrees
        speaker_out_degrees = pd.DataFrame({
            'Speaker': uniquenames_all,
            'Weighted Out-Degree': wout_degrees
        })
        speaker_out_degrees_sorted = speaker_out_degrees.sort_values(by='Weighted Out-Degree', ascending=False)
        top_10_values = speaker_out_degrees_sorted.nlargest(10, "Weighted Out-Degree")
        st.write(top_10_values)



######################################################
# Themenspezifisch
######################################################
st.header("Themenspezifische Interventionsnetzwerke")
st.subheader("Wähle einen Themenbereich:")

themen_annot = st.session_state.themen_annot
# --- Schritt 1: Thema auswählen ---
erlaubte_themen = sorted({t for v in themen_annot.values() for t in v.keys()})
thema = st.selectbox("Wähle ein Thema:", erlaubte_themen, index=4)

# --- Score-Schwelle auswählen ---
score_threshold = st.slider(
    "Mindest-Score für das Thema:",
    min_value=0.0, max_value=1.0, value=0.5, step=0.05
)

# --- Schritt 3: Relevante Reden filtern ---
selected_speeches = []
#if st.button("Suche starten"):
# IDs der Reden mit Thema >= Schwellwert
relevant_ids = [
    rid for rid, topics in themen_annot.items()
    if thema in topics and topics[thema] >= score_threshold
]

# Reden extrahieren
selected_speeches = [r for r in alleReden_wc if r["id"] in relevant_ids]

st.write(f"Gefundene Reden: {len(selected_speeches)}")

#list of dictionaries erstellen mit rednern, parteien,...

#selected_speeches = alleReden_wc[20000:20003]
#st.write(len(selected_speeches))

nodes = {}
for redner in selected_speeches:
    name = redner["name"]
    # If the speaker is already in the dictionary, increment the count
    if name in nodes:
        nodes[name]["speech_count"] += 1
        # Otherwise, add the speaker to the dictionary with speech count 1
    else:
        nodes[name] = {
            "name": redner["name"],
            "party": redner["party"],
            "speech_count": 1,
            "Regierung/Opposition": "unk" if redner["party"] == "unknown" else "Regierung" if redner["party"] == "FDP" or redner["party"] == "BÜNDNIS 90/DIE GRÜNEN" or redner["party"] == "SPD" else "Opposition"#Wenn eine andere Regierungsperiode analysiert werden soll, muss hier die Definition von Regierung und Opposition angepasst werden
        }

# Convert the unique speakers back to a list of dictionaries
nodelist = list(nodes.values())
#st.write(len(nodelist))
#Liste für Matrix erstellen
uniquenames = [d["name"] for d in nodelist]
#st.write(len(uniquenames))

# Erstellen der Matrix
# Namen werden innerhalb von Reden nur einmal gezählt->mehrere Zwischenrufe von der selben Person in derselben Rede werden nicht berücksichtigt

n = len(uniquenames)
matrix = np.zeros((n, n), dtype=int)
# Create a mapping from name to index
name_to_index = {name: i for i, name in enumerate(uniquenames)}
# This is how comment are coded
Kommentar = r"\{\(.*?\)\}"

# Populate the matrix
for speech in selected_speeches:
    speaker_name = speech["name"]
    speaker_index = name_to_index[speaker_name]

    Kommentarcontent = re.findall(Kommentar, speech["text"])

    # Join all text found inside curly brackets into a single string for easier name search
    inside_text = " ".join(Kommentarcontent)

    for name in uniquenames:
        if name != speaker_name:  # Avoid counting the speaker's own name
            if name in inside_text:
                target_index = name_to_index[name]
                matrix[speaker_index][target_index] += 1
                # Break the loop or conditionally skip if already counted in this speech

#Matrix transponieren für intuitivere Interpretierbarkeit
#Nach transponieren bedeutet ein "Pfeil" von A zu B, dass A bei B einen Zwischenruf getätigt hat
TransponierteMatrix = matrix.T
TMatrix = TransponierteMatrix.tolist()
#st.write(TMatrix[0])


#Verteilung der gewichteten Ausgangsgrade
#Gewichteter Ausgangsgrad einer Person: Anzahl an Reden bei der die Person mindestens einen Zwischenruf getätigt hat
#Ausgangsgrad einer Person: Anzahl an Rednern bei denen die Person mindestens einen Zwischenruf getätigt hat

# Calculate the weighted out-degree for each speaker (sum of rows in the matrix)
wout_degrees = np.sum(TMatrix, axis=1)
# Count the occurrences of each out-degree
degree_distribution = Counter(wout_degrees)
# Sort the distribution by out-degree for the plot
sorted_degrees = sorted(degree_distribution.items())
# Unpack the degrees and counts for plotting
wout_degree_values, counts = zip(*sorted_degrees)

if st.button("Berechne die Häufigkeitsverteilung"):
    # Create the dot plot
    fig=plt.figure(figsize=(16, 6))
    plt.scatter(wout_degree_values, counts, color="blue")
    #plt.xscale('log')  # Set x-axis to logarithmic scale
    plt.title('Anzahl der Zwischenrufe pro Redner*in')
    plt.xlabel('Anzahl Zwischenrufe')
    plt.ylabel('Anzahl Redner*innen')
    plt.grid(True)
    st.pyplot(fig)
    plt.close(fig)

with st.expander("Hier sind die 10 Aktivsten!"):
    # Create a table with speakers and their respective out-degrees
    speaker_out_degrees = pd.DataFrame({
        'Speaker': uniquenames,
        'Weighted Out-Degree': wout_degrees
    })
    speaker_out_degrees_sorted = speaker_out_degrees.sort_values(by='Weighted Out-Degree', ascending=False)
    top_10_values = speaker_out_degrees_sorted.nlargest(10, "Weighted Out-Degree")
    st.write(top_10_values)



# --- Checkbox für LCC ---
st.sidebar.subheader("Netzwerkoptionen:")
# Eingabe von Anzahl der Samples
edge_threshold = st.sidebar.number_input(
    label="Filter Kantengewicht",
    min_value=1,
    max_value=5,
    value=1,  # Default-Wert
    step=1
)
num_edges = np.sum(matrix >= edge_threshold)
if num_edges > 1000:
    st.sidebar.info(f"Das Netzwerk hat {num_edges} Kanten.")
    st.sidebar.warning("Die Visualisierung wird dauern!")
else:
    st.sidebar.info(f"Das Netzwerk hat {num_edges} Kanten.")
st.sidebar.write("---")
show_lcc = st.sidebar.checkbox("Nur größte Zusammenhangskomponente (LCC) anzeigen", value=True)

if st.button("Zeig mir jetzt das Netzwerk!",type="primary"):
    G = nx.DiGraph()
    # Add nodes with attributes (name, age, affiliation)
    for speaker in nodelist:
        G.add_node(speaker["name"], **speaker)

    # Add edges based on the matrix
    for i, speaker in enumerate(nodelist):
        for j, target_speaker in enumerate(nodelist):
            if TMatrix[i][j] >= edge_threshold:  # Only add an edge if there's a mention
                G.add_edge(speaker["name"], target_speaker["name"], weight=TMatrix[i][j], arrows="to")

    # Create PyVis network
    st.info(f"Anzahl Knoten/Kanten gesamt: {len(G)}/{G.number_of_edges()}")
    # --- ggf. LCC extrahieren ---
    if show_lcc and len(G) > 0:
        largest_cc = max(nx.connected_components(G.to_undirected()), key=len)
        G = G.subgraph(largest_cc).copy()
        st.info(f"Anzahl Knoten/Kanten in LCC: {len(G)}/{G.number_of_edges()}")

    net = Network(height="700px", width="100%", bgcolor="#ffffff", font_color="black")
    #net.force_atlas_2based()
    net.barnes_hut(gravity=-20000, central_gravity=0.2,
                   spring_length=160, spring_strength=0.03, damping=0.8)

    # options = """
    #             {
    #               "nodes": {
    #                 "font": {
    #                   "size": 14,
    #                   "face": "Arial",
    #                   "color": "black"
    #                 }
    #               }
    #             }
    #             """
    # net.set_options(options)

    party_colors = {
        "SPD": "#e30613",  # red
        "CDU/CSU": "#333333",  # black
        "BÜNDNIS 90/DIE GRÜNEN": "#64a12d",  # green
        "FDP": "#ffed00",  # yellow
        "AfD": "#009ee0",  # blue
        "DIE LINKE": "#b4006e",  # magenta
        "unknown": "gray",
    }

    for node, data in G.nodes(data=True):
        party = data.get("party", "unknown")
        reg_opp = data.get("Regierung/Opposition", "unk")
        shape = "dot" if reg_opp == "Regierung" else "square"
        color = party_colors.get(party, "gray")
        net.add_node(node,
                     label=node,
                     title=f'{node} ({party})\nAnzahl Reden: {data["speech_count"]}',
                     #font={"size": 30},
                     color=color,
                     #size=10 + G.degree(node) * 1,
                     size=20 + G.out_degree(node, weight="weight")/3,
                     #size=10 + data["speech_count"] * 1,
                     shape=shape)


    # Add edges with weights
    for u, v, d in G.edges(data=True):
        net.add_edge(u, v, value=d['weight'], arrows="to")

    net_html = net.generate_html()
    html(net_html, height=800, scrolling=True)


# # Save and embed in Streamlit
#net.save_graph("pyvis_topic_network.html")
#components.html(open("pyvis_topic_network.html", "r", encoding="utf-8").read(), height=750)





# Export the graph to GEXF format
#nx.write_gexf(G, "Zwischenrufe.gexf")

#print("GEXF file created")