import os
import json
import curlify
import requests
from os import path
from dataclasses import dataclass
from urllib.parse import urlparse, urlunparse
from pathlib import Path
# from dotenv import load_dotenv


@dataclass
class API:
    zenodo_token: str
    zenodo_endpoint: str
    zenodo_sandbox: str
    databus_token: str
    databus_endpoint: str
    databus_context_url: str
    moss_endpoint: str

    def __init__(self,
                 zenodo_token, zenodo_endpoint, zenodo_sandbox,
                 databus_token, databus_endpoint, databus_context_url,
                 moss_endpoint) -> None:

        self.zenodo_token = zenodo_token
        self.zenodo_endpoint = zenodo_endpoint
        self.zenodo_sandbox = zenodo_sandbox

        self.databus_token = databus_token
        self.databus_endpoint = databus_endpoint
        self.databus_context_url = databus_context_url

        self.moss_endpoint = moss_endpoint

    def default_info(self):
        docu_info = '{"metadata": {"title": "My first upload", "upload_type": "Dataset", "description": "This is my first upload", "creators": [{"name": "Doe, John", "affiliation": "Zenodo"}]}}'
        return docu_info

    def json_content_header(self):
        return {"Content-Type": "application/json"}

    def multipart_content_header(self):
        return {"Content-Type": "multipart/form-data"}

    def build_url(self, *args):
        url = path.join(self.zenodo_endpoint, *args)
        return url

    def record_build_url(self, *args):
        return self.build_url("records", *args)

    def build_deposit_url(self, *args):
        return self.build_url("deposit", "depositions", *args)

    def build_publish_url(self, id):
        return self.build_deposit_url(str(id), "actions", "publish")

    def build_file_url(self, id, *args, deposit=True):
        if deposit:
            return self.build_deposit_url(id, "files", *args)
        return self.record_build_url(id, "files", *args)

    def authenticate(self, url):
        return f"{url}?access_token={self.zenodo_token}"

    def list_all_deposits(self):
        route = self.build_deposit_url()
        url = self.authenticate(route)
        req = requests.get(url)
        data = req.json()

        for record in data:
            print(record)

    def create_deposit(self, metadata=None):
        if not metadata:
            metadata = json.dumps(self.default_info())
            metadata = "{}"
        header = self.json_content_header()
        route = self.build_deposit_url()
        url = self.authenticate(route)
        req = requests.post(url, data=metadata, headers=header)
        curl = curlify.to_curl(req.request)
        print(curl)

        return req.json()

    def get_deposit(self, id):
        identifier = str(id)
        route = self.build_deposit_url(identifier)
        url = self.authenticate(route)
        req = requests.get(url)
        return req

    def update_deposit(self, id, metadata=None):
        # Already added when you pass json= but not when you pass data=
        headers = {'Content-Type': 'application/json', }

        identifier = str(id)
        route = self.build_deposit_url(identifier)
        url = self.authenticate(route)

        params = {'access_token': self.zenodo_token, }
        if not metadata:
            raise TypeError("Metadata should not be empty")

        response = requests.put(url, params=params,
                                headers=headers, json=metadata)
        print(response.json())
        return response

    def delete_deposit(self, id) -> bool:
        identifier = str(id)
        route = self.build_deposit_url(identifier)
        url = self.authenticate(route)
        response = requests.delete(url)
        print(response.headers)
        print(response.status_code)
        return response.ok

    def get_files_of_deposit(self, id):
        identifier = str(id)
        route = self.build_deposit_url(identifier, "files")
        url = self.authenticate(route)
        req = requests.get(url)
        return req.json()

    def get_files_of_record(self, id):
        identifier = str(id)
        route = self.record_build_url(identifier, "files")
        url = self.authenticate(route)
        req = requests.get(url)
        return req.json()["entries"]

    def _get_extension(self, filename):
        res = os.path.splitext(filename)[1]
        return res[1:]

    def get_deposit_file_links(self, deposit_id):
        files = self.get_files_of_deposit(deposit_id)
        links = []
        for file in files:
            url = file["links"]["download"]
            name = file["filename"]
            file_info = {
                "name": name,
                "formatExtension": self._get_extension(name),
                "compression": "None",
                "downloadURL": url,
             }
            links.append(file_info)
        return links

    def get_record_file_links(self, record_id):
        files = self.get_files_of_record(record_id)
        links = []
        for file in files:
            url = file["links"]["content"]
            name = file["key"]
            checksum = file["checksum"]
            file_info = {
                "name": name,
                "formatExtension": self._get_extension(name),
                "compression": "None",
                "downloadURL": url,
                "checksum": checksum
             }
            links.append(file_info)
        return links

    def upload_file(self, deposit_id, file_path):
        file_path = os.path.abspath(file_path)
        if not path.exists(file_path):
            raise FileNotFoundError
        if not path.isfile(file_path):
            raise FileNotFoundError

        deposit = self.get_deposit(deposit_id)
        deposit_id = str(deposit_id)
        bucket_link = deposit.json()["links"]["bucket"]

        _, file_name = path.split(file_path)
        route = f"{bucket_link}/{file_name}"
        url = self.authenticate(route)

        with open(file_path, "rb") as fp:
            params = {"-X": "PUT"}
            req = requests.put(url, data=fp, params=params)
            response = req.json()
            print(json.dumps(response, indent=4))
            return response

    def list_records(self):
        route = self.record_build_url()
        url = self.authenticate(route)
        response = requests.get(url)
        return response

    def get_record(self, record_id):
        route = self.record_build_url(record_id)
        response = requests.get(route)
        return response

    def show_files(self, record_id):
        route = self.build_file_url(record_id, deposit=False)
        print(route)
        response = requests.get(route)
        return response

    def show_file(self, record_id, file_id):
        route = self.build_file_url(record_id, file_id, deposit=False)
        print(route)
        response = requests.get(route)
        return response

    def publish_deposit(self, deposit_id):
        route = self.build_publish_url(deposit_id)
        url = self.authenticate(route)
        response = requests.post(url)
        return response

    def collect_files(self, directory):
        files = os.listdir(directory)
        print(files)
        return files

    def create_complete_file_paths(self, csv_file, metadatajson):
        csv_file = "model_draft__ind_steel_oxyfu_0.csv"
        csv_file = path.abspath(path.join("example-upload", csv_file))
        metadatajson = "metadata.json"
        metadatajson = path.abspath(path.join("example-upload", metadatajson))

        return csv_file, metadatajson

    def calculate_locally(self, url):
        """ TODO:
            use hashlib to compute sha256 of file
            and compute bytesize of file
            locally
        """
        ...

    def extract_metadata_info(self, metdatajsonfile):
        with open(metdatajsonfile, "rb") as metafile:
            return json.load(metafile)

    def generate_databus_input(self, download_url, format_extension,
                               metadatajson, user=None, debug=False):

        header = {
            "Accept": "application/json",
            "X-API-KEY": self.databus_token,
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
            "@context": self.databus_context_url,
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

        return self.databus_upload(data=data, header=header)

    def generate_zendodo_input(self, metadatajson):
        metadata = {
            'metadata': {
                'title': metadatajson["title"],
                'upload_type': 'Dataset',
                'description': metadatajson["description"],
                'creators': [
                    {
                        'name': 'Doe, John',
                        'affiliation': 'Script',
                    },
                ],
            },
        }
        return metadata

    def to_databus(self, depo_id, csv_file, metadatajson,
                   hasVersion, user, type="Version"):

        header = {
            "Accept": "application/json",
            "X-API-KEY": self.databus_token,
            "Content-Type": "application/ld+json",
        }

        data = self.generate_databus_input(depo_id, metadatajson,
                                           hasVersion, user)

        print(data)
        return self.databus_upload(data=data, header=header)

    def databus_upload(self, data={}, header={}):
        response = requests.post(self.databus_endpoint, headers=header,
                                 data=json.dumps(data))
        return response, data

    def publish_file(self, csv_file, metadatajson,
                     version, user=None, depo_id=None):
        csv_file, metadatajson, = self.create_complete_file_paths(csv_file,
                                                                  metadatajson)

        if not depo_id:
            info = self.create_deposit()
            depo_id = info["id"]

            metadata = self.generate_zendodo_input(metadatajson)
            self.update_deposit(depo_id, metadata=metadata)

            try:
                response = self.upload_file(depo_id, csv_file)
                print(response)
            except FileNotFoundError:
                print(f"Wrong File Path for {csv_file}, aborting...")
                _ = self.delete_deposit(depo_id)
                print("Error while uploading to Zenodo,\
                    deleting newly created Deposit: ", depo_id)
                return
            print("Successful Upload on Zenodo", depo_id)

        if not user:
            user = "prototype"

        depo_id = str(depo_id)
        res = self.publish_deposit(depo_id)
        res = self.get_record(depo_id)
        record_id = str(res.json()["id"])

        if res.ok:
            print("published Deposit", depo_id)
            print("Now Record", record_id)

            response, data = self.to_databus(depo_id, csv_file,
                                             metadatajson, version, user)
            if response.ok:
                self.to_moss(data["@graph"][0]["@id"], metadatajson)

    def to_moss(self, databus_uri, metadatajson, data=None):

        files = {"annotationGraph": open(metadatajson, "rb")}
        data = {
            "databusURI": databus_uri,
            "modType": "OEMetadataMod",
            "modVersion": "1.0.0"
        }
        response = requests.post(self.moss_endpoint, files=files, data=data)
        print(response)
