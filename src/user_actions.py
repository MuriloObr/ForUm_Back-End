from sqlmodel import Session, select
from src.db.models.user import User
from src.db.engine import engine
from utils.api_types import NewUser
from utils.error_decorators import errorHandler
import os
import bcrypt
import jwt
import datetime as date

secret_key = os.getenv("JWT_SECRET_KEY")
jwt_algorithm = os.getenv("JWT_ALGORITHM")


def _get_user_data(session: Session, id: int):
    data = session.get(User, id)

    if data is None:
        return None

    jsonData = data.model_dump()
    jsonData.pop("password")

    return jsonData


@errorHandler("get")
def get_user_by_id(session: Session, id: int):
    return _get_user_data(session, id)


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

    hasUsername = session.exec(
        select(User).where(User.username == user.username)
    ).first()

    hasEmail = session.exec(
        select(User).where(User.email == user.email)
    ).first()

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


def login_with_user_or_email(user_email: str, password: str) -> list[None | str]:
    with Session(engine) as session:
        try:
            if "@" in user_email:
                user = session.exec(
                    select(User).where(User.email == user_email)
                ).first()
            else:
                user = session.exec(
                    select(User).where(User.username == user_email)
                ).first()

            if user is None:
                return [None, None]

        except Exception as e:
            session.rollback()
            return [None, str(e)]

        else:
            if bcrypt.checkpw(password.encode("utf-8"), user.password.encode("utf-8")):
                token = jwt.encode({
                    "user_id": user.id,
                    "exp": date.datetime.now() + date.timedelta(hours=12)
                }, secret_key, algorithm=jwt_algorithm)

                return [token, None]
            else:
                return [None, None]
