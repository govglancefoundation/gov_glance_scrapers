import requests
from xml.etree.ElementTree import Element, tostring
from xml.dom import minidom
# import boto3
from datetime import datetime, timedelta
startTime = datetime.now()
import os, sys
# import pandas as pd
import firebase_admin
from firebase_admin import credentials, messaging
import json 
import boto3
# state_codes = ['AL','CO','NY']
# ,"AL","AK","AZ","AR","CA","CO","CT","DE","DC","FL","GA","HI","ID","IL","IN","IA","KS","KY","LA","ME","MD","MA","MI","MN","MS","MO","MT","NE","NV","NH","NJ","NM","NY","NC","ND","OH","OK","OR","PA","PR","RI","SC","SD","TN","TX","UT","VT","VA","WA","WV","WI","WY"]
apikey = 'AIzaSyAziQidVEBcVQNcKJ56E_mdJmXpM4bOMxU'

url = f'https://www.googleapis.com/civicinfo/v2/elections?key={apikey}'

class Differences():
    def __init__(self, db_urls: list, web_urls: list) -> list: # the list will be unorder since we are going to get set of items
        self.db_urls = db_urls
        self.web_urls = web_urls
    
    def needed_urls(self):
        try: 
            print("\n items in db: \n", self.db_urls[:10])
            differences = list(set(self.web_urls) - set(self.db_urls))
            if len(differences) > 0:
                print('\n---------------------\nThere are similarities, printing out the amount of differences: \n---------------------\n')
                print('Amount of items needed: ', len(differences))
                return differences
            if len(differences) == 0:
                sys.exit('NO ITEMS NEEDED, DB IS UP TO DATE')
        except Exception as err:
            print(err)

def get_json(url: str) -> dict:
    response = requests.get(url)
    return (response.json())

def get_civic_info(elections: str, apikey: str ) -> dict:
    url = f'https://www.googleapis.com/civicinfo/v2/{elections}?key={apikey}'
    content = get_json(url)
    (content['elections']).pop(0)
    return content['elections']

def dict_to_xml(tag: str, d: dict):
 
    elem = Element(tag)
    for key, val in d.items():
        child = Element(key)
        child.text = str(val)
        elem.append(child)
         
    return elem

def push_spaces(filePath, name, schem,fileName):
    session = boto3.session.Session()
    client = session.client('s3',
                            endpoint_url='https://gov-glance-state-xml.nyc3.digitaloceanspaces.com', # Find your endpoint in the control panel, under Settings. Prepend "https://".
                            region_name='nyc3', # Use the region in your endpoint.
                            aws_access_key_id='DO00XP7FXWXLU9VLEBLD', # Access key pair. You can create access key pairs using the control panel or API.
                            # aws_secret_access_key=os.getenv('SPACES_SECRET')) # Secret access key defined through an environment variable.
                            aws_secret_access_key='7kyckkV7MEGXLshIWFkgt8dqRLoqsh/tDqLuhwV+TtM')
    # Step 3: Call the put_object command and specify the file to upload.

    client.put_object(Bucket=f'{schem}-xml', # The path to the directory you want to upload the object to, starting with your Space name.
                        Key= name+'.xml', # Object key, referenced whenever you want to access this file later.
                        Body=open(filePath+'/xml/{}.xml'.format(fileName), 'rb'),# The object's contents.
                        ACL='public-read', # Defines Access-control List (ACL) permissions, such as private or public.
                        ContentType = 'text/xml',
                        Metadata={ # Defines metadata tags.
                            'x-amz-meta-content-type': 'xml'
                        }
                    )

# def notification_push(title, body, dir):
#     path = dir.replace('/civic_clerk/elections', '')
#     cred = credentials.Certificate(
#         f"{path}/firebase2/gov-glance-firebase-adminsdk-3osxk-6fc6be7677.json")
#     firebase_admin.initialize_app(cred)

#     topic = 'allUSNews'
#     # topic = 'test'

#     message = messaging.Message(
#         notification=messaging.Notification(
#             title=title, body=body),
#         topic=topic,
#     )
#     messaging.send(message)

def make_dict_xml(fileName, dir, content):
    xml_data = [f'<rss version = "2.0" encoding="utf-8">\n<channel>\n\t<title>{fileName}</title>\n\t<link>govglance.org</link>\n\t<description/>\n\t<language>en</language>\n']
    for i in content:
        e = dict_to_xml('item', i)
        pretty = minidom.parseString(tostring(e)).toprettyxml(indent="\t\t").replace('<?xml version="1.0" ?>','').replace('<item>','\t<item>').replace('</item>', '\t</item>')
        xml_data.append(pretty)
    print(xml_data)
    with open(dir+f'/xml/{fileName}.xml','w') as f:
            for line in xml_data:
              f.write('\t'+(line))

    ending = ('\n</channel>\n\n</rss>')
    with open(dir+f'/xml/{fileName}.xml','a') as f:
        f.write(ending)

def get_path():
    return os.path.dirname(os.path.realpath(sys.argv[0]))

schema_name = 'civic_clerk'
table_name = 'elections_data'
'''
pull from api
'''
new_data = (get_civic_info('elections', apikey))
for i in range(len(new_data)):
        if new_data[i]['name'] == 'VIP Test Election':
            del new_data[i]
            break

print(new_data)
id_list_new = [ sub['id'] for sub in new_data]
print(id_list_new)
'''
get elections and compare to previous json file. return the differences
'''

f = open(get_path()+"/{}.json".format(table_name), "r")
print(f)
if f is not None:
    old_data = json.load(f)

    print(old_data)

    id_list_old = [ sub['id'] for sub in old_data ]

    print(id_list_old)
    diff = Differences(id_list_old,id_list_new).needed_urls()
    print(len(diff))
    print(diff)
else:
    diff = []
needed_data = []
for item in new_data:
    if item['id'] in diff:
        needed_data.append(item)

# # the values here are going to be used to send the notification message
print(needed_data)
# needed_data_df = pd.DataFrame(needed_data).sort_values(by='electionDay', ascending=False)

# # # '''
# # # make data into dataframe
# # # '''

# df = pd.DataFrame(new_data).sort_values(by='electionDay', ascending=False)
# print(df['name'])

# # # '''
# # # get the title of the different value and same to a variable
# # # '''

# title = needed_data_df.iloc[0]['name']
# date = needed_data_df.iloc[0]['electionDay']

# if len(needed_data_df) == 1:
#     notification_message = (f'The {title}  is coming up on {date}. Check it out!')
# else:
#     notification_message = f'{title} is coming up on {date} and {len(needed_data_df)-1} more are available to view!'


json_string = json.dumps(new_data, indent =4)
with open(get_path() + '/{}.json'.format(table_name), "w") as outfile:
    outfile.write(json_string)

make_dict_xml(table_name,get_path(),new_data)

push_spaces(get_path(),table_name,schema_name,table_name)

# print(notification_message)

# notification_push('U.S. Elections', notification_message, get_path())
print(datetime.now() - startTime)