from datetime import datetime
startTime = datetime.now()
from process import clean_items
from response import get_needed_items
from notification import SendNotification
import logging


def main():
    url = 'https://www.atlantafed.org/rss/GDPNow'
    table = 'gdp'
    topic = 'economy'
    link_variable_name = 'link'
    notification_title = 'GDP Updates'

    logging.basicConfig(level=logging.INFO,filename=f"log/{table}.log", 
                        format='%(asctime)s - %(message)s', 
                        filemode='a')

    items = (get_needed_items(url, table, link_variable_name, topic))
    number_of_items = len(items)
    cleaned = clean_items(items)
    print(cleaned)
    notify = SendNotification(topic)
    recent = notify.get_recent_value(cleaned)
    message = notify.message(cleaned, recent['title'])
    notify.notification_push(table, message)
    
    logging.info(f'The total items needed are: {number_of_items}')



if __name__ == '__main__':
    main()

# def getRssContent(link):
#     session = requests.Session()
#     session.headers.update({'User-Agent': "Mozilla/5.0 (iPhone; CPU iPhone OS 13_5_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1.1 Mobile/15E148 Safari/604.1"})
#     resp = session.get(link)
#     soup = BeautifulSoup(resp.content, features="xml")
#     itemContent = soup.find_all('item')
#     return itemContent


# def getTags(content, idColumnName):
#     tagNames = []
#     # tagNames.append(idColumnName)
#     for item in content:
#         allTags = item.find_all()
#         for tag in allTags:
#             if tag.name not in tagNames:
#                 tagNames.append(tag.name)
#     return [x.lower() for x in tagNames]
            

# def getIds(content):
#     itemList = []
#     for item in content:
#         allTags = item.find_all()
#         for tag in allTags:
#             if tag.name == 'guid':
#                 itemList.append(tag.text)# here we need to look through the text and check if there are any editing tags and styling 

#     return itemList

# class DatabaseConnect():
#     def __init__(self, address:str, port:str, username:str, secret:str, dbname:str):
#         self.address = address
#         self.port = port
#         self.username = username
#         self.secret = secret
#         self.dbname = dbname
    
#     def engine(self):
#         postgres_str = (f'postgresql://{self.username}:{self.secret}@{self.address}:{self.port}/{self.dbname}')
#         engine = create_engine(postgres_str)
#         return engine

# class DatabaseFunction():
#     def __init__(self, engine, schema_name: str, table_name: str):
#         self.schema_name = schema_name
#         self.engine = engine
#         self.table_name = table_name

#     def get_package_ids(self, date: str, id_name: str) -> list: # Here we are going to get the most recent one hundred results
#         try: 
#             with self.engine.connect() as conn:
#                 if not inspect(conn).has_table(self.table_name, schema=self.schema_name):
#                     sys.exit('table does not exists! Make table in the database')
#                 metadata_obj = db.MetaData()
#                 # database name
#                 profile = Table(self.table_name, metadata_obj,
#                     (Column(f'{id_name}', db.String)),schema=self.schema_name)
            
#                 metadata_obj.create_all(conn)
#                 stmt = select(profile).order_by(text(f'"{date}" desc')).limit(100)
#                 bill_list = []
                
#                 result = conn.execute(stmt)
#                 for item in result:
#                     bill_list.append(item[0])
                    
#                 conn.close()
#                 return bill_list
#         except SQLAlchemyError as e:
#             error = str(e.__dict__['orig'])
#             return error
        
#     def get_recent_db_results(self, word_columns: list, date: str): # Here we are going to get the most recent one hundred results
#         try: 
#             with self.engine.connect() as conn:
#                 print('pulling from table: ',self.table_name)
#                 if not inspect(conn).has_table(self.table_name, schema=self.schema_name):
#                     sys.exit('table does not exists! Make table in the database')
#                 metadata_obj = db.MetaData()
#                 # database name
#                 profile = Table(self.table_name, metadata_obj,
#                     *((Column(word, db.String) for word in word_columns)),schema=self.schema_name)
            
