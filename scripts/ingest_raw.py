from utils.sqlhelper import SQLHandler
from utils.propertieshelper import load_sql_properties, load_property_by
import os

script_dir = os.path.dirname(__file__)

conf = 'resource/config.ini'

credentials = load_sql_properties(conf)

tables = load_property_by(conf, 'data', 'tables').split(",")

executor = SQLHandler()

try:
    cursor = executor.sql_connect(credentials)
except Exception as ex:
    print("Error occurred while initializing connection to sql. Error Message : {}".format(ex))
    exit(2)
else:
    print("Running the script from {}\n".format(script_dir))

created = 0
ingested = 0
for data_file in tables:

    data_file_path = "data/" + data_file + ".csv"
    ddl_file_path = "ddls/" + data_file + "_table_create.sql"
    print("Creating table : {}".format(data_file))
    with open(ddl_file_path, "r") as file_obj:
        sql_statement = file_obj.read()
    try:
        if executor.execute_ddl(cursor, sql_statement):
            created += 1
        else:
            print("Skipping {} table creation".format(data_file))
    except IOError as f_ex:
        print("File {} not accessible, Error message : {}".format(ddl_file_path, f_ex))
        exit(1)

    try:
        if executor.ingest_csv(cursor, data_file_path, data_file):
            ingested += 1
        else:
            print("Please check")
    except Exception as ex:
        print("Unable to ingest : {}".format(data_file_path, ex))