from sqlalchemy import create_engine
from dotenv import load_dotenv
from os import getenv

load_dotenv()

server = getenv("DATABASE_HOST")
username = getenv("DATABASE_USERNAME")
password = getenv("DATABASE_PASSWORD")
database = getenv("DATABASE")

print(server, username, password, database)

engine = create_engine(
    f"mysql+pymysql://{username}:{password}@{server}/{database}", echo=True)
