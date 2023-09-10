from sqlalchemy import create_engine
from dotenv import load_dotenv
from os import getenv

load_dotenv()

database = getenv("DATABASE_URL")

engine = create_engine(
    f"{database}", echo=True)
