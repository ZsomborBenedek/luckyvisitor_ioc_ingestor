import argparse
from requests.packages import urllib3
import json
from elasticsearch import Elasticsearch

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def main(file_path, elasticsearch, es_index, api_key):

    es = Elasticsearch(
        [elasticsearch], ssl_show_warn=False, verify_certs=False, api_key=api_key
    )

    with open(file_path, "r", encoding="utf-8") as indicators:
        for indicator in indicators.readlines():
            data_row = json.loads(indicator)
            # print(data_row)
            es.index(index=es_index, document=data_row)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Parse txt IOC data into Kibana.")

    parser.add_argument(
        "-fp", "--file_path", type=str, help="Path to log file containing iocs"
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
        file_path=args.file_path,
        elasticsearch=args.elasticsearch,
        es_index=args.elasticsearch_index,
        api_key=args.api_key,
    )
