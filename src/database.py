import os
import psycopg2
import logging
from psycopg2 import errors

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
    
    def check_item(self,name, url): # the name variable is something that you write in the code block
        try:
            
            table = name.lower().replace(' ', '_')
            self.cur.execute(f"""SELECT url FROM {self.schema}.{table} WHERE url = '{url}'""")
            results = [i[0] for i in self.cur.fetchall()]
            if results:
                print(url +'exists!')
                return True
            else:
                return False
        except errors.UndefinedTable as e:
            # Handle the UndefinedTable exception here
            logging.info(f"The table {table} does not exist.")
            return False            
        except Exception as e:
            logging.critical("Critical : %s", str(e))
            raise SystemExit(-1)
        
        finally: 
            self.cur.close()
            self.connection.close()
            print("Connection closed.")

class WriteItems:

    def __init__(self, schema):

        POSTGRES_USERNAME = os.environ.get('POSTGRES_USERNAME')
        POSTGRES_PASS = os.environ.get('POSTGRES_PASS')
        POSTGRES_ADDRESS = os.environ.get('POSTGRES_ADDRESS')
        POSTGRES_PORT = os.environ.get('POSTGRES_PORT')
        POSTGRES_DBNAME = os.environ.get('POSTGRES_DBNAME')
        self.schema = schema
        self.connection = psycopg2.connect(host=POSTGRES_ADDRESS, user=POSTGRES_USERNAME, password=POSTGRES_PASS, dbname=POSTGRES_DBNAME, port=POSTGRES_PORT)
        self.cur = self.connection.cursor()


    def process_item(self, items, table, topic): # Here we are going to get a dictionary or dataframe and publish new data
        try:
            for item in items:
                schema = self.schema
                table_name = table.lower().replace(' ', '_')

                print(table_name)
                '''if table does not exist, create it'''
                columns = []

                """
                - Here we can add description if we do not have it in the key of items
                - We added a condition to look for created_at to add it as a timestamp with timezone for consistency 
                - 

                """
                columns.append("id integer NOT NULL GENERATED ALWAYS AS IDENTITY ( INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 2147483647 CACHE 1 )")

                if 'description' not in item.keys():
                    columns.append("description VARCHAR")
                
                for key in item.keys():
                    if key == 'created_at':
                        columns.append(f'{key} timestamp with time zone')
                    else:
                        columns.append(f"{key} VARCHAR")

                # columns = [f"{key} VARCHAR" for key in item.keys()] # removed this code and made it so it looks for craeted at 
                
                '''
                These appends are gor the columns that every table will need like id, topic, and collected_at
                '''
                collection_name = table.title().replace('_', ' ')
                columns.append(f"""topic character varying COLLATE pg_catalog."default" DEFAULT '{topic}'::character varying""")
                columns.append(f"""collection_name character varying COLLATE pg_catalog."default" DEFAULT '{collection_name}'::character varying""")

                columns.append(f"""CONSTRAINT {table_name}_pkey PRIMARY KEY (id)""")
                columns.append("collected_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP")
                columns.append("ts tsvector GENERATED ALWAYS AS (to_tsvector('english'::regconfig, title)) STORED")

               # Constructing the full query
                query = f"CREATE TABLE IF NOT EXISTS {schema}.{table_name} ({', '.join(columns)})"
                self.cur.execute(query)

                '''Inserting the data into the table'''
               
                columns = ', '.join(item.keys())
                values = ', '.join('%({})s'.format(key) for key in item.keys())
                print(item)
                query = f"INSERT INTO {schema}.{table_name} ({columns}) VALUES ({values})"
                print(f"Item inserted to {schema}.{table_name}")
                self.cur.execute(query, item)
                self.connection.commit()
                logging.info(f"Value inserted {query}")
        
        except errors.UndefinedColumn as err:
            # Handle the UndefinedTable exception here
            print(item)
            logging.info(f"The column {table} does not exist.")
        
        except Exception as e:
            logging.critical("Critical : %s", str(e))
        
        finally:
            self.cur.close()
            self.connection.close()
            print("Connection closed.")