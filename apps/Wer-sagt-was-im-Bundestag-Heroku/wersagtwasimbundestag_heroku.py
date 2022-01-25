import streamlit as st
import pandas as pd
import numpy as np
import requests
import spacy
#nlp = spacy.load('de') #load spacy model
nlp_de = spacy.load('de_core_news_sm') #load spacy model
#nlp_en = spacy.load('en-core-web-sm-2.3.1')
import tqdm
import seaborn as sns

#import sys

import webbrowser                                                               # does not need to be installed 
import os

sns.set_style("whitegrid")

import altair as alt

from collections import Counter

##################### 
img_width = 300
img_height = 200
##################### 

st.sidebar.header("**Sidebar**")
language = st.sidebar.selectbox("language/parliament", ("German","English (UK)") )
st.sidebar.markdown("---------------------")

if language == "German":
    no_fraktionslos = st.sidebar.checkbox("Fraktionslose in Darstellung ausschließen", value = True)
    hints = st.sidebar.checkbox("Hinweise anzeigen", value = False)
    
    if hints:
        st.sidebar.info("Groß- und Kleinschreibung wird unterschieden." )
        st.sidebar.markdown(" *Bsp.: 'Bundestag' enthält nicht 'bund'*")
        st.sidebar.info("Der Suchbegriff wird auch innerhalb einzelner Wörter gesucht.")
        st.sidebar.markdown(" *Bsp.: 'Bundestag' enthält die Suchbegriffe 'Bund', sowie 'des'*")
        st.sidebar.info("Die Suche innerhalb einzelner Wörter kann vermieden werden, indem vor und/oder nach dem Suchbegriff ein Leerzeichen gesetzt wird.")
        st.sidebar.markdown(" *Bsp.: 'Bundestag' enthält '<Leerzeichen>Bund', jedoch nicht 'Bund<Leerzeichen>'*")    
    
    per_word = False
    sentence = True
    advanced = st.sidebar.checkbox("Erweiterte Einstellungen")
    agg_slider = 3
    cos_sim_thresh = 0.4    
    graph_select = ['Reskaliert']
    if advanced:
        st.sidebar.markdown("---------------------")

        graph_select = st.sidebar.multiselect("Graphen:", ['Reskaliert','Absolut','Anteil'])
        
        per_word = st.sidebar.checkbox("Anzahl der Nennungen des Suchbegriffs anstatt Anzahl der Redebeiträge (Mehrfachnennungen des Suchbegriffs innerhalb einer Rede werden gezählt)")
    
        sentence = st.sidebar.checkbox("Aussagen (Sätze) heraussuchen, die beide Suchbegriffe enthalten", value = True)
        agg_slider = st.sidebar.slider("Daten über x Monate aggregieren", 1, 12, 3)     # min, max, default
    st.sidebar.markdown("---------------------")
    show_graph = st.sidebar.checkbox("Netzwerk der Reden anzeigen", value = True)

    if show_graph == True:
        cos_sim_thresh = st.sidebar.slider("Schwellenwert für Kosinus-Ähnlichkeit (Lemmatisiert)", 0.1, 1.0, 0.4, 0.05)     # min, max, default, step   
    ##############################

    st.markdown('<p style="font-size: 30pt; font-weight: bold; color: white; \
        background-color: #000">&nbsp;\
        <a >Wer sagt was im Bundestag?</a>\
        </p>', unsafe_allow_html=True)
    
    ##################### 
    @st.cache(suppress_st_warning=True, show_spinner=False)
    def load_de():
        loading_data = st.markdown("** *Datensatz wird geladen...* **")
        json = {'search_query': " ", 
                'dataset_name':'deu', 
                'start_date':'2016-1-1', 
                'end_date':'2021-1-1'}
        result = requests.get('https://penelope.vub.be/parliament-data/get-speeches/deu/2016-01-01/2021-01-01/%20/1000000000000')
    
        all_speeches = []
        for speech in result.json()["speeches"]:
            all_speeches.append(speech)
        # code to sort list on date 
        all_speeches.sort(key = lambda x:x['date'])
        
        loading_data.empty()

        return all_speeches
    
    ##################### 
    
    def fct_search(such_term):
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
                if ('90' in speech['party']):                   #if (speech['party'] == 'BÜNDNIS 90/DIE GRÜNEN' or speech['party'] == 'Bündnis 90/Die Grünen' or speech['party'] == 'BUENDNIS 90/DIE GRUENEN'):
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
      #          if speech['party'] != 'CDU/CSU' and speech['party'] != 'SPD' and speech['party'] != 'AfD' and speech['party'] != 'FDP' and speech['party'] != 'BÜNDNIS 90/DIE GRÜNEN' and speech['party'] != 'Bündnis 90/Die Grünen' and speech['party'] != 'DIE LINKE' and speech['party'] != 'fraktionslos' and speech['party'] != 'Fraktionslos' and speech['party'] != 'Bremen':
       #             st.write(speech['party'])
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
                if ('90' in speech['party']):                                   # if (speech['party'] == 'BÜNDNIS 90/DIE GRÜNEN' or speech['party'] == 'Bündnis 90/Die Grünen'):
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
            elif ('90'in speech['party']):                                      # speech['party'] == 'BÜNDNIS 90/DIE GRÜNEN' or speech['party'] == 'Bündnis 90/Die Grünen' or speech['party'] == 'BUENDNIS 90/DIE GRUENEN'):
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
            elif ('90'in speech['party']):                                      # (speech['party'] == 'BÜNDNIS 90/DIE GRÜNEN' or speech['party'] == 'Bündnis 90/Die Grünen' or speech['party'] == 'BUENDNIS 90/DIE GRUENEN'):
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
    
    def fct_dfplot(dfagg):  
      
        date = []
        party = []                                                              #df['CDU/CSU']+df['SPD']+df['BÜNDNIS 90/DIE GRÜNEN']+df['DIE LINKE']+df['AfD']+df['FDP']+df['fraktionslos']
        num = []
        
        dfagg = dfagg.reset_index()
        
    #    st.write("dfagg:",dfagg)
        
        for i in dfagg.index:
            date.extend([dfagg['datetime'][i]] * 7) 

            party.append('CDU/CSU')
            party.append('SPD')
            party.append('BÜNDNIS 90/DIE GRÜNEN')    
            party.append('DIE LINKE')
            party.append('AfD')
            party.append('FDP')
            party.append('fraktionslos')
    
            num.append(dfagg['CDU/CSU'][i])
            num.append(dfagg['SPD'][i])
            num.append(dfagg['BÜNDNIS 90/DIE GRÜNEN'][i])
            num.append(dfagg['DIE LINKE'][i])
            num.append(dfagg['AfD'][i])
            num.append(dfagg['FDP'][i])
            num.append(dfagg['fraktionslos'][i])
    
        dfplot = pd.DataFrame()
        dfplot['Datum'] = date
        dfplot.index = dfplot['Datum']
        dfplot['Fraktion'] = party
        dfplot['n'] = num
        
    #    st.write(dfplot)
    
        return dfplot
    
    ##########################
    
    def altair_plot(dfplot):
    
        data = alt.Chart(dfplot).mark_area(opacity = 0.7).encode(
                x= 'Datum',
                y= 'n',                    
                color= alt.Color('Fraktion', scale=alt.Scale(domain=domain, range=color_codes_party)),
                tooltip = ['Datum', 'n', 'Fraktion']
                ).properties(width = img_width, height = img_height*1.2)   
        st.altair_chart(data, use_container_width=True)
    
    ##########################
        
    all_speeches = load_de()
    #st.write("number of all speeches:", len(all_speeches) , "type:", type(all_speeches), "size in bytes:" ,sys.getsizeof(all_speeches), "first elements:", all_speeches[:2])      # alle 11990 Reden
    
    num_words_party = count_words(all_speeches)
    num_words_all = sum(num_words_party)
    # weight: mentions per 100,000 words
    words_bal = [i/j for i,j in zip([100000 for i in range(7)],num_words_party)]    
    
    num_speeches_party = count_speeches(all_speeches)
    # weight: mentions per 100,000 words
    speeches_bal = [i/j for i,j in zip([1000 for i in range(7)],num_speeches_party)]
    
    
    st.markdown("--------------------------------------------------------------------------------------------------")    
    
    #st.write("bytes speeches_de:", sys.getsizeof(all_speeches))
    st.subheader(" **Wonach willst du suchen?**")
    
    search_query = st.text_input(label = "", value = "EU" )                     # EU                            
    if search_query == "":
        search_query = " "    
    
    speeches = []
    speeches = fct_search(search_query)
    
    #########################
    
    df = build_df(speeches)
    #st.write(df)
    dfagg = df.resample(f'{agg_slider}M').sum()
    
    ##########################
    
    m = None
    l = None
    
    if per_word:
        m = sum(df['CDU/CSU'])+sum(df['SPD'])+sum(df['BÜNDNIS 90/DIE GRÜNEN'])+sum(df['DIE LINKE'])+sum(df['AfD'])+sum(df['FDP'])+sum(df['fraktionslos'])
        if search_query == ' ' or search_query == '':                               
            st.write(f"Der Datensatz umfasst insgesamt {num_words_all:,} Wörter.")
        else:
            st.write(f"Der Begriff _{search_query}_ wird {m} mal genannt.")
    
    else:
        l = len(speeches)
        if search_query == ' ' or search_query == '':
            st.write(f"Der Datensatz umfasst {l} Reden.")
        else:
            st.write(f"Der Begriff _{search_query}_ wird in {l} verschiedenen Reden genannt.")
            
    #####################
    
    # colors for plotting
    domain = ['AfD', 'BÜNDNIS 90/DIE GRÜNEN', 'CDU/CSU', 'DIE LINKE', 'FDP', 'SPD', 'fraktionslos']
    color_codes_party = ["#009ee0","#46962b","#000000","#800080","#ffed00", "#e3000f","#808080" ] # color codes parties
    
    
    if m == 0 or l == 0:
        pass
    else:
        if per_word:        
            if no_fraktionslos:
                words_bal[6] = 0                                                # weight of "Fraktionslose" is 0
            dfagg_bal = dfagg*words_bal
        else:
            if no_fraktionslos:
                speeches_bal[6] = 0                                             # weight of "Fraktionslose" is 0
            dfagg_bal = dfagg*speeches_bal                            
    
    
        if "Reskaliert" in graph_select: 
            if per_word:
                st.write("**Absolute Anzahl pro 100.000 gesprochene Wörter der Fraktionen**")
            else:
                st.write("**Absolute Anzahl pro 1000 gehaltene Reden der Fraktionen**")
        
            dfplot = fct_dfplot(dfagg_bal)           
            altair_plot(dfplot)
    
        if "Absolut" in graph_select:
        
            st.write("**Absolute Anzahl**")

            dfplot = fct_dfplot(dfagg)         
            altair_plot(dfplot)
        
        if "Anteil" in graph_select:    
            st.write("**Anteil der Fraktionen an absoluter Anzahl**")
            
            total_n = np.array(dfplot['n'])
            chunked_sum  = np.repeat(np.sum(total_n.reshape(-1,7), axis = 1),7) # sum 
            dfplot_div = dfplot
            dfplot_div['n'] = [i/j for i,j in zip(dfplot['n'], chunked_sum)] 
            altair_plot(dfplot)   

            
        #######################################################
    st.markdown("--------------------------------------------------------------------------------------------------")
    st.subheader("**Wonach willst du noch suchen?**")
    search_query2 = st.text_input(label = "", value = "Bürokratie")             # Bürokratie
    
    if search_query2 == "":
        search_query2 = " "                                             
    speeches2 = fct_search(search_query2)
    
    df2 = build_df(speeches2)
    df2agg = df2.resample(f'{agg_slider}M').sum()
    
    m2 = None
    l2 = None
    
    if per_word:
        m2 = sum(df2['CDU/CSU'])+sum(df2['SPD'])+sum(df2['BÜNDNIS 90/DIE GRÜNEN'])+sum(df2['DIE LINKE'])+sum(df2['AfD'])+sum(df2['FDP'])+sum(df2['fraktionslos'])
        if search_query2 == ' ' or search_query2 == '':                               
            st.write(f"Der Datensatz umfasst insgesamt {m2} Wörter.")                    
        else:
            st.write(f"Der Begriff _{search_query2}_ wird {m2} mal genannt.")
    
    else:
        l2 = len(speeches2)
        if search_query2 == ' ' or search_query == '':
            st.write(f"Der Datensatz umfasst {l2} Reden.")
        else:
            st.write(f"Der Begriff _{search_query2}_ wird in {l2} verschiedenen Reden genannt.")
    
    if m2 == 0 or l2 == 0:
        pass
    else:  
        if per_word:       
            if no_fraktionslos:
                words_bal[6] = 0  
            
            df2agg_bal = df2agg*words_bal
        else:
            if no_fraktionslos:
                speeches_bal[6] = 0          
            df2agg_bal = df2agg*speeches_bal
    
    
    
        if "Reskaliert" in graph_select:
            if per_word:
                st.write("**Absolute Anzahl pro 100.000 gesprochene Wörter der Fraktionen**")
            else:
                st.write("**Absolute Anzahl pro 1000 gehaltene Reden der Fraktionen**")
        #    st.area_chart(df2agg_bal,img_width,img_height,True)
        
            dfplot = fct_dfplot(df2agg_bal)           
            altair_plot(dfplot)
    
        if "Absolut" in graph_select:

                st.write("**Absolute Anzahl**")    
            #    st.area_chart(df2agg,img_width,img_height,True)
                
                dfplot = fct_dfplot(df2agg)         
                altair_plot(dfplot)
            
        if "Anteil" in graph_select:
            st.write("**Anteil der Fraktionen an absoluter Anzahl**")
            
        #    st.area_chart(df2agg.div(df2agg.sum(axis=1), axis=0).fillna(0),img_width,img_height,True)
        
            total_n = np.array(dfplot['n'])
            chunked_sum  = np.repeat(np.sum(total_n.reshape(-1,7), axis = 1),7) # sum 
            dfplot_div = dfplot
            dfplot_div['n'] = [i/j for i,j in zip(dfplot['n'], chunked_sum)] 
            altair_plot(dfplot_div)
        
    #########################################################
    st.markdown("--------------------------------------------------------------------------------------------------")
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
            dfjagg = dfj.resample(f'{agg_slider}M').sum()
            dfjagg_bal = dfjagg*speeches_bal
            if per_word:        
                if no_fraktionslos:
                    words_bal[6] = 0                                            # weight of "Fraktionslose" is 0
                dfjagg_bal = dfjagg*words_bal
            else:
                if no_fraktionslos:
                    speeches_bal[6] = 0                                         # weight of "Fraktionslose" is 0
                dfjagg_bal = dfjagg*speeches_bal                            
    
            if "Reskaliert" in graph_select:
    
                if per_word:
                    st.write("**Absolute Anzahl pro 100.000 gesprochene Wörter der Fraktionen**")
                else:
                    st.write("**Absolute Anzahl pro 1000 gehaltene Reden der Fraktionen**")
        #        st.area_chart(dfjagg_bal,img_width,img_height,True)
        
                dfplot = fct_dfplot(dfjagg_bal)         
                altair_plot(dfplot)
                
            if "Absolut" in graph_select:
    
                    st.write("**Absolute Anzahl**")  
            #        st.area_chart(dfjagg,img_width,img_height,True)
            
                    dfplot = fct_dfplot(dfjagg)         
                    altair_plot(dfplot)                
                                        
            if "Anteil" in graph_select:       
                
                    st.write("**Anteil der Fraktionen an absoluter Anzahl**")
            #        st.area_chart(dfjagg.div(dfjagg.sum(axis=1), axis=0).fillna(0),img_width,img_height,True)
            
                    total_n = np.array(dfplot['n'])
                    chunked_sum  = np.repeat(np.sum(total_n.reshape(-1,7), axis = 1),7)     # sum
                    dfplot_div = dfplot
                    dfplot_div['n'] = [i/j for i,j in zip(dfplot['n'], chunked_sum)] 
                    altair_plot(dfplot_div)
            
    #######################
            if search_query != search_query2 :
                if sentence:     
                    loading = st.markdown("*Suche nach Aussagen läuft...*")
                    sentence_bar = st.progress(0)
                    sentence_bar_counter = 0
                    step = round((1/len(tqdm.tqdm(jointspeeches))),7) *0.999               
                    stm_list=[]

                    for speech in tqdm.tqdm(jointspeeches):                     # tqdm: progress bar
                        sentence_bar_counter += step
                        sentence_bar.progress(sentence_bar_counter)                        
                        
                        doc = nlp_de(speech["text"])                           

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
                    sentence_bar.empty()
                    
                    if len(stm_list) != 0:
                        num_stm_list = len(stm_list)
                        st.write(f'Folgende {num_stm_list} Aussagen (Sätze) beinhalten beide Suchbegriffe:') 
                        st.write(stm_list)
                        
            ##########################################################
            
            if len(jointspeeches) < 300 and show_graph == True:


                loading_graph = st.markdown("*Netzwerk wird erzeugt...*")                            
                graph_bar = st.progress(0)
                graph_bar_counter = 0                            

                def text_cosine_similarity(text1, text2):
                    
                    c1 = Counter(text1.split())                                 # 'EU-Ebene' -> one word, no comma
                    c2 = Counter(text2.split())
                    terms = set(c1).union(c2)                                  
                    dotprod = sum(c1.get(k, 0) * c2.get(k, 0) for k in terms)   # c1.get(k, 0) -> returns number of mentions (k) or 0 if words doesn't exist
                    magA = (sum(c1.get(k, 0)**2 for k in terms))**0.5
                    magB = (sum(c2.get(k, 0)**2 for k in terms))**0.5
                    
                    return dotprod / (magA * magB)                    

                def create_graph_data():                
          
                    id_list = [f'id{i}' for i in range(len(j_lemma))]
                    
                    color_map = []
                    link_list = []
                    cos_sim_list = []
                    
                    speech1_count = 0
                    speech2_count = 0
                    global graph_bar
                    global graph_bar_counter
                    step_graph_2 = 1/len(j_lemma)*0.3999
                    for speech in tqdm.tqdm(j_lemma):
                        if speech['party'] == 'AfD':
                            color_map.append('#009ee0')
                        if ('90'in speech['party']):
                            color_map.append('#46962b')
              #              st.write('Grüne')                 
                        if speech['party'] == 'CDU/CSU':
                            color_map.append('#000000')
                        if speech['party'] == 'DIE LINKE':
                            color_map.append('#800080')
                        if speech['party'] == 'FDP':
                            color_map.append('#ffed00')
                        if speech['party'] == 'SPD':
                            color_map.append('#e3000f')
                        if speech['party'] == 'fraktionslos'or speech['party'] == 'Fraktionslos' or speech['party'] == 'Bremen':
                            color_map.append('#808080')
               #         if speech['party'] != 'AfD' and  ('90'in speech['party'] == False) and speech['party'] != 'CDU/CSU' and speech['party'] != 'DIE LINKE' and speech['party'] != 'FDP' and speech['party'] != 'SPD' and speech['party'] != 'fraktionslos' :
                #            st.write('Achtung:', speech['party'])
                        
                        for speech2 in j_lemma:

                            cos_sim = text_cosine_similarity(speech['text'], speech2['text'])
                            cos_sim_list.append(cos_sim) 
                            
                            if speech2_count > speech1_count: # doppelte Links verhindern
                                if cos_sim > cos_sim_thresh:
                                    link = {'source': f'id{speech1_count}',
                                             'target': f'id{speech2_count}'
                                            }
                                    link_list.append(link)

                            speech2_count += 1
                        graph_bar_counter += step_graph_2
                        graph_bar.progress(graph_bar_counter) 
                        speech2_count = 0
                        speech1_count += 1
                    graph_bar.empty()    
                    return (id_list, color_map, link_list, cos_sim_list)
                
                def text_to_lemma_str(text):

                    doc = nlp_de(text)
                    lemma_list = []
                    for word in doc:
                        lemma_list.append((word.lemma_,word.pos_) )
                    tag_list = []
                    for i in range(len(lemma_list)):
                        if (lemma_list[i][1] == 'NOUN' or lemma_list[i][1] == 'ADJ' or lemma_list[i][1] == 'VERB'or lemma_list[i][1] == 'PROPN'):
                            tag_list.append(lemma_list[i][0])
 
                    return' '.join(tag_list)
                
                # create new list of dictionaries - solves problem with streamlit cache
                party_list = []
                text_list = []
                for speech in jointspeeches:
                    party_list.append(speech['party'])
                    text_list.append(speech['text'])

                text_list_lemma = []
                step_graph_1 = 1/len(text_list)*0.5999                
                for i in text_list:
                    text_list_lemma.append(text_to_lemma_str(i))
                    graph_bar_counter += step_graph_1
                    graph_bar.progress(graph_bar_counter) 
                
                j_lemma = [{'party': i, 'text': j} for i,j, in zip(party_list,text_list_lemma)]

                id_list, color_map, link_list, cos_sim_list = create_graph_data()

                node_list = []
                for i in range(len(id_list)):
                    dict = {'id': id_list[i],
                            'color': color_map[i]
                            }
                    node_list.append(dict)
                
                st. write(f"Schwellenwert für Kosinus-Ähnlichkeit: {cos_sim_thresh}")
                median_links = round(np.median(cos_sim_list), 4)
                st. write(f"Median der Links: {median_links}")
                std_links = round(np.std(cos_sim_list), 4)
                st. write(f"Standardabweichung der Links: {std_links}", )
                
                loading_graph.empty()
                            
                ###################
                # create HTML
                
                htmlcode = f''' <head>
                                <style> body {{margin: 0;}} </style>
                                <script src="https://unpkg.com/force-graph"></script>
                            
                                </head>
                                <body>
                                    <div id="graph"></div>
                                    <script>
                                        var data = {{'nodes': {node_list}, 
                                                    'links': {link_list}
                                        }};
                                        const elem = document.getElementById('graph');
                                        const Graph = ForceGraph()(elem).nodeLabel('id')
                                        .graphData(data)
                                
                                    </script>
                                </body>
                                
                                '''                                       
                ######################################################
                # open HTML

                f = open('speeches_graph.html','w')

                f.write(htmlcode)
                f.close()
                
                #Change path to reflect file location
                
                filename = 'file:///'+os.getcwd()+'/' + 'speeches_graph.html'   # works for local host
             #   filename = 'speeches_graph.html'                                   
              #  filename = '/app/speeches_graph.html'                          # non of these work for Heroku
                webbrowser.open_new_tab(filename)  
                st.write("**Lemmatisierte Reden:**")
                st.write(j_lemma)
                            
