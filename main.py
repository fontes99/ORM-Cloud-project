from client import Client
from misc import *

client = Client('us-east-1')
client.cleanUp()

client2 = Client('us-east-2')
client2.cleanUp()


# =========  Make instance in us-east-1 =================
print(HEADER+'\n[us-east-1] '+ENDC+'Setting up machines'+ENDC)

#-------------- Django ----------------
client.makeKeyPair('DJkey')
client.createSecurityGrp('ssh-enable', 'enable ssh', [22])
client.launchInstance('Django', open('configDJ.sh').read(), key='DJkey', secGr='ssh-enable')

# ------------ Webserver ---------------
client.makeKeyPair('Webserver')
client.createSecurityGrp('webserver-8080', 'enable ssh', [22, 8080, 80])
client.launchInstance('Webserver', open('configApp.sh').read(), key='Webserver', secGr='webserver-8080')


# =========  Make instance in us-east-2 =================
print(HEADER+'\n[us-east-2] '+ENDC+'Setting up machines'+ENDC)

# ------------ postgres DB ---------------
client2.makeKeyPair('postgresDB')
client2.createSecurityGrp('ssh-enable', 'enable ssh', [22])
client2.launchInstance('postgresDB', open('configDB.sh').read(), key='postgresDB', secGr='ssh-enable')
