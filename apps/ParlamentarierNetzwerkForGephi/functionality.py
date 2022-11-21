import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
import networkx as nx
import tqdm


# processes the data with spacy and adds POS as well as lemmatized words in a list
def get_processed_speeches(reden, nlp):
    new_reden = []
    for rx, rede in tqdm.tqdm(enumerate(reden)):
        doc = nlp(rede["text"])
        text_lem = []
        text_pos = []
        for token in doc:
            text_lem.append(token.lemma_)
            text_pos.append(token.pos_)
        rede.update({'text_lem': text_lem})
        rede.update({'text_pos': text_pos})
        new_reden.append(rede)
    return new_reden

# saves the graph to the current dictionary
def save_gephi_graph(graph, fileName):
    nx.write_gexf(graph, f"{fileName}.gexf")


# restructures the graph, so that it can easily be opened in gephi. Currently not very general, but can and should be possible
def reorganize_to_gephi_structure(graph):
    graphforgephi = nx.Graph()
    for node in graph['nodes']:
        graphforgephi.add_node(node['id'], name=node['name'], party=node['party'], msw=node['maxTFIDF'],
                               nReden=node['nReden'], nWorte=node['nWorte'])

    for link in graph['links']:
        if link['weight'] >= 0.25:
            graphforgephi.add_edge(link['source'], link['target'], weight=link['weight'], community=0)

    return graphforgephi


# creates a graph out of the list of dicts. Each dicts becomes a node.
# The weight of the edges is read from the corresponding similarity matrix
def cotop_graph_erstellen(parlamentarier, min_weight, similarity):

    graph = {
        'directed': False,
        'graph': 'semant_graph',
        'links': [],
        'nodes': parlamentarier,
    }

    for ix, nodeI in enumerate(graph['nodes']):
        for jx, nodeJ in enumerate(graph['nodes']):
            if nodeI['id'] < nodeJ['id']:
                source = nodeI['id']
                target = nodeJ['id']
                # weight = cos_sim(nodeI['vec_numbers'], nodeJ['vec_numbers'])
                # r = np.corrcoef(nodeI['vec_numbers'], nodeJ['vec_numbers'])
                # weight = r[0,1]
                weight = similarity[ix, jx]
                if weight > min_weight:
                    link_dict = {
                        'source': source,
                        'target': target,
                        'weight': weight
                    }
                    graph['links'].append(link_dict)
    return graph


# creates a list of dicts. Each dict contains the following elements:
# - index
# - name
# - no of held speeches
# - lemmatized text from all the speeches the parliament member held
# - vec_number: vector that includes the tf_idf score for each word
# - msw: word that has the highest tf-idf Score in vec_number
def liste_von_parla_mit_dict_vec(reden, parlamentarier, X_csr, vectorizer):
    parlamentarier_vec = []

    for count, parla in enumerate(parlamentarier):
        hilf = {
            'id': count + 1,
            'name': parla['name'],
            'party': parla['party'],
            'nReden': parla['nReden'],
            'nWorte': parla['nWorte'],
            'text': parla['text_lem']
        }

        vec_numbers = np.array(X_csr.getrow(count).toarray()[0])

        maxWX = np.argmax(vec_numbers)

        # vec_numbers = vec_numbers/np.linalg.norm(vec_numbers)

        hilf.update({'vec_numbers': vec_numbers})
        msw = list(vectorizer.vocabulary_.keys())[list(vectorizer.vocabulary_.values()).index(np.argmax(vec_numbers))]
        hilf.update({'maxTFIDF': msw})

        parlamentarier_vec.append(hilf)

    return parlamentarier_vec


# calculates the tf-idf score for each word said by a parliament member.
# Further information can be found in german:
#
# Erstellt eine Matrix, welche als Zeilen die einzelnen Parlamentarier enthält. Die Zeilen sind gegeben durch die von allen Rednern gesagten Worte. Die einzelnen Eniträge sind die tf-idf Gewichte des von einem Parlamentarier gesagten Wortes. Die Berechnung der tfidf erfolgt folgerndermaßen:
# tf-idf(t, d) = tf(t, d) * idf(t)
# tf(t,d) = termfrequency des Terms t im Dokument d
# idf(t,d) = log [ (1 + n) / (1 + df(t)) ] + 1 inverse
# wobei df(t) die document frequency eines Wortes ist, also in wie vielen Worten eine Dokument vorkommt
def get_tfidf_scores(parlamentarier):
    corpus = [parla['text_lem'] for parla in parlamentarier]
    vectorizer = TfidfVectorizer(max_df=0.8, min_df=(2 / 781))
    tf_idf_matrix = vectorizer.fit_transform(corpus)
    return tf_idf_matrix, vectorizer


