import json
import re
import argparse


def setup_parser():
    parser = argparse.ArgumentParser(description='Publish on Zenodo and Databus')
    parser.add_argument('--complete', nargs=3,
                        metavar=("csv_file", "metadatafile", "Version"),
                        help="Upload on Zenodo and Databus")
    parser.add_argument('-u', '--user', nargs=1,
                        metavar=("user"),
                        help="Specifiy user for databus")
    parser.add_argument('-id', '--depo_id', metavar=("deposit_id"),
                        help="deposit_id")
    parser.add_argument('-ds', '--deposits', action="store_true",
                        help="List all Deposits of a User")
    return parser


def parse_id(id):
    non_number = re.compile(r'\D+')
    match = re.findall(non_number, id)
    if len(match) > 0:
        print("Wrong ID: ", id)
        exit()
    return id


def log_response(response):
    formatted = json.dumps(response, indent=2)
    print(formatted)
    return formatted


def parse(api):
    parser = setup_parser()
    args = parser.parse_args()
    if args.complete:
        arguments = args.complete
        depo_id = args.depo_id
        user = args.user
        csv_file, metadata, version = arguments
        return csv_file, metadata, depo_id, *user
    if args.deposits:
        response = api.list_all_deposits()
        print(response)
    return None, None, None, None
