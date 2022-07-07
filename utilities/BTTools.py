

def filter_for(what, search_terms, speeches):
    filtered_speeches = []
    if what == 'text':
        search_terms_low = []
        for st in search_terms:
            search_terms_low.append(st.lower())
        for speech in speeches:
            match = [st in speech[what].lower() for st in search_terms_low]
            #if all(st == True for st in match):
            if any(st in speech[what] for st in search_terms):
                #print(match)
            #if ( search_terms in speech[what] ):
                filtered_speeches.append(speech)
    else:
        for speech in speeches:
            if ( speech[what] in set(search_terms) ):
                filtered_speeches.append(speech)
        
    filtered_speeches.sort(key = lambda x:x['date'])   
    return filtered_speeches



def groupSpeechesByDiscussionTitle(speeches):
    groupedSpeeches = {}
    for speech in speeches:
        top = speech['discussion_title']
        if top in groupedSpeeches:
            groupedSpeeches[top].append(speech)
        else:
            groupedSpeeches[top] = [speech]
    
    return groupedSpeeches