
# coding: utf-8

# # Library imports and file definitions

# In[1]:

#!/usr/bin/env python


import xml.etree.cElementTree as ET
import pprint
import re
from collections import defaultdict
import codecs
import json

directory = '/Users/DerekAtWork/Google Drive/Data Science/Udacity/Project3.Data Wrangling with MongoDB/'
#directory = '/Users/DerekAtWork/GitHub/Udacity/Project3'

#sample = True
sample = False

if sample:
    print "Using sample"
    osmfile = directory + 'sample.osm'
    jsonfile = osmfile + ".json"  
else:
    print "Using complete file"
    osmfile = directory + 'vancouver_canada.osm'
    jsonfile = osmfile + ".json"
print osmfile
print jsonfile
filename = osmfile


# # Code for creating sample

# In[13]:

'''
#!/usr/bin/env python
# -*- coding: utf-8 -*-

import xml.etree.ElementTree as ET  # Use cElementTree or lxml if too slow
'''

OSM_FILE = osmfile  # Replace this with your osm file
SAMPLE_FILE = directory + "sample.osm"

k = 20 # Parameter: take every k-th top level element

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


with open(SAMPLE_FILE, 'wb') as output:
    output.write('<?xml version="1.0" encoding="UTF-8"?>\n')
    output.write('<osm>\n  ')

    # Write every kth top level element
    for i, element in enumerate(get_element(OSM_FILE)):
        if i % k == 0:
            output.write(ET.tostring(element, encoding='utf-8'))

    output.write('</osm>')


# # Key Types
# [Same as Lesson 6 code]

# In[15]:

"""
Your task is to explore the data a bit more.
Before you process the data and add it into MongoDB, you should check the "k"
value for each "<tag>" and see if they can be valid keys in MongoDB, as well as
see if there are any other potential problems.

We have provided you with 3 regular expressions to check for certain patterns
in the tags. As we saw in the quiz earlier, we would like to change the data
model and expand the "addr:street" type of keys to a dictionary like this:
{"address": {"street": "Some value"}}
So, we have to see if we have such tags, and if we have any tags with
problematic characters.

Please complete the function 'key_type', such that we have a count of each of
four tag categories in a dictionary:
  "lower", for tags that contain only lowercase letters and are valid,
  "lower_colon", for otherwise valid tags with a colon in their names,
  "problemchars", for tags with problematic characters, and
  "other", for other tags that do not fall into the other three categories.
See the 'process_map' and 'test' functions for examples of the expected format.
"""


lower = re.compile(r'^([a-z]|_)*$')
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')


def key_type(element, keys):
    if element.tag == "tag":
        # Note to self: This is code I added to template
        key = element.get("k") 
        #print key
        if re.match(lower, key): #Note to self: match starting from beginning of string
            keys["lower"] += 1
            #keys["lower"].append(key)
            #print key
        elif re.match(lower_colon, key): 
            keys["lower_colon"]  += 1
            #keys["lower_colon"].append(key)
            #print key
        elif  re.search(problemchars, key): #search anywhere
            keys["problemchars"]  += 1
            #keys["problemchars"].append(key)
             #print key
        else:
            keys["other"]  += 1

                #keys["other"].append(key) 
                #print key       
    return keys



def process_map(filename):
    keys = {"lower": 0, "lower_colon": 0, "problemchars": 0, "other": 0}
    for _, element in ET.iterparse(filename):
        keys = key_type(element, keys)

    return keys

print "Using " + osmfile
process_map(osmfile)


# # Users
# [Same as Lesson 6 code]

# In[16]:

def get_user(element):
    return


def process_map(filename):
    users = set()
    for _, element in ET.iterparse(filename):
        pass
        if element.tag == "node":
            user = element.get("user") 
            if user not in users:
                users.add(user) #Pedagogical note: not users.append(user) because users is a set, not a dict

    return users

pprint.pprint(process_map(osmfile))


# # Auditing 

# In[12]:


############ Street types

street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)

expected_street = ["Street", "Avenue", "Boulevard", "Drive", "Alley", "Broadway", "Walk","Crescent", "Esplanade", "Highway","Kingsway","Mews","Mall","Court", "Place", "Square", "Lane", "Road", 
            "Trail", "Parkway", "South","Commons","Way","West","East"]


def audit_street_type(street_types, street_name):
    '''If the street type is not in the list of expected types, adds the type to a dictionary.'''
    m = street_type_re.search(street_name)
    if m:
        street_type = m.group()
        if street_type not in expected_street:
            street_types[street_type].add(street_name)


