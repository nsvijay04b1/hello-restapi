#!/usr/bin/python
import psycopg2
from config import config
from flask import Flask, request, jsonify, json, make_response
from flask_restful import reqparse, abort, Api, Resource
from datetime import datetime, timedelta, date
import calendar
from argparse import ArgumentParser

# configurable - datedelta , no of days atleast dob should be older than 
datedelta=1  
datelimit = datetime.today() - timedelta(days=datedelta)
now = datetime.now()


app = Flask(__name__)
api = Api(app)
parser = ArgumentParser()
parser.add_argument('--mode')
args = parser.parse_args()
mode=args.mode
app.config['mode'] = args.mode
print('Passed item: ', app.config['mode'])

#welcome page or default page
class welcome(Resource):
    def get(self):
        return jsonify( message =  """Hello World REST API.  
 PUT /hello/username { "dateOfBirth" : "YYYY-MM-DD" } for insert/update username and dateofbirth.  
 GET /hello/username to get birthday message.""")

# PUT class
class put_dob(Resource):
    def put(self,user_id,dob):
        """ Connect to the PostgreSQL database server """
        conn = None
        user = None
        try:
            #validate - username must contain only letters
            if not user_id.isalpha():
                description= "Hello, "+user_id+" ! Your username must contain only letters."
                return make_response(jsonify( message = description),400)

            #validate - DateOfBirth must be a date before today date
            if datetime.strptime(dob, "%Y-%m-%d").strftime('%Y-%m-%d') > datelimit.strftime('%Y-%m-%d'):
                description= "Hello, "+user_id+" ! Your DateOfBirth must be a date before today date."
                return make_response(jsonify( message = description),400)

            # read connection parameters
            sql="""INSERT INTO hello (username, dateofbirth)
                   VALUES ( '%s', '%s' ) 
                   ON CONFLICT ON CONSTRAINT firstkey
                   DO UPDATE  SET username = '%s' , dateofbirth='%s' RETURNING username;""" 
            data=(user_id,dob,user_id,dob)
            params = config(mode=app.config['mode'])

            # connect to the PostgreSQL server
            print('Connecting to the PostgreSQL database...')
            conn = psycopg2.connect(**params)

            # create a cursor
            cur = conn.cursor()

            # execute a statement and commit
            print('Query:'+sql)
            cur.execute(sql%data)
            conn.commit()
            #print(cur.fetchone())
            user = cur.fetchone()[0]
            print(" user: "+user);
            # close the communication with the PostgreSQL
            cur.close()
            # return response
            if user is None:
                print( "PUT request failed  for"+ user_id)
                description= "Hello "+user+" , PUT /hello/"+user+" { \"dateOfBirth\" : \"YYYY-MM-DD\" } for insert/update username and dateofbirth "
                return make_response(jsonify( message = description),500)
            else :
                return make_response(jsonify( message =  "PUT method complete,  username : "+user_id + " dateOfBirth: "+dob ), 204)
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
            description = "PUT failed for given username & dateOfBirth ."
            return make_response(jsonify(message = description+str(error)),400)
        finally:
            if conn is not None:
                conn.close()
                print('Database connection closed.')
 
#GET class
class get_dob(Resource):
    def get(self,user_id):
        """ Connect to the PostgreSQL database server """
        conn = None
        try:
            # read connection parameters
            sql="""SELECT username, TO_CHAR(dateofbirth, 'YYYY-MM-DD') FROM hello where username like trim('%s')"""
            ret_row={}
            user=(user_id)
            params =config(mode=app.config['mode'])
 
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

            # return response
            if ret_row is None:
                print( user + " not found ")
                description= "Hello "+user+" , PUT /hello/"+user+" { \"dateOfBirth\" : \"YYYY-MM-DD\" } for insert/update username and dateofbirth "
                return make_response(jsonify( message = description),400)
            else :
                if datetime.strptime(ret_row[1], "%Y-%m-%d").date() == datetime.today().date():
                    return jsonify( message =  "Hello, "+ret_row[0]+" !  Happy birthday!") 

                print(ret_row[1])
                days=calculate(ret_row[1])
                print(days)
                return jsonify( message =  "Hello, "+ret_row[0]+" ! Your birthday is in "+str(days)+" day(s)")
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
            description = "GET failed for given username ."
            return make_response(jsonify(message = description+str(error)),400)
        finally:
            if conn is not None:
                conn.close()
                print('Database connection closed.')
 
# 404 error response 
@app.errorhandler(404)
def page_not_found(e):
    return jsonify(error=str(e)), 404

#calculate days to next birthday 
def calculate(dob):
    print("in calculate: dob "+dob)
    dobyear=datetime.strptime(dob, "%Y-%m-%d").date().year
    dobmonth=datetime.strptime(dob, "%Y-%m-%d").date().month
    dobday=datetime.strptime(dob, "%Y-%m-%d").date().day
    curyear=datetime.now().year
    curmonth=datetime.now().month
    curday=datetime.now().day

    if dobmonth == 2 and dobday == 29:
      leapyear=curyear
      while(not calendar.isleap(leapyear)):
        leapyear=leapyear+1
      if not leapyear == curyear:
        days = (max(datetime(leapyear, dobmonth, dobday), datetime(curyear, curmonth, curday)) - now).days
      else:
        if datetime(curyear, dobmonth, dobday)  > datetime(curyear, curmonth, curday):
          days = (max(datetime(leapyear, dobmonth, dobday), datetime(curyear, curmonth, curday)) - now).days
        else:
          days = (max(datetime(leapyear, dobmonth, dobday), datetime(curyear, curmonth, curday)) - now).days 
    else:
      date1=datetime.now()
      date2=datetime(curyear, dobmonth, dobday)
      delta1 = datetime(curyear, dobmonth, dobday)
      delta2 = datetime(curyear+1, dobmonth, dobday)
      days = (max(delta1, delta2) - now).days

    print(days)
    return days 


#based on request call GET or PUT classes
api.add_resource(welcome, '/' , '/hello',methods=['GET'])
api.add_resource(get_dob, '/hello/<string:user_id>',methods=['GET'])
url='/hello/<string:user_id> { "dateOfBirth" : "<string:dob>" }'
api.add_resource(put_dob, url, methods=['PUT'])

#main
if __name__ == '__main__':
    if ( app.config['mode'] == "dev" ):
      app.run(host='0.0.0.0',port=9090,debug=True)
    elif ( app.config['mode'] == "prod" ) :
      app.run(host='0.0.0.0',debug=True,port="5050")
    else:
      print(" mode should be either dev or prod")
