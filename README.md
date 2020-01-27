# hello-restapi
REST Api to update username and date of birth using PUT method. 

To find the number of days left to next birthday and get "happy birthday" message if birthday is same as today using GET method.

# Out-of-scope
1. Time zones of the api user. 
2. User authentication for api or DB

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














