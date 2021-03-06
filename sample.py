#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Use the following code to take a systematic sample of elements from your original OSM region. Try changing the value of k so that your resulting SAMPLE_FILE ends up at different sizes. When starting out, try using a larger k, then move on to an intermediate k before processing your whole dataset.
'''

import xml.etree.ElementTree as ET  # Use cElementTree or lxml if too slow
import pprint

OSM_FILE = "manhattan_new-york.osm"  # Replace this with your osm file
SAMPLE_FILE = "sample.osm"

k = 100 # Parameter: take every k-th top level element

def get_specific_element(osm_file, id, tags=('node', 'way', 'relation')):
    # return element with a specific id and which has the right kind of tag
    context = iter(ET.iterparse(osm_file, events=('start', 'end')))
    _, root = next(context)
    for event, elem in context:
        if event == 'end' and elem.tag in tags:
            if elem.attrib['id'] == id:
                return elem
                root.clear()

def get_element(osm_file, tags=('node', 'way', 'relation')):
    """Yield element if it is the right type of tag

    Reference:
    http://stackoverflow.com/questions/3095434/inserting-newlines-in-xml-file-generated-via-xml-etree-elementtree-in-python
    """
    context = iter(ET.iterparse(osm_file, events=('start', 'end')))
    _, root = next(context)
    for event, elem in context:
        if event == 'end' and elem.tag in tags:
            yield elem
            root.clear()


def write_sample(samplefile):
    with open(samplefile, 'wb') as output:
        output.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        output.write('<osm>\n  ')

        # Write every kth top level element
        for i, element in enumerate(get_element(OSM_FILE)):
            if i % k == 0:
                output.write(ET.tostring(element, encoding='utf-8'))

        output.write('</osm>')

if __name__ == "__main__":
    write_sample(SAMPLE_FILE)

    # print ET.tostring(get_specific_element(OSM_FILE, '265347583'), encoding = 'utf-8')
