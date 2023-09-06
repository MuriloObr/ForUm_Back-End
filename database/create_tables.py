from models import Base, User, Post, Comment
from connect import engine


print("Creating Tables...")
Base.metadata.create_all(bind=engine)
