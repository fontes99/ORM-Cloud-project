#!/bin/bash

mkdir -p keys

chmod +x task-list
sudo cp task-list /usr/bin/

python3 main.py

echo 'INSTALL completed'