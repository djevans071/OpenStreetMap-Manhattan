"""
Your task in this exercise has two steps:

- audit the OSMFILE and change the variable 'mapping' to reflect the changes needed to fix
    the unexpected street types to the appropriate ones in the expected list.
    You have to add mappings only for the actual problems you find in this OSMFILE,
    not a generalized solution, since that may and will depend on the particular area you are auditing.
- write the update_name function, to actually fix the street name.
    The function takes a string with street name as an argument and should return the fixed name
    We have provided a simple test so that you see what exactly is expected
"""
import xml.etree.cElementTree as ET
from collections import defaultdict
import re
import pprint
import pdb

OSMFILE = "manhattan_new-york.osm"
street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)


expected = ["Street", "Avenue", "Boulevard", "Drive",
            "Court", "Place", "Square", "Lane", "Road",
            "Trail", "Parkway", "Commons", "Terrace",
            'North', 'East', 'West', 'South', 'Plaza',
            'Walk', 'Slip', 'Highway', 'Expressway', 'Concourse',
            'Circle', 'Center', 'Broadway', 'Crescent', 'Loop',
            'Way', 'Alley', 'Bowery', 'A', 'B', 'C', 'D',
            'Extension', 'Oval', 'Park', 'Mews', 'Village' ]

mapping = { "St": "Street", 'street': 'Street',
            "St.": "Street", 'ST': 'Street',
            'st': 'Street', 'Steet': 'Street',
            'Street,': 'Street',
            'avenue': 'Avenue', 'Ave': 'Avenue',
            'Ave.': 'Avenue', 'ave': 'Avenue',
            'Av': 'Avenue',
            'Rd.': 'Road', 'Rd': 'Road',
            'Broadway.': 'Broadway',
            'Avene': 'Avenue', 'Aveneu': 'Avenue',
            'Blvd': 'Boulevard',
            'Lafayette': 'Lafayette Street',
            'Macdougal': 'MacDougal Street',
            '41st': '41st Street', '42nd': '42nd Street'}

def is_street_name(elem):
    return (elem.attrib['k'] == "addr:street")

def is_zip(elem):
    return (elem.attrib['k'] == "addr:postcode")

def audit_street_type(street_types, street_name):
    # first update street name before auditing to check for more
    # anamolous street names
    street_name = update_name(street_name, mapping)
    m = street_type_re.search(street_name)
    if m:
        street_type = m.group()
        if street_type not in expected:
            street_types[street_type].add(street_name)


def audit(osmfile, keyword):
    osm_file = open(osmfile, "rb")
    street_types = defaultdict(set)
    zip_types = set()
    for event, elem in ET.iterparse(osm_file, events=("start",)):

        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_street_name(tag):
                    audit_street_type(street_types, tag.attrib['v'])
                if is_zip(tag):
                    zipname = tag.attrib['v']
                    zipname = update_zip(tag.attrib['v'])
                    zip_types.add(zipname)
    osm_file.close()
    if keyword == 'street':
        return street_types
    if keyword == 'zip':
        return zip_types


def update_name(name, mapping):
    # update street name
    word_list = name.split()
    if word_list[-1] in mapping:
        word_list[-1] = mapping[word_list[-1]]
    elif word_list[-1] == '10024':
        ind = name.find('NYC')
        return name[:ind-1]
    elif word_list[-1] in ['USA', 'Unidos', 'Uniti']:
        # take the address before first comma and recursively update street name
        street = name.split(',')[0]
        return update_name(street, mapping)
    elif word_list[-1] == 'NY': # slice address before 'New York' and recursively update the street name
        ind = name.find('New York')
        return update_name(name[:ind-1], mapping)
    elif word_list[-1] == "Americas":
        return '6th Avenue'
    name = ' '.join(word_list)
    return name

def update_zip(zip_name):
    # returns consistent zip code values
    try:    #try converting zip code to int value
        int(zip_name)
    except ValueError: # process zip code if it contains non-int values
        if '-' in zip_name:
            betterzip = zip_name.split('-')[0]
        elif 'NY' in zip_name:
            betterzip = zip_name.split()[-1]
        return betterzip
    else: #special cases
        if zip_name == '100014':
            zip_name = '10014'
        elif zip_name == '320':
            zip_name = '07024'
        elif zip_name == '97657':
            zip_name = '07657'
        return zip_name


if __name__ == '__main__':
    # st_types = audit(OSMFILE, 'street')
    # pprint.pprint(dict(st_types))

    zip_types = audit(OSMFILE, 'zip')
    pprint.pprint(zip_types)
