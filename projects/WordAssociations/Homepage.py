import streamlit as st
import matplotlib.pyplot as plt

# This sets the webpage basic configuration
st.set_page_config(
    menu_items={
        'Get Help': 'mailto:ufqoe@gmail.com',
        'Report a bug': "mailto:ufqoe@gmail.com",
        'About': "This app has been created by Paul Jack, student of the Karlsruhe Institute of Technology, under the guidance of Dr Sven Banisch."}
)

st.title('Assoziationen in Bundestagsreden')

st.write("Diese App bietet die Möglichkeit Wortassoziationen in den Bundestagsreden der Legislaturperiode 19 und 20 zu u"
         "ntersuchen. Die Nutzer:innen haben die Möglichkeit ein Wort auszuwählen. Dann wird ein Netzwerk angezeigt, da"
         "s aus 40 Wörtern besteht und die Wörter mit der höchsten Assoziation zu dem ausgewählten Wort beinhaltet. "
        "Die Assoziation eines Worts mit einem anderen Wort wird von der Häufigkeit abgeleitet, wie oft die zwei Wörter mit einem"
        " Abstand von maximal 20 Worten zusammen in den Bundestagsreden vorkommen.")

st.write("Es werden nicht zwischen allen 40 Wörtern bzw. Knoten die zugehörigen Assoziationen als Kanten abgebildet, sondern lediglic"
         "h die stärksten 10 % der Assoziationen. Die Dicke der Kanten ist die logarithmierte Stärke der Assoziation. "
         "Die Größe der Knoten in dem Netzwerk stellt die Stärke der Assoziation zu dem ausgewählten Wort dar.")

st.write("Für eine genauere Beschreibung der Datengrundlage und der Bildung des Netzwerks steht die ReadMe-Datei in der"
         " App zur Verfügung.")
#%%

#%%

#%%

#%%

#%%

#%%
