#!/bin/bash

cd /home/ubuntu

sudo apt update && sudo apt upgrade

git clone https://github.com/raulikeda/tasks.git

sed -i 's/node1/ipzao/g' tasks/portfolio/settings.py

cd tasks/
sh ./install

sudo reboot
