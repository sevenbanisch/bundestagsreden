from matplotlib import pyplot as plt

from word_cloud_functions import topics_to_word_clouds
from topic_network_functions import get_speeches, get_corpus, corpus_by_POS, get_matrix_and_feature_names, \
    create_model, get_topic_word_lists, get_topic2_topic, create_topic2topic_graph, get_graph_template, \
    write_html_file, group_speeches_by_discussion_title


def create_topic_network_page():
    original_speeches = get_speeches()
    grouped_speeches_by_tops = group_speeches_by_discussion_title(original_speeches)
    corpus = get_corpus(grouped_speeches_by_tops)

    consider = ['NOUN']
    noun_groups = corpus_by_POS(corpus, consider)

    tfidf_matrix, feature_names, tf_matrix = get_matrix_and_feature_names(noun_groups)
    model = create_model(tfidf_matrix)
    tl, etl, tw = get_topic_word_lists(model, feature_names)

    # topic2word = model.components_
    # doc2topic = (tf_matrix * topic2word.T)

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

    return tw


def main():
    tw = create_topic_network_page()

    topics_to_word_clouds(tw)

    return


if __name__ == '__main__':
    main()
