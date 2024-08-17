from database.models import User
from database.connect import engine
from sqlalchemy.orm import Session
from database.schemas import UserSchema
from utils.api_types import NewUser
from utils.error_decorators import errorHandler
import os
import bcrypt
import jwt
import datetime as date

secret_key = os.getenv("JWT_SECRET_KEY")
jwt_algorithm = os.getenv("JWT_ALGORITHM")


@errorHandler("get")
def get_user_by_id(session: Session, id: int):
    schema = UserSchema()
    data = session.query(User).filter_by(id=id).first()

    if data is None:
        return None

    jsonData = schema.dump(data)
    jsonData.pop("password")

    return jsonData


@errorHandler("post")
def create_new_user(session: Session, user: NewUser):
    pwd = f"{user.password}"

    hashPassword = bcrypt.hashpw(
        pwd.encode("utf-8"), bcrypt.gensalt())

    if "@" in user.username:
        raise Exception("'@' char is not allowed in username")

    undefined = [
        True for val in user.model_dump().values() 
        if val.strip() is None or val.strip() == ""
    ]
    
    if any(undefined):
        return None
    
    hasUsername = session.query(User).filter_by(
        username=user.username).first()

    hasEmail = session.query(User).filter_by(
        email=user.email).first()

    if hasUsername or hasEmail:
        return None

    data = User(
        username=user.username,
        nickname=user.nickname,
        password=hashPassword.decode("utf-8"),
        email=user.email
    )

    session.add(data)

    return f"User: {data.username} Created"


def login_with_user_or_email(user_email: str, password: str) -> list[None|str]:
    with Session(engine) as session:
        try:
            if "@" in user_email:
                user = session.query(User).filter_by(email=user_email).first()
            else:
                user = session.query(User).filter_by(
                    username=user_email).first()

            if not user:
                return [None, None]

        except Exception as e:
            session.rollback()
            return [None, str(e)]

        else:
            if bcrypt.checkpw(password.encode("utf-8"), user.password.encode("utf-8")):
                schema = UserSchema()
                user_id = schema.dump(user)["id"]

                token = jwt.encode({
                    "user_id": user_id,
                    "exp": date.datetime.now() + date.timedelta(hours=12)
                }, secret_key, algorithm=jwt_algorithm)

                return [token, None]
            else:
                return [None, None]
