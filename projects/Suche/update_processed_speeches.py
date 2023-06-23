
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



import os
import json

def write_unique_ids_to_txt(json_dir, txt_file):
    # Load IDs from the txt file if it already exists
    ids_set = set()
    if os.path.exists(txt_file):
        with open(txt_file, 'r') as f:
            for line in f:
                ids_set.add(line.strip())

    # Iterate over JSON files in the directory
    for filename in os.listdir(json_dir):
        if filename.endswith('.json'):
            with open(os.path.join(json_dir, filename), 'r') as f:
                data = json.load(f)
                id_ = data.get('id')
                if id_ is not None and id_ not in ids_set:
                    # ID is unique, add it to the set and write it to the txt file
                    ids_set.add(id_)
                    with open(txt_file, 'a') as out_file:
                        out_file.write(id_ + '\n')


# Example usage
write_unique_ids_to_txt('../../data/speeches_topic', 'processed_speeches.txt')


