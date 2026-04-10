import streamlit as st
import os, json
import networkx as nx
from pyvis.network import Network
from streamlit.components.v1 import html

st.set_page_config(page_title="Gesamt-Konzeptnetzwerk", layout="wide")
st.title("Konzeptnetzwerke aus vorberechneten Annotationen")

# --- 1. Dateien finden ---
annotation_dir = "../annotations/concepts"
files = [f for f in os.listdir(annotation_dir) if f.startswith("concept_annotations_") and f.endswith(".json")]

if not files:
    st.error("⚠️ Keine vorab berechneten Annotationen gefunden.")
    st.stop()

# --- 2. Use Case auswählen ---
st.subheader("Use Cases")
choices = {f.replace("concept_annotations_", "").replace(".json", ""): f for f in files}
keyword = st.selectbox("Wähle einen Use Case (Keyword):", sorted(choices.keys()),index=1)

file_path = os.path.join(annotation_dir, choices[keyword])

# --- 3. Datei laden ---
with open(file_path, "r", encoding="utf-8") as f:
    concept_annotations = json.load(f)

st.success(f"Geladene Datei: {file_path} mit {len(concept_annotations)} Reden")

# --- 4. Gesamt-Netzwerk bauen ---
all_assocs = []
for speech_id, assocs in concept_annotations.items():
    all_assocs.extend(assocs)

st.info(f"Gefundene Assoziationen insgesamt: {len(all_assocs)}")

# --- Checkbox für LCC ---
show_lcc = st.sidebar.checkbox("Nur größte Zusammenhangskomponente (LCC) anzeigen", value=True)

with st.expander("Zeige die Konzepte!"):
    konzepte = list({assoc['source_concept'] for assoc in all_assocs} |
                    {assoc['target_concept'] for assoc in all_assocs})

    konzepte.sort()  # Optional: alphabetisch
    cols = st.columns(3)  # 3 Spalten, platzsparend

    for i, concept in enumerate(konzepte):
        cols[i % 3].markdown(f"- {concept}")


if st.button("Zeig mir jetzt das Netzwerk!",type="primary"):
    G = nx.DiGraph()
    node_vals, node_degree = {}, {}

    def get_coherence(a: dict) -> str:
        return a.get("source_target_logical_coherence") or "unknown"
    def safe_float(x, default=0.0):
        """Versuche, x in float zu wandeln – egal ob Zahl, String oder Liste."""
        try:
            if isinstance(x, list):
                if not x:  # leere Liste
                    return default
                return float(x[0])  # nimm erstes Element
            return float(x)
        except (TypeError, ValueError):
            return default

    for a in all_assocs:
        src, tgt = a.get("source_concept"), a.get("target_concept")
        if not src or not tgt:
            continue

        coh = get_coherence(a).lower()
        certainty = float(a.get("certainty_score", 0) or 0)
        strength = safe_float(a.get("association_valence"))

        if coh == "consistent":
            color = "#1f9d55"
        elif coh == "inconsistent":
            color = "#e3342f"
        else:
            color = "#6c757d"

        width = 1 + 6 * (certainty * abs(strength))

        # Nodes sammeln
        sv = safe_float(a.get("source_valence"))
        tv = safe_float(a.get("target_valence"))
        node_vals.setdefault(src, []).append(sv)
        node_vals.setdefault(tgt, []).append(tv)

        node_degree[src] = node_degree.get(src, 0) + 1
        node_degree[tgt] = node_degree.get(tgt, 0) + 1

        evidence = " | ".join(a.get("evidence", [])[:2]) if a.get("evidence") else ""
        assoc_type = a.get("association_type", "")
        epistemic = a.get("epistemic_frame", "")

        title = (
            f"{src} → {tgt}\n"
            f"coherence: {coh}\n"
            f"type: {assoc_type}, epistemic: {epistemic}\n"
            f"certainty: {certainty:.2f}, strength: {strength:.2f}\n"
            f"evidence: {evidence}"
        )

        G.add_edge(src, tgt, color=color, width=width, title=title, arrows="to")

    # Node-Farben (Valenz)
    def val_to_color(v: float) -> str:
        v = max(-1.0, min(1.0, v))
        if v >= 0:
            g = int(128 + v * (255-128))
            r = int(128 - v * 64)
            b = int(128 - v * 64)
        else:
            v = abs(v)
            r = int(128 + v * (255-128))
            g = int(128 - v * 64)
            b = int(128 - v * 64)
        return f"rgb({r},{g},{b})"



    # ---- Nur größte Komponente nehmen ----
    st.info(f"Anzahl Knoten/Kanten gesamt: {len(G)}/{G.number_of_edges()}")
    # --- ggf. LCC extrahieren ---
    if show_lcc and len(G) > 0:
        largest_cc = max(nx.connected_components(G.to_undirected()), key=len)
        G = G.subgraph(largest_cc).copy()
        st.info(f"Anzahl Knoten/Kanten in LCC: {len(G)}/{G.number_of_edges()}")

    avg_val = {n: (sum(vs)/len(vs)) for n, vs in node_vals.items()}
    max_deg = max(node_degree.values()) if node_degree else 1

    net = Network(height="720px", width="100%", bgcolor="#ffffff", directed=True)
    net.barnes_hut(gravity=-25000, central_gravity=0.3, spring_length=160, spring_strength=0.03, damping=0.9)

    options = """
            {
              "nodes": {
                "font": {
                  "size": 24,
                  "face": "Arial",
                  "color": "black"
                }
              }
            }
            """
    net.set_options(options)

    for n in G.nodes():
        v = avg_val.get(n, 0.0)
        col = val_to_color(v)
        deg = node_degree.get(n, 1)
        size = 10 + 20 * (deg / max_deg)

        node_id = str(n) if n is not None else "UNKNOWN"
        #st.write(node_id)

        net.add_node(
            node_id,
            label=node_id,
            color=col,
            value=deg,
            title=f"{node_id}\navg valence: {v:.2f}\ndegree: {deg}",
            size=size
        )

    for u, v, d in G.edges(data=True):
        net.add_edge(str(u), str(v),
                     color=d.get("color", "#999"),
                     width=d.get("width", 1.0),
                     title=d.get("title", ""),
                     arrows="to")

    legend_html = """
    <div style="font-family:system-ui,Segoe UI,Arial; font-size:13px;">
      <b>Legende</b>:
      <span style="color:#1f9d55;">● consistent (positiv)</span>&nbsp;&nbsp;
      <span style="color:#e3342f;">● inconsistent (negativ)</span>&nbsp;&nbsp;
      <span style="color:#6c757d;">● neutral/unbekannt</span>\n
      Node-Farbe = Ø Valenz (rot→grau→grün), Größe = Grad
    </div>
    """
    net_html = net.generate_html()
    html(legend_html + net_html, height=800, scrolling=True)
