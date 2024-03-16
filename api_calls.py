import os
import json
import curlify
import requests
from os import path
from dataclasses import dataclass


@dataclass
class API:
    token: str
    sandbox = "https://sandbox.zenodo.org/"
    endpoint = "https://zenodo.org/api/"

    def __init__(self, token) -> None:
        self.token = token
        self.fields = [
            "id",
            "links",
            "files"
        ]

    def default_info(self):
        info = "{metadata:{ title: My generated Depot, upload_type: presentation, description: This is my first upload, creators: [ {name: Python, Script, affiliation: Zeno} ], }}"
        return info

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
        route = self.build_url("deposit", "depositions")
        url = self.authenticate(route)
        req = requests.get(url)
        data = req.json()

        for record in data:
            print(record)
            # for field in self.fields:
            #     print(field)
            #     print(json.dumps(record[field], indent=2))

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
        if not metadata:
            print("insufficient data for update")
            print("using default")
            # exit()
        identifier = str(id)
        route = self.build_deposit_url(identifier)
        url = self.authenticate(route)
        metadata = self.default_info()
        print(url)
        print(metadata)
        req = requests.put(url, data=json.dumps(metadata))
        return req.json()

    def delete_deposit(self, id):
        identifier = str(id)
        route = self.build_deposit_url(identifier)
        url = self.authenticate(route)
        req = requests.delete(url)
        print(req.headers)

    def get_files_of_deposit(self, id):
        identifier = str(id)
        route = self.build_deposit_url(identifier, "files")
        url = self.authenticate(route)
        req = requests.get(url)
        return req.json()

    def upload_file(self, deposit_id, file_path):
        if not path.exists(file_path):
            raise FileNotFoundError
        if not path.isfile(file_path):
            raise FileNotFoundError

        deposit_id = str(deposit_id)
        header = self.multipart_content_header()
        route = self.build_file_url(deposit_id)
        print(route)

        url = self.authenticate(route)

        _, file_name = path.split(file_path)
        print(file_name)
        fp = path.join(os.getcwd(), file_name)
        print(fp)

        files = {
            'name': (None, file_name),
            'file': open(fp, "rb")
        }

        params = {"-X": "POST"}

        print(url)
        req = requests.post(url, headers=header, files=files, params=params)
        print(requests.post(url, headers=header, files=files, params=params))
        response = req.json()
        print(json.dumps(response, indent=4))


# curl -i -H "Content-Type: application/json"
# -X PUT 
# --data '{"metadata": 
#             {"title": "My first upload", 
#             "upload_type": "poster", 
#             "description": "This is my first upload",
#             "arbitrary": "some more additional metadata",
#             "creators": [
#                 {"name": "Doe, John",
#                 "affiliation": "Zenodo"}
#             ]
#         }
#     }' 
# https://zenodo.org/api/deposit/depositions/10817080\?access_token\=iVkHh6aGfWIOlgy1XcCx3SvBqtFS4XJhlL8yomqoZuzGGjO9ga0PsCIS53DI