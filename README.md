# README

## Setup

- Make sure Python3 is installed (3.7 or higher)
  - `sudo apt install python3`

1. Create virtual environment (execute the command venv)
 
```shell
python -m venv /path/to/new/virtual/environment
```
2. Activate virtual environment

```shell
source <venv>/bin/activate
```
3. Install required packages

```shell
pip install -r requirements.txt
```
4. Run the program (e.g. python3 main.py --help)

```shell
python3 main.py -h
usage: main.py [-h] [--complete directory Group Artifact Version License] [-c] [-d deposit_id] [-dl deposit_id] [-f deposit_id] [-ul deposit_id] [-ud deposit_id]
               [-s deposit_id] [-p deposit_id] [-id deposit_id] [-del deposit_id] [-ds] [-rs] [-r record_id] [-rfs record_id] [-rf record_id file_id]

options:
  -h, --help            show this help message and exit
  --complete directory Group Artifact Version License
                        Upload on Zenodo and Databus
  -c, --create_deposit  Create a new Deposit
  -d deposit_id, --deposit deposit_id
                        Retrieve a deposit by id
  -dl deposit_id, --download deposit_id
                        List all download links of files in a Deposit
  -f deposit_id, --files deposit_id
                        List all files of a Deposit
  -ul deposit_id, --upload deposit_id
                        Upload a file to a Deposit
  -ud deposit_id, --update deposit_id
                        Update a Deposit
  -s deposit_id, --sync_databus deposit_id
                        Update a Deposit
  -p deposit_id, --publish deposit_id
                        Upload to Databus
  -id deposit_id, --depo_id deposit_id
                        deposit_id
  -del deposit_id, --delete_deposit deposit_id
                        Delete a deposit by id
  -ds, --deposits       List all Deposits of a User
  -rs, --records        List all Records
  -r record_id, --record record_id
                        Show a specific Record
  -rfs record_id, --record_files record_id
                        Show files from a specific Record
  -rf record_id file_id, --record_file record_id file_id
                        Show file from a specific Record
```

5. Example: Upload File to Zenodo, publish the Deposit and publish the metadata on the Databus

This command creates a new deposit, uploads a file in a specified directory to Zenodo
and publishes the metadata on the databas specified under the parameters:

- csv
  - path to the csv that will be uploaded to zenodo
- metadata.json
  - path to the metadata.json describing the csv data 
- version
  - artifact version on the databus
- (Optional) username
  - if not specified the user name is set to "prototype"

```bash
python3 main.py --complete <file-to-csv> <file-to-metadatajson> <version> <optional-user-name>
```
