from client import Client

client = Client('us-east-1')
client2 = Client('us-east-2')

# client.createSecurityGrp('ssh-enabled', 'Criei com boto 3 uhul', [22])
# response = client.makeKeyPair('boto3')
# print(response['KeyMaterial'])

# client2.makeKeyPair('boto3')



# response = client.launchInstance('olhaso')

# for instance in response['Instances']:
#     print(instance['InstanceId'])

# response = client2.launchInstance('olhaso', key='')

# for instance in response['Instances']:
#     print(instance['InstanceId'])

# ---

key='chave1'
client.makeKeyPair(key)
client.createSecurityGrp('ssh-enable', 'enable ssh', [22])
client.launchInstance('teste1', key=key, secGr='ssh-enable')