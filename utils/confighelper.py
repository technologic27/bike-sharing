import base64
import os
from configparser import RawConfigParser


class ConfigHandler:

    def __init__(self):
        self.config = {}
        self.parser = RawConfigParser()

    def add(self, key, value):
        self.config[key] = value

    def havekey(self, key):
        if key in self.config.keys():
            return True
        else:
            return False

    def get(self, section, option):
        if option == "table_prefix":
            return os.environ['TABLE_PREFIX']
        return self.parser.get(section, option)

    def getfloat(self, section, option):
        return self.parser.getfloat(section, option)

    def getint(self, section, option):
        return self.parser.getint(section, option)

    def getvalue(self, key):
        return self.config[key]

    def read(self, site_config_path):
        self.parser.read(site_config_path)


    def read_config_section(self, section_name):

        print("From Config {}, Reading Section {}.".format(self.config_path, section_name))

        config = dict()
        return config

    def read_config_key(self, site_config_path, section_name, key_name):
        self.parser.read(site_config_path)
        print("From Config {}, Reading Key {} from Section {}.".format(self.config_path, key_name, section_name))

        return value