#                 metadata_obj.create_all(conn)
#                 stmt = select(profile).order_by(text(f'"{date}" desc')).limit(100)
#                 bill_list = []
            
#                 for row in conn.execute(stmt):
                    
#                     item = (row._asdict())
#                     bill_list.append(item)
                    
#                 conn.close()
#                 df = pd.DataFrame(bill_list)
#                 return df
#         except SQLAlchemyError as e:
#             error = str(e.__dict__['orig'])
#             return error

#     def publish_results(self, df, name): # Here we are going to get a dictinoary or dataframe and publish new data
#         engine = self.engine
#         try:
#             with engine.connect() as conn:
#                 df.to_sql(name, con=engine, schema = self.schema_name, if_exists='append', index=False)
#                 conn.close()
#                 print('Connection closed')
#         except SQLAlchemyError as e:
#             print(e)

# class Differences():
#     def __init__(self, db_ids: list, web_ids: list) -> list: # the list will be unorder since we are going to get set of items
#         self.db_ids = db_ids
#         self.web_ids = web_ids
    
#     def needed_urls(self):
#         try: 
#             differences = list(set(self.web_ids) - set(self.db_ids))
#             if len(differences) > 0:
#                 print('Amount of items needed: ', len(differences))
#                 return differences
#             if len(differences) == 0:
#                 sys.exit('NO ITEMS NEEDED, DB IS UP TO DATE')
#         except Exception as err:
#             print(err)

# def getItems(content, needed_ids):
#     # initialize list
#     itemList = []
#     # iterate through items in rss feed
#     for item in content:
#         if (item.find('guid').text) in needed_ids:
#             # initialize dict
#             itemDict = {}
#             # Make sure to look for all the tags in content
#             allTags = item.find_all()
#             for tag in allTags:
#                 # make sure to look for all the tags with the name guid
#                 editText = tag.text.replace('\n', '')
#                 itemDict[tag.name] = editText # here we need to look through the text and check if there are any editing tags and styling 
#             itemList.append(itemDict)
#     return itemList

# def make_rss(dataF, filePath, fileName, tagList):
#     xml_data = [f'<rss version = "2.0" encoding="utf-8">\n<channel>\n\t<title>{fileName}</title>\n\t<link>govglance.org</link>\n\t<description/>\n\t<language>en</language>\n\n']
#     root = et.Element('channel')
#     for row in dataF.iterrows():
#         et.indent(root,space='\t')
#         # Here we are labeling the tags in the xml file, feel free to change tag names
#         report = et.SubElement(root, 'item')
        
#         for tag in tagList:
#             # Here we are labeling the tags in the xml file, feel free to change tag names
#             name = et.SubElement(report, tag)
#             name.text = str(row[1][tag])
    
#         et.indent(root,space='\t')
#         xml = et.tostring(report, pretty_print=True).decode('utf-8')
#         xml_data.append('\t')
#         xml_data.append(xml)
#         # xml_data.append('\t')
#     print('xml_data created for state id: '+fileName)
#     xml_data.append('\n</channel>\n\n</rss>')

#     print(len(xml_data))
#     with open(filePath+'/{}.xml'.format(fileName), 'w') as f:
#         for line in xml_data:
#             f.write(line)

# def push_spaces(filePath, name, schem):
#     session = boto3.session.Session()
#     client = session.client('s3',
#                             endpoint_url='https://gov-glance-state-xml.nyc3.digitaloceanspaces.com', # Find your endpoint in the control panel, under Settings. Prepend "https://".
#                             region_name='nyc3', # Use the region in your endpoint.
#                             aws_access_key_id='DO00UQRCZGBMYZA8PRA9', # Access key pair. You can create access key pairs using the control panel or API.
#                             # aws_secret_access_key=os.getenv('SPACES_SECRET')) # Secret access key defined through an environment variable.
#                             aws_secret_access_key='u5kTjaKJeSIk22VSoCn8iqHYfCfOXRgnWi+mCiqBWpA')
#     # Step 3: Call the put_object command and specify the file to upload.

