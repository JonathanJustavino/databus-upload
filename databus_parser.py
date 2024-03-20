import json
import re
import argparse
from os import path


def setup_parser():
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('-c', '--create_deposit', action="store_true",
                        help="Create a new Deposit")
    parser.add_argument('-d', '--deposit', metavar=("deposit_id"),
                        help="Retrieve a deposit by id")
    parser.add_argument('-dl', '--download', metavar=("deposit_id"),
                        help="List all download links of files in a Deposit")
    parser.add_argument('-f', '--files', metavar=("deposit_id"),
                        help="List all files of a Deposit")
    parser.add_argument('-u', '--upload', metavar=("deposit_id"),
                        help="Upload a file to a Deposit")
    parser.add_argument('-s', '--update', metavar=("deposit_id"),
                        help="Update a Deposit")
    parser.add_argument('-p', '--publish', metavar=("deposit_id"),
                        help="Upload to Databus")
    parser.add_argument('--complete', nargs=4,
                        metavar=("directory", "Group", "Artifact", "Version"),
                        help="Upload on Zenodo and Databus")
    parser.add_argument('-del', '--delete_deposit', metavar=("deposit_id"),
                        help="Delete a deposit by id")
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


def parse(api):
    parser = setup_parser()
    args = parser.parse_args()
    if args.create_deposit:
        print("wellll")
        response = api.create_deposit()
        print(response)
    if args.files:
        depo_id = parse_id(args.files)
        response = api.get_files_of_deposit(depo_id)
        print(response)
    if args.update:
        depo_id = parse_id(args.update)
        metadata = None
        response = api.update_deposit(depo_id, metadata=metadata)
        print(response)
    if args.delete_deposit:
        depo_id = parse_id(args.delete_deposit)
        resp = api.delete_deposit(depo_id)
        print(resp)
    if args.deposits:
        api.list_all_deposits()
    if args.upload:
        file_path = path.join(path.expanduser('~'),
                              "Documents/workspace/whk/zenodo/abc.jsonld")
        depo_id = parse_id(args.upload)
        response = api.upload_file(depo_id, file_path)
        print(response)
    if args.publish:
        depo_id = parse_id(args.publish)
        response = api.collect_for_databus(depo_id)
        print(json.dumps(response.text, indent=2))
    if args.download:
        depo_id = parse_id(args.download)
        links = api.get_download_links(depo_id)
        print(links)
    if args.deposit:
        depo_id = parse_id(args.deposit)
        response = api.get_deposit(depo_id)
        print(response)
    if args.complete:
        arguments = args.complete
        response = api.publish_files(*arguments)
        if not response:
            print("Error while uploading to Databus")
        if response.ok:
            print("Upload to Databus successful")
            print("Response:")
            print("\n", response.text)

