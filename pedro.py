"""
Client for treating
"""

import sys
import requests 
import json

ip = sys.argv[1]

payload = {
    "title" : "foi",
    "pub_date" : "2020-11-20T14:25:17Z",
    "description" : "foi python"
}
r = requests.post(f'http://{ip}:8080/tasks/post', data=payload)


r = requests.get(f'http://{ip}:8080/tasks/')
print(r.json())