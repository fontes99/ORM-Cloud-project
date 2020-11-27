#!/bin/bash

mkdir -p keys

chmod +x task-list-template

sed -e "s|path_to_pedro|$(pwd)|g" task-list-template > task-list

chmod +x task-list

sudo mv task-list /usr/bin/

python3 main.py

echo 'INSTALL completed'