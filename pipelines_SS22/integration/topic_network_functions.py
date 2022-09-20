# look up in Sven/kommentare.ipynb, Sven/xTopicModel.ipynb & Julians notebook
import json
import os.path
import pickle
from typing import List, Any

import spacy
import tqdm
from sklearn.decomposition import NMF
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import normalize


def get_speeches():
    with open('../../data/speeches_20.jsonl', 'r', encoding='utf8') as fp:
        return [json.loads(line) for line in list(fp)]


def group_speeches_by_discussion_title(speeches):
    grouped_speeches = {}
    for speech in speeches:
        tpo = speech['discussion_title']
        if tpo in grouped_speeches:
            grouped_speeches[tpo].append(speech)
        else:
            grouped_speeches[tpo] = [speech]

    return grouped_speeches


def get_corpus(tops):
    corpus = []

    for top in tops.values():
        aggregate = [speech['text'] for speech in top]
        corpus.append(' '.join(aggregate))

    return corpus


def corpus_by_POS(corpus, consider) -> List[str]:
    nlp = spacy.load('de_core_news_sm')
    groups = []

    groups_file_name = 'groups.pickle'
    if os.path.exists(groups_file_name):
        with open(groups_file_name, 'rb') as f:
            groups = pickle.load(f)
            print(f'found "{groups_file_name}" containing the groups')
    else:
        print(f"didn't find '{groups_file_name}' file. Generating groups now.")
        for row in tqdm.tqdm(corpus):
            doc = nlp(row)
            new_row = []
            for token in doc:
                if token.pos_ in consider:
                    new_row.append(token.lemma_)
            groups.append(' '.join(new_row))
        with open(groups_file_name, 'wb') as f:
            pickle.dump(groups, f)

    return groups


def get_matrix_and_feature_names(noun_groups: List[str]) -> (Any, Any, Any):
    tfidf_vectorizer = TfidfVectorizer(max_df=0.8, min_df=0.01, lowercase=False)
    tfidf_matrix = tfidf_vectorizer.fit_transform(noun_groups)
    feature_names = tfidf_vectorizer.get_feature_names_out()

    tf_vectorizer = TfidfVectorizer(vocabulary=feature_names, use_idf=False, norm='l1')
    tf_matrix = tf_vectorizer.fit_transform(noun_groups)

    return tfidf_matrix, feature_names, tf_matrix


def create_model(matrix):
    n_topics = 10
    m = NMF(n_components=n_topics)
    m.fit(matrix)

    return m


def get_topic_word_lists(topic_model, feature_names):
    n_words = 10
    n_words_features = 100

    topic_list = []
    extended_topic_list = []
    topic_words = []

    for idx, topic in enumerate(topic_model.components_):
        top_n = [feature_names[i] for i in topic.argsort()[-n_words:]][::-1]
        topic_list.append(f"topic_{'_'.join(top_n[:3])}")
        top_features = ' '.join(top_n)
        extended_topic_list.append(top_features)

        top_n = [feature_names[i] for i in topic.argsort()[-n_words_features:]][::-1]
        topic_words.append(top_n)

        print(f'Topic {idx}: {top_features}')

    return topic_list, extended_topic_list, topic_words


def get_topic2_topic(tm):
    normalized_matrix = normalize(tm.components_, axis=1, norm='l1')
    print(f'normalized_matrix: {normalized_matrix.shape}')

    topic_to_topic = cosine_similarity(normalized_matrix)
    print(f'topic2topic: {topic_to_topic.shape}')

    return topic_to_topic


def create_topic2topic_graph(t2t, extended_topic_list):
    nodes = []
    count = 1

    for i, topic in enumerate(t2t):
        nodes.append({
            'id': count,
            'topicname': extended_topic_list[i]
        })
        count += 1

    graph = {
        'directed': False,
        'graph': 'semant_graph',
        'links': [],
        'nodes': nodes
    }

    for i, node_i in enumerate(graph['nodes']):
        for j, node_j in enumerate(graph['nodes']):
            if i < j:
                source = node_i['id']
                target = node_j['id']
                weight = t2t[i, j]
                if weight > 0.15:
                    link = {
                        'source': source,
                        'target': target,
                        'weight': weight
                    }
                    graph['links'].append(link)

    return graph


def get_graph_template(graph, properties):
    node_label = properties['nodelabel']
    node_coloring = properties['nodecoloring']

    lv = '//' if properties['edgevisibility'] else ''
    parts = '//' if not properties['particles'] else ''
    dm = '//' if not properties['darkmode'] else ''

    d3graph = {
        'nodes': graph['nodes'],
        'links': graph['links']
    }

    htmlcode = f"""<head>
        <style>
            body {{
                margin: 0;
                font-family: Arial;
            }}
            h3 {{text-align: center;}}
            .center {{
              display: block;
              margin-left: auto;
              margin-right: auto;
            }}
        </style>
        <script src="https://unpkg.com/force-graph"></script>
        <meta charset="UTF-8">
    </head>
    <body>
    <img src="imgs/Logo.png" height="150" width="300" class="center">
    <h3>DebSearch ist eine statistische Website, welche die aktuelle Legislaturperiode</h3>
    <h3>in verschiedenen Kategorieren auswertet und visualisiert.</h3>
    <div id="graph"></div>
    <script>
        var data = {d3graph};
        const elem = document.getElementById('graph');
        const Graph = ForceGraph()(elem)
            .graphData(data)
            .nodeLabel('{node_label}')
            .nodeRelSize(3)
            .nodeVal('nReden')
            .nodeAutoColorBy('{node_coloring}')
            {dm}.backgroundColor('#000000')
            {dm}.linkColor(() => 'rgba(255,255,255,0.2)')
            {lv}.linkVisibility('false')
            {parts}.linkDirectionalParticles(2)
            {parts}.linkDirectionalParticleWidth(1.4)
            //.onNodeClick (node => {{window.open(`wordnet.html`, '_blank')}})
            .onNodeClick (node => {{
                const path = 'TOPnets/TOPnet4topic' + node.id + '.html';
                window.open(path, '_blank');
            }})
            //.onNodeHover(node => elem.style.cursor = node ? 'pointer' : null)
            .onNodeRightClick(node => {{
                // Center/zoom on node
                Graph.centerAt(node.x, node.y, 1000);
                Graph.zoom(4, 2000);
            }});
    </script>
    </body>
    """

    return {'graph': htmlcode}


def write_html_file(html):
    with open(f'./topic_network.html', 'w') as f:
        f.write(html['graph'])
