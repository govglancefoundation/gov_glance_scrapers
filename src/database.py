import os
import psycopg2
import logging

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
    
    def check_item(self,name, url): # the name variable is something that you write in the code block
        try:
            table = name.lower()
            self.cur.execute(f"""SELECT url FROM {self.schema}.{table} WHERE url = '{url}'""")
            results = [i[0] for i in self.cur.fetchall()]
            # print(results)
            if results:
                return True
            else:
                return False
        except Exception as e:
            logging.critical("Critical : %s", str(e))
            raise SystemExit(-1)

class WriteItems:

    def __init__(self):

        POSTGRES_USERNAME = os.environ.get('POSTGRES_USERNAME')
        POSTGRES_PASS = os.environ.get('POSTGRES_PASS')
        POSTGRES_ADDRESS = os.environ.get('POSTGRES_ADDRESS')
        POSTGRES_PORT = os.environ.get('POSTGRES_PORT')
        POSTGRES_DBNAME = os.environ.get('POSTGRES_DBNAME')
        self.schema = "united_states_of_america"
        self.connection = psycopg2.connect(host=POSTGRES_ADDRESS, user=POSTGRES_USERNAME, password=POSTGRES_PASS, dbname=POSTGRES_DBNAME, port=POSTGRES_PORT)
        self.cur = self.connection.cursor()


    def process_item(self, item, table): # Here we are going to get a dictionary or dataframe and publish new data
        try:

            table_name = table.lower().replace(' ', '_')
            schema = self.schema
            columns = ', '.join(item.keys())
            values = ', '.join('%({})s'.format(key) for key in item.keys())
            # values = ', '.join('%({})s'.format(key) if not 'references' else 'ARRAY[%({})s]::TEXT[]'.format(key) for key in item.keys())
            query = f"INSERT INTO {schema}.{table_name} ({columns}) VALUES ({values})"
            # print(query)
            self.cur.execute(query, item)
            self.connection.commit()
        except Exception as e:
            logging.critical("Critical : %s", str(e))

