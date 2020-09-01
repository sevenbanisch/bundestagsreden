import streamlit as st
import pandas as pd
import numpy as np
import requests
import spacy
nlp = spacy.load('de') #load spacy model
import tqdm
import seaborn as sns
import matplotlib.pyplot as plt
sns.set_style("whitegrid")

import json


##################### 
img_width = 300
img_height = 200
##################### 


st.title("Wer sagt was im Bundestag?")

st.subheader("Wonach willst du suchen?")
search_query = st.text_input("","erneuerbar")

##################### 
@st.cache
def suche(such_term):
    json = {'search_query':such_term, 
            'dataset_name':'deu', 
            'start_date':'2016-1-1', 
            'end_date':'2021-1-1'}
    result = requests.post('https://penelope.vub.be/parliament-data/get-speeches', json=json)

    speeches = []
    for speech in result.json()["speeches"]:
        speeches.append(speech)
    # code to sort list on date 
    speeches.sort(key = lambda x:x['date']) 
    return speeches
##################### 

speeches = suche(search_query)

l = len(speeches)
if search_query == ' ' or search_query == '':
    st.write(f"There are {l} speeches.")
else:
    st.write(f"There are {l} speeches containing _{search_query}_.")

#####################
def build_df(speeches):
 
    parties = []
    cdu = []
    spd = []
    gruene = []
    linke = []
    afd = []
    fdp = []
    dates = []
    for speech in speeches:
        parties.append(speech['party'])
        dates.append(speech['date'])
        if (speech['party'] == 'CDU/CSU'):
            cdu.append(1)
        else: 
            cdu.append(0)
        if (speech['party'] == 'SPD'):
            spd.append(1)
        else: 
            spd.append(0)
        if (speech['party'] == 'BÜNDNIS 90/DIE GRÜNEN'):
            gruene.append(1)
        else: 
            gruene.append(0)    
        if (speech['party'] == 'DIE LINKE'):
            linke.append(1)
        else: 
            linke.append(0)     
        if (speech['party'] == 'AfD'):
            afd.append(1)
        else: 
            afd.append(0)
        if (speech['party'] == 'FDP'):
            fdp.append(1)
        else: 
            fdp.append(0)               

    # Create an empty dataframe
    df = pd.DataFrame()
    # Create a column from the datetime variable
    df['datetime'] = dates
    # Convert that column into a datetime datatype
    df['datetime'] = pd.to_datetime(df['datetime'])
    # Set the datetime column as the index
    df.index = df['datetime'] 
    # Create a column from the numeric score variable
    df['party'] = parties
    df['CDU/CSU'] = cdu
    df['SPD'] = spd
    df['BÜNDNIS 90/DIE GRÜNEN'] = gruene
    df['DIE LKINKE'] = linke
    df['FDP'] = fdp
    df['AfD'] = afd

    return df
#####################

df = build_df(speeches)
#chart_data = pd.DataFrame(np.random.randn(20, 3), columns=['a', 'b', 'c'])
#st.write(np.random.randn(20, 3))
dfagg = df.resample('M').sum()
#st.write(df)
#st.write(dfagg)
st.area_chart(dfagg,img_width, img_height,True)
dfagg = df.resample('3M').sum()
st.area_chart(dfagg.div(dfagg.sum(axis=1), axis=0).fillna(0),img_width,img_height,True)

st.subheader("Wonach willst du noch suchen?")


search_query2 = st.text_input("","wirtschaftlich")
speeches2 = suche(search_query2)
l2 = len(speeches2)
if search_query2 == ' ' or search_query == '':
    st.write(f"There are {l2} speeches.")
else:
    st.write(f"There are {l2} speeches containing _{search_query2}_.")

df2 = build_df(speeches2)
df2agg = df2.resample('M').sum()
#total2 = df2.resample('M').agg({'party':'count'})
st.area_chart(df2agg,img_width,img_height,True)
df2agg = df2.resample('3M').sum()
st.area_chart(df2agg.div(df2agg.sum(axis=1), axis=0).fillna(0),img_width,img_height,True)
#st.write(df2agg.div(df2agg.sum(axis=1), axis=0).fillna(0))


st.subheader("Der Zusammenhang?")

jointspeeches=[]
for speech in speeches:
    if search_query in speech['text'] and search_query2 in speech['text']:
        jointspeeches.append(speech)
#st.write(jointspeeches)
ljoint = len(jointspeeches)
st.write(f"There are {ljoint} speeches containing _{search_query}_ and _{search_query2}_")

dfj = build_df(jointspeeches)
dfjagg = dfj.resample('3M').sum()
#total2 = df2.resample('M').agg({'party':'count'})
st.area_chart(dfjagg,img_width,img_height,True)
dfjagg = dfj.resample('3M').sum()
st.area_chart(dfjagg.div(dfjagg.sum(axis=1), axis=0).fillna(0),img_width,img_height,True)

stm_list=[]
for speech in tqdm.tqdm(jointspeeches):
    doc = nlp(speech["text"])
    for sent in doc.sents:
        if search_query in sent.text and search_query2 in sent.text:
            #print(sent)
            stm_dict = {
                'name'  : speech["name"],
                'party' : speech["party"],
                'text'  : sent.text
            }
            stm_list.append(stm_dict)

st.write('Folgende Aussagen (Sätze) bringen beide Begriffe in Verbindung:') 
st.write(stm_list)            