import streamlit as st
from streamlit.components.v1 import html
import jsonlines
import json
import pandas as pd
from collections import Counter, defaultdict
from langchain_openai import ChatOpenAI
import networkx as nx
from pyvis.network import Network
from openai import OpenAI

from transformers import AutoTokenizer
tokenizer = AutoTokenizer.from_pretrained("bert-base-german-cased")

import os

#base_url = 'http://thages.philosophie.kit.edu:8080/v1'
#thages_key = os.environ['THAGES_API_KEY']

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

#####################################################################################

#####################################################################################

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

    sys_msg = "Du bist Expert*in für Diskursanalyse und Argument-Mining und Teil einer Computational Social Science Pipeline für Datenanalyse."

    N = 8
    user_msg = f"""
    Analysiere die untenstehende REDE. 
    
    Ziele: 
    
    1. Identifiziere die {N-2} - {N+2} wichtigsten Konzepte in der Rede. 
    2. Extrahiere die wichtigsten Assoziationen zwischen diesen Konzepten.
    3. Klassifiziere die Assoziationen nach Konsistenz (z.B. negativ: ablehnen/reduzieren, positiv: zustimmen/erhöhen)
    
    Gib AUSSCHLIESSLICH ein JSON-Objekt zurück, das diesem SCHEMA strikt entspricht:
    
    {SCHEMA}
    
     INSTRUCTIONS:
     
    - Verwende ausschließlich die REDE.
    - Wähle sinntragende Konzepte (keine Funktionswörter und Verben), wenn möglich Einzelworte.
    - Wähle nur EIN Source-Konzept und EIN Target-Konzept pro Assoziation (falls zwei Konzepte mit und verknüpft sind, behandele dies als zwei Assoziationen).
    - Likert und float Scores müssen Wertebereiche einhalten (certainty_score ∈ [0..1], valence ∈ [-1.0..1.0]).
    - Verwende wenn möglich nur exakte Zitate aus der REDE.
    - Sei konsistent, knapp, logisch.
    - Gib keine Erklärungen oder Hinweise außerhalb des SCHEMAs!
    - Nur das SCHEMA zur weiteren Analyse.
 
    -- -
    
    REDE:
    \"\"\"{rede["text"]}\"\"\"
    
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

def get_coherence(a: dict) -> str:
    return a.get("source_target_logical_coherence") or "unknown"

#####################################################################################

#####################################################################################

        # --- Daten laden aus Session ---
alleReden = st.session_state.alleReden
themen_annot = st.session_state.themen_annot
legislatur = st.session_state.legislatur

st.title("LLM-basierte Identifikation von Konzepten und Assoziationen")

# --- Schritt 1: Thema auswählen ---
st.subheader("Wähle zunächst einen Themenbereich:")
erlaubte_themen = sorted({t for v in themen_annot.values() for t in v.keys()})
thema = st.selectbox("Wähle ein Thema:", erlaubte_themen,index=5)

# --- Score-Schwelle auswählen ---
score_threshold = st.slider(
    "Mindest-Score für das Thema:",
    min_value=0.0, max_value=1.0, value=0.5, step=0.05
)

# --- Schritt 2: Keyword eingeben ---

st.subheader("Vielleicht willst Du die Suche noch etwas spezifizieren?")
keyword = st.text_input("Keyword-Suche innerhalb des Themas:")

# --- Schritt 3: Relevante Reden filtern ---
selected_speeches = []
if st.button("Suche starten",type="primary"):
    # IDs der Reden mit Thema >= Schwellwert
    relevant_ids = [
        rid for rid, topics in themen_annot.items()
        if thema in topics and topics[thema] >= score_threshold
    ]

    # Reden extrahieren
    selected_speeches = [r for r in alleReden if r["id"] in relevant_ids]


    # Wenn Keyword gesetzt: weiter filtern
    if keyword:
        keyword_lower = keyword.lower()
        selected_speeches = [r for r in selected_speeches if keyword_lower in r["text"].lower()]

    # DataFrame für Übersicht
    if selected_speeches:
        df_out = pd.DataFrame([
            {
                "Datum": r["date"],
                "Redner": r["name"],
                "Partei": r["party"],
                "Titel": r["discussion_title"],
                "Textauszug": r["text"][:200] + "..."
            }
            for r in selected_speeches
        ])
        st.write(f"Gefundene Reden: {len(df_out)}")
        st.dataframe(df_out, use_container_width=True)
        st.session_state.selected_speeches = selected_speeches
    else:
        st.warning("Keine passenden Reden gefunden.")


#####################################################################################

#####################################################################################

# --- Schritt 4: LLM Annotations

# Check, ob "selected_speeches" existiert
if "selected_speeches" in st.session_state:
    selected_speeches = st.session_state.selected_speeches
    #st.write("✅ Reden geladen:", selected_speeches)
else:
    st.warning("Bitte führe zunächst die Keyword-Suche durch.")



# llm = ChatOpenAI(
#     model = "meta-llama/Llama-3.1-8B-Instruct",
#     base_url=base_url,
#     openai_api_key=thages_key,
#     max_tokens=1600,
#     temperature=0.1,
#     top_p=0.9
# )

if "selected_speeches" in st.session_state and st.session_state.selected_speeches:
    # Dropdown mit Reden (Datum + Redner + Partei)
    options = {
        f"{r['date']} | {r['name']} ({r['party']}) | {r['discussion_title']}": r
        for r in selected_speeches
    }

    st.subheader(f"Nun kannst Du eine von {len(selected_speeches)} Reden wählen:")
    choice = st.selectbox("Wähle eine Rede für die Annotation:", list(options.keys()))
    chosen_speech = options[choice]

    st.write("**Vorschau:**")
    st.text_area("Rede", chosen_speech["text"][:1000] + "...", height=200)

    messages = prompt_associations(chosen_speech)
    with st.expander("System Message Anzeigen!"):
        st.write(messages[0]['content'])
    with st.expander("User Message Anzeigen!"):
        st.write(messages[1]['content'])

    if st.button("LLM Annotation starten"):
        # 👉 hier rufst du dein LLM auf
        messages = prompt_associations(chosen_speech)
        #response = llm.invoke(messages)
        response = call_llm(messages,temperature=0.0)
        st.write(response)
        raw_response = response
        result = parse_json_safely(raw_response)
        st.session_state.annotation_result = result
        st.success("Annotation abgeschlossen ✅")
        with st.expander("Zeige den vollständigen LLM Output!"):
            st.json(result["associations"])

#else:
#    st.warning("Bitte zuerst Reden filtern, bevor du weiter machst.")
#####################################################################################






#####################################################################################

# --- Schritt 5: Netzwerk
# --- C: Netzwerk ---
#st.markdown("### 5️⃣ Netzwerk der Konzepte")

if st.button("Draw as Network",type="primary"):
    if "annotation_result" not in st.session_state:
        st.warning("⚠️ Bitte zuerst eine Rede annotieren.")
    else:
        result = st.session_state.annotation_result
        with st.expander("Zeige den vollständigen LLM Output!"):
            st.json(result["associations"])
        all_assocs = result.get("associations", [])

        if not all_assocs:
            st.warning("Keine Assoziationen in der Annotation gefunden.")
        else:
            # ---- Controls ----
            min_certainty = 0.0
            min_strength  = 0.0

            # ---- Graph aufbauen ----
            G = nx.DiGraph()
            node_vals, node_degree = {}, {}

            for a in all_assocs:
                src = a.get("source_concept")
                tgt = a.get("target_concept")
                if not src or not tgt:
                    continue

                coh = get_coherence(a).lower()
                certainty = float(a.get("certainty_score", 0) or 0)
                strength  = float(a.get("association_valence", 0) or 0)

                if certainty < min_certainty:
                    continue

                # signierte Kante
                if coh == "consistent":
                    color = "#1f9d55"  # grün
                elif coh == "inconsistent":
                    color = "#e3342f"  # rot
                else:
                    color = "#6c757d"  # grau

                width = 1 + 6 * (certainty * abs(strength))

                # Node-Infos
                sv = float(a.get("source_valence", 0) or 0)
                tv = float(a.get("target_valence", 0) or 0)
                node_vals.setdefault(src, []).append(sv)
                node_vals.setdefault(tgt, []).append(tv)

                node_degree[src] = node_degree.get(src, 0) + 1
                node_degree[tgt] = node_degree.get(tgt, 0) + 1

                # Edge hinzufügen
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

            # ---- Node visuals ----
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

            avg_val = {n: (sum(vs) / len(vs)) for n, vs in node_vals.items()}
            max_deg = max(node_degree.values()) if node_degree else 1

            net = Network(height="680px", width="100%", bgcolor="#ffffff", directed=True)
            net.barnes_hut(gravity=-20000, central_gravity=0.2,
                           spring_length=160, spring_strength=0.03, damping=0.8)

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
                net.add_node(n, label=n, color=col, value=deg,
                             title=f"{n}\navg valence: {v:.2f}\ndegree: {deg}",
                             size=size)

            for u, v, d in G.edges(data=True):
                net.add_edge(u, v, color=d.get("color", "#999"),
                             width=d.get("width", 1.0),
                             title=d.get("title", ""), arrows="to")

            # Legende + Render
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
            html(legend_html + net_html, height=720, scrolling=True)

# SCHEMA = {
#     "language": "de",
#     "associations": [
#         {
#             "source_concept": "<string>",
#             "target_concept": "<string>",
#             "source_valence":"<float in [-1.0, 1.0]>",
#             "target_valence":"<float in [-1.0, 1.0]>",
#             "source_target_logical_coherence": "consistent|inconsistent|neutral",
#             "association_type": "claim|data|warrant|backing|qualifier|rebuttal|",
#             "association_valence":"<float in [-1.0, 1.0]>",
#             "epistemic_frame": "belief|knowledge|uncertainty|inquiry",
#             "explicitness_level": "explicit|implicit|fragmentary",
#             "evaluation_terms": ["<Wertungen/Adjektive>"],
#             "certainty_score": "<float in [0.0, 1.0]>",
#             "evidence": ["<exakte Zitatphrase>", "..."],
#             "justification": "string"
#         }
#     ]
# }
# st.json(SCHEMA)