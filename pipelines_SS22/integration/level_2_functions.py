from typing import List

from sklearn.feature_extraction.text import TfidfVectorizer


def create_graph(groupedby_discussion: dict, topic_names: List[str], similarity_topic) -> dict:
    nodes = []
    count = 1
    for j, top_ix in enumerate(topic_names):
        node_dict = {
            'id': count,
            'top': top_ix,
            'date': groupedby_discussion[topic_names[j]][0]['date'],
            'nReden': len(groupedby_discussion[topic_names[j]])
        }
        nodes.append(node_dict)
        count += 1

    graph = {
        'directed': False,
        'graph': 'semant_graph',
        'links': [],
        'nodes': nodes,
    }

    min_weight = 0.15
    for ix, nodeI in enumerate(graph['nodes']):
        for jx, nodeJ in enumerate(graph['nodes']):
            if ix < jx:
                source = nodeI['id']
                target = nodeJ['id']
                weight = similarity_topic[ix, jx]
                if weight > min_weight:
                    link_dict = {
                        'source': source,
                        'target': target,
                        'weight': weight
                    }
                    graph['links'].append(link_dict)

    nn = len(graph['nodes'])
    ne = len(graph['links'])
    print(f"This graph has {nn} nodes and {ne} links.")

    return graph


def embed_graph_in_html(graph: dict) -> str:
    d3graph = {"nodes": graph["nodes"], "links": graph["links"]}

    return f"""<head>
                <style> body {{margin: 0;}} </style>
                <script src="https://unpkg.com/force-graph"></script>
                <meta charset="UTF-8">
            </head>
            <body>
            <div id="graph"></div>
            <script>
                var data = {d3graph};
                const elem = document.getElementById('graph');
                const Graph = ForceGraph()(elem)
                    .graphData(data)
                    .nodeLabel('top')
                    .nodeRelSize(1)
                    .nodeVal('nReden')
                    //.linkVisibility('true')
                    //.onNodeClick (node => {{window.open(`wordnet.html`, '_blank')}})
                    //.onNodeHover(node => elem.style.cursor = node ? 'pointer' : null)
                    .onNodeRightClick(node => {{
                        // Center/zoom on node
                        Graph.centerAt(node.x, node.y, 1000);
                        Graph.zoom(4, 2000);
                    }});
            </script>
            </body>
            """


def safe_html_graph(i: int, html: str) -> None:
    with open(f'./TOPnets/TOPnet4topic{i}.html', 'w') as f:
        f.write(html)


def generate_networks_for_topics(
        topics_len: int, corpus, top_topic_num: list, gropuedby_discussion: dict, feature_names: List[str],
        feature_topic_num):
    print(f'start generate_networks_for_topics, iterating over {topics_len} elements.')
    for i in range(topics_len):
        topic_selection = []
        topic_indices = []
        topic_names = []

        for j, topic in enumerate(corpus):
            if top_topic_num[j] == i:
                topic_selection.append(topic)
                topic_indices.append(j)
                topic_names.append(list(gropuedby_discussion.keys())[j])

        topic_features = []
        for j, word in enumerate(feature_names):
            if feature_topic_num[j] != i:
                topic_features.append(word)

        if len(topic_selection) == 0:
            print(f'Topic {i} cannot be constructed!!!')
        else:
            vectorizer_topic = TfidfVectorizer(vocabulary=topic_features, lowercase=False)
            tf_idf_matrix_topic = vectorizer_topic.fit_transform(topic_selection)
            pairwise_similarity_topic = tf_idf_matrix_topic * tf_idf_matrix_topic.T
            similarity_topic = pairwise_similarity_topic.toarray()

            # TODO
            # filter_for_topics_top. Für jedes Topic, die Liste der Tagesordnungspunkte filtern.
            # Aus Sven/xTopicModel.ipynb 'topics'-Variable
            # Für jeden dieser selektierten Tagesordnungspunkte die Reden selektieren.
            # Für alle diese Reden ein Balkendiagramm mit der "Beifall"-Reaktion erstlellen.
            # reaction-bars bekommen wir aus Marcel/Report_comments_parties.ipynb
            # print(next(gropuedby_discussion.items()))

            print(similarity_topic.shape)

            graph = create_graph(gropuedby_discussion, topic_names, similarity_topic)
            html = embed_graph_in_html(graph)
            safe_html_graph(i, html)

    print('end generate_networks_for_topics')
