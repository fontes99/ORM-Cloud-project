import sys
import requests 
import json

from src.misc import Color as c
from src.client import Client

"""
Client for treating Djson endpoints

Todo:
    - List all tasks 
    - Insert new task with input values
"""

client = Client('us-east-1')

response = client.loadbalancer.describe_load_balancers(
    LoadBalancerNames=[
        'myLoadBalancer',
    ])

dns = response['LoadBalancerDescriptions'][0]['DNSName']
    
try:
    cmd = sys.argv[1]

    # ===== POST =======

    if cmd == 'post':

        title = input("Title of task: ")
        date_h = input("Due date of task (dd/mm/yyyy): ")
        description = input("Description of task: ")

        date = date_h.split('/')
        day = date[0]
        month = date[1]
        year = date[2]

        payload = {
            "title" : title,
            "pub_date" : f"{year}-{month}-{day}T09:00:00Z",
            "description" : description
        }

        r = requests.post(f'http://{dns}/tasks/post', data=payload)

        print(c.HEADER+"\nTask created:"+c.ENDC)
        print(f"[ ] {title}")
        print(f"    - {description} ({date_h})")


    #====== GET ========

    elif cmd == 'list':
            
        r = requests.get(f'http://{dns}/tasks/')
        r = r.json()

        print(c.HEADER+c.UNDERLINE+"Tasks:\n"+c.ENDC)

        for task in r:
            date = []
            date.append(task['pub_date'][:4])
            date.append(task['pub_date'][5:7])
            date.append(task['pub_date'][8:10])

            print(f"[ ] {task['title']}")
            print(f"    - {task['description']} ({date[2]}/{date[1]}/{date[0]})\n")


    else:
        print(c.HEADER+c.UNDERLINE+"--TASK MANAGER--"+c.ENDC)
        print('''
    post: Create a new task
    list: List all existent tasks
        ''')
    
except:

    print(c.HEADER+c.UNDERLINE+"--TASK MANAGER--"+c.ENDC)
    print('''
post: Create a new task
list: List all existent tasks
    ''')
