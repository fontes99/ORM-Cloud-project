"""
Client for treating
"""

import sys
import requests 
import json

r = requests.get('http://54.146.179.135:8080/tasks/')
print(r.json())


payload = {
    "title" : "foi",
    "pub_date" : "2020-11-20T14:25:17Z",
    "description" : "foi python"
}
r = requests.post('http://54.146.179.135:8080/tasks/post', data=payload)
