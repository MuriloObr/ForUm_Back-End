from sqlalchemy import create_engine
from dotenv import load_dotenv
from os import getenv

dev_mode = True

load_dotenv()

if dev_mode == False:
  database = getenv("DATABASE_URL_POSTGRES")
else:
  database = getenv("DATABASE_URL_POSTGRESDEV")

print(database)
engine = create_engine(database, echo=True, client_encoding="utf8")
