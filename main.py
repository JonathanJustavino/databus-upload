import os
from api_calls import API
from dotenv import load_dotenv


load_dotenv()
api_key = os.getenv("ACCESS_TOKEN")
wrapper = API(api_key)

records = wrapper.list_all_deposits()

# for record in records:
print(records)
