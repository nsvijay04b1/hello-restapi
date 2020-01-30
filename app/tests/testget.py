#!/usr/bin/python
import requests

headers = {
    'Content-type': 'application/json',
}

data = '{"username":"TestLeap"}'

response = requests.get('http://localhost:9090/hello/TestLeap', headers=headers)

assert response.status_code  ==  200

