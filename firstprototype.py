import streamlit as st
import pandas as pd
import numpy as np
import requests
import spacy
#nlp = spacy.load('de') #load spacy model
nlp = spacy.load('de_core_news_sm') #load spacy model
import tqdm
import seaborn as sns
import matplotlib.pyplot as plt
sns.set_style("whitegrid")

import json

import altair as alt
import sys

##################### 
img_width = 300
img_height = 200
##################### 


st.title("Wer sagt was im Bundestag?")

hints = st.checkbox("Hinweise anzeigen", value = True)
if hints:
    st.write("- Groß- und Kleinschreibung wird unterschieden.  \n (Beispiel: 'Bundestag' enthält nicht 'bund')" )
    st.write("- Der Suchbegriff wird auch innerhalb einzelner Wörter gesucht.  \n (Beispiel: 'Bundestag' enthält die Suchbegriffe 'Bund', sowie 'des') ")
    st.write("- Die Suche innerhalb einzelner Wörter kann vermieden werden, indem vor und/oder nach dem Suchbegriff ein Leerzeichen gesetzt wird.  \n (Beispiel: 'Bundestag' enthält '*Leerzeichen*Bund', jedoch nicht 'Bund*Leerzeichen*')")
    #st.write(f"*(Der Datensatz enthält momentan {num_words_all:,} Wörter - häufig genannte Suchbegriffe können zu einer etwas längeren Rechendauer führen.)*")
    st.write(f"*(Der Datensatz enthält momentan rund 7 mio. Wörter - häufig genannte Suchbegriffe können zu einer etwas längeren Rechendauer führen.)*")
st.write("**Einstellungen**")
st.write(" ")

per_word = st.checkbox("Anzahl der Nennungen des Suchbegriffs anstatt Anzahl der Redebeiträge (Mehrfachnennungen des Suchbegriffs innerhalb einer Rede werden gezählt)")

wo_fraktionslos = st.checkbox("Fraktionslose für Reskalierung ausschließen")
saetz = st.checkbox("Aussagen (Sätze) heraussuchen, die beide Suchbegriffe enthalten")

##################### 
@st.cache(suppress_st_warning=True, show_spinner=False)
def laden():
    loading_data = st.markdown("** *Datensatz wird geladen...* **")
    json = {'search_query':'', 
            'dataset_name':'deu', 
            'start_date':'2016-1-1', 
            'end_date':'2021-1-1'}
    result = requests.post('https://penelope.vub.be/parliament-data/get-speeches', json=json)

    all_speeches = []
    for speech in result.json()["speeches"]:
        all_speeches.append(speech)
    # code to sort list on date 
    all_speeches.sort(key = lambda x:x['date'])
    
    loading_data.empty()

    return all_speeches

##################### 

def suche(such_term):
    speeches = []
    for speech in all_speeches:
        if such_term in speech['text'] :
            speeches.append(speech)
    speeches.sort(key = lambda x:x['date']) 
    return speeches

#####################

