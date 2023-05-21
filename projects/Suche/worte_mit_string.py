
import jsonlines                    # zum Laden der Daten
import nltk                         # natural language toolkit
nltk.download('punkt')     
nltk.download('stopwords')         # das brauchen wir nur beim ersten Mal
german_stop_words = nltk.corpus.stopwords.words('german')

from collections import Counter     # um worte zu zählen
import matplotlib.pyplot as plt     # Für Visualisierung
from wordcloud import WordCloud     # Für Wordclouds

################# LADEN DER DATEN ####################

# Hier legen wir fest, welche Daten (Wahlperiode 19 oder 20) wir laden:
legislatur = 20

# Wir generieren eine leere Liste:
alleReden = []

# Wir öffnen den entsprechende File (Dateipfad anpassen!):
with jsonlines.open(f'../../data/speeches_{legislatur}.jsonl') as f:
    for line in f.iter():
        # Wir packen alles Zeile für Zeile zu unserer Liste:
        alleReden.append(line)

# Wir sortieren nach Datum:
alleReden.sort(key = lambda x :x['date'])


print("ALLE Reden", alleReden)


################# FUNKTIONEN #####################

# Zunächst brauchen wir eine Funktion, die uns die Reden gibt, die ein bestimmtes Wort enthalten.
#  Funktion für Textsuche:
#  Gibt eine Untermenge an Reden zurück, die einen bestimmten String (Wort) enthalten.

def find_speeches_with_word(search_term, speeches):
    filtered_speeches = []
    for speech in speeches:
        if ( search_term in speech['text'] ):
            filtered_speeches.append(speech)
    return filtered_speeches

# Reden sind lang und die Worte tauchen in verschiedenen Kontexten auf.
#  Wir würden gerne alle Sätze sehen, in denen der Suchbegriff vorkommt.
#  Aber natürlich kommt unser Suchstring nur in Sätzen vor, die in de Untermenge an Reden sind.

def find_sentences_with_word(search_term, speeches):
    sents_with_word = []
    for speech in speeches:
        sent_list = nltk.sent_tokenize(speech['text'])
        for sent in sent_list:
            if search_term in sent:
                sents_with_word.append(sent)
    return sents_with_word


# Nun wäre es doch spannend, die Reden einer Partei oder eines Politikers zu sehen.
#  Dazu entwickeln wir eine Funktion, die es erlaubt, in den anderen Felder (keys) zu suchen.
#  Funktion, mit der man eine Menge an Reden nach verschiedenen Kriterien filtern kann.
#  Es wird die entsprechende Untermenge zurückgegeben.
#  'what' enthält den Key, wo gesucht werden soll. Interessant vor allem: 'name' und 'party'

def filter_speeches_for(what, search_term, speeches):
    filtered_speeches = []
    for speech in speeches:
        if search_term in speech[what]:
            filtered_speeches.append(speech)

    filtered_speeches.sort(key=lambda x: x['date'])
    return filtered_speeches

# Zusätzlche Funktion.
# Nun möchte ich alle Worte, die einen bestimmten String enthalten ausgeben.

def find_words_which_contain(string,satz_liste):
    wort_liste = []
    for sx, satz in enumerate(satz_liste):
        # print(f' Satz {sx+1}: {satz}')
        worte = nltk.word_tokenize(satz)
        # print(f' Satz {sx+1}: {worte}')
        wort_liste.extend(worte)
    worte_mit_string = []
    for wort in wort_liste:
        if string in wort:
            worte_mit_string.append(wort)
    return worte_mit_string


################ Anwendung ################


such_string = 'Kapital'
#such_string = 'kapital'    # probiert doch einmal aus, ob das Ergebnis gleich ist.

# oder auch das hier als weiteres Beispiel:
#such_string = 'krise'

untermenge = find_speeches_with_word(such_string, alleReden)
saetze = find_sentences_with_word(such_string, untermenge)
wort_liste = find_words_which_contain(such_string,saetze)

print(f'Es gibt {len(wort_liste)} Worte, die "{such_string}" enthalten.')

#counts = Counter(wort_liste).most_common()
counts = Counter(wort_liste)
print(counts)

# Wir wollen das Ergebnis graphisch ausgeben.
# Dieses Mal als Wordcloud (oben importiert mit "from wordcloud import WordCloud")

wordcloud = WordCloud(width=400, height=400, mode = "RGBA", background_color='rgba(255, 255, 255, 0)', max_words=100, colormap='rainbow').generate_from_frequencies(counts)

fig = plt.figure(figsize=(10,10))
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis("off")

plt.show()