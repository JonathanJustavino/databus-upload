from databus_parser import parse
from api_calls import setup_api


if __name__ == '__main__':
    api = setup_api()
    parse(api)