# collects all texts spoken by the respective speaker, as well as other statistics
def get_text_clean(speaker, reden):
    text = ''
    nReden = 0
    nWorte = 0
    for rede in reden:
        if rede['name'] == speaker:
            nReden += 1
            nWorte += len(rede['text_lem'])
            text += ' '.join(rede['text_lem'])
    return text, nReden, nWorte


# creates a list of dictionaries, where each dictionary corresponds to a parliamant member and
# includes the persons name, party, text, no_speeches etc.
def liste_von_parla_mit_dict_text(reden, names, parties):
    parlamentarier = []

    for count, name in enumerate(names):
        hilf = {
            'id': count + 1,
            'name': names[count],
            'party': parties[count]
        }

        text, nReden, nWorte = get_text_clean(name, reden)

        hilf.update({'text_lem': text, 'nReden': nReden, 'nWorte': nWorte})

        parlamentarier.append(hilf)

    return parlamentarier


# gets the unique names and the unique partie names form all the speeches
def get_names_and_parties(reden_clean):
    names = []
    parties = []
    for rede in reden_clean:
        if rede['name'] not in names:
            names.append(rede['name'])
            parties.append(rede['party'])
    return names, parties


# filters a speech, so that only the wanted parts of speeches are returned. The argument can be a list if multiple POS
# are of interest. Another variable is the to be filtered speech. It has to be preprocessed,
# so that the POS for each word is known.
def filter_for_POS(consider, rede):
    rel_lemmata = [ele for ex, ele in enumerate(rede['text_lem']) if rede['text_pos'][ex] in consider]
    rede['text_lem'] = rel_lemmata
    rede['text_pos'] = [ele for ele in rede['text_pos'] if ele in consider]


# removes the wrongly entered names, so the same person does not count as two persons
# this function is unnecessary, when we use the list of parliament members with their respective id's
def clean_data_of_spelling_mistakes(Reden):

    for rede in Reden:
        rede['party'] = rede['party'].replace(u'\xa0', u' ')
        if rede['party'] == 'Bündnis 90/Die Grünen':
            rede['party'] = 'BÜNDNIS 90/DIE GRÜNEN'
        if rede['party'] == 'Fraktionslos':
            rede['party'] = 'fraktionslos'

        if rede['name'] == 'Albert H. Weiler':
            rede['name'] = 'Albert Weiler'
        if rede['name'] == 'Eva-Maria Elisabeth Schreiber':
            rede['name'] = 'Eva-Maria Schreiber'
        if rede['name'] == 'Heidrun Bluhm-Förster':
            rede['name'] = 'Heidrun Bluhm'
        if rede['name'] == ' in der Beek':
            rede['name'] = 'Olaf in der Beek'
        if rede['name'] == ' ':
            rede['name'] = 'Unbekannt'
        if rede['name'] == 'Eberhardt Alexander Gauland':
            rede['name'] = 'Alexander Gauland'
        if rede['name'] == 'Joana Eleonora Cotar':
            rede['name'] = 'Joana Cotar'
        if rede['name'] == 'Wolfgang Schäuble':
            rede['name'] = 'Dr. Wolfgang Schäuble'
        if rede['name'] == 'Thomas de Maizière':
            rede['name'] = 'Thomas Maizière'
        if rede['name'] == 'Alterspräsident Dr. Hermann Otto Solms':
            rede['name'] = 'Hermann Otto Solms'
        if rede['name'] == 'Konstantin Elias Kuhle':
            rede['name'] = 'Konstantin Kuhle'
        if rede['name'] == 'Konstantin Elias Kuhle':
            rede['name'] = 'Konstantin Kuhle'
        if rede['name'] == 'Elvan Korkmaz':
            rede['name'] = 'Elvan Korkmaz-Emre'
