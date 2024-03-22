import os
import json
import curlify
import requests
from os import path
from dataclasses import dataclass
from dotenv import load_dotenv


def setup_api():
    load_dotenv()
    api_key = os.getenv("ACCESS_TOKEN")
    databus_api_key = os.getenv("DATABUS_API_KEY")
    wrapper = API(api_key, databus_api_key)
    return wrapper


@dataclass
class API:
    token: str
    databus_token: str
    databus_endpoint = "https://dev.databus.dbpedia.org/api/publish?fetch-file-properties=true&log-level=debug"
    context_url = "https://dev.databus.dbpedia.org/res/context.jsonld"
    sandbox = "https://sandbox.zenodo.org/"
    endpoint = "https://zenodo.org/api/"

    def __init__(self, token, databus_token) -> None:
        self.token = token
        self.databus_token = databus_token

    def default_info(self):
        docu_info = '{"metadata": {"title": "My first upload", "upload_type": "poster", "description": "This is my first upload", "creators": [{"name": "Doe, John", "affiliation": "Zenodo"}]}}'
        return docu_info

    def json_content_header(self):
        return {"Content-Type": "application/json"}

    def multipart_content_header(self):
        return {"Content-Type": "multipart/form-data"}

    def build_url(self, *args):
        url = path.join(self.endpoint, *args)
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
        return f"{url}?access_token={self.token}"

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

        params = {'access_token': self.token, }
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
        # curl -i -X POST https://zenodo.org/api/deposit/depositions/1234/actions/publish?access_token=ACCESS_TOKEN
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

    def generate_databus_input(self, depo_id, metadatajson, hasVersion, user=None):
        file_info = self.get_files_of_record(depo_id)[0]
        with open(metadatajson, "rb") as metafile:
            metadatajson = json.load(metafile)
            distribution = [
                {
                    "@type":  "Part",
                    "compression": "none",
                    "formatExtension": self._get_extension(file_info["key"]),
                    "downloadURL": file_info['links']['content']
                }
            ]

            id = metadatajson["wasGeneratedBy"]["used"].split('#')[0]
            # TODO: temp fix for id
            if not user:
                user = "prototype"
            group = "my-group"
            artifact = "my-artifact"
            version = hasVersion
            id = f"https://dev.databus.dbpedia.org/{user}/{group}/{artifact}/{version}"
            license = metadatajson["wasGeneratedBy"]["license"]
            description = metadatajson["description"]
            title = metadatajson["title"]

            data = {
                "@context": self.context_url,
                "@graph": [
                    {
                        "@type": "Version",
                        "@id": id,  # TODO: muss version URI sein -> aus der metadatajson die used uri nehmen und alles nach dem fragment nehmen
                        "hasVersion": hasVersion,
                        "title": title,
                        "description": description,
                        "license": license,  # TODO: nimm license aus der metadatajson
                        "distribution": distribution,
                    }
                ],
            }
            return data

    def generate_zendodo_input(self, metadatajson):
        with open(metadatajson, "rb") as file:
            metadatajson = json.load(file)
            metadata = {
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
            }
            return metadata

    def to_databus(self, depo_id, csv_file, metadatajson, hasVersion, user, type="Version"):

        header = {
            "Accept": "application/json",
            "X-API-KEY": self.databus_token,
            "Content-Type": "application/ld+json",
        }

        data = self.generate_databus_input(depo_id, metadatajson, hasVersion, user)

        print(data)

        response = requests.post(self.databus_endpoint, headers=header,
                                 data=json.dumps(data))
        return response

    def publish_file(self, csv_file, metadatajson,
                     version, user=None, depo_id=None):
        csv_file, metadatajson, = self.create_complete_file_paths(csv_file, metadatajson)

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
            return self.to_databus(depo_id, csv_file, metadatajson, version, user)
