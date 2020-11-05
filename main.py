from client import Client

client = Client()

client.createSecurityGrp('ssh-enabled', 'Criei com boto 3 uhul', [22])

response = client.launchInstance(secGr='ssh-enabled')

for instance in response['Instances']:
    print(instance['InstanceId'])