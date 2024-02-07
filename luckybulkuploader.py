import os
from datetime import datetime
import argparse
import logging
from luckyioc import LuckyIoc


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


def main(root_folder, output_path):
    output_filename = f"{os.path.splitext(output_path)[0]}.ndjson"

    # Get the Logger
    logger = logging.getLogger("luckyvisitor")
    logger.setLevel(logging.DEBUG)

    handler = logging.FileHandler(output_filename, mode="w", encoding="utf-8")

    logger.addHandler(handler)

    # Traverse the folder structure
    for root, dirs, files in os.walk(root_folder):
        for file in files:
            if file == 'ioc.txt':
                file_path = os.path.join(root, file)
                # Process each ioc.txt file and append the data to the combined list
                for ioc in process_ioc_file(file_path):
                    logger.info(ioc)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description='Parse txt IOC data into Kibana.')

    parser.add_argument('root_folder', type=str, help='root_folder')
    parser.add_argument('output_path', type=str,
                        help='Path of the output file')

    args = parser.parse_args()

    main(args.root_folder, args.output_path)