########################################################################################################################################
########################################################################################################################################
########################################################################################################################################

if language == "English (UK)":
    
    hints = st.sidebar.checkbox("Show hints", value = False)
    
    if hints:
        st.sidebar.info("Upper and lower case letters are distinguished." )
        st.sidebar.markdown(" *e.g.: 'United Kingdom' does not contain 'united'*")
        st.sidebar.info("The search term is also searched within single words.")
        st.sidebar.markdown(" *e.g.: 'United Kingdom' contains 'it' and 'do'*")
        st.sidebar.info("The search within individual words can be avoided by placing a space before and/or after the search term.")
        st.sidebar.markdown(" *e.g.: 'United Kingdom' contains '<space>King', but not 'King<space>'*")    
        
       # st.sidebar.info(f"*(The dataset currently contains around 7 million words - frequently used search terms can lead to a somewhat longer calculation time.)*")
    
    per_word = False
    sentence = True
    agg_slider = 3
    advanced = st.sidebar.checkbox("Advanced search")
    graph_select = ['rescaled']
    if advanced:
        st.sidebar.markdown("---------------------")
        
        graph_select = st.sidebar.multiselect("Graphs:", ['rescaled','absolute number','share'])
        per_word = st.sidebar.checkbox("Number of mentions of the search term instead of number of speeches (multiple mentions of the search term within a speech are counted)")
    
        sentence = st.sidebar.checkbox("List statements (sentences) that contain both search terms", value = False)
        agg_slider = st.sidebar.slider("Daten über x Monate aggregieren", 1, 12, 3)     # min, max, default    
    ##############################

    st.markdown('<p style="font-size: 30pt; font-weight: bold; color: white; \
        background-color: #000">&nbsp;\
        <a >Who says what in parliament?</a>\
        </p>', unsafe_allow_html=True)
    

       ##################### 
    @st.cache(suppress_st_warning=True, show_spinner=False)
    def laden_uk():
        all_speeches_uk = []
        loading_data = st.markdown("** *Data set is being loaded...* **")
        json = {'search_query': '', 
                'dataset_name':'gbr', 
                'start_date':'2018-8-1', 
                'end_date':'2019-1-1'}
        result = requests.get('https://penelope.vub.be/parliament-data/get-speeches/gbr/2016-01-01/2021-01-01/%20/1000000000000')
    

        for speech in result.json()["speeches"]:
            all_speeches_uk.append(speech)
  
        # code to sort list on date 
        all_speeches_uk.sort(key = lambda x:x['date'])
        
        loading_data.empty()
        
        return all_speeches_uk
    
    ##################### 
    
    def fct_search(such_term):
        speeches = []
        for speech in all_speeches_uk:
            if such_term in speech['text'] :
                speeches.append(speech)
        speeches.sort(key = lambda x:x['date']) 
        return speeches
    
    #####################
    
    def build_df(speeches_arg):
    
        if per_word:
            parties = []
            conservative = []
            labour = []
            liberal = []
            scottish = []
            dup = []
            none = []
            speaker = []
            dates = []   
            
            if speeches_arg == speeches:
                such_term = search_query
                
            elif speeches_arg == speeches2:
                such_term = search_query2    
            else:
                st.write("wrong data set")
                such_term = ""    
    # "conservative" "labour" "liberal-democrat" "scottish-national-party"  "dup" "None"  "speaker" ## "labourco-operative"  
            for speech in speeches_arg:
                parties.append(speech['party'])
                dates.append(speech['date'])
                if (speech['party'] == 'conservative'):
                    conservative.append(speech['text'].count(such_term)) 
                else: 
                    conservative.append(0)
                if (speech['party'] == 'labour'):
                    labour.append(speech['text'].count(such_term))
                else: 
                    labour.append(0)
                if (speech['party'] == 'liberal-democrat'):                   
                    liberal.append(speech['text'].count(such_term))
                else: 
                    liberal.append(0)    
                if (speech['party'] == 'scottish-national-party'):
                    scottish.append(speech['text'].count(such_term))
                else: 
                    scottish.append(0)     
                if (speech['party'] == 'dup'):
                    dup.append(speech['text'].count(such_term))
                else: 
                    dup.append(0)
                if (speech['party'] == 'None'):
                    none.append(speech['text'].count(such_term))
                else: 
                    none.append(0)               
                if (speech['party'] == 'speaker'):
                    speaker.append(speech['text'].count(such_term))
                else: 
                    speaker.append(0)
      #          if speech['party'] != 'CDU/CSU' and speech['party'] != 'SPD' and speech['party'] != 'AfD' and speech['party'] != 'FDP' and speech['party'] != 'BÜNDNIS 90/DIE GRÜNEN' and speech['party'] != 'Bündnis 90/Die Grünen' and speech['party'] != 'DIE LINKE' and speech['party'] != 'fraktionslos' and speech['party'] != 'Fraktionslos' and speech['party'] != 'Bremen':
       #             st.write(speech['party'])
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
            df['conservative'] = conservative
            df['labour'] = labour
            df['liberal-democrat'] = liberal
            df['scottish-national-party'] = scottish
            df['dup'] = dup
            df['None'] = none
            df['speaker'] = speaker
    
            return df        
        
        else:
            
            parties = []
            conservative = []
            labour = []
            liberal = []
            scottish = []
            dup = []
            none = []
            speaker = []
            dates = []  
            
            for speech in speeches_arg:
           
                parties.append(speech['party'])
                dates.append(speech['date'])
                if (speech['party'] == 'conservative'):
                    conservative.append(1)
                else: 
                    conservative.append(0)
                if (speech['party'] == 'labour'):
                    labour.append(1)
                else: 
                    labour.append(0)
                if (speech['party'] == 'liberal-democrat'):                                       # if (speech['party'] == 'BÜNDNIS 90/DIE GRÜNEN' or speech['party'] == 'Bündnis 90/Die Grünen'):
                    liberal.append(1)
                else: 
                    liberal.append(0)    
                if (speech['party'] == 'scottish-national-party'):
                    scottish.append(1)
                else: 
                    scottish.append(0)     
                if (speech['party'] == 'dup'):
                    dup.append(1)
                else: 
                    dup.append(0)
                if (speech['party'] == 'None'):
                    none.append(1)
                else: 
                    none.append(0)               
                if (speech['party'] == 'speaker'):
                    speaker.append(1)
                else: 
                    speaker.append(0)
         #       if speech['party'] != 'conservative' and speech['party'] != 'labour' and speech['party'] != 'liberal-democrat' and speech['party'] != 'scottish-national-party' and speech['party'] != 'dup' and speech['party'] != 'None' and speech['party'] != 'speaker' :
           #         st.write(speech['party'])
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
            df['conservative'] = conservative
            df['labour'] = labour
            df['liberal-democrat'] = liberal
            df['scottish-national-party'] = scottish
            df['dup'] = dup
            df['None'] = none
            df['speaker'] = speaker
        
            return df
        
    #####################
    
    def count_words(speeches):
    
        num_words_party = [0,0,0,0,0,0,0]
        for speech in speeches:
            if (speech['party'] == 'conservative'):
                num_words_party[0] += len(speech['text'].split())
            elif (speech['party'] == 'labour'):
                num_words_party[1] += len(speech['text'].split())
            elif (speech['party'] == 'liberal-democrat'):                                              
                num_words_party[2] += len(speech['text'].split()) 
            elif (speech['party'] == 'scottish-national-party'):
                num_words_party[3] += len(speech['text'].split())  
            elif (speech['party'] == 'dup'):
                num_words_party[4] += len(speech['text'].split())
            elif (speech['party'] == 'None'):
                num_words_party[5] += len(speech['text'].split())
            elif (speech['party'] == 'speaker'):
                num_words_party[6] += len(speech['text'].split())           
        return num_words_party
        
    #####################
    
    def count_speeches(speeches):
 
        num_speeches_party = [0,0,0,0,0,0,0]
            
        for speech in speeches:
            if (speech['party'] == 'conservative'):
                num_speeches_party[0] += 1
            elif (speech['party'] == 'labour'):
                num_speeches_party[1] += 1
            elif (speech['party'] == 'liberal-democrat'):                                          # (speech['party'] == 'BÜNDNIS 90/DIE GRÜNEN' or speech['party'] == 'Bündnis 90/Die Grünen' or speech['party'] == 'BUENDNIS 90/DIE GRUENEN'):
                num_speeches_party[2] += 1
            elif (speech['party'] == 'scottish-national-party'):
                num_speeches_party[3] += 1
            elif (speech['party'] == 'dup'):
                num_speeches_party[4] += 1
            elif (speech['party'] == 'None'):
                num_speeches_party[5] += 1
            elif (speech['party'] == 'speaker'):
                num_speeches_party[6] += 1     
        return num_speeches_party
    
    ######################### 
    
    def fct_dfplot(dfagg):  
      
        date = []
        party = []                                                           #df['CDU/CSU']+df['SPD']+df['BÜNDNIS 90/DIE GRÜNEN']+df['DIE LINKE']+df['AfD']+df['FDP']+df['fraktionslos']
        num = []
        
        dfagg = dfagg.reset_index()
        
    #    st.write("dfagg:",dfagg)
        
        for i in dfagg.index:
            date.extend([dfagg['datetime'][i]] * 7)      

            party.append('conservative')
            party.append('labour')
            party.append('liberal-democrat')    
            party.append('scottish-national-party')
            party.append('dup')
            party.append('None')
            party.append('speaker')
    
            num.append(dfagg['conservative'][i])
            num.append(dfagg['labour'][i])
            num.append(dfagg['liberal-democrat'][i])
            num.append(dfagg['scottish-national-party'][i])
            num.append(dfagg['dup'][i])
            num.append(dfagg['None'][i])
            num.append(dfagg['speaker'][i])
    
        dfplot = pd.DataFrame()
        dfplot['date'] = date
        dfplot.index = dfplot['date']
        dfplot['party'] = party
        dfplot['n'] = num
        
    #    st.write(dfplot)
    
        return dfplot
    
    ##########################
    
    def altair_plot(dfplot):
    
        data = alt.Chart(dfplot).mark_area(opacity = 0.7).encode(
                x= 'date',
                y= 'n',                    
                color= alt.Color('party', scale=alt.Scale(domain=domain, range=color_codes_party)),
                tooltip = ['date', 'n', 'party']
                ).properties(width = img_width, height = img_height*1.2)   
        st.altair_chart(data, use_container_width=True)
    
    ##########################
        
    all_speeches_uk = laden_uk()
    #st.write("number of all speeches:", len(all_speeches) , "type:", type(all_speeches), "size in bytes:" ,sys.getsizeof(all_speeches), "first elements:", all_speeches[:2])      # alle 11990 Reden
    
    
    num_words_party = count_words(all_speeches_uk)
    num_words_all = sum(num_words_party)
    # Gewichtung: Nennung pro 100.000 Wörter
    words_bal = [i/j for i,j in zip([100000 for i in range(7)],num_words_party)]    
    
    num_speeches_party = count_speeches(all_speeches_uk)
    # Gewichtung: Nennung pro 1000 Reden
    speeches_bal = [i/j for i,j in zip([1000 for i in range(7)],num_speeches_party)]

    no_fraktionslos = st.checkbox("exclude parties with 5 or less seats ", value = False)
    st.markdown("--------------------------------------------------------------------------------------------------")        
    #st.write("bytes speeches_uk:", sys.getsizeof(all_speeches_uk))    
    st.subheader(" **First search term **")
    
    search_query = st.text_input(label = "", value = "Merkel" )                                             
    if search_query == "":
        search_query = " "    
    
    speeches = []
    speeches = fct_search(search_query)
    
    #########################
    
    df = build_df(speeches)
    #st.write(df)
    dfagg = df.resample(f'{agg_slider}M').sum()
    
    ##########################
    
    m = None
    l = None

    if per_word:
        m = sum(df['conservative'])+sum(df['labour'])+sum(df['liberal-democrat'])+sum(df['scottish-national-party'])+sum(df['dup'])+sum(df['None'])+sum(df['speaker'])
        if search_query == ' ' or search_query == '':                               
            st.write(f"The data set contains {num_words_all:,} words.")
        else:
            st.write(f"The search term _{search_query}_ is mentioned {m} times.")
    
    else:
        l = len(speeches)
        if search_query == ' ' or search_query == '':
            st.write(f"The data set contains {l} speeches.")
        else:
            st.write(f"The search term _{search_query}_ is mentioned in {l} different speeches.")
            
    #####################
    
    # colors for plotting
    domain = ["conservative", "labour", "liberal-democrat", "scottish-national-party",  "dup", "None",  "speaker"]
    color_codes_party = [" #3498db"," #e74c3c "," #f39c12 ","#ffed00"," #922b21 ", "#808080","#000000" ] # color codes parties
    
    
    if m == 0 or l == 0:
        pass
    else:
        if per_word:        
            if no_fraktionslos:
                words_bal[6] = 0                                                    # Fraktionslosen keine Gewichtung zuweisen
            dfagg_bal = dfagg*words_bal
        else:
            if no_fraktionslos:
                speeches_bal[6] = 0                                                 # Fraktionslosen keine Gewichtung zuweisen
            dfagg_bal = dfagg*speeches_bal                            
    
    
        if "rescaled" in graph_select:
            if per_word:
                st.write("**Absolute number per 100,000 spoken words of the party**")
            else:
                st.write("**Absolute number per 1000 speeches given by the party**")
        
          
        
            dfplot = fct_dfplot(dfagg_bal)           
            altair_plot(dfplot)
        

    
    
        if "absolute number" in graph_select:
    
        
            st.write("**Absolute number**")
          
    
        
            dfplot = fct_dfplot(dfagg)         
            altair_plot(dfplot)
        
    
        if "share" in graph_select:
            st.write("**Share of the party**")
        
    
            
            total_n = np.array(dfplot['n'])
            chunked_sum  = np.repeat(np.sum(total_n.reshape(-1,7), axis = 1),7)                              # summiert 
            dfplot_div = dfplot
            dfplot_div['n'] = [i/j for i,j in zip(dfplot['n'], chunked_sum)] 
            altair_plot(dfplot)   
        
    
            
        #######################################################
    st.markdown("--------------------------------------------------------------------------------------------------")
    st.subheader("**Second search term**")
    search_query2 = st.text_input(label = "", value = "Macron")
    
    if search_query2 == "":
        search_query2 = " "                                             
    speeches2 = fct_search(search_query2)
    
    df2 = build_df(speeches2)
    df2agg = df2.resample(f'{agg_slider}M').sum()
    
    m2 = None
    l2 = None
    
    if per_word:
        m2 = sum(df2['conservative'])+sum(df2['labour'])+sum(df2['liberal-democrat'])+sum(df2['scottish-national-party'])+sum(df2['dup'])+sum(df2['None'])+sum(df2['speaker'])
        if search_query2 == ' ' or search_query2 == '':                               
            st.write(f"The data set contains {m2} words.")                    
        else:
            st.write(f"The search term _{search_query2}_ is mentioned {m2} times.")
    
    else:
        l2 = len(speeches2)
        if search_query2 == ' ' or search_query == '':
            st.write(f"The data set contains {l2} speeches.")
        else:
            st.write(f"The search term _{search_query2}_ is mentioned in {l2} different speeches.")
    
    if m2 == 0 or l2 == 0:
        pass
    else:  
        if per_word:       
            if no_fraktionslos:
                words_bal[6] = 0  
            
            df2agg_bal = df2agg*words_bal
        else:
            if no_fraktionslos:
                speeches_bal[6] = 0          
            df2agg_bal = df2agg*speeches_bal
    
    
    
        if "rescaled" in graph_select:
            if per_word:
                st.write("**Absolute number per 100,000 spoken words of the party**")
            else:
                st.write("**Absolute number per 1000 speeches given by the party**")
        #    st.area_chart(df2agg_bal,img_width,img_height,True)
        
            dfplot = fct_dfplot(df2agg_bal)           
            altair_plot(dfplot)
        
        
    
    
        if "absolute number" in graph_select:
    
    
    
            st.write("**Absolute number**")    
        #    st.area_chart(df2agg,img_width,img_height,True)
            
            dfplot = fct_dfplot(df2agg)         
            altair_plot(dfplot)
        
    
        if "share" in graph_select:
            st.write("**Share of the party**")
            
        #    st.area_chart(df2agg.div(df2agg.sum(axis=1), axis=0).fillna(0),img_width,img_height,True)
        
            total_n = np.array(dfplot['n'])
            chunked_sum  = np.repeat(np.sum(total_n.reshape(-1,7), axis = 1),7)         # summiert 
            dfplot_div = dfplot
            dfplot_div['n'] = [i/j for i,j in zip(dfplot['n'], chunked_sum)] 
            altair_plot(dfplot_div)
        
    
        
    #########################################################
    st.markdown("--------------------------------------------------------------------------------------------------")
    st.subheader("**The relation**")
    
    #st.write(speeches)
    
    if per_word:
        st.write("*The relation is not calculated for number of mentions*")
    else:
        jointspeeches=[]
        for speech in speeches:
            if search_query in speech['text'] and search_query2 in speech['text']:
                jointspeeches.append(speech)
        #st.write(jointspeeches)
        ljoint = len(jointspeeches)
    
        
        if ljoint == 0:
            st.write(f"There are no speeches that contain both _{search_query}_ and _{search_query2}_.")
        else:
            st.write(f"There are {ljoint} speeches that contain both _{search_query}_ and _{search_query2}_.")
            dfj = build_df(jointspeeches)
            dfjagg = dfj.resample(f'{agg_slider}M').sum()
            dfjagg_bal = dfjagg*speeches_bal
    
            if per_word:        
                if no_fraktionslos:
                    words_bal[6] = 0                                                    # Fraktionslosen keine Gewichtung zuweisen
                dfjagg_bal = dfjagg*words_bal
            else:
                if no_fraktionslos:
                    speeches_bal[6] = 0                                                 # Fraktionslosen keine Gewichtung zuweisen
                dfjagg_bal = dfjagg*speeches_bal                            
    
    
    
    
    
    
            if "rescaled" in graph_select:
                if per_word:
                    st.write("**Absolute number per 100,000 spoken words of the party**")
                else:
                    st.write("**Absolute number per 1000 speeches given by the party**")
        #        st.area_chart(dfjagg_bal,img_width,img_height,True)
        
                dfplot = fct_dfplot(dfjagg_bal)         
                altair_plot(dfplot)
                
         #       st.write(jointspeeches)
        
        
    
            
            if "absolute number" in graph_select:
    
                
                st.write("**Absolute number**")  
        #        st.area_chart(dfjagg,img_width,img_height,True)
        
                dfplot = fct_dfplot(dfjagg)         
                altair_plot(dfplot)                
                
                
            if "share" in graph_select:    
                st.write("**Share of the party**")
        #        st.area_chart(dfjagg.div(dfjagg.sum(axis=1), axis=0).fillna(0),img_width,img_height,True)
        
                total_n = np.array(dfplot['n'])
                chunked_sum  = np.repeat(np.sum(total_n.reshape(-1,7), axis = 1),7)     # summiert 
                dfplot_div = dfplot
                dfplot_div['n'] = [i/j for i,j in zip(dfplot['n'], chunked_sum)] 
                altair_plot(dfplot_div)
        
    
    
    #######################
            if search_query != search_query2 :
                if sentence:     
                    loading = st.markdown("*Searching for statements...*")
                    sentence_bar = st.progress(0)
                    sentence_bar_counter = 0
                    step = round((1/len(tqdm.tqdm(jointspeeches))),7) *0.999                         
                    stm_list=[]
                    for speech in tqdm.tqdm(jointspeeches):
                        sentence_bar_counter += step
                        sentence_bar.progress(sentence_bar_counter)                                
                        doc = nlp_de(speech["text"])                                       # npl() natural language processing
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
                    sentence_bar.empty()
                    if len(stm_list) != 0:
                        num_stm_list = len(stm_list)
                        st.write(f'The following {num_stm_list} statements (sentences) contain both search terms:') 
                        st.write(stm_list)
                    else:
                        st.write("There are no statements (sentences) that contain both search terms.")                            