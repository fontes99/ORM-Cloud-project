from src.client import Client
from src.misc import Color
import time

t1 = time.time()

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
DB_ip = client2.launchInstance('postgresDB', open('config_scripts/configDB.sh').read(), key='postgresDB', secGr='postgresql')


# =========  Make instance in us-east-1 =================
print(c.HEADER+'\n[us-east-1] '+c.ENDC+'Setting up machines'+c.ENDC)

#-------------- Django ----------------
print(c.HEADER+c.UNDERLINE+'\n-Setting up Django-\n'+c.ENDC)
client.makeKeyPair('DJkey')
client.createSecurityGrp('django-security', 'enable ssh, 8080 and 80', [22, 8080, 80])
DJ_ip = client.launchInstance('Django', open('config_scripts/configDJ.sh').read().replace('ipzao', DB_ip), key='DJkey', secGr='django-security')


# ====== Loadbalancer + Auto scaling ===================
print(c.HEADER+c.UNDERLINE+"\n-Setting up Loadbalancer and Auto scaling-\n"+c.ENDC)
lb_id = client.create_lb()
client.autoscale()

t2 = time.time()

print(f"\nTime elapsed: {round(t2-t1, 2)} seconds ({round((t2-t1)/60, 2)} minutes)\n")