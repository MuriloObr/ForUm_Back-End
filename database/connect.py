from sqlalchemy import create_engine
from dotenv import load_dotenv
from os import getenv

dev_mode = False

load_dotenv()

if not dev_mode:
  database = getenv("DATABASE_URL_POSTGRES")
else:
  database = getenv("DATABASE_URL_POSTGRESDEV")

engine = create_engine(database, echo=False, client_encoding="utf8")
