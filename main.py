import os
import re
import json
import argparse
from api_calls import API
from dotenv import load_dotenv


# records = wrapper.list_all_deposits()
# print(records)

# deposit_id = 10817144

# deposit = wrapper.get_files_of_deposit(deposit_id)
# print(json.dumps(deposit, indent=4))

# deposit = wrapper.get_deposit(deposit_id)
# print(json.dumps(deposit, indent=4))

# wrapper.upload_file(deposit_id, "./rli_dibt_windzone_vg_variant.json")

# deposit = wrapper.get_deposit(deposit_id)
# print(json.dumps(deposit, indent=4))

def setup_parser():
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('-c', '--create_deposit', action="store_true",
                        help="Create a new Deposit")
    parser.add_argument('-d', '--deposit', help="Retrieve a deposit by id")
    parser.add_argument('-f', '--files', help="List all files of a Deposit")
    parser.add_argument('-u', '--upload', help="Upload a file to a Deposit")
    parser.add_argument('-s', '--update', help="Update a Deposit")
    parser.add_argument('-del', '--delete_deposit',
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


def setup_api():
    load_dotenv()
    api_key = os.getenv("ACCESS_TOKEN")
    wrapper = API(api_key)
    return wrapper


if __name__ == '__main__':
    parser = setup_parser()
    args = parser.parse_args()
    api = setup_api()
    if args.deposit:
        depo_id = parse_id(args.deposit)
        response = api.get_deposit(depo_id)
        print(response)
    if args.create_deposit:
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
        # response = api.get_deposit(depo_id)
        resp = api.delete_deposit(depo_id)
        print(resp)
    if args.deposits:
        api.list_all_deposits()
    if args.upload:
        api.list_all_deposits()
