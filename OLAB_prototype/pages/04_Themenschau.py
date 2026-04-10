
import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
from collections import defaultdict
from collections import Counter
import pandas as pd
from sklearn.preprocessing import StandardScaler
from matplotlib.colors import ListedColormap
import networkx as nx
import random
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.decomposition import PCA
import seaborn as sns
from pyvis.network import Network
import streamlit.components.v1 as components
from networkx.algorithms.community import greedy_modularity_communities

def repel_positions(pos, min_dist=0.05, iterations=50, step=0.01):
    """
    Push nodes apart if they are closer than min_dist.
    pos: dict {node: (x, y)}
    """
    nodes = list(pos.keys())
    P = np.array([pos[n] for n in nodes], dtype=float)

    for _ in range(iterations):
        for i in range(len(P)):
            for j in range(i + 1, len(P)):
                diff = P[i] - P[j]
                dist = np.linalg.norm(diff)
                if dist < min_dist:  # too close -> repel
                    if dist == 0:
                        diff = np.random.rand(2) - 0.5
                        dist = np.linalg.norm(diff)
                    move = step * (min_dist - dist) * diff / dist
                    P[i] += move
                    P[j] -= move
    return {n: tuple(P[i]) for i, n in enumerate(nodes)}





#####################################################################################



def signed_best_response_coloring(
        G: nx.Graph,
        init_colors: dict | None = None,
        weight_attr: str = "weight",
        self_weight: float = 1.0,
        max_iters: int = 100,
        seed: int | None = 42,
):
    rng = random.Random(seed)
    nodes = list(G.nodes())

    # initialize colors
    if init_colors is not None:
        color = init_colors.copy()
    else:
        color = {n: i for i, n in enumerate(nodes)}  # unique color per node

    for it in range(1, max_iters + 1):
        changed = False
        # for each node in random order
        for u in rng.sample(nodes, len(nodes)):
            counts = Counter()
            counts[color[u]] += self_weight  # self-vote

            for v in G.neighbors(u):
                w = float(G[u][v].get(weight_attr, 1.0))
                if w >= 0:
                    counts[color[v]] += 1 #* w
                else:
                    counts[color[v]] -= 1 #* abs(w)

                # find max count
                max_count = max(counts.values())
                candidates = [c for c, v in counts.items() if v == max_count]

                # tie-break: prefer current color if possible, else random choice
                # if color[u] in candidates:
                #     best_color = color[u]
                # else:
                best_color = rng.choice(candidates)

            if best_color != color[u]:
                color[u] = best_color
                changed = True

        if not changed:
            return color, it, True  # converged

    return color, max_iters, False  # hit iteration cap



#####################################################################################

alleReden = st.session_state.alleReden
themen_annot = st.session_state.themen_annot
legislatur = st.session_state.legislatur

st.title("Thematischer Überblick")

#st.markdown("Visualizing co-occurrence of debate topics across sessions.")


# Step 1: Group speeches by TOP
top_to_speech_ids = defaultdict(list)
speech_id_to_top = {}

for speech in alleReden:
    top = speech.get('discussion_title', '')
    speech_id = speech['id']
    speech_id_to_top[speech_id] = top
    top_to_speech_ids[top].append(speech_id)

# Step 2: Aggregate themes by TOP
top_to_topic = defaultdict(lambda: defaultdict(float))

for speech_id, theme_json in themen_annot.items():
    themes = theme_json
    top = speech_id_to_top.get(speech_id)
    if not top:
        continue
    for theme, score in themes.items():
        top_to_topic[top][theme] += score

df = pd.DataFrame(top_to_topic).T.fillna(0)
top_to_topic_scores = df.values  # This is your NumPy array

#st.write(top_to_topic_scores.shape)

# Normalize TOPs (X)
scaler_top = StandardScaler()
X_top = scaler_top.fit_transform(df.T.values)
# 1. Compute cosine similarity between TOPs
similarity_matrix = cosine_similarity(scaler_top.transform(df.T.values))

# 2. Create graph
G = nx.Graph()
topic_names = df.columns.tolist()

# Add nodes
for topic in topic_names:
    G.add_node(topic)

# Dynamic thresholding
sim_vals = similarity_matrix[np.triu_indices_from(similarity_matrix, k=1)]
abs_vals = np.abs(sim_vals)
mean_sim = abs_vals.mean()
std_sim  = abs_vals.std()
x = 0.0
threshold = mean_sim + x * std_sim

