#!/bin/bash
cd /home/
pkill -f 'main.py'
pkill -f chromedriver
pkill -f chrome
rm -r washington-kdmid-bot
git clone -b master https://github.com/apokaliepsis/washington-kdmid-bot
cd washington-kdmid-bot/
python3.7 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt --no-cache-dir
python3.7 main.py /home/auth_keys.json

