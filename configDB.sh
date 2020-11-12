#!/bin/bash

cd /home/ubuntu

sudo apt update && sudo apt upgrade
sudo apt install postgresql postgresql-contrib -y

sudo su - postgres

psql -c "CREATE USER cloud WITH PASSWORD 'cloud';"

createdb -O cloud tasks

sed -i "s/#listen_addresses = 'localhost'/listen_addresses = '*'/g" /etc/postgresql/10/main/postgresql.conf

echo 'host    all             all             0.0.0.0/0             trust' >> /etc/postgresql/10/main/pg_hba.conf

exit

sudo ufw allow 5432/tcp

sudo systemctl restart postgresql