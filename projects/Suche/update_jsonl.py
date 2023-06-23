
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

# directory of json files
json_dir = '../../data/speeches_topic'

# create a dictionary of all jsons
json_dict = {}

for json_file in os.listdir(json_dir):
    if json_file.endswith(".json"):
        with open(os.path.join(json_dir, json_file), 'r') as file:
            data = json.load(file)
            json_dict[data['id']] = data['topic']

# path to jsonl file and new updated jsonl file
jsonl_file_path = '../../data/speeches_20.jsonl'
updated_jsonl_file_path = '../../data/speeches_20_V3.jsonl'

# read and update the jsonl file
with open(jsonl_file_path, 'r') as jsonl_file, open(updated_jsonl_file_path, 'w') as updated_jsonl_file:
    for line in jsonl_file:
        line_json = json.loads(line)
        matching_topic = json_dict.get(line_json['id'])
        if matching_topic is not None:
            line_json['topic'] = matching_topic
        updated_jsonl_file.write(json.dumps(line_json) + '\n')

