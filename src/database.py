import os
import psycopg2
import logging
from psycopg2 import errors


class CheckColumns:
    def __init__(self):

        POSTGRES_USERNAME = os.environ.get('POSTGRES_USERNAME')
        POSTGRES_PASS = os.environ.get('POSTGRES_PASS')
        POSTGRES_ADDRESS = os.environ.get('POSTGRES_ADDRESS')
        POSTGRES_PORT = os.environ.get('POSTGRES_PORT')
        POSTGRES_DBNAME = os.environ.get('POSTGRES_DBNAME')
        self.connection = psycopg2.connect(host=POSTGRES_ADDRESS, user=POSTGRES_USERNAME, password=POSTGRES_PASS, dbname=POSTGRES_DBNAME, port=POSTGRES_PORT)
        self.cur = self.connection.cursor()

    def find_column_names(self, schema_name, table_name):
        try:
            self.cur.execute(f'SELECT * FROM {schema_name}.{table_name} LIMIT 0')
            table_keys = [desc[0] for desc in self.cur.description]
        except Exception as e:
            logging.critical("Critical : %s", str(e))

        finally:
            self.cur.close()
            self.connection.close()
            
        return table_keys
    
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
            query = '''SELECT url FROM {schema}.{table} WHERE url = %s'''.format(schema=self.schema, table=table)
            self.cur.execute(query, (url,))
            results = [i[0] for i in self.cur.fetchall()]
            if results:
                print(url +' ALREADY EXISTS!')
                return True
            else:
                print(url + " IS NEEDED!!!")
                return False
        except errors.UndefinedTable as e:
            # Handle the UndefinedTable exception here
            logging.info(f"The table {table} does not exist.")
            return False            
        except Exception as e:
            logging.critical("Critical : %s", str(e), url)
            print(name, url)
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
                
                if 'category' not in item.keys():
                    columns.append("category VARCHAR")
                for key in item.keys():
                    if key == 'created_at':
                        columns.append(f'{key} timestamp with time zone')
                    elif key in ['table_summary', 'sessions']:
                        columns.append(f'{key} jsonb')
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

                '''
                The code appends the script if the values are the same
                '''

                query = f"INSERT INTO {schema}.{table_name} ({columns}) VALUES ({values}) RETURNING id;"
                self.cur.execute(query, item)
                
                
                id_of_new_row = self.cur.fetchone()[0]
                print(f"id for inserted item {id_of_new_row}")
                query = f"INSERT INTO world_search_results (id, source, schema_source, ts) VALUES (%s, %s, %s, to_tsvector('english'::regconfig, %s));"
                self.cur.execute(query, (id_of_new_row, table_name, schema, item['title'] ))

                print(f"Item inserted to {schema}.{table_name}")
                self.connection.commit()

        except errors.UndefinedColumn as err:
            # Handle the UndefinedTable exception here
            print(item)
            logging.info(f"Error: {err}")
        
        except Exception as e:
            logging.critical("Critical : %s", str(e))
            print(item)
        
        finally:
            self.cur.close()
            self.connection.close()
            print("Connection closed.")
        
    def process_dynamic_columns(self, items, table, topic):
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
                
                if 'category' not in item.keys():
                    columns.append("category VARCHAR")
                for key in item.keys():
                    if key == 'created_at':
                        columns.append(f'{key} timestamp with time zone')
                    elif key in ['table_summary', 'sessions']:
                        columns.append(f'{key} jsonb')
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

                '''
                The code appends the script if the values are the same
                '''
                query = f"INSERT INTO {schema}.{table_name} ({columns}) VALUES ({values}) RETURNING id;"
                self.cur.execute(query, item)

                id_of_new_row = self.cur.fetchone()[0]
                print(f"id for inserted item {id_of_new_row}")
                query = f"INSERT INTO world_search_results (id, source, schema_source, ts) VALUES (%s, %s, %s, to_tsvector('english'::regconfig, %s));"
                self.cur.execute(query, (id_of_new_row, table_name, schema, item['title'] ))

                print(f"Item inserted to {schema}.{table_name}")
                self.connection.commit()

        except errors.UndefinedColumn as err:
            to_append_keys = list(item.keys())
            table_keys = CheckColumns().find_column_names(schema, table_name)

            difference_result = [item for item in to_append_keys if item not in table_keys]
            column_with_datatype = [f"{column} VARCHAR" for column in difference_result]
            alter = AlterTable()
            alter.alter_table(table_name,schema, column_with_datatype)
            alter.process_item(item, table_name, schema, columns, values)
            logging.info(f"Error: {err} ------ Running ALTER TABLE class and functionsKeys Needed: {difference_result}")

        except Exception as e:
            logging.critical("Critical : %s", str(e))
            print(item)
        
        finally:
            self.cur.close()
            self.connection.close()
            print("Connection closed.")



class AlterTable:

    def __init__(self):

        POSTGRES_USERNAME = os.environ.get('POSTGRES_USERNAME')
        POSTGRES_PASS = os.environ.get('POSTGRES_PASS')
        POSTGRES_ADDRESS = os.environ.get('POSTGRES_ADDRESS')
        POSTGRES_PORT = os.environ.get('POSTGRES_PORT')
        POSTGRES_DBNAME = os.environ.get('POSTGRES_DBNAME')
        self.connection = psycopg2.connect(host=POSTGRES_ADDRESS, user=POSTGRES_USERNAME, password=POSTGRES_PASS, dbname=POSTGRES_DBNAME, port=POSTGRES_PORT)
        self.cur = self.connection.cursor()

    def alter_table(self, table_name, schema, needed_columns):
        try:
            query = f"ALTER TABLE {schema}.{table_name} ADD COLUMN {', '.join(needed_columns)}"
            self.cur.execute(query)
            self.connection.commit()
        except Exception as e:
            logging.critical("Critical : %s", str(e))

    def process_item(self, item, table_name, schema, columns, values):
        try:
            query = f"INSERT INTO {schema}.{table_name} ({columns}) VALUES ({values}) RETURNING id;"
            self.cur.execute(query, item)
            self.connection.commit()
        except Exception as e:
            logging.critical("Critical : %s", str(e))
            print(item)
    
    