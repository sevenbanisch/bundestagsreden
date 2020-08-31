import streamlit as st
import pandas as pd
import numpy as np
import requests
import spacy
import tqdm

import json


st.title("Wer sagt was im Bundestag?")

st.subheader("Wonach willst du suchen?")
search_query = st.text_input("","Digitalisierung")

json = {'search_query':search_query, 
        'dataset_name':'deu', 
        'start_date':'2018-1-1', 
        'end_date':'2019-1-1'}
result = requests.post('https://penelope.vub.be/parliament-data/get-speeches', json=json)

speeches = []
for speech in result.json()["speeches"]:
    speeches.append(speech) 

l = len(speeches)
if search_query == ' ' or search_query == '':
    st.write(f"There are {l} discussions.")
else:
    st.write(f"There are {l} discussions containing _{search_query}_.")

#print(result)   