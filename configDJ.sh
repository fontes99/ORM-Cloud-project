#!/bin/bash

cd /home/ubuntu

sudo apt update

git clone https://github.com/raulikeda/tasks.git

sed -i 's/node1/ipzao/g' tasks/portfolio/settings.py

cd tasks/

sudo sed -i '/python3 manage.py createsuperuser --noinput/d' install.sh
./install.sh

sudo reboot
