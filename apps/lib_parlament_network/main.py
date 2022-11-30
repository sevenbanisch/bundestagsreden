import sys
import functionality as fnct
import jsonlines
import json


# executed method if main.py is called. Takes the name of the list od speeches as a variable and wether or not it
# is already preprocessed
def exec():

    period = input('Select legislative period (19 or 20): ')
    isPreprocessed = 'y'#input('Is the preprocessed data available? (y or n): ')

    if isPreprocessed == 'y':
        isPreprocessed = True
    else:
        isPreprocessed = False
    
    DATAPATH = '../../data/'
    path = DATAPATH + f"speeches_{period}_preprocessed.json"
    #print(path)

    if isPreprocessed == 'False':
        print("Loading Spacy")

        import spacy

        nlp = spacy.load('de_core_news_sm')  # load spacy model

        import nltk
        nltk.download('punkt')

        print("Opening not yet processed json-file named " + path)
        data = []
        with jsonlines.open(path) as f:
            for line in f.iter():
                data.append(line)

        alleReden = data.copy()
        print(len(alleReden))
        alleReden.sort(key=lambda x: x['date'])

        print("Processing and cleaning the speeches")
        alleReden = fnct.get_processed_speeches(alleReden, nlp)

        fnct.clean_data_of_spelling_mistakes(alleReden)

        print("Saving processed Speeches")
        with open('speeches_preprocessed.json', 'w') as fp:
            json.dump(alleReden, fp, sort_keys=True, indent=4)

        path = DATAPATH + f'speeches_{period}_preprocessed.json'

    print("Opening json-file named " + path)
    with open(path, 'r') as fp:
        data = json.load(fp)
        #data = list(fp)

    #originaldata = []
    #for line in data:
    #    originaldata.append(json.loads(line))
    
    fp.close()

    #with open(path, 'r') as json_file:
    #    data = list(json_file)

    
    alleReden = data.copy()
    print("Opening complete. Now further processing the data")

    # the kept POS. can be changed if wanted
    consider = ['NOUN']
    for rede in alleReden:
        fnct.filter_for_POS(consider, rede)

    names, parties = fnct.get_names_and_parties(alleReden)

    parlamentarier = fnct.liste_von_parla_mit_dict_text(alleReden, names, parties)

    print("Now calculating the weight of the edges")
    tf_idf_matrix, vectorizer = fnct.get_tfidf_scores(parlamentarier)

    parlamentarier_vec = fnct.liste_von_parla_mit_dict_vec(alleReden, parlamentarier, tf_idf_matrix.copy(), vectorizer)

    # calculated the cosine similarity for each pair of parliament members
    pairwise_similarity = tf_idf_matrix * tf_idf_matrix.T
    similarity = pairwise_similarity.toarray()

    print("Creating the graph")
    graph = fnct.cotop_graph_erstellen(parlamentarier_vec, 0.25, similarity)

    graph_for_gephi = fnct.reorganize_to_gephi_structure(graph)

    print("Saving the graph")
    fnct.save_gephi_graph(graph_for_gephi, f"graph_for_gephi_{period}")
    print("Saving complete. The graph can now be used in Gephi")


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    exec()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
