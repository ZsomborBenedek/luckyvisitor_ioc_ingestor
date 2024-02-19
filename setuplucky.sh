#!/bin/bash

read -p "Enter Elastic IP: " elastic_ip
read -p "Enter token: " token

# Create directory and download initial data
path="$(pwd)"
git clone https://github.com/JPCERTCC/Lucky-Visitor-Scam-IoC.git

# Parse data and upload it to Elasticsearch
python3 luckybulkuploader.py -f ./Lucky-Visitor-Scam-IoC -o lucky.ndjson -es "https://$elastic_ip:9200" -ei logs-ti_luckyvisitor -ak "$token"

# Add a cronjob for running luckyingester.py
(crontab -l ; echo "0 1 * * * /usr/bin/python3 $path/luckyingester.py -err $path/luckyvisitor_error.log -es 'https://$elastic_ip:9200' -ei logs-ti_luckyvisitor -ak '$token'") | crontab -
