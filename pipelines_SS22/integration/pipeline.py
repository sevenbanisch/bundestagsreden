from typing import List, Tuple, Any

from matplotlib import pyplot as plt

from level_2_functions import generate_networks_for_topics
from word_cloud_functions import topics_to_word_clouds
from topic_network_functions import get_speeches, get_corpus, corpus_by_POS, get_matrix_and_feature_names, \
    create_model, get_topic_word_lists, get_topic2_topic, create_topic2topic_graph, get_graph_template, \
    write_html_file, group_speeches_by_discussion_title


def create_topic_network_page() -> (List[list], List[str], List[str], Tuple[Any, Any, Any]):
    """This function creates a html-document with a graph representing the topic-model."""
    original_speeches = get_speeches()
    grouped_speeches_by_tops = group_speeches_by_discussion_title(original_speeches)
    corpus = get_corpus(grouped_speeches_by_tops)

    consider = ['NOUN']
    noun_groups = corpus_by_POS(corpus, consider)

    tfidf_matrix, feature_names, tf_matrix = get_matrix_and_feature_names(noun_groups)
    model = create_model(tfidf_matrix)
    tl, etl, tw = get_topic_word_lists(model, feature_names)

    topic2word = model.components_
    doc2topic = (tf_matrix * topic2word.T)

    topic2topic = get_topic2_topic(model)

    plt.matshow(topic2topic)
    plt.show()

    t2t_graph = create_topic2topic_graph(topic2topic, etl)

    properties = {
        'nodecoloring': 'topicname',
        'nodelabel': 'topicname',
        "darkmode": False,
        "edgevisibility": True,
        "particles": False
    }

    html_graph = get_graph_template(t2t_graph, properties)
    write_html_file(html_graph)

    return tw, corpus, grouped_speeches_by_tops, (doc2topic, feature_names, topic2word)


def get_top_topic_num(grouped_speeches_by_tops, doc2topic, n_topics):
    top_topic_num = []
    for tx, top in enumerate(grouped_speeches_by_tops):
        if doc2topic[tx].max() > 0:
            topic_num = doc2topic[tx].argmax()
        else:
            topic_num = n_topics

        top_topic_num.append(topic_num)

    return top_topic_num


def get_feature_topic_num(feature_names, topic2word, n_topics: int) -> List[int]:
    feature_topic_num = []
    for wx, word in enumerate(feature_names):
        if topic2word.T[wx].max() > 0:
            topic_num = topic2word.T[wx].argmax()
        else:
            topic_num = n_topics

        feature_topic_num.append(topic_num)

    return feature_topic_num


def main() -> None:
    tw, corpus, grouped_speeches_by_tops, later_use = create_topic_network_page()

    word_clouds = topics_to_word_clouds(tw)

    # topics: list<dict>[11], dict {'name': str, 'words': [str], 'tops': [str] } => topics_len
    # corpus: list<str>[208]
    # top_topic_num: list<int>[208]
    # gropuedby_dicussion: dict{'topxy': [speeches]}
    # feature_names: list<str>[7548]
    # feature_topic_num: list<int>[7548]

    # TODO: Hier weitermachen! :-(
    # in combination with `level_2_functions.py` and `Sven/xTopicModel.ipynb`

    doc2topic, feature_names, topic2word = later_use
    top_topic_num = get_top_topic_num(grouped_speeches_by_tops, doc2topic, len(tw))
    feature_topic_num = get_feature_topic_num(feature_names, topic2word, len(tw))

    generate_networks_for_topics(len(tw), corpus, top_topic_num, grouped_speeches_by_tops, feature_names, feature_topic_num)

    return


if __name__ == '__main__':
    main()