def build_df(speeches_arg):

    if per_word:
        parties = []
        cdu = []
        spd = []
        gruene = []
        linke = []
        afd = []
        fdp = []
        fraktionslos = []
        dates = []   
        
        if speeches_arg == speeches:
            such_term = search_query
            
        elif speeches_arg == speeches2:
            such_term = search_query2    
        else:
            st.write("Achtung falscher Datensatz")
            such_term = ""    

        for speech in speeches_arg:
            parties.append(speech['party'])
            dates.append(speech['date'])
            if (speech['party'] == 'CDU/CSU'):
                cdu.append(speech['text'].count(such_term)) 
            else: 
                cdu.append(0)
            if (speech['party'] == 'SPD'):
                spd.append(speech['text'].count(such_term))
            else: 
                spd.append(0)
            if (speech['party'] == 'BÜNDNIS 90/DIE GRÜNEN' or speech['party'] == 'Bündnis 90/Die Grünen' or speech['party'] == 'BUENDNIS 90/DIE GRUENEN'):
                gruene.append(speech['text'].count(such_term))
            else: 
                gruene.append(0)    
            if (speech['party'] == 'DIE LINKE'):
                linke.append(speech['text'].count(such_term))
            else: 
                linke.append(0)     
            if (speech['party'] == 'AfD'):
                afd.append(speech['text'].count(such_term))
            else: 
                afd.append(0)
            if (speech['party'] == 'FDP'):
                fdp.append(speech['text'].count(such_term))
            else: 
                fdp.append(0)               
            if (speech['party'] == 'fraktionslos'or speech['party'] == 'Fraktionslos' or speech['party']== 'Bremen' ):
                fraktionslos.append(speech['text'].count(such_term))
            else: 
                fraktionslos.append(0)
   #         if speech['party'] != 'CDU/CSU' and speech['party'] != 'SPD' and speech['party'] != 'AfD' and speech['party'] != 'FDP' and speech['party'] != 'BÜNDNIS 90/DIE GRÜNEN' and speech['party'] != 'Bündnis 90/Die Grünen' and speech['party'] != 'DIE LINKE' and speech['party'] != 'fraktionslos' and speech['party'] != 'Fraktionslos' and speech['party'] != 'Bremen':
      #!          st.write(speech['party'])
  #              gruene.append(speech['text'].count(such_term))
                     
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
        df['DIE LINKE'] = linke
        df['FDP'] = fdp
        df['AfD'] = afd
        df['fraktionslos'] = fraktionslos

        return df        
    
    else:
        
        parties = []
        cdu = []
        spd = []
        gruene = []
        linke = []
        afd = []
        fdp = []
        fraktionslos = []
        dates = []
        
        for speech in speeches_arg:
            
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
            if (speech['party'] == 'BÜNDNIS 90/DIE GRÜNEN' or speech['party'] == 'Bündnis 90/Die Grünen'):
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
            if (speech['party'] == 'fraktionslos'or speech['party'] == 'Fraktionslos' or speech['party'] == 'Bremen' ):
                fraktionslos.append(1)
            else: 
                fraktionslos.append(0)
  #          if speech['party'] != 'CDU/CSU' and speech['party'] != 'SPD' and speech['party'] != 'AfD' and speech['party'] != 'FDP' and speech['party'] != 'BÜNDNIS 90/DIE GRÜNEN' and speech['party'] != 'Bündnis 90/Die Grünen' and speech['party'] != 'DIE LINKE' and speech['party'] != 'fraktionslos' and speech['party'] != 'Fraktionslos' and speech['party'] != 'Bremen':
   #             st.write(speech['party'])
       #!         gruene.append(1)

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
        df['DIE LINKE'] = linke
        df['FDP'] = fdp
        df['AfD'] = afd
        df['fraktionslos'] = fraktionslos
    
        return df
    
#####################

def count_words(speeches):

    num_words_party = [0,0,0,0,0,0,0]
    for speech in speeches:
        if (speech['party'] == 'CDU/CSU'):
            num_words_party[0] += len(speech['text'].split())
        elif (speech['party'] == 'SPD'):
            num_words_party[1] += len(speech['text'].split())
        elif (speech['party'] == 'BÜNDNIS 90/DIE GRÜNEN' or speech['party'] == 'Bündnis 90/Die Grünen' or speech['party'] == 'BUENDNIS 90/DIE GRUENEN'):
            num_words_party[2] += len(speech['text'].split()) 
        elif (speech['party'] == 'DIE LINKE'):
            num_words_party[3] += len(speech['text'].split())  
        elif (speech['party'] == 'AfD'):
            num_words_party[4] += len(speech['text'].split())
        elif (speech['party'] == 'FDP'):
            num_words_party[5] += len(speech['text'].split())
        elif (speech['party'] == 'fraktionslos'or speech['party'] == 'Fraktionslos' or speech['party'] == 'Bremen'):
            num_words_party[6] += len(speech['text'].split())           
    return num_words_party
    
#####################

def count_speeches(speeches):
    
    num_speeches_party = [0,0,0,0,0,0,0]
        
    for speech in speeches:
        if (speech['party'] == 'CDU/CSU'):
            num_speeches_party[0] += 1
        elif (speech['party'] == 'SPD'):
            num_speeches_party[1] += 1
        elif (speech['party'] == 'BÜNDNIS 90/DIE GRÜNEN' or speech['party'] == 'Bündnis 90/Die Grünen' or speech['party'] == 'BUENDNIS 90/DIE GRUENEN'):
            num_speeches_party[2] += 1
        elif (speech['party'] == 'DIE LINKE'):
            num_speeches_party[3] += 1
        elif (speech['party'] == 'AfD'):
            num_speeches_party[4] += 1
        elif (speech['party'] == 'FDP'):
            num_speeches_party[5] += 1
        elif (speech['party'] == 'fraktionslos'or speech['party'] == 'Fraktionslos' or speech['party'] == 'Bremen'):
            num_speeches_party[6] += 1     
    return num_speeches_party

#########################
    
