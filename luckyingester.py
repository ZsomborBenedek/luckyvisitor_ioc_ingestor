from datetime import datetime
import argparse
import requests
from requests.packages import urllib3
import logging
from logging.handlers import RotatingFileHandler
import json
from elasticsearch import Elasticsearch

from luckyioc import LuckyIoc
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def build_url(date: datetime):
    return f"https://raw.githubusercontent.com/JPCERTCC/Lucky-Visitor-Scam-IoC/main/{date.strftime('%Y')}/{date.strftime('%m')}/{date.strftime('%d')}/ioc.txt"


def fetch_data(url):
    response = requests.get(url, verify=False)
    content = response.text
    response.raise_for_status()
    return content.splitlines()


def add_indicator(input_path, data_row: dict):
    with open(input_path, 'a', newline='') as logfile:
        logfile.write(f"{json.dumps(data_row)}\n")


def main(error_path, elasticsearch, es_index, api_key):

    log_format = '%(asctime)s - %(levelname)s - %(message)s'
    max_log_size_bytes = 4096
    backup_count = 3

    error_logger = logging.getLogger("luckyvisitor_error")
    error_logger.setLevel(logging.ERROR)
    error_handler = RotatingFileHandler(
        error_path, maxBytes=max_log_size_bytes, backupCount=backup_count)
    error_handler.setFormatter(logging.Formatter(log_format))
    error_logger.addHandler(error_handler)

    try:
        date = datetime.now()

        url = build_url(date)
        new_data = fetch_data(url)

        es = Elasticsearch([elasticsearch], ssl_show_warn=False,
                           verify_certs=False, api_key=api_key)

        for item in new_data:
            indicator = LuckyIoc(datetime.strptime(str(date.date()), "%Y-%m-%d"), indicator=item)
            # print(indicator)
            es.index(index=es_index, document=indicator.asdict())
    except Exception as e:
        error_logger.error(e)
        # raise Exception("error") from e


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Parse txt IOC data into Kibana.')

    parser.add_argument('-err', '--error_path', type=str,
                        help='Path to log file containing errors')
    parser.add_argument('-es', '--elasticsearch', type=str,
                        help='Elasticsearch address', default="https://localhost:9200")
    parser.add_argument('-ei', '--elasticsearch_index', type=str,
                        help='Elasticsearch index', required=True)
    parser.add_argument('-ak', '--api_key', type=str,
                        help='Elasticsearch api key', required=True)
    args = parser.parse_args()

    main(error_path=args.error_path,
         elasticsearch=args.elasticsearch, es_index=args.elasticsearch_index, api_key=args.api_key)
