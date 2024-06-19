import re
import dateutil.parser
import logging
import html



def camel_to_snake_case(key):
    """
    Convert camelCase string to snake_case, keeping only letters and numbers.
    """
    # Replace special characters with underscores
    key = re.sub(r'[^a-zA-Z0-9]', '', key)
    # Convert camelCase to snake_case
    return re.sub(r'(?<!^)(?=[A-Z0-9])', '_', key).lower()

def convert_keys_to_snake_case(dictionary):
    """
    Convert all keys in a dictionary from camelCase to snake_case.
    """
    new_dict = {}
    for key, value in dictionary.items():
        
        new_key = camel_to_snake_case(key)
        new_key = new_key.replace("link", "url") # Replace any instance of link with url
        new_dict[new_key] = value
    return new_dict

def replace_key(dictionary, **kwargs):
    """
    Replace keys in a dictionary with new keys.
    """
    for old_key, new_key in kwargs.items():
        if old_key in dictionary:
            dictionary[new_key] = dictionary.pop(old_key)
    return dictionary

def clean_description(description):
    # Remove the specific HTML comment and anchor tag
    cleaned_description = re.sub(r'<!--Full Text Link--><a[^>]*>Full Text</a><!--Full Text Link-->', '', description)
    # Remove HTML tags
    cleaned_description = re.sub(r'<[^>]*>', ' ', cleaned_description)
    # Remove extra whitespaces and newline characters
    cleaned_description = re.sub(r'\s+', ' ', cleaned_description)
    pattern = r'^p(.*?)\/p$'
    match = re.match(pattern, cleaned_description)
    if match:
        cleaned_description =match.group(1)
    # Remove leading and trailing whitespaces
    cleaned_description = cleaned_description.rstrip().lstrip()
    pattern = re.compile(r'[\x00-\x1F\x7F-\x9F]|\u2060')
    cleaned_text = pattern.sub('', cleaned_description).replace("●", "-").replace('• ', "")
    return cleaned_text

def translate_date_string(date_str):
    # Dictionaries for Spanish to English month and weekday names
    spanish_to_english_months = {
        'Enero': 'January', 'Febrero': 'February', 'Marzo': 'March', 'Abril': 'April',
        'Mayo': 'May', 'Junio': 'June', 'Julio': 'July', 'Agosto': 'August',
        'Septiembre': 'September', 'Octubre': 'October', 'Noviembre': 'November', 'Diciembre': 'December'
    }
    
    spanish_to_english_weekdays = {
    'Lunes': 'Monday', 'Martes': 'Tuesday', 'Miércoles': 'Wednesday', 'Jueves': 'Thursday',
    'Viernes': 'Friday', 'Sábado': 'Saturday', 'Domingo': 'Sunday'
    }

    # Replace Spanish month names with English month names
    for spanish_month, english_month in spanish_to_english_months.items():
        date_str = date_str.replace(spanish_month, english_month)

    # Replace Spanish weekday names with English weekday names
    for spanish_weekday, english_weekday in spanish_to_english_weekdays.items():
        date_str = date_str.replace(spanish_weekday, english_weekday)

    return date_str

def clean_date(date):
    try: 
        new_date = dateutil.parser.parse(date)
        return new_date
    except:
        date = date.replace('de','')
        split_dates = [i.title().replace(',','') for i in (date.split())]
        new_date = dateutil.parser.parse(translate_date_string(' '.join(split_dates)))
        return new_date


class CleanUpProcess:

    def process_item(self, item):
        try:
            required_keys = ('url', 'title', 'created_at')
            if set(required_keys).issubset(item.keys()):
                for key, val in item.items():
                    if key == 'description':
                        item[key] = str(clean_description(html.unescape(val))).title()
                    if key == 'content':
                        item[key] = str(clean_description(html.unescape(val)))
                    if key == 'encoded':
                        item[key] = str(clean_description(html.unescape(val)))
                    if key == 'created_at':
                        item[key] = str(clean_date(val))
                    if key == 'guid':
                        if isinstance(val, dict):
                            item[key] = val['#text']
                    if key == 'title':
                        val = clean_description(html.unescape(val)).replace('\r','').replace('\n','')
                        item[key] = val.title()
                return item
            else:
                logging.critical("Critical: This item need required keys. Placing in txt file to investigate", item)
                with open('log/critical_items_add_to_db_manually.txt', 'a') as f:
                    f.write(str(item) + '\n')
        except Exception as e:
            logging.error(f'Error in processing item: {item}. Error: {e}')

    
def clean_items(content: list):
    cleaned = []
    
    for item in content:
        try:
            item = convert_keys_to_snake_case(item)
            """
            replace any key you want. The variable name is the old key and the value is the new key
            """
            item = replace_key(item, pub_date='created_at', pdf='document_link') 
            item = CleanUpProcess().process_item(item)
            cleaned.append(item)
        except Exception as e:
            logging.error(f'Error in processing item: {item}. Error: {e}')
            pass

    return cleaned