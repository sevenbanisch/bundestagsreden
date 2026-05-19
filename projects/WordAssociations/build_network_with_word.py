#%%
import pandas as pd
import networkx as nx
import math
def build_network_with_word(wort_wahl):

    """
    build_network_with_word builds a NetworkX graph with 40 words (a word given as a parameter and the 39 words with the
    highest association to that word). For that it uses the association matrix 'data/coo_matrix.h5'. The nodes are the
    words. The size of the nodes is the association to the given parameter word. Only the 10 % highest association
    between the words get visualized as edges. The weight of the edges is the association. For better visualization
    the associations get logarithmised before applied as node sizes and edge weights.

    :param wort_wahl: the word for which the 39 words with highest association are searched
    :return: returns the NetworkX graph
    """

    #import the data
    coo_matrix = pd.read_hdf('data/coo_matrix.h5', key='df')
    
    #build a dataframe with the chosen word and the 39 words with the highest association with the chosen word
    woerter = coo_matrix[wort_wahl].sort_values(ascending=False)[0:39].index
    woerter_dummy_list = list(woerter)
    if wort_wahl in woerter_dummy_list:
        woerter = coo_matrix[wort_wahl].sort_values(ascending=False)[0:40].index
    else:
        woerter_dummy_list.append(wort_wahl)
        woerter = pd.Index(woerter_dummy_list)
    df_40 = coo_matrix[woerter].loc[woerter]

    #change word association with words itself to 0 since we don't need these values
    i=0
    for text in df_40:
        df_40[text][i] = 0
        i=i+1
    #for visualization
    df_40.loc[wort_wahl,wort_wahl] = 3

    #calculate the log for the associations (better visualization in network)
    for i in range(0,40):
        for j in range (0,40):
            df_40.iloc[i,j] = math.log(df_40.iloc[i,j] + 1) * 3

    #create a dictionary with the 40 words (used in the next step)
    list_woerter = []
    for i in range(len(woerter)):
        list_woerter.append(woerter[i])
    list_dict_woerter = []
    for i in range(len(list_woerter)):
        list_dict_woerter.append({'id': str(i), 'name': list_woerter[i]})
        
    #create graph with the 40 words as nodes and the associations as the weight of the edges
    graph = {
        'directed': False,
        'graph': 'semant_graph',
        'links': [],
        'nodes': list_dict_woerter,
    }
    # To add the edges, we iterate over the different nodes and check the corresponding entry in the distance matrix
    for ix,nodeI in enumerate(graph['nodes']):
        for jx,nodeJ in enumerate(graph['nodes']):
            # As this graph is not directed, we only want to add an edge once. If the graph is directed, we do not need the if condition
            if nodeI['id'] < nodeJ['id']:
                source = nodeI['id']
                target = nodeJ['id']
                weight = df_40.iloc[ix,jx]
                # We only add edges for the words with the 10%-strongest association
                if weight > df_40.stack().quantile(0.9):
                    link_dict = {
                        'source':source,
                        'target':target,
                        'weight':weight
                    }
                    graph['links'].append(link_dict)

    # The following creates a networkx graph based on the previously defined graph
    graph_40 = nx.Graph()

    # Add the nodes on by one
    for node in graph['nodes']:
        if node['name'] == wort_wahl:
            graph_40.add_node(node['id'],
                              label=node['name'],
                              size=3*df_40.loc[wort_wahl,node["name"]],
                              color="lightcoral")
        else:
            graph_40.add_node(node['id'],
                              label=node['name'],
                              size=3*df_40.loc[wort_wahl,node["name"]])

    # Add the edges one by one
    for link in graph['links']:
        graph_40.add_edge(link['source'], link['target'], weight = link['weight'], color="steelblue",community=0)

    #returns graph
    return graph_40