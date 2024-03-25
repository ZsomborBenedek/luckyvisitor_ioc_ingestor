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


def main(
    error_path: str, mapping: str, elasticsearch: str, es_index: str, api_key: str
):

    log_format = "%(asctime)s - %(levelname)s - %(message)s"
    max_log_size_bytes = 4096
    backup_count = 3

    error_logger = logging.getLogger("luckyvisitor_error")
    error_logger.setLevel(logging.ERROR)
    error_handler = RotatingFileHandler(
        error_path, maxBytes=max_log_size_bytes, backupCount=backup_count
    )
    error_handler.setFormatter(logging.Formatter(log_format))
    error_logger.addHandler(error_handler)

    try:
        es = Elasticsearch(
            [elasticsearch], ssl_show_warn=False, verify_certs=False, api_key=api_key
        )

        resp = es.indices.create(
            index=es_index,
            body={
                "settings": {"number_of_shards": 1},
                "mappings": json.load(open(mapping, "r")),
            },
        )
        print(resp)
    except Exception as e:
        error_logger.error(e)
        # raise Exception("error") from e


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Parse txt IOC data into Kibana.")

    parser.add_argument(
        "-err", "--error_path", type=str, help="Path to log file containing errors"
    )
    parser.add_argument(
        "-mp",
        "--mapping",
        type=str,
        help="Mapping json file",
        required=True,
    )
    parser.add_argument(
        "-es",
        "--elasticsearch",
        type=str,
        help="Elasticsearch address",
        default="https://localhost:9200",
    )
    parser.add_argument(
        "-ei",
        "--elasticsearch_index",
        type=str,
        help="Elasticsearch index",
        required=True,
    )
    parser.add_argument(
        "-ak", "--api_key", type=str, help="Elasticsearch api key", required=True
    )
    args = parser.parse_args()

    main(
        error_path=args.error_path,
        mapping=args.mapping,
        elasticsearch=args.elasticsearch,
        es_index=args.elasticsearch_index,
        api_key=args.api_key,
    )
