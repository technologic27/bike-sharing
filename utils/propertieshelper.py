import json
from utils.confighelper import ConfigHandler

def load_properties(conf_file, section_name):
    parser = ConfigHandler()
    parser.read(conf_file)
    return parser.parser[section_name]

def load_list_props_from_json(js_str):
    col_dict = json.loads(js_str)
    col_list = []
    for k in col_dict:
        col_list.append(col_dict[k])
    return col_list

def load_sql_properties(conf_file):
    parser = ConfigHandler()
    parser.read(conf_file)
    credentials = dict()
    credentials['POSTGRES_ADDRESS'] = parser.get('sql', 'host')
    credentials['POSTGRES_DBNAME'] = parser.get('sql', 'database')
    credentials['POSTGRES_USERNAME'] = parser.get('sql', 'username')
    credentials['POSTGRES_PASSWORD'] = parser.get('sql', 'password')
    credentials['POSTGRES_PORT'] = parser.get('sql', 'port')
    return credentials

def load_property_by(conf_file, grp, key):
    parser = ConfigHandler()
    parser.read(conf_file)
    return parser.get(grp, key)