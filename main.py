import os
import json
import requests
from pathlib import Path
from api_calls import API
from dotenv import load_dotenv
from databus_parser import parse
from urllib.parse import urlparse, urlunparse


# getting values from .env
def setup_api():
    load_dotenv()
    ZENODO_API_KEY = os.getenv("ZENODO_ACCESS_TOKEN")
    ZENODO_ENDPOINT = os.getenv("ZENODO_ENDPOINT")
    ZENODO_SANDBOX = os.getenv("ZENODO_SANDBOX")

    DATABUS_API_KEY = os.getenv("DATABUS_API_KEY")
    DATABUS_ENDPOINT = os.getenv("DATABUS_ENDPOINT")
    DATABUS_CONTEXT_URL = os.getenv("DATABUS_CONTEXT_URL")

    MOSS_ENDPOINT = os.getenv("MOSS_ENDPOINT")

    return API(ZENODO_API_KEY,
               ZENODO_ENDPOINT,
               ZENODO_SANDBOX,
               DATABUS_API_KEY,
               DATABUS_ENDPOINT,
               DATABUS_CONTEXT_URL,
               MOSS_ENDPOINT)


# loading oemetadata JSON into memory object
def load_metadata_info(metadatajsonfile):
    metadatajson = None
    with open(metadatajsonfile, "rb") as file:
        metadatajson = json.load(file)

    if not metadatajson:
        raise TypeError("Metadata should not be empty")

    return metadatajson


# creating a deposit, then uploading the csv file, then publishing it as record
def upload_to_zenodo(api, csv_file, metadatajson, depo_id=None):
    success = False
    # create new deposit, can be skipped for debugging by re-using deposit id
    if not depo_id:
        info = api.create_deposit()
        depo_id = info["id"]

        metadata = api.generate_zendodo_input(metadatajson)
        api.update_deposit(depo_id, metadata=metadata)

        try:
            # uploading the csv file
            response = api.upload_file(depo_id, csv_file)
            print(response)
            success = response.ok
        except FileNotFoundError:
            print(f"Wrong File Path for {csv_file}, aborting...")
            _ = api.delete_deposit(depo_id)
            print("Error while uploading to Zenodo,\
                deleting newly created Deposit: ", depo_id)
            return None, None, None
        print("Successful Upload on Zenodo", depo_id)

    # finalize deposit into a persisten record
    depo_id = str(depo_id)
    _ = api.publish_deposit(depo_id)
    record_id = api.get_record(depo_id)["id"]

    # getting the download_url for the databus
    file_info = api.get_files_of_record(depo_id)[0]
    download_url = file_info['links']['content']

    return download_url, record_id, success


def upload_to_databus(api, download_url, format_extension, metadatajson,
                      user=None):
    header = {
        "Accept": "application/json",
        "X-API-KEY": api.databus_token,
        "Content-Type": "application/ld+json",
    }

    if not user:
        user = "prototype"

    url = urlparse(metadatajson["wasGeneratedBy"]["used"])
    version = Path(url.path).parts[-1]
    user_replaced_path = os.path.join(user, *Path(url.path).parts[2:])
    id = urlunparse(url._replace(fragment="", path=user_replaced_path))

    # building the databus data object from the JSON-LD
    data = {
        "@context": api.databus_context_url,
        "@graph": [
            {
                "@type": "Version",
                "@id": id,
                "hasVersion": version,
                "title": metadatajson["title"],
                "description": metadatajson["description"],
                "license": metadatajson["licenses"][0]["path"],
                "distribution": [{
                    "@type":  "Part",
                    "compression": "none",
                    "formatExtension": format_extension,
                    "downloadURL": download_url
                }],
            }
        ],
    }

    return api.databus_upload(data=data, header=header)


def upload_to_moss(api, databus_uri, metadatajsonfile, data=None):
    files = {"annotationGraph": open(metadatajsonfile, "rb")}
    data = {
        "databusURI": databus_uri,
        "modType": "OEMetadataMod",
        "modVersion": "1.0.0"
    }
    response = requests.post(api.moss_endpoint, files=files, data=data)
    print(response)
    return response


if __name__ == '__main__':
    # Setup | Load API keys and set endpoints
    api = setup_api()

    # Load metadata information
    csv_file, metadatajsonfile, depo_id, user = parse(api)
    csv_file, metadatajsonfile = api.create_complete_file_paths(csv_file,
                                                                metadatajsonfile)
    metadata = load_metadata_info(metadatajsonfile)

    # Upload file to Zenodo
    # set record here for debugging
    record_id = "10844724"
    # depo_id = record_id
    # if not depo_id:
    #     download_url, record_id, successful_upload = upload_to_zenodo(api,
    #                                                                   csv_file,
    #                                                                   metadata,
    #                                                                   depo_id=depo_id)

    #     if successful_upload:
    #         print("Successful upload to Zenodo")

    # print("""******************
    # Upload metadata to Databus
    # *****************""")
    download_url = api.get_files_of_record(record_id)[0]['links']['content']
    # format_extension is used from local csv file
    format_extension = api._get_extension(csv_file)
    databus_response, data = upload_to_databus(api, download_url,
                                               format_extension,
                                               metadata, user=user)
    if databus_response.ok:
        print("Successful upload to Databus")

    # Annotate DatabusURI with Metadata Graph
    databus_uri = data["@graph"][0]["@id"]
    moss_response = upload_to_moss(api, databus_uri, metadatajsonfile)

    if moss_response.ok:
        print("Successful upload to Databus")
