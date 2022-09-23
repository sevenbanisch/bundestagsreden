import json
import os

from lxml import etree


JSON_FILE_NAME = 'parsed_mdbs.json'
PREPROCESSED_DATA_DIRECTORY = '../data/'


def parse_names(names):
    name_dict = {}
    
    # Use last added name from names. The later on relation between mdb and speech is done via the id and not the name!
    name = names.getchildren()[-1].getchildren()
    
    name_dict['surname'] = name[0].text
    name_dict['forename'] = name[1].text
    name_dict['salutation_title'] = name[5].text
    name_dict['academic_title'] = name[6].text
    
    return name_dict


def parse_biography(biography):
    bio_dict = {}
    
    bio = biography.getchildren()
    
    bio_dict['birth_date'] = bio[0].text
    bio_dict['birth_place'] = bio[1].text
    bio_dict['birth_country'] = bio[2].text
    bio_dict['gender'] = bio[4].text
    bio_dict['civil_status'] = bio[5].text
    bio_dict['religion'] = bio[6].text
    bio_dict['profession'] = bio[7].text
    bio_dict['party'] = determine_party(bio[8].text)
    
    return bio_dict


def determine_party(text):
    without_party = 'Fraktionslos'
    valid_parties = ['BÜNDNIS 90/DIE GRÜNEN', 'CDU/CSU', 'AfD', 'SPD', 'FDP', 'DIE LINKE']

    party_text = without_party if text is None else text
    party_text = party_text.replace('.', '')
    party_text = 'CDU/CSU' if party_text in ['CDU', 'CSU'] else party_text
    party_text = party_text if party_text in valid_parties else without_party

    return party_text


def parse_legislative_period(period_elem):
    period_dict = {}
    
    period = period_elem.getchildren()
    
    period_dict['period_number'] = period[0].text
    period_dict['wkr_number'] = period[3].text
    period_dict['wkr_name'] = period[4].text
    period_dict['wkr_land'] = period[5].text
    period_dict['mandat_type'] = period[7].text
    
    return period_dict
    

def parse_mdb(mdb):
    children = mdb.getchildren()
    
    mdb_dict = {}
    
    mdb_dict['id'] = children[0].text
    mdb_dict['name'] = parse_names(children[1])
    mdb_dict['biography'] = parse_biography(children[2])
    mdb_dict['legislative_periods'] = [parse_legislative_period(period) for period in children[3].getchildren()]

    return mdb_dict
        

def get_mdb_rawdata():
    mdb_core_data_path = 'MdB-Stammdaten-data/MDB_STAMMDATEN.XML'
    root = etree.parse(mdb_core_data_path)
    
    mdbs = root.findall('.//MDB')
    
    return [parse_mdb(mdb) for mdb in mdbs]


def write_dict_to_json_file(dictionary):
    path = os.path.join(PREPROCESSED_DATA_DIRECTORY, JSON_FILE_NAME)
    with open(path, 'w') as outfile:
        json.dump(dictionary, outfile, indent=2)


def parse_mdb_data():
    print('parsing mdb data from xml')
    mdb_data = get_mdb_rawdata()

    print('writing parsed mdb data to json')
    write_dict_to_json_file(mdb_data)


def read_mdbs_from_json():
    return json.loads(open(os.path.join(PREPROCESSED_DATA_DIRECTORY, JSON_FILE_NAME)).read())


def main():
    parse_mdb_data()

    # The following lines demonstrate how to read the generated data.
    print('reading mdb data from json')
    mdbs = read_mdbs_from_json()

    print(f'got {len(mdbs)} mdbs from json')
    print('This is the first mdb entry:')
    print(mdbs[0])


if __name__ == '__main__':
    main()
