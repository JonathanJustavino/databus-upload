import os
import json
from api_calls import API
from dotenv import load_dotenv
from databus_parser import parse

# see main below

# return download url for Databus 
def upload_to_zenodo(api, csv_file, metadatajson, depo_id=None, user=None):

    if not depo_id:
		# create new deposit
        info = api.create_deposit()
        depo_id = info["id"]
        # use oemetadata to set zenodo metadata        
        api.update_deposit(depo_id, {
            'metadata': {
                'title': metadatajson["title"],
                'upload_type': 'poster',
                'description': metadatajson["description"],
                'creators': [
                    {
                        'name': 'Doe, John',
                        'affiliation': 'Script',
                    },
                ],
            },
        })

		# upload file
        try:
            response = api.upload_file(depo_id, csv_file)
            print(response)
        except FileNotFoundError:
            print(f"Wrong File Path for {csv_file}, aborting...")
            _ = api.delete_deposit(depo_id)
            print("Error while uploading to Zenodo,\
                deleting newly created Deposit: ", depo_id)
            return
        print("Successful Upload on Zenodo", depo_id)

    if not user:
        user = "prototype"

	# publish repository
    depo_id = str(depo_id)
    _ = api.publish_deposit(depo_id)
    return depo_id


def upload_to_databus(api, depo_id, metadatajson,
                      hasVersion, user=None, type="Version"):

    header = {
        "Accept": "application/json",
        "X-API-KEY": api.databus_token,
        "Content-Type": "application/ld+json",
    }

    file_info = api.get_files_of_record(depo_id)[0]
    format_extension = api._get_extension(file_info["key"])
    download_url = file_info['links']['content']

    distribution = [
        {
            "@type":  "Part",
            "compression": "none",
            "formatExtension": format_extension,
            "downloadURL": download_url
        }
    ]

    # id = metadatajson["wasGeneratedBy"]["used"].split('#')[0]
    # TODO: temp fix for id
    if not user:
        user = "prototype"
    group = "my-group"
    artifact = "my-artifact"
    version = hasVersion
    id = f"https://dev.databus.dbpedia.org/{user}/{group}/{artifact}/{version}"

    data = {
        "@context": api.context_url,
        "@graph": [
            {
                "@type": "Version",
                "@id": id,  # TODO: muss version URI sein
                            # aus der metadatajson die used uri nehmen
                            # und alles nach dem fragment trimmen
                "hasVersion": hasVersion,
                "title": metadatajson["title"],
                "description": metadatajson["description"],
                # TODO: nimm license aus der metadatajson
                "license": metadatajson["wasGeneratedBy"]["license"],
                "distribution": distribution,
            }
        ],
    }

    return api.databus_upload(data=json.dumps(data), header=header)


def upload_to_moss():
    # TODO:
    ...


def publish_file(api, csv_file, metadatajsonfile,
                 version, user=None, depo_id=None):

    metadatajson = {}
    with open(metadatajsonfile, "rb") as metafile:
        metadatajson = json.load(metafile)

    record_id = upload_to_zenodo(api, csv_file,
                                 metadatajson, depo_id=depo_id, user=user)

    response, data = upload_to_databus(api, record_id, csv_file,
                                       metadatajson, version,
                                       user=user, type="Version")
    print("\n\n\n")
    print(response)
    print("\n\n\n")

    # TODO:
    upload_to_moss()


if __name__ == '__main__':
    # Setup from .env
    load_dotenv()
    API_KEY = os.getenv("ZENODO_ACCESS_TOKEN")
    SANDBOX = os.getenv("SANDBOX")
    ZENODO_ENDPOINT = os.getenv("ZENODO_ENDPOINT")
    
    
    DATABUS_API_KEY = os.getenv("DATABUS_API_KEY")
    DATABUS_ENDPOINT = os.getenv("DATABUS_ENDPOINT")
    CONTEXT_URL = os.getenv("CONTEXT_URL")

    
    MOSS_ENDPOINT = os.getenv("MOSS_ENDPOINT")
    

    api = API(API_KEY, DATABUS_API_KEY, MOSS_ENDPOINT,
              DATABUS_ENDPOINT, CONTEXT_URL, SANDBOX, ZENODO_ENDPOINT)
	# reading CLI
    csv_file, metadatajsonfile, version, depo_id, user = parse(api)
    csv_file, metadatajsonfile = api.create_complete_file_paths(csv_file, metadatajsonfile)

    # reading oemetadata.json
    metadatajson = None
    with open(metadatajsonfile, "rb") as file:
        metadatajson = json.load(file)

    if not metadatajson:
        raise TypeError("Metadata should not be empty")

	# zenodo
	# NOT COMPLETE, uses only title and description from oemetadata.json
    if not depo_id:
        record_id = upload_to_zenodo(api, csv_file, metadatajson,
                                     depo_id=depo_id, user=user)
    else:
        record_id = depo_id
        response, data = upload_to_databus(api, record_id, metadatajson,
                                           version, user=user)
        # TODO:
        upload_to_moss()