def is_street_name(elem):
    '''Checks if elem.attrib['k'] is addr:street.'''
    return (elem.attrib['k'] == "addr:street")


############ City Names

expected_city = ['Vancouver', 'North Vancouver', 'Richmond','North Vancouver City']

def audit_city_name(city_names, city_name):
    '''If the city name is not in the list of expected cities, adds the city to a dictionary.'''
    if city_name not in expected_city:
        city_names[city_name].add(city_name)

def is_city_name(elem):
    '''Checks if elem.attrib['k'] is addr:city.'''
    return (elem.attrib['k'] == "addr:city")


############ Province
expected_prov = ['British Columbia']

def audit_prov_name(prov_names, prov_name):
    '''If the province is not in the list of expected provinces, adds the province to a dictionary.'''
    if prov_name not in expected_prov:
        prov_names[prov_name].add(prov_name)

def is_prov_name(elem):
    '''Checks if elem.attrib['k'] is addr:province.'''    
    return (elem.attrib['k'] == "addr:province")

############ Postal Codes

expected_postalcodes_re = re.compile(r'V[5|6][A-Z] [0-9][A-Z][0-9]$')

def audit_postal_code(postal_codes, postal_code):
    '''If the postal code is not in the expected format, add the postal code to a dictionary.'''
    if not expected_postalcodes_re.search(postal_code):
        postal_codes[postal_code].add(postal_code)

    '''
    Pseudo code:
    postalcoce_missing_space_re = 
    if postalcode_missing_spacewithspace
        postal_codes
    #could maybe expand to modify vs flag
        
    
    '''
        
        
        
def is_postal_code(elem):
    '''Checks if elem.attrib['k'] is addr:postcode.'''    
    return (elem.attrib['k'] == "addr:postcode")


############ MAIN AUDIT

def audit(osmfile):
    '''Reads osmfile and returns a dictionaries of unexpected entries for the following:
    Street types (Drive, Road, etc..)
    City names
    Province names
    Postal codes.'''
    osm_file = open(osmfile, "r")
    street_types = defaultdict(set)
    city_names = defaultdict(set)
    prov_names = defaultdict(set)
    postal_codes = defaultdict(set)
    for event, elem in ET.iterparse(osm_file, events=("start",)):

        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_street_name(tag):
                    audit_street_type(street_types, tag.attrib['v'])
                if is_city_name(tag):
                    audit_city_name(city_names, tag.attrib['v'])
                if is_prov_name(tag):
                    audit_prov_name(prov_names, tag.attrib['v'])
                if is_postal_code(tag):
                    audit_postal_code(postal_codes, tag.attrib['v'])
    osm_file.close()
    return street_types, city_names, prov_names, postal_codes

def update_name_with_mapping(name, mapping):

    for key, value in mapping.iteritems():
        key_at_end = re.escape(key) + r"$"
        name = re.sub(key_at_end, value, name)

    return name

def update_name_with_mapping(name, mapping):

    for key, value in mapping.iteritems():
        key_at_end = re.escape(key) + r"$"
        name = re.sub(key_at_end, value, name)

    return name

def update_name_with_formula(name, mapping):

    for key, value in mapping.iteritems():
        key_at_end = re.escape(key) + r"$"
        name = re.sub(key_at_end, value, name)

    return name



# In[6]:

st_types, cty_names, prv_names, pstl_codes = audit(osmfile)


# # Updating Street Types
# [Same as Lesson 6 code]

# In[15]:

mapping_street = { "Blvd": "Boulevard",
            "St": "Street",
            "St.": "Street",
            "Ave": "Avenue",
            "Rd.": "Road",
            "Steet": "Street",
            "street": "Street",
            "venue": "Avenue",
            "Broughton": "Broughton Street",
            "Jervis": "Jervis Street",
            "Jarvis": "Jervis Street"
            }

pprint.pprint(dict(st_types))
for st_type, ways in st_types.iteritems():
    for name in ways:
        better_name = update_name_with_mapping(name, mapping_street)
print(better_name)


# # Updating City Names
# [Adapted from Lesson 6 code]

# In[8]:

mapping_city = { "Vancovuer": "Vancouver",
            "vancouver": "Vancouver",
            }

pprint.pprint(dict(cty_names))
for cty_names, ways in cty_names.iteritems():
    for name in ways:
        better_name = update_name_with_mapping(name, mapping_city)


# # Updating Province Name
# [Same as Auditing City Name; I realize that it would be better to have these functions be generic, so that they could handle both city names and province names, but I didn't have time to implement that.]

