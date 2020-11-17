from client import Client
from misc import Color

c = Color()

client = Client('us-east-1')
client.cleanUp()

client2 = Client('us-east-2')
client2.cleanUp()

# # =========  Make instance in us-east-2 =================
print(c.HEADER+'\n[us-east-2] '+c.ENDC+'Setting up machines'+c.ENDC)

# ------------ postgres DB ---------------
print(c.HEADER+c.UNDERLINE+'\n-Setting up Database-\n'+c.ENDC)
client2.makeKeyPair('postgresDB')
client2.createSecurityGrp('postgresql', 'postgresql security', [22, 5432])
DB_ip = client2.launchInstance('postgresDB', open('configDB.sh').read(), key='postgresDB', secGr='postgresql')


# =========  Make instance in us-east-1 =================
print(c.HEADER+'\n[us-east-1] '+c.ENDC+'Setting up machines'+c.ENDC)

#-------------- Django ----------------
print(c.HEADER+c.UNDERLINE+'\n-Setting up Django-\n'+c.ENDC)
client.makeKeyPair('DJkey')
client.createSecurityGrp('ssh-enable', 'enable ssh', [22, 8080, 80])
DJ_ip = client.launchInstance('Django', open('configDJ.sh').read().replace('ipzao', DB_ip), key='DJkey', secGr='ssh-enable')

# # ------------ Webserver ---------------
print(c.HEADER+c.UNDERLINE+'\n-Setting up Webserver-\n'+c.ENDC)
client.makeKeyPair('Webserver')
client.createSecurityGrp('webserver-8080', 'enable ssh', [22, 8080, 80])
Webserver_ip = client.launchInstance('Webserver', open('configApp.sh').read(), key='Webserver', secGr='webserver-8080')
