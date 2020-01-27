#!/usr/bin/python
import psycopg2
from config import config
from flask import Flask, request, jsonify, json, make_response
from flask_restful import reqparse, abort, Api, Resource
from datetime import datetime

app = Flask(__name__)
api = Api(app)

#@app.route('/', methods=['GET']) -old
class welcome(Resource):
    def get(self):
        return jsonify( message =  """Hello World REST API.  
 PUT /hello/username { "dateOfBirth" : "YYYY-MM-DD" } for insert/update username and dateofbirth.  
 GET /hello/username to get birthday message.""")

class put_dob(Resource):
    def put(self,user_id,dob):
        """ Connect to the PostgreSQL database server """
        conn = None
        user = None
        try:
            # read connection parameters
            sql="""INSERT INTO hello (username, dateofbirth)
                   VALUES ( '%s', '%s' ) 
                   ON CONFLICT ON CONSTRAINT firstkey
                   DO UPDATE  SET username = '%s' , dateofbirth='%s' RETURNING username;"""
            data=(user_id,dob,user_id,dob)
            params = config()

            # connect to the PostgreSQL server
            print('Connecting to the PostgreSQL database...')
            conn = psycopg2.connect(**params)

            # create a cursor
            cur = conn.cursor()

            # execute a statement
            print('Query:'+sql)
            cur.execute(sql%data)
            conn.commit()
            user = cur.fetchone()[0]
            print(" user: "+user);
            # close the communication with the PostgreSQL
            cur.close()
            if user is None:
                print( "PUT request failed  for"+ user_id)
                description= "Hello "+user+" , PUT /hello/"+user+" { \"dateOfBirth\" : \"YYYY-MM-DD\" } for insert/update username and dateofbirth "
                return make_response(jsonify( message = description),500)
            else :
                return make_response(jsonify( message =  "PUT method complete,  username : "+user_id + " dateOfBirth: "+dob ), 204)
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            if conn is not None:
                conn.close()
                print('Database connection closed.')
 

class get_dob(Resource):
    def get(self,user_id):
        """ Connect to the PostgreSQL database server """
        conn = None
        try:
            # read connection parameters
            sql="""SELECT username, TO_CHAR(dateofbirth, 'YYYY-MM-DD') FROM hello where username like trim('%s')"""
            #user=("vijay")
            ret_row={}
            user=(user_id)
            params = config()
 
            # connect to the PostgreSQL server
            print('Connecting to the PostgreSQL database...')
            conn = psycopg2.connect(**params)
      
            # create a cursor
            cur = conn.cursor()
        
            # execute a statement
            print('Query:'+sql)
            cur.execute(sql%user)
            print("The number of parts: ", cur.rowcount)
            row = cur.fetchone()
            ret_row=row
 
            while row is not None:
               print(row)
               row = cur.fetchone() 
            # close the communication with the PostgreSQL
            cur.close()
            if ret_row is None:
                print( user + " not found ")
                description= "Hello "+user+" , PUT /hello/"+user+" { \"dateOfBirth\" : \"YYYY-MM-DD\" } for insert/update username and dateofbirth "
                return jsonify( message = description)
            else :
                return jsonify( message =  "Hello, "+ret_row[0]+" ! Your birthday is in N day(s)")
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            if conn is not None:
                conn.close()
                print('Database connection closed.')
 
 
@app.errorhandler(404)
def page_not_found(e):
    return jsonify(error=str(e)), 404

api.add_resource(welcome, '/' , '/hello',methods=['GET'])
api.add_resource(get_dob, '/hello/<string:user_id>',methods=['GET'])
url='/hello/<string:user_id> { "dateOfBirth" : "<string:dob>" }'
api.add_resource(put_dob, url, methods=['PUT'])

if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=True)
