######### StatementGraphs.py
# Author: Sven Banisch
# Last Change: 14.11.2019 by Armin Pournaki

import collections
import json
import tqdm as tqdm
import spacy

# see devStatementGraph and devPaperPipeline for development and documentation
def StatementGraphGenerator(inParams):

    stm_list = inParams['data']
    
    if inParams['language'] == 'en':
        nlp = spacy.load('en_core_web_sm') #load english spacy model
    elif inParams['language'] == 'de':
        nlp = spacy.load('de_core_news_sm') #load german spacy model
    elif inParams['language'] == 'fr':
        nlp = spacy.load('fr_core_news_sm') #load french spacy model
    elif inParams['language'] == 'es':
        nlp = spacy.load('es_core_news_sm') #load spanish spacy model
    elif inParams['language'] == 'pt':
        nlp = spacy.load('pt_core_news_sm') #load portuguese spacy model
    elif inParams['language'] == 'it':
        nlp = spacy.load('it_core_news_sm') #load italian spacy model
    elif inParams['language'] == 'nl':
        nlp = spacy.load('nl_core_news_sm') #load dutch spacy model
    elif inParams['language'] == 'el':
        nlp = spacy.load('el_core_news_sm') #load greek spacy model
    elif inParams['language'] == 'nb':
        nlp = spacy.load('nb_core_news_sm') #load norwegian bokmal spacy model
    elif inParams['language'] == 'lt':
        nlp = spacy.load('lt_core_news_sm') #load lithuanian spacy model
    elif inParams['language'] == 'xx':
        nlp = spacy.load('xx_ent_wiki_sm') #load multi-language spacy model

    else:
        print('ERROR! Language not supported!')
        
    relevantPOS = inParams['pos']
    ignoreLEM = inParams['ignore']
    
    # 1.2.2 Note: requires spacy and language model to be loaded
    print('apply nlp pipeline')
    for value in tqdm.tqdm(stm_list):
        doc = nlp(value['text'])
        value.update({'doc' : doc})
    
    # 1.2.3
    # Data cleaning options
    print('filter words')
    #relevantPOS = ['NOUN','VERB','ADJ']
    #ignoreLEM = ['Herr','Kollege','Dame','Frau','Präsident']
    #ignoreLEM = []

    stm_list_nlp = []
    statements_lemma_list = []
    #statements_pos_list = []
    for stm in tqdm.tqdm(stm_list):
        lemmas = []
        pos = []
        for token in stm['doc']:
            if token.is_punct is not True and token.is_stop is not True and token.pos_ in relevantPOS and token.lemma_ not in ignoreLEM:
                lemmas.append(token.lemma_)
                pos.append(token.pos_)
        stm.update({'lemmata' : lemmas})    
        statements_lemma_list.append(lemmas)
        #statements_pos_list.append(pos)

    # 1.2.4
    print('count and order lemmata')
    flattened = [val for lemmas in statements_lemma_list for val in lemmas]
    lemma_frequency_list = collections.Counter(flattened).most_common()
    all_lemmata_list = [ i[0] for i in lemma_frequency_list ]
    all_lemmata_count = [ i[1] for i in lemma_frequency_list ]

    # remove single items
    # 1.2.5
    print('remove singles')
    all_freq_lemmata_list = [ all_lemmata_list[i] for i,v in enumerate(all_lemmata_list) if (all_lemmata_count[i] > 1) ]
    all_freq_lemmata_count = [ all_lemmata_count[i] for i,v in enumerate(all_lemmata_count) if (all_lemmata_count[i] > 1) ]
        
    all_lemmata_list = all_freq_lemmata_list
    all_lemmata_count = all_freq_lemmata_count 

    # Construct word browsable dict for later use in semantic relatedness computation
    wordscounts_dict = {}
    for lx,lem in enumerate(all_lemmata_list):
        wordscounts_dict.update({ lem : all_lemmata_count[lx] })
 
    # From this file
    stmnet_dict = {
        'graph' : {
        'directed' : 'false',
        'type'  : 'statement_graph',
        'nodes' : [],
        'links' : []
        }    
    }

    for ix,stm in enumerate(stm_list):
        if len(stm['lemmata']) > 0:
            node_dict = {
                'id' : ix+1
            }
            for ele in stm:
                if ele != 'lemmata' and ele != 'doc':
                    node_dict.update({ele : stm[ele]})
            
            mfic = [ lem for lem in all_lemmata_list if (lem in stm['lemmata'] )]
            #freqI = collections.Counter(stmI).most_common()
            #lemmataI = [ i[0] for i in freqI ]
            if len(mfic)>0:
                node_dict.update({'mfic' : mfic[0]})
            else:
                node_dict.update({'mfic' : ' '})
    
            stmnet_dict['graph']['nodes'].append(node_dict)
    
    
    #stmnet_dict['graph']['edges'] = []
    for nodeI in tqdm.tqdm(stmnet_dict['graph']['nodes']):
        stmI = stm_list[ nodeI['id']-1 ]['lemmata']
        for nodeJ in stmnet_dict['graph']['nodes']:     
            if nodeI['id'] < nodeJ['id']:
                stmJ = stm_list[ nodeJ['id']-1 ]['lemmata']
                overlap = [ lem for lem in set(stmI) if (lem in set(stmJ))]  # set overlap
                if (len(overlap) > 0):
                    edge_dict = {
                        'source' : nodeI['id'],
                        'target' : nodeJ['id'],
                        'weight' : len(overlap)
                        }
                    stmnet_dict['graph']['links'].append(edge_dict)
    
    return stmnet_dict