#     client.put_object(Bucket=f'{schem}-xml', # The path to the directory you want to upload the object to, starting with your Space name.
#                         Key= name+'.xml', # Object key, referenced whenever you want to access this file later.
#                         Body=open(filePath+'/{}.xml'.format(name), 'rb'),# The object's contents.
#                         ACL='public-read', # Defines Access-control List (ACL) permissions, such as private or public.
#                         ContentType = 'text/xml',
#                         Metadata={ # Defines metadata tags.
#                             'x-amz-meta-content-type': 'xml'
#                         }
#                     )
# def notification_push(title, body, dir):
#     master_dir = 'gov_glance'
#     relative_path = get_path().split(master_dir, 1)[0]
#     cred = credentials.Certificate(
#         f"{relative_path}/gov_glance/firebase2/gov-glance-firebase-adminsdk-3osxk-6fc6be7677.json")
#     firebase_admin.initialize_app(cred)

#     topic = 'economyNews'
#     # topic = 'test'

#     message = messaging.Message(
#         notification=messaging.Notification(
#             title=title, body=body),
#         topic=topic,
#     )
#     # print(message)
#     messaging.send(message)

# def get_keys(keyname):
#     master_dir = 'gov_glance'
#     relative_path = get_path().split(master_dir, 1)[0]
#     with open(relative_path + 'gov_glance/secret/constants.json') as f:
#         return json.load(f)[keyname]
    
# def get_path():
#     return os.path.dirname(os.path.realpath(sys.argv[0]))

# path = get_path()
# url = "https://www.atlantafed.org/rss/GDPNow"

# POSTGRES_ADDRESS = 'db-postgresql-nyc1-03135-do-user-9254433-0.b.db.ondigitalocean.com'
# POSTGRES_PORT = '25060'
# POSTGRES_USERNAME = 'doadmin'
# POSTGRES_PASS = get_keys('Gov_glance_db')
# POSTGRES_DBNAME = 'defaultdb'

# path = get_path()
# idName = 'id'
# name_table = 'gdp'
# name_schema = 'united_states_of_america'
# notification_title = 'GDP News Updates'

# lis = getRssContent(url)
# tags = getTags(lis, idName)
# print(tags)
# ids = getIds(lis)

# engine = DatabaseConnect(POSTGRES_ADDRESS,POSTGRES_PORT,POSTGRES_USERNAME,POSTGRES_PASS,POSTGRES_DBNAME).engine()
# db_func = DatabaseFunction(engine, name_schema, name_table)
# db_ids = (db_func.get_package_ids('created_at','feed_id'))

# diff = Differences(db_ids,ids).needed_urls()
# print(len(diff))
# print(diff)

# items = getItems(lis, diff)
# print((items))
# df = pd.DataFrame.from_records(items).sort_values(by='pubDate', ascending = False)
# df.rename(columns = {'pubDate': 'created_at', 'guid':'feed_id', 'link': 'url'}, inplace = True)
# # remove the tags that are not needed
# columns = list(df.columns)

# db_func.publish_results(df, name_table)

# # columns = ["title", "created_at", "url", "description"]
# # recent = (db_func.get_recent_db_results(columns,'created_at'))
# # recent.rename(columns = {'created_at': 'pubDate'}, inplace = True)

# # make_rss(recent, path, 'gdp_watch',recent.columns)
# # push_spaces(path, 'gdp_watch', name_schema)

# most_recent_result = (df.iloc[0]['title'])
# print(most_recent_result)
# if len(df) == 1:
#     notification_message = f'{most_recent_result} is available to read'
# else:
#     notification_message = f'{most_recent_result[:80]}... and {len(df)-1} more are available to read!'

# notification_push(notification_title, notification_message, path)

# print(datetime.now() - startTime)