# In[9]:

mapping_prov = { "BC": "British Columbia",
            "B.C.": "British Columbia",
            "bc": "British Columbia",
            }

pprint.pprint(dict(prv_names))
for st_type, ways in prv_names.iteritems():
    for name in ways:
        better_name = update_name_with_mapping(name, mapping_prov)
#'''


# # Updating Postal Codes
# [Adapted from Auditing City Name]

# In[10]:

#'''
pprint.pprint(dict(pstl_codes))
for pstl_codes, ways in pstl_codes.iteritems():
    for name in ways:
        better_name = update_name(name, mapping)
#'''


# # Code for printing out file

# In[17]:

def shape_element(element):
    print element
    if element.tag == "node" or element.tag == "way" or element.tag == "relation" :
        for key, value in element.attrib.iteritems():
            print 'key', 'value', key, value
        

        for child in element:
            print 'child', child
            for key, value in child.attrib.iteritems():
                print "key, value", key, value


# # Code for preparing for MongoDB

# In[28]:

lower = re.compile(r'^([a-z]|_)*$')
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

CREATED = [ "version", "changeset", "timestamp", "user", "uid"]


def shape_element(element):
    node = {}
    if element.tag == "node" or element.tag == "way" :
        # Note to self: This is code I added to template
        this_created = {}
        node['type'] = element.tag
        # based on https://discussions.udacity.com/t/my-code-is-not-finding-a-specific-tag-attribute/157674/5
        
        for key, value in element.attrib.iteritems():
            #attributes in the CREATED array should be added under a key "created"
            #attributes for latitude and longitude should be added to a "pos" array,for use in geospacial indexing. Make sure the values inside "pos" array are floats and not strings. 
            created_list = ['version','changeset','timestamp','user','uid']
            if key in created_list:
                this_created[key] = element.attrib[key]
            
            elif key == 'lon':
                pass      # will be dealt with in 'lat' 
            elif key == 'lat': 
                node['pos'] = [float(element.attrib['lat']), float(element.attrib['lon'])]          
            else:
                node[key] = value
        node['created'] = this_created
        if element.tag == "way":
            node['node_refs'] = []
                
            #if the second level tag "k" value starts with "addr:", it should be added to a dictionary "address"
        this_address = {}
        keyfornode = ""
        for child in element: #note: not an interior loop of above, though 
            for key, value in child.attrib.iteritems():
                #if the second level tag "k" value contains problematic characters, it should be ignored
                if 'k' in child.attrib: #make sure that there is a key tag
                    if  re.search(problemchars, child.attrib['k']):     
                        print "k Has problem chars: ", child.attrib['k']
                    elif re.match('addr:',child.attrib['k']): #if k tag starts with addr:
                        if child.attrib['k'].count(':') > 1: #if k tag has 2 colons, ignore
                            pass
                        else:
                            temp = child.attrib['k'].split(':')[1]
                            this_address[temp] = child.attrib['v']
                            #insert here
                    
                    elif child.attrib['k'].count(':') > 0: #if k tag does not start with addr: but has a colon
                        if child.attrib['k'].count(':') > 1: #if k tag has 2 colons, ignore
                            pass
                        else:
                            # capture the content before the colon
                            if keyfornode == "" or keyfornode != child.attrib['k'].split(':')[0]:
                                keyfornode = child.attrib['k'].split(':')[0]
                                this_other = {}
                            subkey = child.attrib['k'].split(':')[1]
                            this_other[subkey] = child.attrib['v']
                            node[keyfornode] = this_other #update
                    else:
                        node[child.attrib['k']] = child.attrib['v']
                elif 'ref' in child.attrib:
                    node['node_refs'].append(child.attrib['ref'])
                elif 'v' not in child.attrib:
                     print 'the child.attrib is something other than k, v, or ref: ', child.attrib
                   
                else:
                    pass
        if this_address: #if this_address is not empty
            node['address'] = this_address

        
        return node
    else:
        return None




# # Code for dumping to JSON

# In[30]:

def process_map(file_in, pretty = False):
    # Note from Udacity: You do not need to change this file
    file_out = "{0}.json".format(file_in)
    data = []
    with codecs.open(file_out, "w") as fo:
        for _, element in ET.iterparse(file_in):
            el = shape_element(element)
            if el:
                data.append(el)
                if pretty:
                    fo.write(json.dumps(el, indent=2)+"\n")
                else:
                    fo.write(json.dumps(el) + "\n")
    return data
data = process_map(osmfile, False)

