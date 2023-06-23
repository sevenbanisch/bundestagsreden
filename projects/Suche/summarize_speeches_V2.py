
import jsonlines                    # zum Laden der Daten
import openai
from dotenv import load_dotenv
import os
import json
import time

from collections import Counter     # um worte zu zählen
import matplotlib.pyplot as plt     # Für Visualisierung

load_dotenv()


# Authentication
openai.api_key = os.getenv("OPENAI_KEY", "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")




#------------------------------------------------------------------

def read_json_file(file_name):
    with open(file_name, 'r') as file:
        data = json.load(file)
    return data



################# SPEICHERN DER DATEN ####################
def save_dict_to_json(dictionary, speech_id):
    # Generate the file name with the idea
    file_name = f"../../data/speeches_topic/{speech_id}_data.json"
    # Open the file in write mode and save the dictionary as JSON
    with open(file_name, 'w') as json_file:
        json.dump(dictionary, json_file)



################# SPEICHERN DER DATEN ####################

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

timeout_seconds = 5
retry_delay_seconds = 1

import time

import os
import json

# File to store processed speech ids
processed_speeches_file = "processed_speeches.txt"

def call_api_with_retry(speech):
    speech_string = f'''Hier ist eine Rede, die im Deutschen Bundestag gehalten wurde: {speech["text"]}
    Was ist die Haltung der Person die diese Rede gehalten hat. Antworte mit einem Satz. Nutze das Folgende Antwortschema 
    "Haltung:" '''
    chat_history = [{"role": "user", "content": speech_string}]
    response = openai.ChatCompletion.create(
        model='gpt-3.5-turbo-16k-0613',
        messages=chat_history
    )
    message = response.choices[0]['message']
    print("{}: {}".format(message['role'], message['content']))
    save_dict_to_json({
        "topic": message['content'],
        "id": speech["id"],
        "period": speech["period"],
        "date": speech["date"],
        "name": speech["name"],
        "party": speech["party"],
        "redner_id": speech["redner_id"],
        "discussion_title": speech["discussion_title"]
    }, speech["id"])

    # Mark this speech as processed by adding its id to the processed_speeches_file
    with open(processed_speeches_file, 'a') as f:
        f.write(speech["id"] + "\n")


# Get already processed speeches
if os.path.exists(processed_speeches_file):
    with open(processed_speeches_file, 'r') as f:
        processed_speeches = f.read().splitlines()
else:
    processed_speeches = []

for speech in alleReden:
    try: 
        # Only process the speech if it hasn't been processed yet
        if speech["id"] not in processed_speeches:
            call_api_with_retry(speech)
    except Exception as e: 
        print("Exception encountered:", str(e))
        if (str(e) == ("This model's maximum context length is 16385 tokens. However, your messages resulted in 17674 tokens. Please reduce the length of the messages.")):
            continue
        else: 
            print("Retrying after 1 second...")
            time.sleep(1)  # Delay for 1 second
            call_api_with_retry(speech)



