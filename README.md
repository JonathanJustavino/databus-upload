# README

## Setup & Install

```bash
# For Ubuntu
sudo apt install python3 python3.10-venv
# setting venv to "virtualenv"
python3 -m venv virtualenv
source virtualenv/bin/activate
# getting python dependency
pip install -r requirements.txt
```

## Credentials

create an .env file with the api keys

```bash
# Zenodo
ZENODO_ACCESS_TOKEN=XXX
ZENODO_ENDPOINT=XXX
ZENODO_SANDBOX=XXX

# Databus
DATABUS_API_KEY=XXX
DATABUS_ENDPOINT=XXX
DATABUS_CONTEXT_URL=XXX

# Moss
MOSS_ENDPOINT=XXX
```

## Quickstart

An example run with a sample csv and json.
Example files were taken from https://databus.openenergyplatform.org/anik/Industry_test/ind_steel_oxyfu_0/v1
MOSS Prov-O information was added to metadata.json

```bash
CSVFILE="example-upload/model_draft__ind_steel_oxyfu_0.csv"
OEMETADATA="example-upload/metadata.json"
python3 main.py --complete $CSVFILE $OEMETADATA
```

## Setup

- Make sure `Python3` is installed (3.7 or higher)
  - `sudo apt install python3`

1. Create virtual environment (execute the command venv)

```shell
python3 -m venv /path/to/new/virtual/environment
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
usage: main.py [-h] [--complete csv_file metadatafile]

Publish on Zenodo and Databus

options:
  -h, --help            show this help message and exit
  --complete csv_file metadatafile
                        Upload on Zenodo and Databus
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
python3 main.py --complete <file-to-csv> <file-to-metadatajson>
```
