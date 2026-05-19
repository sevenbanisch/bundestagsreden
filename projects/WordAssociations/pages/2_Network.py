import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
from pyvis.network import Network
from build_network_with_word import build_network_with_word
import networkx as nx
import numpy as np

#import the data for building a list for the options of words for the user
coo_matrix = pd.read_hdf('data/coo_matrix.h5', key='df')

# Sort the columns alphabetically
coo_matrix_sorted = coo_matrix.reindex(sorted(coo_matrix.columns), axis=1)

#user can choose a word from the list
selected_word = st.selectbox('Mit Klick in das Feld und anschließendem Benutzen der Backspace-Taste kann ein eigenes Wort gesucht werden.', coo_matrix_sorted.columns, index=list(coo_matrix_sorted.columns).index("rechtsextrem"))

# builds the graph with the chosen word
G = build_network_with_word(selected_word)

# This creates the settings for the HTML file which will later contain the graph
graph_ch = Network(height='550px', width='100%', notebook=True, bgcolor="black", font_color="white")

# Configure the graph. Play around with the values to see what the settings change
graph_ch.set_options("""
{
  "nodes": {
    "color": {
         "inherit": true
       },
    "size": 1000
  },
  "edges": {
    "width": 1000,
     "color": {
      "inherit": true
    },
    "selfReferenceSize": null,
    "selfReference": {
      "angle": 0.7853981633974483
    },
    "smooth": false
  },
  "physics": {
    "enabled": true,
    "barnesHut": {
      "gravitationalConstant": -8000
    },
    "minVelocity": 0.075,
    "maxVelocity": 2
  }
}""")

# the datatype "float32" cant be saved in a html file, the following code converts to normal float
for node in G.nodes(data=True):
    for key, value in node[1].items():
        if isinstance(value, np.float32):
            node[1][key] = float(value)
for edge in G.edges(data=True):
    for key, value in edge[2].items():
        if isinstance(value, np.float32):
            edge[2][key] = float(value)

# This creates a pyvis graph from the networkx graph (we do this because a pyvis graph is easily stored as an HTML file which we can load into streamlit)
graph_ch.from_nx(G)

# The pyvis graph is saved in a html file
graph_ch.save_graph("data/graph_40.html")
print("saved")

# This opens the HTML file
print("preopen")
HtmlFile = open("data/graph_40.html", 'r', encoding='utf-8')
source_code = HtmlFile.read()

# This embeds the HTML file in the streamlit webpage
print("preshow")
components.html(source_code, height=560, width=900, scrolling=True)
