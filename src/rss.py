from datetime import datetime
startTime = datetime.now()
import psycopg2
import os
import logging
from xml.etree.ElementTree import Element, tostring
from xml.dom import minidom

'''
One issue is trying to figure out how to get the xml in the right location
'''

def xml_tags(content):
    tagNames = []
    # tagNames.append(idColumnName)
    for item in content:
        allTags = item.find_all()
        for tag in allTags:
            if tag.name not in tagNames:
                tagNames.append(tag.name)
    return [x.lower() for x in tagNames]

'''
When we parse the xml file we need to spit out a dictionary when we are done parsing. This will allow the pipeline to work without any issues. 

xmltodict is not working for parsing the speeches_statements xml feed.
'''

class ParseXml:
    def __init__(self, content):
        self.content = content

    
    def getTags(self):
        tagNames = []
        # tagNames.append(idColumnName)
        for item in self.content:
            allTags = item.find_all()
            for tag in allTags:
                if tag.name not in tagNames:
                    tagNames.append(tag.name)
        return [x.lower() for x in tagNames]

    def getItems(self):
        # initialize list
        itemList = []
        # iterate through items in rss feed
        for item in self.content:
            
            # initialize dict
            itemDict = {}
            # Make sure to look for all the tags in content
            allTags = item.find_all()
            for tag in allTags:
                # make sure to look for all the tags with the name guid
                editText = tag.text.replace('\n', '')
                itemDict[tag.name] = editText 
                # here we need to look through the text and check if there are any editing tags and styling 
            itemList.append(itemDict)
        return itemList

class ReadArticles:

    def __init__(self):
            
        POSTGRES_USERNAME = os.environ.get('POSTGRES_USERNAME')
        POSTGRES_PASS = os.environ.get('POSTGRES_PASS')
        POSTGRES_ADDRESS = os.environ.get('POSTGRES_ADDRESS')
        POSTGRES_PORT = os.environ.get('POSTGRES_PORT')
        POSTGRES_DBNAME = os.environ.get('POSTGRES_DBNAME')
        self.schema = "united_states_of_america"
        self.connection = psycopg2.connect(host=POSTGRES_ADDRESS, user=POSTGRES_USERNAME, password=POSTGRES_PASS, dbname=POSTGRES_DBNAME, port=POSTGRES_PORT)
        self.cur = self.connection.cursor()
    
    def items_to_dict(self,name): # the name variable is something that you write in the code block
        try:
            table = name.lower()
            self.cur.execute(f"""SELECT * FROM {self.schema}.{table} ORDER BY created_at DESC LIMIT 100""")
            results = results = [i for i in self.cur.fetchall()]
            columns = [desc[0] for desc in self.cur.description]
            result_dict_list = []
            for row in results:
                result_dict = {}
                for idx, column in enumerate(columns):
                    result_dict[column] = row[idx]
                result_dict_list.append(result_dict)
            return result_dict_list
        except Exception as e:
            logging.critical("Critical : %s", str(e))
            raise SystemExit(-1)
        
def dict_to_xml(tag: str, d: dict):
    '''
    Turn a simple dict of key/value pairs into XML
    '''
    elem = Element(tag)
    for key, val in d.items():
        child = Element(key)
        child.text = str(val)
        elem.append(child)
    return elem
    # elem = Element(tag)
    # for key, val in d.items():
    #     if val != None:
    #         val = val
    #     else:
    #         val = ''
    #     child = Element(key)
    #     child.text = str(val)
    #     elem.append(child)
    # return elem

# def generate_xml(dir,file_name,content):
def list_of_dicts_to_xml(tag, l):
        root = Element(tag)
        for d in l:
            root.append(dict_to_xml('item', d))
        return root
        # name_lower = file_name.lower()
        # name_no_underscore = file_name.replace('_', ' ')
        # xml_data = [f'<rss version = "2.0" encoding="utf-8">\n<channel>\n\t<title>{name_no_underscore}</title>\n\t<link>govglance.org</link>\n\t<description/>\n\t<language>en</language>\n']
        # for i in content:
        #     e = dict_to_xml('item', i)
        #     pretty = minidom.parseString(tostring(e)).toprettyxml(indent="\t\t").replace('<?xml version="1.0" ?>','').replace('<item>','\t<item>').replace('</item>', '\t</item>')
        #     xml_data.append(pretty)

        # ending = ('\n</channel>\n\n</rss>')
        # xml_data.append(ending)
        # return xml_data

def generate_xml(data):
    xml_root = list_of_dicts_to_xml('item', data)

    # Save XML content to a list
    xml_list = []
    xml_list.append(tostring(xml_root))
    return xml_list[0]
"""
I think it would make sense to create a different file/project that takes a list of all the table in a schema and then runs this function so anytime there is a new item being added the xml file is updated
"""

# print(generate_xml(data=(ReadArticles().items_to_dict('bea'))))

print(datetime.now() - startTime)

