from cgitb import handler
import os
import csv
from datetime import datetime
import argparse
import json
import logging
from logging.handlers import RotatingFileHandler
import ecs_logging
import re


class Ioc():
    date: datetime
    indicator: str

    def __init__(self, date: datetime, indicator: str) -> None:
        self.date = date
        self.indicator = indicator


def is_ip_address(text: str):
    """
    Check if the given text is an IP address.
    """
    ip_pattern = r'\b(?:\d{1,3}\.){3}\d{1,3}\b'
    return re.match(ip_pattern, text) is not None


def is_url(text: str):
    """
    Check if the given text is a URL.
    """
    url_pattern = r'\b(?:https?://)?(?:www\.)?[\w.-]+\.[a-zA-Z]{2,}(?:/\S*)?\b'
    return re.match(url_pattern, text) is not None


def process_ioc_file(file_path) -> list[Ioc]:
    # Read the content of the ioc.txt file
    with open(file_path, 'r') as ioc_file:
        lines = ioc_file.read().splitlines()

    # Extract date information from the file path
    date_parts = file_path.split(os.path.sep)[-4:-1]
    date_str = '-'.join(date_parts)
    date_obj = datetime.strptime(date_str, "%Y-%m-%d")

    # Create a list of dictionaries with date, ip, and url
    data = [Ioc(date_obj, line) for line in lines]
    # data = [{'date': date_obj, 'indicator': line} for line in lines]

    return data


def main(root_folder, output_path):
    output_filename = f"{os.path.splitext(output_path)[0]}.ndjson"
    max_log_size_bytes = 8192
    backup_count = 3

    # Get the Logger
    logger = logging.getLogger("luckyvisitor")
    logger.setLevel(logging.DEBUG)

    # Add an ECS formatter to the Handler
    handler = logging.FileHandler(output_filename, mode="w", encoding="utf-8")
    # handler = RotatingFileHandler(
    #     output_filename, maxBytes=max_log_size_bytes, backupCount=backup_count)
    # handler.setFormatter(ecs_logging.StdlibFormatter(
    #     validate=True, exclude_fields=["process"], ))
    logger.addHandler(handler)

    # Traverse the folder structure
    for root, dirs, files in os.walk(root_folder):
        for file in files:
            if file == 'ioc.txt':
                file_path = os.path.join(root, file)
                # Process each ioc.txt file and append the data to the combined list
                for ioc in process_ioc_file(file_path):
                    if is_ip_address(ioc.indicator):
                        # print(f"{ioc.indicator} was an ip!")
                        logger.info(json.dumps({
                            "@timestamp": ioc.date.isoformat(),
                            "message": ioc.indicator,
                            "threat": {
                                "indicator": {
                                    "type": "ipv4-addr",
                                    "ip": ioc.indicator
                                }
                            }
                        }))
                    elif is_url(ioc.indicator):
                        # print(f"{ioc.indicator} was a url!")
                        logger.info(json.dumps({
                            "@timestamp": ioc.date.isoformat(),
                            "message": ioc.indicator,
                            "threat": {
                                "indicator": {
                                    "type": "url",
                                    "url": {
                                        "domain": ioc.indicator
                                    }
                                }
                            }
                        }))
                    # else:
                        # print(f"{ioc.indicator} was neither!")


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description='Parse txt IOC data into Kibana.')

    parser.add_argument('root_folder', type=str, help='root_folder')
    parser.add_argument('output_path', type=str,
                        help='Path of the output file')

    args = parser.parse_args()

    main(args.root_folder, args.output_path)
