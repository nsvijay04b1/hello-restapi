# hello-restapi
REST Api to update username and date of birth using PUT method. 

To find the number of days left to next birthday and get "happy birthday" message if birthday is same as today using GET method.

# Out-of-scope
1. Time zones of the api user. 
2. User authentication for api

# Assumptions
1. Assuming PUT and GET is done from same time zone.
2. username's are unique and each user has already authenticated to run the api , if PUT call is made again for the same username, it will allow to uppate the date of birth.

# Notes for API users
1. <username> must contains only letters.
2. YYYY-MM-DD must be date before the todays date.

# API call scenarios covered 

|             HTTP method - API route       | condition/validation           | Http response code     | json message   |
| --------------------------- | --------------------------     |-------------  | ---------------------|
| GET /hello/\<username\>       | `username` exists and birthday is not today    | 200 SUCCESS  |  "message": "Hello, `username` ! Your birthday is in N day(s)"|
| GET /hello/\<username\>       | `username` exists and birthday is today  | 200 SUCCESS  |"message": "Hello `username`! , Happy Birthday! "  |
| GET /hello/\<username\>       | if `username` doesnot exist    |  400 BAD REQUEST  | "message": "Hello `username` , PUT /hello/\<username\> { "dateOfBirth" : "YYYY-MM-DD" } for insert/update `username` and `dateofbirth` " |
| PUT /hello/\<username\> { "dateOfBirth" : "YYYY-MM-DD" } | `username` has only letters & `dateOfBirth` is not today or future date |  204  SUCCESS | NO CONTENT |
| PUT /hello/\<username\> { "dateOfBirth" : "YYYY-MM-DD" } | `username` has only alphanumerics  |400 BAD REQUEST   | "message": "Hello, `username` ! Your `username` must contain only letters." |
| PUT /hello/\<username\> { "dateOfBirth" : "YYYY-MM-DD" } | `dateOfBirth` is today or future date |  400 BAD REQUEST  | "message": "Hello, `username` ! Your DateOfBirth must be a date before today date." |
| PUT /hello/\<username\> { "dateOfBirth" : "YYYY-MM-DD" } | `username` is fine but `dateOfBirth` is NOT a valid date  | 400 BAD REQUEST |  "message": "PUT failed for given `username` & `dateOfBirth`  .time data '202-02-03' does not match format '%Y-%m-%d'"|
| PUT /hello/\<username\> { "dateOfBirth" : "YYYY-MM-DD" } | `username` is too long but `dateOfBirth` is a valid date  | 400 BAD REQUEST |  "message": "PUT failed for given `username` & `dateOfBirth` .value too long for type character varying(40)\n"|


# Devops lifecycle - 

* webapp =  Python Flask REST API run in a docker container ( for prod flask is supervised by uwsgi )
* DB =      postgresql in  a container 
* CI = github Actions  (  Steps included  docker build run, python test , docker image push to docker hub.)
* CD =  Terraform to create and provision cloud infrastructure ( this is for prod only)

#  Project structure 

* Python Flask application project files

```
app
├── config.py                     
├── config.pyc
├── database.ini
├── flask_restful
│   ├── reqparse.py
├── hello.nginx
├── main.py
├── main.pyc
├── prestart.sh
├── test.py
├── tests
│   ├── preparedata.py
│   ├── testdata.txt
│   ├── test-dbpreparation.py
│   └── testget.py
├── uwsgi.ini
└── wsgi.py
```


* Terraform AWS prod env project files
```
aws-terraform
├── helloapp.service
├── hello-nginx-site
├── index.html
├── inventory.fut
├── inventory.tpl
├── LICENSE
├── main.ELB
├── main.tf
├── modules
│   └── db
│       ├── CHANGELOG.md
│       ├── examples
│       │   ├── complete-mssql
│       │   │   ├── main.tf
│       │   │   ├── outputs.tf
│       │   │   └── README.md
│       │   ├── complete-mysql
│       │   │   ├── main.tf
│       │   │   ├── outputs.tf
│       │   │   └── README.md
│       │   ├── complete-oracle
│       │   │   ├── main.tf
│       │   │   ├── outputs.tf
│       │   │   └── README.md
│       │   ├── complete-postgres
│       │   │   ├── main.tf
│       │   │   ├── outputs.tf
│       │   │   └── README.md
│       │   ├── enhanced-monitoring
│       │   │   ├── main.tf
│       │   │   └── README.md
│       │   ├── replica-mysql
│       │   │   ├── main.tf
│       │   │   ├── outputs.tf
│       │   │   └── README.md
│       │   └── replica-postgres
│       │       ├── main.tf
│       │       ├── outputs.tf
│       │       └── README.md
│       ├── LICENSE
│       ├── main.tf
│       ├── Makefile
│       ├── modules
│       │   ├── db_instance
│       │   │   ├── main.tf
│       │   │   ├── outputs.tf
│       │   │   ├── README.md
│       │   │   └── variables.tf
│       │   ├── db_option_group
│       │   │   ├── main.tf
│       │   │   ├── outputs.tf
│       │   │   ├── README.md
│       │   │   └── variables.tf
│       │   ├── db_parameter_group
│       │   │   ├── main.tf
│       │   │   ├── outputs.tf
│       │   │   ├── README.md
│       │   │   └── variables.tf
│       │   └── db_subnet_group
│       │       ├── main.tf
│       │       ├── outputs.tf
│       │       ├── README.md
│       │       └── variables.tf
│       ├── outputs.tf
│       ├── README.md
│       └── variables.tf
├── outputs.tf
├── README.md
├── vars.tf
└── versions.tf

````

# Development env ( docker )


To test on local machine, run docker compose build and up which create a web & db service.
  application run on dockerhost on port 80.
  
python tests is written to check basic functionality checks.  
  
``
docker-compose -f  docker-compose.yaml  up -d --build
``

After successful test push code to guthib.

After code is pushed to github , github actions kickin run a build , test  and upload a package to github.
  ![github-Actions-CI](images/github-ci.JPG)
  
  



# Production env ( AWS ) 

 For production environments, we add Gunicorn, a production-grade WSGI server.
 
 ```
After=network.target

[Service]
User=ec2-user
Group=ec2-user
WorkingDirectory=/app/hello-app
Environment="PATH=/app/hello-app"
ExecStart=/usr/bin/gunicorn --workers 5 --bind unix:/app/hello-app/helloapp.sock -m 007 wsgi:app

[Install]
WantedBy=multi-user.target
```

 let's add Nginx into the mix to act as a reverse proxy for Gunicorn to handle client requests as well as serve up static files.
 
 ```
 server {
    listen 5000;
    listen [::]:5000;

    server_name hello-elb-*.us-east-1.elb.amazonaws.com www.hello-elb-*.us-east-1.elb.amazonaws.com http://hello-elb-*.us-east-1.elb.amazonaws.com;

    access_log /var/log/nginx/helloapp.access.log;
    error_log /var/log/nginx/helloapp.error.log;

    location / {
        include proxy_params;
        proxy_pass http://unix:/app/hello-app/helloapp.sock;
    }
}
```



# Terraform is used to create aws cloud infrastructure.


* AWS HA architecture used

![AWS architecture](images/re-aws-pic.JPG)










