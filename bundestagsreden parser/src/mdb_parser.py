import json
import os

from lxml import etree


JSON_FILE_NAME = 'parsed_mdbs.json'
PREPROCESSED_DATA_DIRECTORY = '../data/'


def parseNames(names):
    name_dict = {}
    
    # Use last added name from names. The later on relation between mdb and speech is done via the id and not the name!
    name = names.getchildren()[-1].getchildren()
    
    name_dict['surname'] = name[0].text
    name_dict['forename'] = name[1].text
    name_dict['salutation_title'] = name[5].text
    name_dict['academic_title'] = name[6].text
    
    return name_dict


def parseBiography(biography):
    bio_dict = {}
    
    bio = biography.getchildren()
    
    bio_dict['birth_date'] = bio[0].text
    bio_dict['birth_place'] = bio[1].text
    bio_dict['birth_country'] = bio[2].text
    bio_dict['gender'] = bio[4].text
    bio_dict['civil_status'] = bio[5].text
    bio_dict['religion'] = bio[6].text
    bio_dict['profession'] = bio[7].text
    bio_dict['party'] = bio[8].text
    
    return bio_dict


def parseLegislativePeriod(period_elem):
    period_dict = {}
    
    period = period_elem.getchildren()    
    
    period_dict['period_number'] = period[0].text
    period_dict['wkr_number'] = period[3].text
    period_dict['wkr_name'] = period[4].text
    period_dict['wkr_land'] = period[5].text
    period_dict['mandat_type'] = period[7].text
    
    return period_dict
    

def parseMdb(mdb):
    children = mdb.getchildren()
    
    mdb_dict = {}
    
    mdb_dict['id'] = children[0].text
    mdb_dict['name'] = parseNames(children[1])
    mdb_dict['biography'] = parseBiography(children[2])
    mdb_dict['legislative_periods'] = [parseLegislativePeriod(period) for period in children[3].getchildren()]
    
    return mdb_dict
        

def getMdbCoredata():
    mdb_core_data_path = os.path.join(PREPROCESSED_DATA_DIRECTORY, 'MdB-Stammdaten-data/MDB_STAMMDATEN.XML')
    root = etree.parse(mdb_core_data_path)
    
    mdbs = root.findall('.//MDB')
    
    return [parseMdb(mdb) for mdb in mdbs]


def write_dict_to_json_file(dictionary):
    path = f'{PREPROCESSED_DATA_DIRECTORY}{JSON_FILE_NAME}'
    with open(path, 'w') as outfile:
        json.dump(dictionary, outfile, indent=2)


def parse_mdb_data():
    print('parsing mdb data from xml')
    mdb_data = getMdbCoredata()

    print('writing parsed mdb data to json')
    write_dict_to_json_file(mdb_data)


def read_mdbs_from_json():
    return json.loads(open(f'{PREPROCESSED_DATA_DIRECTORY}{JSON_FILE_NAME}').read())


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
