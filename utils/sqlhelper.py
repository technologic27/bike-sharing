#!/usr/bin/env python
# coding: utf-8

import csv
import logging
import psycopg2 as ps

logging.basicConfig(format='%(asctime)s [%(filename)s:%(lineno)s - %(module)s:%(funcName)10s() : %(levelname)s] %('
                           'message)s',
                    level=logging.DEBUG)

class SQLHandler:

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)

    def sql_connect(self, credentials):
        conn = ps.connect(host=credentials['POSTGRES_ADDRESS'],
                          database=credentials['POSTGRES_DBNAME'],
                          user=credentials['POSTGRES_USERNAME'],
                          password=credentials['POSTGRES_PASSWORD'],
                          port=credentials['POSTGRES_PORT'])

        conn.autocommit = True
        cursor = conn.cursor()
        return cursor

    def get_latest_timestamp(self, column_name, data_table, cursor):
        query_sql = "SELECT MAX({}) AS max_ts FROM {};".format(column_name, data_table)
        self.logger.debug("Query SQL : {}".format(query_sql))
        try:
            response = cursor.execute(query_sql, encoding='json')
            self.logger.debug("\n\nResponse for last ingested datetime : {}\n".format(response))
        except Exception as ex:
            self.logger.error("Error occurred while getting info of last file loaded. Error Message : {}".format(ex))
            return False, "None"

    def execute_ddl(self, cursor, sql_statement):
        self.logger.debug("Executing the following DDL : \n{}".format(sql_statement))
        try:
            response = cursor.execute(sql_statement)

            self.logger.debug("\nResponse : {}\n".format(response))
        except Exception as ex:
            self.logger.error("Error occurred while executing DDL. Error Message : {}".format(ex))
            return False

    def execute_dml(self, cursor, sql_statement, sqltype):
        """Adding (inserting), deleting, and modifying (updating) data"""
        self.logger.info("Running {} Job".format(sqltype))
        self.logger.debug("{} SQL : {}".format(sqltype, sql_statement))
        error = ""
        try:
            response = cursor.execute(sql_statement)
            self.logger.debug("\n\nResponse from {} job : {}\n".format(sqltype, response))
            return True, 0, error
        except Exception as ex:
            error = "Error occurred during {} job. Check Log".format(sqltype)
            self.logger.error("Error occurred during {} job. Error Message : {}".format(sqltype, ex))
            return False, 0, error

    def ingest_csv(self, cursor, data_file_path, table_name):
        self.logger.debug("Ingesting {} rows from {}".format(self.get_row_count(data_file_path), data_file_path))
        try:
            with open(data_file_path, "r", encoding="utf-8") as flat_file:
                reader = csv.reader(flat_file)
                cols = tuple(next(reader))
                cursor.copy_from(flat_file, table_name, sep=',', columns=cols)
            return True
        except Exception as ex:
            self.logger.error("Error occurred during ingestion job of table {}. Error Message : {}".format(table_name, ex))
            return False

    def get_row_count(self, data_file_path):
        try:
            with open(data_file_path, "r") as flat_file:
                reader = csv.reader(flat_file, delimiter=",")
                data = list(reader)
                row_count = len(data)
            print("Provided file has {} rows".format(row_count))
            return row_count
        except FileNotFoundError:
            print("File does not exist")
            return False
        except Exception as ex:
            print("Error occurred while counting rows for the file : {}. Error Message : {}".format(data_file_path, ex))
            return False