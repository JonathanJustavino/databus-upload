import json
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

    def _add_credentials(self, url):
        return f"{url}?access_token={self.token}"

    def build_url(self, *args):
        url = path.join(self.endpoint, *args)
        return self._add_credentials(url)

    def list_all_deposits(self):
        url = self.build_url("deposit", "depositions")
        req = requests.get(url)
        data = req.json()

        for record in data:
            for field in self.fields:
                print(field)
                print(json.dumps(record[field], indent=2))

    def default_info(self):
        info = """
        {
            "metadata": {
                "title": "My generated Upload",
                "upload_type": "presentation",
                "upload_type": "presentation",
                "creators": [
                    {"name": "Python, Script", "affiliation": "Zeno"}
                ],
            }
        }
        """
        return info

    def set_header(self):
        ...

    def create_deposit(self, metadata=None):
        url = self.build_url("deposit", "depositions")
        print(url)
