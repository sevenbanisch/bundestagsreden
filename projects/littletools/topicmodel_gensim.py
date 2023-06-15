import gensim
from gensim import corpora
from gensim.models import LdaModel

# Dokumente als Liste von Token-Listen definieren
documents = [['Apfel', 'Birne', 'Banane', 'Erdbeere'],
['Apfel', 'Birne', 'Mango', 'Pfirsich'],
['Birne', 'Zitrone', 'Orange', 'Aprikose'],
['Ananas', 'Banane', 'Orange', 'Papaya']]

# Ein Wörterbuch für die Token erstellen
dictionary = corpora.Dictionary(documents)

# Eine Bag of Words Repräsentation für die Dokumente erstellen
corpus = [dictionary.doc2bow(document) for document in documents]

# Ein Topic Model erstellen
num_topics = 2
lda_model = LdaModel(corpus=corpus,
                     id2word=dictionary,
                     num_topics=num_topics,
                     passes=10)

# Die Top 3 Wörter für jedes Thema ausgeben
for topic in lda_model.print_topics(num_topics=num_topics, num_words=3):
    print(topic)

#%%
