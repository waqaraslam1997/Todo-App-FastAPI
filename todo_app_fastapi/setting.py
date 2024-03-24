from starlette.config import Config
from starlette.datastructures import Secret

try:
    config = Config(".env")
except FileNotFoundError:
    config = Config()

Database_URL = config("Database_URL", cast = Secret)

Test_Database_URL = config("Test_Database_URL", cast = Secret)