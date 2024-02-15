import re
import dateutil.parser
import logging

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
    # Remove leading and trailing whitespaces
    cleaned_description = cleaned_description.strip()
    return cleaned_description


class CleanUpProcess:

    def process_item(self, item):
        for key, val in item.items():
            if key == 'description':
                item[key] = clean_description(val)
            if key == 'created_at':
                item[key] = dateutil.parser.parse(val)
            if key == 'guid':
                if isinstance(val, dict):
                    item[key] = val['#text']
            if key == 'title':
                item[key] = val.title()

        return item
    
def clean_items(content: list):
    cleaned = []
    for item in content:
        item = convert_keys_to_snake_case(item)
        """
        replace any key you want. The variable name is the old key and the value is the new key
        """
        item = replace_key(item, pub_date='created_at', pdf='document_link') 
        item = CleanUpProcess().process_item(item)
        logging.info(f'Processed item: {item}')
        cleaned.append(item)

    return cleaned