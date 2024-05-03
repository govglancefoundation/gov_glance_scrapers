import psycopg2
import os
import logging
from xml.etree.ElementTree import Element, tostring
from xml.dom import minidom
import xml.etree.ElementTree as ET


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

    def getItems(self):
        # initialize list
        itemList = []
        # iterate through items in rss feed
        for item in self.content:
            
            # initialize dict
            itemDict = {}
            # Make sure to look for all the tags in content
            a_tag = item.find('a')
            if a_tag:
                a_tag.decompose()
            allTags = item.find_all()
            for tag in allTags:
                """
                -------------- Add specific tags here and unique operations --------------
                """
                # if tag.name =='enclosure':
                #     print(tag.text)

                # else:
                editText = tag.text.replace('\n', '')
                itemDict[tag.name] = editText
                # here we need to look through the text and check if there are any editing tags and styling 
            itemList.append(itemDict)
        return itemList

class ReadArticles:

    def __init__(self, schema):
            
        POSTGRES_USERNAME = os.environ.get('POSTGRES_USERNAME')
        POSTGRES_PASS = os.environ.get('POSTGRES_PASS')
        POSTGRES_ADDRESS = os.environ.get('POSTGRES_ADDRESS')
        POSTGRES_PORT = os.environ.get('POSTGRES_PORT')
        POSTGRES_DBNAME = os.environ.get('POSTGRES_DBNAME')
        self.schema = schema
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
        