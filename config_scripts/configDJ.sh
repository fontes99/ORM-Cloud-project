#!/bin/bash

cd /home/ubuntu

sudo apt update

git clone https://github.com/fontes99/tasks.git

sed -i 's/node1/ipzao/g' tasks/portfolio/settings.py

cd tasks/

./install.sh

sudo reboot
