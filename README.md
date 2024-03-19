# README

## Setup
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
options:
  -h, --help            show this help message and exit
  -c, --create_deposit  Create a new Deposit
  -d DEPOSIT, --deposit DEPOSIT
                        Retrieve a deposit by id
  -dl DOWNLOAD, --download DOWNLOAD
                        List all download links of files in a Deposit
  -f FILES, --files FILES
                        List all files of a Deposit
  -u UPLOAD, --upload UPLOAD
                        Upload a file to a Deposit
  -s UPDATE, --update UPDATE
                        Update a Deposit
  -p PUBLISH, --publish PUBLISH
                        Upload to Databus
  -del DELETE_DEPOSIT, --delete_deposit DELETE_DEPOSIT
                        Delete a deposit by id
  -ds, --deposits       List all Deposits of a User
```
