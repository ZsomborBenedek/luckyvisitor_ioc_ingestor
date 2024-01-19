import os
import csv
from datetime import datetime
import argparse
import requests
from elasticsearch import Elasticsearch


def process_ioc_file(file_path):
    # Read the content of the ioc.txt file
    with open(file_path, 'r') as ioc_file:
        lines = ioc_file.read().splitlines()

    # Extract date information from the file path
    date_parts = file_path.split(os.path.sep)[-4:-1]
    date_str = '-'.join(date_parts)
    date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()

    # Create a list of dictionaries with date, ip, and url
    data = [{'date': date_obj, 'indicator': line} for line in lines]

    return data


def write_to_csv(output_path, data):
    # Write the data to a CSV file
    with open(output_path, 'w', newline='') as csv_file:
        fieldnames = ['date', 'indicator']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

        # Write header
        writer.writeheader()

        # Write data
        for row in data:
            writer.writerow(row)


def process_ioc_folder(root_folder, output_path):
    # Initialize an empty list to store the combined data
    combined_data = []

    # Traverse the folder structure
    for root, dirs, files in os.walk(root_folder):
        for file in files:
            if file == 'ioc.txt':
                file_path = os.path.join(root, file)
                # Process each ioc.txt file and append the data to the combined list
                combined_data.extend(process_ioc_file(file_path))

    # Write the combined data to a CSV file
    write_to_csv(output_path, combined_data)


def build_url(date: datetime):
    return f"https://raw.githubusercontent.com/JPCERTCC/Lucky-Visitor-Scam-IoC/main/{date.strftime('%Y')}/{date.strftime('%m')}/{date.strftime('%d')}/ioc.txt"


def fetch_data(url):
    response = requests.get(url)
    content = response.text

    return content.splitlines()


def upload_to_elasticsearch(csv_line, index_name, es):
    # Extract values from the CSV line
    date, indicator = csv_line

    # Define the document to be indexed
    document = {
        'date': date,
        'indicator': indicator
    }

    # Index the document into Elasticsearch
    es.index(index=index_name, body=document)


def get_indicators(input_path):
    with open(input_path, 'r') as csv_file:
        reader = csv.DictReader(csv_file)
        return [row['indicator'] for row in reader]


def add_indicator(input_path, indicator_row):
    with open(input_path, 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(indicator_row)


def main(csv_path, es, elasticsearch_index):
    date = datetime.now()
    url = build_url(date)

    new_data = fetch_data(url)
    old_data = get_indicators(csv_path)

    for indicator in new_data:
        if indicator not in old_data:
            data_row = [
                f"{date.strftime('%Y')}-{date.strftime('%m')}-{date.strftime('%d')}", indicator]
            upload_to_elasticsearch(data_row, elasticsearch_index, es)
            add_indicator(csv_path, data_row)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Parse txt IOC data into Kibana.')
    # parser.add_argument('root_folder', type=str, help='root_folder')
    parser.add_argument('output_csv_path', type=str, help='output_csv_path')
    parser.add_argument('elasticsearch', type=str,
                        help='Elasticsearch host', default="http://localhost:9200")
    parser.add_argument('elasticsearch_index', type=str,
                        help='Elasticsearch index')

    args = parser.parse_args()

    es = Elasticsearch([args.elasticsearch], ssl_show_warn=False)

    main(args.output_csv_path, es, args.elasticsearch_index)
    # process_ioc_folder(args.root_folder, args.output_csv_path)
