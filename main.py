from client import Client
from misc import *

client = Client('us-east-1')
client.cleanUp()

client2 = Client('us-east-2')
client2.cleanUp()


# Make instance in us-east-1
print(HEADER+'\n[us-east-1] '+ENDC+'Setting up machines'+ENDC)
key = 'boto3-key'
client.makeKeyPair(key)

security_group = 'ssh-enable'
client.createSecurityGrp(security_group, 'enable ssh', [22])

client.launchInstance('boto3-1', open('configDB.sh').read(), key=key, secGr=security_group)


# Make instance in us-east-2
print(HEADER+'\n[us-east-2] '+ENDC+'Setting up machines'+ENDC)

key2 = 'boto3-key2'
client2.makeKeyPair(key2)

security_group2 = 'ssh-enable'
client2.createSecurityGrp(security_group2, 'enable ssh', [22])

client2.launchInstance('boto3-2', open('configDJ.sh').read(), key=key2, secGr=security_group2)