threshold = st.sidebar.slider(
    "Edge weight threshold:",
    min_value=0.0,
    max_value=float(abs_vals.max()),
    value=mean_sim,
    step=0.01,
)

for i in range(len(topic_names)):
    for j in range(i + 1, len(topic_names)):
        sim = similarity_matrix[i, j]
        if abs(sim) > threshold:
            G.add_edge(topic_names[i], topic_names[j], weight=sim)

# Step 3: PCA layout
# pca = PCA(n_components=2)
#
# coords = PCA(n_components=2).fit_transform(similarity_matrix)
# pos = {name: tuple(coord) for name, coord in zip(topic_names, coords)}
#
# # Apply repulsion to avoid overlaps
# pos = repel_positions(pos, min_dist=0.25, iterations=100, step=0.025)

# PCA with 3 components
pca = PCA(n_components=3)
coords3d = pca.fit_transform(similarity_matrix)
coords = coords3d[:, [0, 1]]

# Let user choose which PCs to plot
pc_options = ["PC1 vs PC2", "PC1 vs PC3", "PC2 vs PC3"]

# Keep track of last selection
if "last_pc_choice" not in st.session_state:
    st.session_state.last_pc_choice = pc_options[0]  # default
if "pos" not in st.session_state:
    # initialize with default coords
    st.session_state.pos = {name: tuple(coord) for name, coord in zip(topic_names, coords)}

# Sidebar selection
choice = st.sidebar.selectbox("Choose PCA mapping:", pc_options, index=pc_options.index(st.session_state.last_pc_choice))

# Only recompute if selection changed
if choice != st.session_state.last_pc_choice:
    if choice == "PC1 vs PC2":
        coords = coords3d[:, [0, 1]]
    elif choice == "PC1 vs PC3":
        coords = coords3d[:, [0, 2]]
    elif choice == "PC2 vs PC3":
        coords = coords3d[:, [1, 2]]
    st.session_state.pos = {name: tuple(coord) for name, coord in zip(topic_names, coords)}
    st.session_state.last_pc_choice = choice

# Build position dict
if "pos" not in st.session_state:
    st.session_state.pos = {name: tuple(coord) for name, coord in zip(topic_names, coords)}

# Apply repulsion if wanted
#pos = repel_positions(pos, min_dist=0.25, iterations=80, step=0.04)

# Button to trigger repel
if st.sidebar.button("Repel nodes"):
    st.session_state.pos = repel_positions(st.session_state.pos, min_dist=0.33, iterations=80, step=0.01)


# communities = list(greedy_modularity_communities(G))
# color_map = {node: i for i, comm in enumerate(communities) for node in comm}
# colors = [color_map[n] for n in G.nodes()]


if "colors_dict" not in st.session_state:
    st.session_state.colors_dict, n_iter, ok = signed_best_response_coloring(G, weight_attr="weight", self_weight=1.0, max_iters=0)

# --- Button to run best response coloring ---
if st.sidebar.button("Apply Clustering"):
    st.session_state.colors_dict, n_iter, ok = signed_best_response_coloring(G,init_colors=st.session_state.colors_dict , weight_attr="weight", self_weight=-0.01, max_iters=10)

if st.sidebar.button("Undo Layout"):
    st.session_state.pos = {name: tuple(coord) for name, coord in zip(topic_names, coords)}
    st.session_state.colors_dict, n_iter, ok = signed_best_response_coloring(G, weight_attr="weight", self_weight=1.0, max_iters=0)

palette = sns.color_palette("hls", n_colors=len(set(st.session_state.colors_dict.values())))
color_map = {c: palette[i] for i, c in enumerate(sorted(set(st.session_state.colors_dict.values())))}
node_colors = [color_map[st.session_state.colors_dict[n]] for n in G.nodes()]

# # qualitative palette for 44 topics
# tab20 = plt.get_cmap('tab20').colors
# tab20b = plt.get_cmap('tab20b').colors
# tab20c = plt.get_cmap('tab20c').colors
# palette = (list(tab20) + list(tab20b) + list(tab20c))[:len(node_colors)]





# Node size = number of TOPs where topic appears (non-zero entries in column)
node_size = [df[col].astype(bool).sum() * 5 for col in df.columns]

dominant_topic = df.idxmax(axis=1)  # pro TOP das wichtigste Thema
first_counts = dominant_topic.value_counts().reindex(df.columns, fill_value=0)
node_size_first = [first_counts[col] * 50 for col in df.columns]

option = st.sidebar.radio(
    "Knotengröße basierend auf:",
    ["Kommt als Thema vor", "Dominantes Thema"]
)

