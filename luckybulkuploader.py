import json
import os
from datetime import datetime
import argparse
import logging
from luckyioc import LuckyIoc
from requests.packages import urllib3
from elasticsearch import Elasticsearch
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def process_ioc_file(file_path) -> list[LuckyIoc]:
    # Read the content of the ioc.txt file
    with open(file_path, 'r') as ioc_file:
        lines = ioc_file.read().splitlines()

    # Extract date information from the file path
    date_parts = file_path.split(os.path.sep)[-4:-1]
    date_str = '-'.join(date_parts)
    date_obj = datetime.strptime(date_str, "%Y-%m-%d")

    # Create a list of dictionaries with date, ip, and url
    data = [LuckyIoc(date_obj, line) for line in lines]
    # data = [{'date': date_obj, 'indicator': line} for line in lines]

    return data


def upload_to_elasticsearch(file_path, elasticsearch, es_index, api_key):
    es = Elasticsearch([elasticsearch], ssl_show_warn=False,
                       verify_certs=False, api_key=api_key)

    with open(file_path, 'r', encoding='utf-8') as indicators:
        for indicator in indicators.readlines():
            data_row = json.loads(indicator)
            # print(data_row)
            es.index(index=es_index, document=data_row)


def main(root_folder, output_path, elasticsearch, es_index, api_key):
    output_filename = f"{os.path.splitext(output_path)[0]}.ndjson"

    # Get the Logger
    logger = logging.getLogger("luckyvisitor")
    logger.setLevel(logging.DEBUG)

    handler = logging.FileHandler(output_filename, mode="w", encoding="utf-8")

    logger.addHandler(handler)

    es = Elasticsearch([elasticsearch], ssl_show_warn=False,
                       verify_certs=False, api_key=api_key)

    # Traverse the folder structure
    for root, dirs, files in os.walk(root_folder):
        for file in files:
            if file == 'ioc.txt':
                file_path = os.path.join(root, file)
                # Process each ioc.txt file and append the data to the combined list
                for ioc in process_ioc_file(file_path):
                    logger.info(ioc)
                    es.index(index=es_index, document=ioc.asdict())


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description='Parse txt IOC data into Kibana.')

    parser.add_argument('-f', '--root_folder', type=str,
                        help='Path of the Luckyvisitor repository')
    parser.add_argument('-o', '--output_path', type=str,
                        help='Path of the output file')
    parser.add_argument('-es', '--elasticsearch', type=str,
                        help='Elasticsearch address', default="https://localhost:9200")
    parser.add_argument('-ei', '--elasticsearch_index', type=str,
                        help='Elasticsearch index', required=True)
    parser.add_argument('-ak', '--api_key', type=str,
                        help='Elasticsearch api key', required=True)

    args = parser.parse_args()

    main(args.root_folder, args.output_path, elasticsearch=args.elasticsearch,
         es_index=args.elasticsearch_index, api_key=args.api_key)
