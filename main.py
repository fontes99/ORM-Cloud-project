from client import Client
from misc import *

client = Client('us-east-1')
client.cleanUp()

client2 = Client('us-east-2')
client2.cleanUp()

# # =========  Make instance in us-east-2 =================
print(HEADER+'\n[us-east-2] '+ENDC+'Setting up machines'+ENDC)

# ------------ postgres DB ---------------
print(HEADER+UNDERLINE+'\n-Setting up Database-\n'+ENDC)
client2.makeKeyPair('postgresDB')
client2.createSecurityGrp('postgresql', 'postgresql security', [22, 5432])
DB_ip = client2.launchInstance('postgresDB', open('configDB.sh').read(), key='postgresDB', secGr='postgresql')


# =========  Make instance in us-east-1 =================
print(HEADER+'\n[us-east-1] '+ENDC+'Setting up machines'+ENDC)

# # ------------ Webserver ---------------
print(HEADER+UNDERLINE+'\n-Setting up Webserver-\n'+ENDC)
client.makeKeyPair('Webserver')
client.createSecurityGrp('webserver-8080', 'enable ssh', [22, 8080, 80])
Webserver_ip = client.launchInstance('Webserver', open('configApp.sh').read(), key='Webserver', secGr='webserver-8080')

#-------------- Django ----------------
print(HEADER+UNDERLINE+'\n-Setting up Django-\n'+ENDC)
client.makeKeyPair('DJkey')
client.createSecurityGrp('ssh-enable', 'enable ssh', [22, 8080, 80])
DJ_ip = client.launchInstance('Django', open('configDJ.sh').read().replace('ipzao', DB_ip), key='DJkey', secGr='ssh-enable')
