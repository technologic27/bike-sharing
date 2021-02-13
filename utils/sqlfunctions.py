import pandas as pd
from utils.propertieshelper import load_sql_properties
from utils.sqlhelper import SQLHandler
import os
import psycopg2.extras


def load_df(cursor, sql_statement):
    try:
        cursor.execute(sql_statement)
        colnames = [descr[0] for descr in cursor.description]
        rows = []
        for row in cursor.fetchall():
            rows.append(row)
        df = pd.DataFrame(rows, columns=colnames)
        print('Dataframe created with length {} and columns {}'.format(len(rows), colnames))
        return df
    except Exception as ex:
        print("Error occurred while creating dataframe. Error Message : {}".format(ex))
        return False


def retrieve_rows(cursor, sql_statement):
    try:
        cursor.execute(sql_statement)
        rows = []
        for row in cursor.fetchall():
            rows.append(row)
        return rows
    except Exception as ex:
        print("Error occurred while retrieving data. Error Message : {}".format(ex))
        return False


def batch_execute(cursor, sql_statement, values):
    return psycopg2.extras.execute_batch(cursor, sql_statement, values)


def make_connection():
    script_dir = os.path.dirname(__file__)
    # print(script_dir)
    conf = script_dir+'/../resource/config.ini'
    credentials = load_sql_properties(conf)
    executor = SQLHandler()
    try:
        cursor = executor.sql_connect(credentials)
    except Exception as ex:
        print("Error occurred while initializing connection to sql. Error Message : {}".format(ex))
        exit(2)
    else:
        print("Running the script from {}\n".format(script_dir))
    return cursor