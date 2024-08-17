from database.connect import engine
from sqlalchemy.orm import Session

def errorHandler(method: str):
    def decorator(func):
        def wrapper(*args, **kwargs):
            with Session(engine) as session:
                try:
                    
                    data = func(session, *args, **kwargs)

                except Exception as e:
                    session.rollback()
                    raise e
                    return [None, e]
                else:
                    if method == "post":
                        session.commit()
                    return [data, None]
        return wrapper
    return decorator


def postErrorHandler(func):
    def wrapper(*args, **kwargs):
        with Session(engine) as session:
            try:
                res = func(session, *args, **kwargs)

                if not res:
                    return {"code": 409, "res": ""}

            except Exception as e:
                session.rollback()
                return {"code": 400, "res": str(e)}
            else:
                session.commit()
                return {"code": 201, "res": res}
    return wrapper