all_speeches = laden()
#st.write("number of all speeches:", len(all_speeches) , "type:", type(all_speeches), "size in bytes:" ,sys.getsizeof(all_speeches), "first elements:", all_speeches[:2])      # alle 11990 Reden


num_words_party = count_words(all_speeches)
num_words_all = sum(num_words_party)
# Gewichtung: Nennung pro 100.000 Wörter
words_bal = [i/j for i,j in zip([100000 for i in range(7)],num_words_party)]    

num_speeches_party = count_speeches(all_speeches)
# Gewichtung: Nennung pro 1000 Reden
speeches_bal = [i/j for i,j in zip([1000 for i in range(7)],num_speeches_party)]




st.subheader("**Erster Suchbegriff**")
search_query = st.text_input("", "erneuerbar" )                                             
if search_query == "":
    search_query = " "    

speeches = []
speeches = suche(search_query)

#########################

df = build_df(speeches)
#st.write(df)
dfagg = df.resample('3M').sum()

##########################

m = None
l = None

if per_word:
    m = sum(df['CDU/CSU'])+sum(df['SPD'])+sum(df['BÜNDNIS 90/DIE GRÜNEN'])+sum(df['DIE LINKE'])+sum(df['AfD'])+sum(df['FDP'])+sum(df['fraktionslos'])
    if search_query == ' ' or search_query == '':                               
        st.write(f"Der Datensatz umfasst insgesamt {num_words_all:,} Wörter.")
    else:
        st.write(f"Das Wort _{search_query}_ wird {m} mal genannt.")

else:
    l = len(speeches)
    if search_query == ' ' or search_query == '':
        st.write(f"Der Datensatz umfasst {l} Reden.")
    else:
        st.write(f"Das Wort _{search_query}_ wird in {l} verschiedenen Reden genannt.")
        
#####################

if m == 0 or l == 0:
    pass
else:
    if per_word:        
        if wo_fraktionslos:
            words_bal[6] = 0                                                    # Fraktionslosen keine Gewichtung zuweisen
        dfagg_bal = dfagg*words_bal
    else:
        if wo_fraktionslos:
            speeches_bal[6] = 0                                                 # Fraktionslosen keine Gewichtung zuweisen
        dfagg_bal = dfagg*speeches_bal                            
    
    
    
    st.write("**Absolute Anzahl**")
    st.area_chart(dfagg,img_width, img_height,True)

# Farben entsprechend der Parteien
    
 #   st.area_chart = (dfagg,img_width, img_height,True, color = alt.Color(col))

 #   st.write(dfagg)

     #define colors (parties)
#    pal = ["#009ee0","#46962b","#000000","#800080","ffed00", "#e3000f","#808080" ]
 #   x = [1,2,3,4,5,6,7,8,9]
  #  y = dfagg['SPD']       
   # fig = plt.stackplot(x,y, colors=pal, alpha=0.4 )
#    st.pyplot(fig)
    
#    x = [1,2,3,4,5,6,7,8,9]
   # y = dfagg['SPD']       
 #   fig = plt.stackplot(x,y, colors=pal, alpha=0.4 )
   # st.pyplot(fig)
    
#    df0 = pd.DataFrame(np.random.randn(200, 3),columns=['a', 'b', 'c'])
 #   c = alt.Chart(df0).mark_circle().encode(
  #  x='a', y='b', size='c', color='c', tooltip=['a', 'b', 'c'])

   # st.altair_chart(c, use_container_width=True)    
    
#    data = alt.Chart(df).mark_area().encode(
#            x= 'datetime',
 #           y= 'CDU/CSU',
  #          y2 = 'SPD',
   #         y3 = 'BÜNDNIS 90/DIE GRÜNEN',
    #        y4 = 'DIE LINKE',
     #       y5 = 'AfD',
      #      y6 = 'FDP',
       #     y7 = 'fraktionslos',
            #color= alt.Color('pal',scale=None)
      #      )
    
   # st.altair_chart(data, use_container_width=True)
    
#    ax = dfagg.plot.area(linewidth=0, colormap=col)     
 #   st.area_chart(dfagg,img_width, img_height,True, color = col)

    st.write("**Anteil der Parteien an absoluter Anzahl**")
    st.area_chart(dfagg.div(dfagg.sum(axis=1), axis=0).fillna(0),img_width,img_height,True)

    if per_word:
        st.write("**Absolute Anzahl pro 100.000 gesprochene Wörter der Parteien**")
    else:
        st.write("**Absolute Anzahl pro 1000 gehaltene Reden der Parteien**")
    st.area_chart(dfagg_bal,img_width, img_height,True)   
    
#######################################################

st.subheader("**Zweiter Suchbegriff**")

