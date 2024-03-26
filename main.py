import os
import json
from pathlib import Path
from api_calls import API
from dotenv import load_dotenv
from databus_parser import parse
from urllib.parse import urlparse, urlunparse


def setup_api():
    load_dotenv()
    API_KEY = os.getenv("ZENODO_ACCESS_TOKEN")
    ZENODO_ENDPOINT = os.getenv("ZENODO_ENDPOINT")
    SANDBOX = os.getenv("SANDBOX")

    DATABUS_API_KEY = os.getenv("DATABUS_API_KEY")
    DATABUS_ENDPOINT = os.getenv("DATABUS_ENDPOINT")
    CONTEXT_URL = os.getenv("CONTEXT_URL")

    MOSS_ENDPOINT = os.getenv("MOSS_ENDPOINT")

    return API(API_KEY,
               DATABUS_API_KEY,
               MOSS_ENDPOINT,
               DATABUS_ENDPOINT,
               CONTEXT_URL,
               SANDBOX,
               ZENODO_ENDPOINT)


def load_metadata_info(metadatajsonfile):
    metadatajson = None
    with open(metadatajsonfile, "rb") as file:
        metadatajson = json.load(file)

    if not metadatajson:
        raise TypeError("Metadata should not be empty")

    return metadatajson


def upload_to_zenodo(api, csv_file, metadatajson, depo_id=None):
    success = False
    if not depo_id:
        info = api.create_deposit()
        depo_id = info["id"]

        metadata = api.generate_zendodo_input(metadatajson)
        api.update_deposit(depo_id, metadata=metadata)

        try:
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

    depo_id = str(depo_id)
    _ = api.publish_deposit(depo_id)
    record_id = api.get_record(depo_id)["id"]

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

    databus_base = "dev.databus.dbpedia.org"
    url = urlparse(metadatajson["wasGeneratedBy"]["used"])
    version = Path(url.path).parts[-1]
    user_replaced_path = os.path.join(user, *Path(url.path).parts[2:])
    id = urlunparse(url._replace(netloc=databus_base, fragment="",
                                 path=user_replaced_path))

    data = {
        "@context": api.context_url,
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


def upload_to_moss():
    # TODO:
    ...


if __name__ == '__main__':
    # Setup | Load API keys and set endpoints
    api = setup_api()

    # Load metadata information
    csv_file, metadatajsonfile, depo_id, user = parse(api)
    csv_file, metadatajsonfile = api.create_complete_file_paths(csv_file,
                                                                metadatajsonfile)
    metadata = load_metadata_info(metadatajsonfile)

    # Upload file to Zenodo
    record_id = "10844724"
    depo_id = record_id
    if not depo_id:
        download_url, record_id, successful_upload = upload_to_zenodo(api,
                                                                      csv_file,
                                                                      metadata,
                                                                      depo_id=depo_id)

        if successful_upload:
            print("Successful upload to Zenodo")

    # Upload publish on Databus
    download_url = api.get_files_of_record(record_id)[0]['links']['content']
    format_extension = api._get_extension(csv_file)
    response, data = upload_to_databus(api, download_url, format_extension,
                                       metadata, user=user)
    if response.ok:
        print("Successful upload to Databus")

    # Annotate DatabusURI with Metadata Graph
    upload_to_moss()
