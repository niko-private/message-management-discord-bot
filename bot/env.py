from pymongo import MongoClient
from cachetools import TTLCache
from dotenv import load_dotenv
import os

load_dotenv()

discord_token = f"{os.getenv('DISCORD_TOKEN')}"
mongodb_string = f"{os.getenv('MONGODB_STRING')}"
cluster = MongoClient(mongodb_string)
users, items = cluster['discord']['users'], cluster['discord']['items']

user_cache = TTLCache(maxsize=100, ttl=300)
paginate_cache = TTLCache(maxsize=100, ttl=500)
trade_cache = TTLCache(maxsize=20, ttl=120)

AUTHOR_ID = int(os.getenv('AUTHOR_ID'))
special_user = (int(os.getenv('SPECIAL_USER')), os.getenv('SPECIAL_PHRASE'))
catch_phrase = ""