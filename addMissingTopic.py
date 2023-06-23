import jsonlines

# Create an empty list to store the updated dictionaries
updated_dicts = []

with jsonlines.open('speeches_20_with_topic.jsonl') as reader:
    for obj in reader:
        # Check if 'topic' key is in the dictionary
        if 'topic' not in obj:
            # If not, add it with the specified value
            obj['topic'] = "Speech exceeds 16k tokens"
        # Append the (potentially updated) dictionary to the list
        updated_dicts.append(obj)

# Write the updated dictionaries back to a new .jsonl file
with jsonlines.open('speeches_20_with_topic_all.jsonl', mode='w') as writer:
    writer.write_all(updated_dicts)