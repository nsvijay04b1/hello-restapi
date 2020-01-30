#!/usr/bin/python
from ConfigParser import ConfigParser
 
 
def config(filename='database.ini', section='postgresql', mode='dev'):
    # create a parser
    parser = ConfigParser()
    # read config file
    parser.read(filename)
    section=section+"_"+mode
    print ("config says "+section)
 
    # get section, default to postgresql
    db = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            print(param)
            db[param[0]] = param[1]
    else:
        raise Exception('Section {0} not found in the {1} file'.format(section, filename))
 
    return db
