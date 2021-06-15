import os

from dotenv import load_dotenv, find_dotenv

from grants.utils import get_engine

load_dotenv(find_dotenv('.env', raise_error_if_not_found=True))

root_engine = get_engine('root', os.getenv('DB_PASS'))
user_engine = get_engine(os.getenv('DB_USER'), os.getenv('DB_PASS'))