if option == "Kommt als Thema vor":
    node_size = node_size
else:
    node_size = node_size_first

# Step 4: Plot
fig = plt.figure(figsize=(12, 10))

nx.draw_networkx_nodes(
    G, st.session_state.pos,
    node_color="white", node_size=node_size,
    alpha=1.0
)

nx.draw_networkx_nodes(
    G, st.session_state.pos,
    node_color=node_colors, node_size=node_size,
    cmap=ListedColormap(palette),
    #cmap='tab10',
    alpha=0.5,
    edgecolors="white",   # border color
    linewidths=2.8        # border thickness
)
# Separate positive and negative edges
pos_edges = [(u, v) for u, v, d in G.edges(data=True) if d['weight'] > 0]
neg_edges = [(u, v) for u, v, d in G.edges(data=True) if d['weight'] < 0]
#widths_pos = [d['weight'] * 20 for (u, v, d) in G.edges(data=True) if d['weight'] > 0]
#widths_neg = [abs(d['weight']) * 20 for (u, v, d) in G.edges(data=True) if d['weight'] < 0]

# sqrt scaling (gentle compression)
widths_pos = [np.sqrt(d['weight']) * 5 for (_, _, d) in G.edges(data=True) if d['weight'] > 0]
widths_neg = [np.sqrt(abs(d['weight'])) * 5 for (_, _, d) in G.edges(data=True) if d['weight'] < 0]


# Draw positive (blue)
nx.draw_networkx_edges(G, st.session_state.pos,
                       edgelist=pos_edges,
                       edge_color='dodgerblue',
                       alpha=0.2,
                       width=widths_pos
                       )
# Draw negative (red)
nx.draw_networkx_edges(G, st.session_state.pos,
                       edgelist=neg_edges,
                       edge_color='crimson',
                       alpha=0.1,
                       width=widths_neg
                       )#, style='dashed'# )


nx.draw_networkx_labels(G, st.session_state.pos, font_size=11)
#plt.title("Themen-Netzwerk (PCA-Based Layout)")
plt.axis('off')
plt.tight_layout()

st.pyplot(fig)
plt.close(fig)

# # Create PyVis network
# net = Network(height="700px", width="100%", bgcolor="#ffffff", font_color="black")
# net.force_atlas_2based()
#
# for node in G.nodes():
#     net.add_node(
#         node,
#         label=node,
#         size=10 + G.degree(node) * 2
#     )
#
# # Add edges with weights
# for u, v, d in G.edges(data=True):
#     net.add_edge(u, v, value=d['weight'])
#
# # Save and embed in Streamlit
# net.save_graph("pyvis_topic_network.html")
# components.html(open("pyvis_topic_network.html", "r", encoding="utf-8").read(), height=750)
#


# sim_vals = similarity_matrix[np.triu_indices_from(similarity_matrix, k=1)]
# # Plot histogram
# fig2 = plt.figure(figsize=(8, 4))
# plt.hist(sim_vals, bins=40, color='dodgerblue', alpha=0.7)
# plt.axvline(sim_vals.mean(), color='red', linestyle='--', label='Mean')
# plt.title("Distribution of Pairwise TOP Similarities")
# plt.xlabel("Cosine Similarity")
# plt.ylabel("Frequency")
# plt.grid(True)
# plt.legend()
# plt.tight_layout()
# st.pyplot(fig2)
# plt.close(fig2)




# st.title("Zeitlicher Verlauf der Themen")
#
#
# # 1. df mit Datum anreichern
# df_dates = df.copy()
# df_dates["TOP"] = df.index
# id_to_date = {r["discussion_title"]: pd.to_datetime(r["date"]) for r in alleReden}
# df_dates["date"] = df_dates["TOP"].map(id_to_date)
#
# # 2. Nur Themen-Spalten (numerisch)
# numeric_topics = df.columns
# df_time = df_dates.set_index("date")[numeric_topics].resample("3M").sum()
#
# ## --- Thema auswählen ---
# #topic = st.selectbox("Wähle ein Thema:", df.columns)
#
# # --- Gestapeltes Diagramm ---
# fig, ax = plt.subplots(figsize=(12, 6))
# df_time.plot.area(ax=ax, alpha=0.85)
#
# ax.set_title("Themenverlauf im Bundestag (monatlich aggregiert)")
# ax.set_ylabel("Summierte Themenintensität")
# ax.set_xlabel("Datum")
# plt.xticks(rotation=45)
#
# st.pyplot(fig)

st.subheader("Hier gibt es die Zahlen:")

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