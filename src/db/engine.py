from sqlmodel import SQLModel, create_engine

from .models.user import User  # noqa: F401
from .models.post import Post  # noqa: F401
from .models.comment import Comment  # noqa: F401

from dotenv import find_dotenv, load_dotenv
from os import getenv

dotenv_path = find_dotenv(".env")

load_dotenv()

isProd = getenv("ISPROD", default=False)

url = getenv("POSTGRES_URL_LOCAL", default="")

if isProd:
    url = getenv("POSTGRES_URL_PROD", default="")

engine = create_engine(url, echo=False)