search_query2 = st.text_input("", "wirtschaftlich")
if search_query2 == "":
    search_query2 = " "                                             
speeches2 = suche(search_query2)

df2 = build_df(speeches2)
df2agg = df2.resample('3M').sum()

m2 = None
l2 = None

if per_word:
    m2 = sum(df2['CDU/CSU'])+sum(df2['SPD'])+sum(df2['BÜNDNIS 90/DIE GRÜNEN'])+sum(df2['DIE LINKE'])+sum(df2['AfD'])+sum(df2['FDP'])+sum(df2['fraktionslos'])
    if search_query2 == ' ' or search_query2 == '':                               
        st.write(f"Der Datensatz umfasst insgesamt {m2} Wörter.")                    
    else:
        st.write(f"Das Wort _{search_query2}_ wird {m2} mal genannt.")

else:
    l2 = len(speeches2)
    if search_query2 == ' ' or search_query == '':
        st.write(f"Der Datensatz umfasst {l2} Reden.")
    else:
        st.write(f"Das Wort _{search_query2}_ wird in {l2} verschiedenen Reden genannt.")

if m2 == 0 or l2 == 0:
    pass
else:  
    if per_word:       
        if wo_fraktionslos:
            words_bal[6] = 0  
        
        df2agg_bal = df2agg*words_bal
    else:
        if wo_fraktionslos:
            speeches_bal[6] = 0          
        df2agg_bal = df2agg*speeches_bal

    st.write("**Absolute Anzahl**")    
    st.area_chart(df2agg,img_width,img_height,True)
    
    st.write("**Anteil der Parteien an absoluter Anzahl**")
    st.area_chart(df2agg.div(df2agg.sum(axis=1), axis=0).fillna(0),img_width,img_height,True)

    if per_word:
        st.write("**Absolute Anzahl pro 100.000 gesprochene Wörter der Parteien**")
    else:
        st.write("**Absolute Anzahl pro 1000 gehaltene Reden der Parteien**")
    st.area_chart(df2agg_bal,img_width,img_height,True)

    
#########################################################

st.subheader("**Der Zusammenhang**")

#st.write(speeches)

if per_word:
    st.write("*Der Zusammenhang wird nicht für Anzahl der Nennungen berechnet.*")
else:
    jointspeeches=[]
    for speech in speeches:
        if search_query in speech['text'] and search_query2 in speech['text']:
            jointspeeches.append(speech)
    #st.write(jointspeeches)
    ljoint = len(jointspeeches)

    if ljoint == 0:
        st.write(f"Es gibt keine Reden, die sowohl _{search_query}_ als auch _{search_query2}_ enthalten.")
    else:
        st.write(f"Es gibt {ljoint} Reden, die sowohl _{search_query}_ als auch _{search_query2}_ enthalten.")
        dfj = build_df(jointspeeches)
        dfjagg = dfj.resample('3M').sum()
        dfjagg_bal = dfjagg*speeches_bal

        st.write("**Absolute Anzahl**")  
        st.area_chart(dfjagg,img_width,img_height,True)
        
        st.write("**Anteil der Parteien an absoluter Anzahl**")
        st.area_chart(dfjagg.div(dfjagg.sum(axis=1), axis=0).fillna(0),img_width,img_height,True)

        if per_word:
            st.write("**Absolute Anzahl pro 100.000 gesprochene Wörter der Parteien**")
        else:
            st.write("**Absolute Anzahl pro 1000 gehaltene Reden der Parteien**")
        st.area_chart(dfjagg_bal,img_width,img_height,True)
        
 #       st.write(jointspeeches)

#######################
        
        if saetz:     
            loading = st.markdown("*Suche nach Aussagen läuft...*")
            stm_list=[]
            for speech in tqdm.tqdm(jointspeeches):
                doc = nlp(speech["text"])                                       # npl() natural language processing
                for sent in doc.sents:
                    if search_query in sent.text and search_query2 in sent.text:
                        #print(sent)
                        stm_dict = {
                            'Name'  : speech["name"],
                            'Partei' : speech["party"],
                            'Datum'  : speech["date"],
                            'Text'  : sent.text
                        }
                        stm_list.append(stm_dict)
            loading.empty()
            if len(stm_list) != 0:
                num_stm_list = len(stm_list)
                st.write(f'Folgende {num_stm_list} Aussagen (Sätze) beinhalten beide Suchbegriffe:') 
                st.write(stm_list)
            else:
                st.write("Es gibt keine Aussagen (Sätze), die beide Suchbegriffe enthalten.")              