#!/usr/bin/python
import sys, os
testdir = os.path.dirname(__file__)
srcdir = '../'
sys.path.insert(0, os.path.abspath(os.path.join(testdir, srcdir)))

import flask_restful
import hello
from config import config

import psycopg2, getopt
from flask import Flask, request, jsonify, json, make_response
from flask_restful import reqparse, abort, Api, Resource
from datetime import datetime, timedelta, date
import calendar
from argparse import ArgumentParser

#prepare  test data
def test_get(user_id):
        """ Connect to the PostgreSQL database server """
        conn = None
        try:
            sql="""SELECT trim(username) FROM hello where username like trim('%s')"""
            ret_row={}
            user=(user_id)
            print(user)
            # read connection parameters
            params = config(mode='dev')
            
            # connect to the PostgreSQL server
            print('Connecting to the PostgreSQL database...')
            conn = psycopg2.connect(**params)

            # create a cursor
            cur = conn.cursor()

            # execute a statement and commit
            cur.execute(sql%user)
            print("The number of parts: ", cur.rowcount)
            row = cur.fetchone()
            ret_row=row

            while row is not None:
               print(row)
               row = cur.fetchone()

            # close the communication with the PostgreSQL
            cur.close()
            # return response
            return ret_row[0]
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            if conn is not None:
                conn.close()
                print('Database connection closed.')


assert test_get('TestLeap') == 'TestLeap'
assert test_get('TestFuture') == 'TestFuture'
assert test_get('TestPast' ) ==	'TestPast'
