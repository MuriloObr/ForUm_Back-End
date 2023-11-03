from sqlalchemy import create_engine
from dotenv import load_dotenv
from os import getenv

load_dotenv()

database = getenv("DATABASE_URL_POSTGRES")

engine = create_engine(database, echo=True, client_encoding="utf8")
