import os
import json
import curlify
import requests
from os import path
from dataclasses import dataclass
import datetime
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

    def build_deposit_url(self, *args):
        deposit_url = self.build_url("deposit", "depositions", *args)
        return deposit_url

    def build_file_url(self, deposit_id, *args):
        deposit_url = self.build_deposit_url(deposit_id, "files", *args)
        return deposit_url

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
        return req.json()

    def update_deposit(self, id, metadata=None):
        # Already added when you pass json= but not when you pass data=
        headers = {'Content-Type': 'application/json', }

        identifier = str(id)
        route = self.build_deposit_url(identifier)
        url = self.authenticate(route)

        params = {'access_token': self.token, }

        json_data = {
            'metadata': {
                'title': 'My first upload',
                'upload_type': 'poster',
                'description': 'This is my first upload',
                'creators': [
                    {
                        'name': 'Doe, John',
                        'affiliation': 'Zenodo',
                    },
                ],
            },
        }

        response = requests.put(url, params=params,
                                headers=headers, json=json_data)
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

    def _get_extension(self, filename):
        res = os.path.splitext(filename)[1]
        return res[1:]

    def get_download_links(self, deposit_id):
        base_path = path.join(path.expanduser("~"), "Downloads", "zenodo")
        files = self.get_files_of_deposit(deposit_id)
        success = []
        errors = []
        for file in files:
            url = file["links"]["download"]
            response = requests.get(self.authenticate(url))
            name = file["filename"]
            if not response.ok:
                file_info = {
                    "name": name,
                    "downloadURL": url,
                }
                errors.append(file_info)
                continue
            file_info = {
                "name": name,
                "formatExtension": self._get_extension(name),
                "compression": "None",
                "downloadURL": url,
             }
            success.append(file_info)
            with open(path.join(base_path, name), "wb") as f:
                f.write(response.content)
        return {"success": success, "error": errors}

    def upload_file(self, deposit_id, file_path):
        file_path = os.path.abspath(file_path)
        if not path.exists(file_path):
            raise FileNotFoundError
        if not path.isfile(file_path):
            raise FileNotFoundError

        deposit = self.get_deposit(deposit_id)
        deposit_id = str(deposit_id)
        bucket_link = deposit["links"]["bucket"]

        _, file_name = path.split(file_path)
        route = f"{bucket_link}/{file_name}"
        url = self.authenticate(route)

        with open(file_path, "rb") as fp:
            params = {"-X": "PUT"}
            req = requests.put(url, data=fp, params=params)
            response = req.json()
            print(json.dumps(response, indent=4))

    def calculate_locally(self, url):
        # calculate checksum and byte size locally
        ...

    def collect_for_databus(self,
                            depo_id,
                            group,
                            artifact,
                            version,
                            required_fields=[
                                "description", "title", "license"
                            ]):
        depo_info = self.get_deposit(depo_id)
        dlinks = self.get_download_links(depo_id)
        if not version:
            version = datetime.datetime.fromisoformat(depo_info["created"])
        hasVersion = version.strftime("%Y-%m-%d")
        metadata = depo_info["metadata"]

        metadata_fields = metadata.keys()
        matches = list(filter(lambda field: field in required_fields,
                              metadata_fields))

        if len(matches) != len(required_fields):
            print("Error")
            return

        description = metadata["description"]
        title = metadata["title"]
        license = metadata["license"]
        id = depo_info["id"]
        username = "prototype"
        id = f"https://dev.databus.dbpedia.org/{username}/{group}/{artifact}/{hasVersion}"

        context = depo_info["links"]["self"]

        def process(item):
            processed = {
                "@type":  "Part",
                "compression": "none",
                "formatExtension": item["formatExtension"],
                "downloadURL": self.authenticate(item['downloadURL'])
            }
            return processed

        distribution = list(map(process, dlinks["success"]))

        response = self.to_databus(context, id, hasVersion, title,
                                   description, license, distribution)
        return response

    def to_databus(self, context, id, hasVersion, title, description,
                   license, distribution, type="Version"):

        # TODO: how to convert to url
        license = "https://creativecommons.org/licenses/by/4.0/"

        header = {
            "Accept": "application/json",
            "X-API-KEY": self.databus_token,
            "Content-Type": "application/ld+json"
        }

        data = {
            "@context": self.context_url,
            "@graph": [
                {
                    "@type": type,
                    "@id": id,
                    "hasVersion": hasVersion,
                    "title": title,
                    "description": description,
                    "license": license,
                    "distribution": distribution,
                }
            ]
        }

        print(data)

        response = requests.post(self.databus_endpoint, headers=header,
                                 data=json.dumps(data))
        # print(curlify.to_curl(response.request))
        return response

    def collect_files(self, directory):
        files = os.listdir(directory)
        print(files)
        return files

    def publish_files(self, directory, group,
                      artifact, version, depo_id=None):

        files = self.collect_files(directory)
        version = datetime.datetime.strptime(version, '%Y-%m-%d').date()

        files = [path.abspath(path.join(directory, file)) for file in files]
        if not depo_id:
            info = self.create_deposit()
            depo_id = info["id"]
            self.update_deposit(depo_id)
        file_reports = []
        current_file = ""
        try:
            for file in files:
                current_file = file
                response = self.upload_file(depo_id, file)
                file_reports.append(response)
        except FileNotFoundError:
            print(f"Wrong File Path for {current_file}, aborting...")
            _ = self.delete_deposit(depo_id)
            print("Error while uploading to Zenodo,\
                  deleting newly created Deposit: ", depo_id)
            return
        print("Successful Upload on Zenodo", depo_id)
        return self.collect_for_databus(depo_id, group, artifact, version)