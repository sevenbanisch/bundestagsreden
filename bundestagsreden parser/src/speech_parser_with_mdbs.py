# TODO: julian hohenöcker: Implement parser according to ./parser.py but retrieve speaker core data (surename, forename, party, etc.) from parsed mdb-data file.

import os
from datetime import datetime
import json
from lxml import etree
from mdb_parser import read_mdbs_from_json

MDB_JSON_FILE = 'parsed_mdbs.json'
DATA_DIRECTORY = '../../data/'
SPEECHES_DIRECTORY = 'data_20/speeches'


def filter_active_mdbs(mdbs):
    active_mdbs = {}
    active_period = '20'
    for mdb in mdbs:
        for period in mdb['legislative_periods']:
            if period['period_number'] == active_period:
                active_mdbs[mdb['id']] = mdb
        
    return active_mdbs


def read_speeches_xml():
    speeches = []
    path = os.path.join(DATA_DIRECTORY, SPEECHES_DIRECTORY)

    for file in os.listdir(path):
        speeches.append(os.path.join(path, file))

    print(f'Found {len(speeches)} files in \'{path}\'.')
    return speeches


def parse_top(top, date, mdbs):
    jsondict = {}
    tagesordnungspunkt = ''
    if top.tag == 'tagesordnungspunkt':
        tagesordnungspunkt = f"{top.attrib['top-id']} {date}"
        # jsondict[f"{top.attrib['top-id']} {date}"] = {}
        jsondict[tagesordnungspunkt] = {}

    # jsondict[f"{top.attrib['top-id']} {date}"]['speeches'] = []
    jsondict[tagesordnungspunkt]['speeches'] = []

    for child in top.getchildren():
        if child.tag == 'rede':
            speech_dict = {}
            text = ''

            for info in child.getchildren():
                if info.attrib == {'klasse': 'redner'}:
                    redner_id = info.getchildren()[0].attrib['id']
                    if redner_id not in mdbs.keys():
                        mdb = {
                            'biography': {
                                'party': 'unknown'
                            },
                            'name': {
                                'forename': 'unknown',
                                'surname': 'unknown'
                            },
                            'legislative_periods': [{'period_number': 0}]
                        }
                    else:
                        mdb = mdbs[redner_id]

                    party = mdb['biography']['party']
                    whole_name = mdb['name']
                    name = whole_name['forename']
                    surname = whole_name['surname']
                
                speech_dict['id'] = child.attrib['id']
                speech_dict['period'] = mdb['legislative_periods'][-1]['period_number']
                speech_dict['date'] = date
                speech_dict['name'] = f'{name} {surname}'
                speech_dict['party'] = party
                speech_dict['redner_id'] = redner_id

                speech_dict['text'] = text
                speech_dict['discussion_title'] = tagesordnungspunkt
        
            jsondict[f"{top.attrib['top-id']} {date}"]['speeches'].append(speech_dict)
    
    return jsondict                    


def parse_file(file, parser, mdbs):
    root = etree.parse(file, parser).getroot()

    date = root.attrib.get('sitzung-datum')
    date = datetime.strptime(date, '%d.%m.%Y').strftime('%Y-%m-%d')

    tops = root.findall('.//sitzungsverlauf/tagesordnungspunkt')

    speeches = [parse_top(top, date, mdbs) for top in tops]

    return speeches


def flatten_speeches(files):
    speeches = []

    for file in files:
        for top in file:
            punkt = list(top.values())[0]
            speeches.extend(punkt['speeches'])

    return speeches


def main():
    # read mdbs
    mdbs = read_mdbs_from_json()
    active_mdbs = filter_active_mdbs(mdbs)

    # read xmls
    xmls = read_speeches_xml()

    parser = etree.XMLParser(dtd_validation=False)
    parsed_files = [parse_file(file, parser, active_mdbs) for file in xmls]

    print(f'got {len(parsed_files)} files')

    speeches = flatten_speeches(parsed_files)

    print(f'got {len(speeches)} speeches')

    # save it
    return


if __name__ == '__main__':
    main()
