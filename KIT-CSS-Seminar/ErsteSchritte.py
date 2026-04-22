import jsonlines

legislatur = 20

alleReden = []
with jsonlines.open(f'../data/speeches_{legislatur}.jsonl') as f:
    for line in f.iter():
        #for line in list(f):
        alleReden.append(line)

alleReden.sort(key = lambda x:x['date'])

print(len(alleReden))
#%%
