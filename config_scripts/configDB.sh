#!/bin/bash

cd /home/ubuntu
sudo apt update
sudo apt install postgresql postgresql-contrib -y
sudo ufw allow 5432/tcp

sudo -u postgres psql -c "CREATE USER cloud WITH PASSWORD 'cloud';"

sudo -u postgres createdb -O cloud tasks

sudo -u postgres sed -i "s/#listen_addresses = 'localhost'/listen_addresses = '*'/g" /etc/postgresql/10/main/postgresql.conf

sudo -u postgres echo 'host    all             all             0.0.0.0/0             trust' >> /etc/postgresql/10/main/pg_hba.conf

sudo -u postgres psql -c "grant all privileges on database tasks to cloud;"

sudo systemctl restart postgresql