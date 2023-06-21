

import streamlit as st
import jsonlines
import matplotlib.pyplot as plt     # Für Visualisierung

#####################

DATA_PATH = "../../data/"

@st.cache
def laden(legislatur):
    # Wir generieren eine leere Liste:
    alleReden = []

    # Wir öffnen den entsprechende File (Dateipfad anpassen!):
    with jsonlines.open(f'{DATA_PATH}speeches_{legislatur}.jsonl') as f:
        for line in f.iter():
            # Wir packen alles Zeile für Zeile zu unserer Liste:
            alleReden.append(line)

    # Wir sortieren nach Datum:
    alleReden.sort(key = lambda x:x['date'])
    return alleReden

#####################

st.title("Wortverwendung nach Parteien")
st.subheader("Dies ist ein einfaches Beispiel für eine interaktive App, die im Browser läuft.")
st.markdown("""<hr style="height:10px;border:none;color:#333;background-color:#333;" /> """, unsafe_allow_html=True)
st.subheader("Wonach willst du suchen?")
such_wort1 = st.text_input("","Klimawandel")

st.subheader("Wonach willst du noch suchen?")
such_wort2 = st.text_input("","Klimakrise")

#####################

alleReden = laden(20)

parties = ['SPD', 'FDP', 'CDU', 'LINKE', 'GRÜNEN', 'AfD', 'unknown']  # sind die richtig geschrieben?

frequencies1 = []
untermenge = [ rede for rede in alleReden if such_wort1 in rede['text']]
for party in parties:
    untermengeP = [ rede for rede in untermenge if party in rede['party']]
    #st.write(f'Die {party} hat {len(untermengeP)} Reden mit "{such_wort1}" gehalten.')
    frequencies1.append(len(untermengeP))

frequencies2 = []
untermenge = [ rede for rede in alleReden if such_wort2 in rede['text']]
for party in parties:
    untermengeP = [ rede for rede in untermenge if party in rede['party']]
    #st.write(f'Die {party} hat {len(untermengeP)} Reden mit "{such_wort2}" gehalten.')
    frequencies2.append(len(untermengeP))

# Wir wollen das Ergebnis natürlich auch visualisieren
# Das machen wir mit matplotlib.pyplot (ganz oben als plt importiert)

plt.bar(parties, frequencies1, label=f'{such_wort1}')
plt.bar(parties, frequencies2, bottom=frequencies1, label=f'{such_wort2}')
plt.title("Verteilung der Häufigkeiten")
plt.xlabel("Partei")
plt.ylabel("Anzahl der Reden")
plt.legend(loc="upper left")

st.pyplot(plt.gcf()) # instead of plt.show()

