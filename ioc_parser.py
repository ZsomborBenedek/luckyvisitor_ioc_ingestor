import os
import csv
from datetime import datetime
import argparse


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


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Parse txt IOC data into Kibana.')
    parser.add_argument('root_folder', type=str, help='root_folder')
    parser.add_argument('output_csv_path', type=str, help='output_csv_path')

    args = parser.parse_args()

    process_ioc_folder(args.root_folder, args.output_csv_path)
