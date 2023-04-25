import os
from datetime import datetime
import json
from lxml import etree
from src.mdb_parser import read_mdbs_from_json


DATA_DIRECTORY = '../data/'
SPEECHES_DIRECTORY = 'data_20'


def filter_active_mdbs(mdbs, lp):
    active_mdbs = {}
    for mdb in mdbs:
        for period in mdb['legislative_periods']:
            if period['period_number'] == lp:
                active_mdbs[mdb['id']] = mdb
        
    return active_mdbs


def read_speeches_xml(lp):
    speeches = []
    path = f'data_{lp}'

    for file in os.listdir(path):
        speeches.append(os.path.join(path, file))

    print(f'Found {len(speeches)} files in \'{path}\'.')
    return speeches


def write_speeches(speeches_list, lp, with_comments):
    file_name = f'speeches_{lp}'
    file_name += '_with_comments' if with_comments else ''
    file_name += '.jsonl'
    path = os.path.join(DATA_DIRECTORY, file_name)
    with open(path, 'w', encoding='utf-8') as f:
        for line in speeches_list:
            json.dump(line, f, ensure_ascii=False)
            f.write('\n')

    print(f'saved {len(speeches_list)} speeches in `{path}`')


def parse_text(info, with_comments):
    text = ''
    if (info.attrib == {'klasse': 'J'}) or (info.attrib == {'klasse': 'J_1'}) or (info.attrib == {'klasse': 'O'}):
        if type(info.text) is str:
            text = info.text
            text += ' '

    if with_comments:
        if (info.tag == 'kommentar') and (type(info.text) is str):
            text += f"{{{str(info.text)}}} "

    return text


def clean_speech_dict_string_fragments(speech_dict):
    updated_dict = {}

    for key in speech_dict.keys():
        if type(speech_dict[key]) == str:
            updated_dict[key] = speech_dict[key].replace(u'\xa0', u' ').replace(u'\xad', u'')
        else:
            updated_dict[key] = speech_dict[key]

    return updated_dict


def get_mdb_from_speech_xml(redner_tag, period):
    name_tag = redner_tag.getchildren()[0].getchildren()[0]

    if name_tag.getchildren()[0].text == 'Dr.':
        fn = name_tag.getchildren()[0].text + ' ' + name_tag.getchildren()[1].text
        sn = name_tag.getchildren()[2].text
    else:
        fn = name_tag.getchildren()[0].text
        sn = name_tag.getchildren()[1].text

    mdb = {
        'biography': {
            'party': 'unknown'
        },
        'name': {
            'forename': fn,
            'surname': sn
        },
        'legislative_periods': [{'period_number': period}]
    }

    return mdb


def parse_top(top, date, mdbs, with_comments):
    jsondict = {}
    tagesordnungspunkt = ''
    if top.tag == 'tagesordnungspunkt':
        tagesordnungspunkt = f"{top.attrib['top-id']} {date}"
        jsondict[tagesordnungspunkt] = {}

    jsondict[tagesordnungspunkt]['speeches'] = []

    for child in top.getchildren():
        if child.tag == 'rede':
            speech_dict = {'text': ''}

            for info in child.getchildren():
                period = next(iter(mdbs.values()))['legislative_periods'][-1]['period_number']
                if info.attrib == {'klasse': 'redner'}:
                    redner_id = info.getchildren()[0].attrib['id']
                    if redner_id not in mdbs.keys():
                        mdb = get_mdb_from_speech_xml(info, period)
                    else:
                        mdb = mdbs[redner_id]

                    party = mdb['biography']['party']
                    whole_name = mdb['name']
                    name = whole_name['forename']
                    surname = whole_name['surname']
                print(name)

                speech_dict['id'] = child.attrib['id']
                speech_dict['period'] = period
                speech_dict['date'] = date
                speech_dict['name'] = f'{name} {surname}'
                speech_dict['party'] = party
                speech_dict['redner_id'] = redner_id

                speech_dict['text'] += parse_text(info, with_comments)
                speech_dict['discussion_title'] = tagesordnungspunkt

                cleaned_dict = clean_speech_dict_string_fragments(speech_dict)
        
            jsondict[f"{top.attrib['top-id']} {date}"]['speeches'].append(cleaned_dict)
    
    return jsondict                    


def parse_file(file, parser, mdbs, with_comments):
    root = etree.parse(file, parser).getroot()

    date = root.attrib.get('sitzung-datum')
    date = datetime.strptime(date, '%d.%m.%Y').strftime('%Y-%m-%d')

    tops = root.findall('.//sitzungsverlauf/tagesordnungspunkt')

    speeches = [parse_top(top, date, mdbs, with_comments) for top in tops]

    return speeches


def flatten_speeches(files):
    speeches = []

    for file in files:
        for top in file:
            punkt = list(top.values())[0]
            speeches.extend(punkt['speeches'])

    return speeches


def parse(legislature_period: int, with_comments: bool) -> None:
    print(f'start parsing with parameters given: {legislature_period} & {with_comments}')
    mdbs = read_mdbs_from_json()
    active_mdbs = filter_active_mdbs(mdbs, legislature_period)

    xmls = read_speeches_xml(legislature_period)

    parser = etree.XMLParser(dtd_validation=False)
    parsed_files = [parse_file(file, parser, active_mdbs, with_comments=with_comments) for file in xmls]

    print(f'got {len(parsed_files)} files')

    speeches = flatten_speeches(parsed_files)

    print(f'got {len(speeches)} speeches')

    write_speeches(speeches, legislature_period, with_comments)

    return


def parse_speeches():
    lp = input('Select legislative period (19 or 20): ')
    with_comments = input('Shall comments be included? (y or n): ')

    parse(lp, with_comments == 'y')


if __name__ == '__main__':
    parse_speeches()


