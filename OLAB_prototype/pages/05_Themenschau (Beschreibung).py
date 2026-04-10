import streamlit as st
import matplotlib.pyplot as plt

st.set_page_config(page_title="Netzwerkanalyse erklärt", layout="wide")

st.title("Erklärung der Bundestag Themen-Netzwerke")

# st.markdown("---")

# # --- Flowchart Abbildung ---
# fig, ax = plt.subplots(figsize=(10, 2))
#
# # Boxen
# ax.text(0.1, 0.5, "Themen–TOP Matrix\n(Zahlen pro Rede)", ha="center", va="center",
#         bbox=dict(boxstyle="round,pad=0.5", facecolor="#a6cee3", edgecolor="black"))
# ax.text(0.4, 0.5, "Themen Netzwerk\n(Kanten = Ähnlichkeiten)", ha="center", va="center",
#         bbox=dict(boxstyle="round,pad=0.5", facecolor="#b2df8a", edgecolor="black"))
# ax.text(0.7, 0.5, "PCA-Layout\n(Koordinaten)", ha="center", va="center",
#         bbox=dict(boxstyle="round,pad=0.5", facecolor="#fb9a99", edgecolor="black"))
# ax.text(0.9, 0.5, "Clustering\n(Farbgruppen)", ha="center", va="center",
#         bbox=dict(boxstyle="round,pad=0.5", facecolor="#fdbf6f", edgecolor="black"))
#
# # Pfeile
# ax.annotate("", xy=(0.28, 0.5), xytext=(0.18, 0.5),
#             arrowprops=dict(arrowstyle="->", lw=2))
# ax.annotate("", xy=(0.58, 0.5), xytext=(0.48, 0.5),
#             arrowprops=dict(arrowstyle="->", lw=2))
# ax.annotate("", xy=(0.82, 0.5), xytext=(0.75, 0.5),
#             arrowprops=dict(arrowstyle="->", lw=2))
#
# ax.axis("off")
# st.pyplot(fig)

st.markdown("---")

# ABSCHNITT 1: NETZWERKAUFBAU
st.header("1️⃣ Aufbau des Netzwerks")

st.write("""
Ausgangspunkt ist die **Themen–TOP-Matrix**  
(Zeilen = Tagesordnungspunkte, Spalten = Themen).  

Daraus konstruieren wir ein **Themen–Themen-Similaritätsnetzwerk**:

- Jeder **Knoten** = ein Thema  
- Jede **Kante** = Kosinus-Ähnlichkeit zwischen zwei Themen  
- Vorzeichen der Kante = **positiv (blau)**, wenn Themen oft gemeinsam auftreten,  
  **negativ (rot)**, wenn sie sich entgegenstehen  
- Gewicht der Kante = Stärke der Ähnlichkeit  
- Durch einen **Schwellenwert** filtern wir schwache Verbindungen heraus
""")

st.info("So wird die hochdimensionale Themenmatrix in ein semantisches Netzwerk überführt.")

st.markdown("---")

# ABSCHNITT 2: PCA LAYOUT
st.header("2️⃣ PCA-Layout")
st.header("PCA-Layout")

st.write("""
Die Anordnung der Knoten im Plot erfolgt mit der **Hauptkomponentenanalyse (PCA)**:

- Wir berechnen die **Korrelationssmatrix** zwischen Themen  
- Anschließend extrahieren wir die ersten 2–3 **Hauptkomponenten**  
- Diese Komponenten dienen als **Koordinaten** im 2D-Raum  
- Ergebnis: Themen, die sich ähnlich über die TOPs verhalten, liegen räumlich nah beieinander

✨ Dadurch entsteht eine **Geometrie der Ideen**, in der Cluster sichtbar werden.
""")

st.success("Nutzer:innen können interaktiv zwischen PC1–PC2, PC1–PC3 und PC2–PC3 wechseln.")

st.markdown("---")

# ABSCHNITT 3: KNOTENFÄRBUNG (CLUSTERING)
st.header("3️⃣ Knotenfärbung (Clustering)")

st.write("""
Um **Gemeinschaften von Themen** sichtbar zu machen, nutzen wir einen  
**Best-Response-Dynamik-Algorithmus** für signierte Graphen:

- Jeder Knoten startet mit einer eigenen Farbe  
- Iterativ aktualisiert jeder Knoten seine Farbe:  
  - **Positive Kanten** → sprechen für die Farbe der Nachbarn  
  - **Negative Kanten** → sprechen gegen die Nachbarfarbe  
  - **Selbststimme** → stabilisiert Entscheidungen  
- Der Prozess läuft, bis **keine Änderungen** mehr auftreten

🎨 Das Ergebnis sind **kohärente Themengruppen**:  
Themen, die zusammengehören, werden farblich gruppiert,  
während gegensätzliche Themen getrennt werden.
""")

st.warning("Diese Methode berücksichtigt die *signierte Natur* des Netzwerks – anders als Standard-Community-Algorithmen.")

st.markdown("---")

# ABSCHNITT 4: DAS GROSSE GANZE
st.header("4️⃣ Das große Ganze")

st.write("""
Zusammengefasst:

1. **Aufbau** des Themen-Similaritätsnetzwerks  
2. **Anordnung** der Knoten über PCA für eine interpretierbare Geometrie  
3. **Clustering** der Knoten durch Best-Response-Dynamik auf signierten Graphen  

➡️ Das Resultat ist eine **Landkarte der Bundestagsdebatten-Themen**:  
welche Themen zusammengehören, welche gegensätzlich sind  
und wie sie die politische Agenda strukturieren.
""")

#st.balloons()
