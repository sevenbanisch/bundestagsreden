
import jsonlines                    # zum Laden der Daten
import nltk                         # natural language toolkit
nltk.download('punkt')              # das brauchen wir nur beim ersten Mal
import openai
from dotenv import load_dotenv
import os



from collections import Counter     # um worte zu zählen
import matplotlib.pyplot as plt     # Für Visualisierung

load_dotenv()



# Authentication
openai.api_key = os.getenv("OPENAI_KEY")


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

################# FUNKTIONEN #####################

for speech in alleReden[30:40]: 
    speech_string = f'Was ist das Hauptthema der Rede in einem Wort. Nutze das Folgende Antwortschema "Hauptthema:" Hier ist die Rede: {speech["text"]}'
    chat_history = [{"role": "user", "content": speech_string}]
    response = openai.ChatCompletion.create(
    model='gpt-3.5-turbo',
    messages=chat_history)
    message = response.choices[0]['message']
    print("{}: {}".format(message['role'], message['content']))

