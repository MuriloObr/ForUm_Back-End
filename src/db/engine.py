from sqlmodel import SQLModel, create_engine

from .models.user import User  
from .models.post import Post  
from .models.comment import Comment  

from dotenv import load_dotenv
from os import getenv

load_dotenv()

isProd = getenv("ISPROD", default=False)

url = getenv("POSTGRES_URL_LOCAL")

if isProd:
    url = getenv("POSTGRES_URL_PROD")

engine = create_engine(url)

SQLModel.metadata.create_all(engine)
