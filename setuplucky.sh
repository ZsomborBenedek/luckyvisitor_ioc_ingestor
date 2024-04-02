#!/bin/bash

# Create a virtual environment
python3 -m venv .lucky_elk

# Activate the virtual environment
source .lucky_elk/bin/activate

# Install required Python packages
pip install elasticsearch requests

read -p "Enter Elastic IP: " elastic_ip
read -p "Enter index for logs [logs-ti_luckyvisitor]: " es_index
read -p "Enter token: " token

es_index=${es_index:-logs-ti_luckyvisitor}
mapping_file="es_mapping.json"

# Create directory and download initial data
path="$(pwd)"
git clone https://github.com/JPCERTCC/Lucky-Visitor-Scam-IoC.git
git pull ./Lucky-Visitor-Scam-IoC

# Create index an apply mapping
python3 luckyessetup.py -err $path/luckyvisitor_error.log -es "https://$elastic_ip:9200" -ei $es_index -ak "$token" -mp $mapping_file

# Parse data and upload it to Elasticsearch
python3 luckybulkuploader.py -f ./Lucky-Visitor-Scam-IoC -o lucky.ndjson -es "https://$elastic_ip:9200" -ei $es_index -ak "$token"

# Add a cronjob for running luckyingester.py
(crontab -l ; echo "0 23 * * * $path/.lucky_elk/bin/python3 $path/luckyingester.py -err $path/luckyvisitor_error.log -es 'https://$elastic_ip:9200' -ei '$es_index' -ak '$token'") | crontab -

# Deactivate the virtual environment
deactivate
