from sqlalchemy import create_engine

engine = create_engine(f"sqlite:///forum.db", echo=True)
