#!/usr/bin/python
import sys, os
testdir = os.path.dirname(__file__)
#srcdir = '../'
srcdir = '/app'
sys.path.insert(0, os.path.abspath(os.path.join(testdir, srcdir)))

from config import config
import psycopg2
from flask import Flask, request, jsonify, json, make_response
from flask_restful import reqparse, abort, Api, Resource
from datetime import datetime, timedelta, date
import calendar
from argparse import ArgumentParser


#prepare  test data
def prepare_data():
        """ Connect to the PostgreSQL database server """
        conn = None
        user = None
        try:
            # read connection parameters
            params = config()
            
            # connect to the PostgreSQL server
            print('Connecting to the PostgreSQL database...')
            conn = psycopg2.connect(**params)

            # create a cursor
            cur = conn.cursor()

            # execute a statement and commit
            sql_file = open('/app/testdata.txt','r')
            cur.execute(sql_file.read())
            sql_file.close()
            conn.commit()
            # close the communication with the PostgreSQL
            cur.close()
            # return response
            return "OK"
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            if conn is not None:
                conn.close()
                print('Database connection closed.')

prepare_data()
