from database.models import User, Post, Comment, posts_likes, posts_views, comments_likes
from database.connect import engine
from sqlalchemy.orm import Session
from database.schemas import UserSchema, PostSchema, CommentSchema
import os
import bcrypt
import jwt
import datetime as date

secret_key = os.getenv("JWT_SECRET_KEY")


def getErrorHandler(func):
    def wrapper(*args, **kwargs):
        with Session(engine) as session:
            try:
                res = func(session, *args, **kwargs)

                if not res:
                    return {"code": 204, "res": ""}

            except Exception as e:
                session.rollback()
                return {"code": 400, "res": str(e)}
            else:
                return {"code": 200, "res": res}
    return wrapper


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


@getErrorHandler
def DBgetUserByID(session, id):
    schema = UserSchema()
    data = session.query(User).filter_by(id=id).first()
    jsonData = schema.dump(data)

    if not jsonData:
        return None

    # jsonData.pop("password")

    return jsonData


@getErrorHandler
def DBgetPostByID(session, id):
    schema = PostSchema()
    data = session.query(Post).filter_by(id=id).first()
    jsonData = schema.dump(data)
    jsonData["user"] = DBgetUserByID(jsonData["user"])["res"]

    if not jsonData:
        return None

    return jsonData


@getErrorHandler
def DBgetAllPosts(session):
    schema = PostSchema()
    data = session.query(Post).all()
    jsonData = []
    for post in data:
        jsonPost = schema.dump(post)
        jsonPost["user"] = DBgetUserByID(jsonPost["user"])["res"]
        jsonData.append(jsonPost)

    if not jsonData:
        return None

    return jsonData


@getErrorHandler
def DBgetAllPostsFromUser(session, id):
    schema = PostSchema()
    data = session.query(Post).filter_by(user_id=id).all()
    jsonData = []
    for post in data:
        jsonPost = schema.dump(post)
        jsonPost["user"] = DBgetUserByID(jsonPost["user"])["res"]
        jsonData.append(jsonPost)

    if not jsonData:
        return None

    return jsonData


@getErrorHandler
def DBgetAllCommentsFromPost(session, id):
    schema = CommentSchema()
    data = session.query(Comment).filter_by(post_id=id).all()
    jsonData = []
    for comment in data:
        jsonComment = schema.dump(comment)
        jsonComment["user"] = DBgetUserByID(jsonComment["user"])["res"]
        jsonData.append(jsonComment)

    if not jsonData:
        return None

    return jsonData


@postErrorHandler
def DBcreateNewPost(session, post, currentUser):
    schema = PostSchema()
    user = session.query(User).get(currentUser)

    if not user:
        return None

    data = Post(
        tittle=post["tittle"],
        content=post["content"],
        closed=False,
        user=user,
    )

    session.add(data)

    return schema.dump(data)


@postErrorHandler
def DBcreateNewComment(session, comment, currentUser):
    schema = CommentSchema()
    user = session.query(User).get(currentUser)
    post = session.query(Post).get(comment["post_id"])

    data = Comment(
        content=comment["content"],
        answer=False,
        user=user,
        post=post
    )

    session.add(data)

    return schema.dump(data)


@postErrorHandler
def DBlikePost(session, post_id, currentUser):
    schemas = [PostSchema(), UserSchema()]
    post = session.query(Post).get(post_id)
    user = session.query(User).get(currentUser)

    jsonPost = schemas[0].dump(post)
    jsonUser = schemas[1].dump(user)

    for like in jsonPost["likes"]:
        if like == jsonUser["id"]:
            return None

    post.likes.append(user)

    return f"Post: {jsonPost['tittle']} Liked by User: {jsonUser['username']}"


@postErrorHandler
def DBrmlikePost(session, post_id, currentUser):
    schemas = [PostSchema(), UserSchema()]
    post = session.query(Post).get(post_id)
    user = session.query(User).get(currentUser)

    jsonPost = schemas[0].dump(post)
    jsonUser = schemas[1].dump(user)

    post.likes.remove(user)

    return f"Post: {jsonPost['tittle']} Like Removed by User: {jsonUser['username']}"


@postErrorHandler
def DBlikeComment(session, comment_id, currentUser):
    schemas = [CommentSchema(), UserSchema()]
    comment = session.query(Comment).get(comment_id)
    user = session.query(User).get(currentUser)

    jsonComment = schemas[0].dump(comment)
    jsonUser = schemas[1].dump(user)

    for like in jsonComment["likes"]:
        if like == jsonUser["id"]:
            return None

    comment.likes.append(user)

    return f"Comment: {jsonComment['id']} Liked by User: {jsonUser['username']}"


@postErrorHandler
def DBrmlikeComment(session, comment_id, currentUser):
    schemas = [CommentSchema(), UserSchema()]
    comment = session.query(Comment).get(comment_id)
    user = session.query(User).get(currentUser)

    jsonComment = schemas[0].dump(comment)
    jsonUser = schemas[1].dump(user)

    comment.likes.remove(user)

    return f"Comment: {jsonComment['id']} Like Removed by User: {jsonUser['username']}"


@postErrorHandler
def DBchooseAnswer(session, post_id, comment_id, currentUser):
    schemas = [CommentSchema(), PostSchema(), UserSchema()]
    comment = session.query(Comment).get(comment_id)
    post = session.query(Post).get(post_id)
    user = session.query(User).get(currentUser)

    allComments = session.query(Comment).all()

    jsonComment = schemas[0].dump(comment)
    jsonPost = schemas[1].dump(post)
    jsonUser = schemas[2].dump(user)

    logicChain = [
        jsonPost["id"] not in jsonUser["posts"],
        jsonComment["id"] not in jsonPost["comments"],
    ]

    if logicChain[0] or logicChain[1]:
        return None

    for anyComment in allComments:
        anyComment.answer = False

    comment.answer = True

    return f"Post: {jsonComment['id']} is now {jsonComment['answer']}"


@postErrorHandler
def DBcloseOpenPost(session, post_id, currentUser):
    schemas = [PostSchema(), UserSchema()]
    post = session.query(Post).get(post_id)
    user = session.query(User).get(currentUser)

    jsonPost = schemas[0].dump(post)
    jsonUser = schemas[1].dump(user)

    if jsonPost["id"] not in jsonUser["posts"]:
        return None

    post.closed = not jsonPost["closed"]

    return f"Post: {jsonPost['id']} is now {not jsonPost['closed']}"


@postErrorHandler
def DBviewPost(session, post_id, currentUser):
    schemas = [PostSchema(), UserSchema()]
    post = session.query(Post).get(post_id)
    user = session.query(User).get(currentUser)

    jsonPost = schemas[0].dump(post)
    jsonUser = schemas[1].dump(user)

    for view in jsonPost["views"]:
        if view == jsonUser["id"]:
            return None

    post.views.append(user)

    return f"Post: {jsonPost['tittle']} Viewed by User: {jsonUser['username']}"


@postErrorHandler
def DBcreateNewUser(session, user):
    schema = UserSchema()

    hashPassword = bcrypt.hashpw(
        user["password"].encode("utf-8"), bcrypt.gensalt())
    print(hashPassword)

    if "@" in user["username"]:
        raise Exception("'@' char is not allowed in username")

    undefined = [True for val in user.values() if val.strip() ==
                 None or val.strip() == ""]
    
    if any(undefined):
        return None

    data = User(
        username=user["username"],
        nickname=user["nickname"],
        password=hashPassword.decode("utf-8"),
        email=user["email"]
    )

    hasUsername = session.query(User).filter_by(
        username=user["username"]).first()

    hasEmail = session.query(User).filter_by(
        email=user["email"]).first()

    if hasUsername or hasEmail:
        return None

    session.add(data)

    return f"User: {schema.dump(data)['username']} Created"


def DBlogin(user_email, password):
    with Session(engine) as session:
        try:
            if "@" in user_email:
                user = session.query(User).filter_by(email=user_email).first()
            else:
                user = session.query(User).filter_by(
                    username=user_email).first()

            if not user:
                return {"code": 204, "res": ""}

        except Exception as e:
            session.rollback()
            return {"code": 400, "res": str(e)}

        else:
            if bcrypt.checkpw(password.encode("utf-8"), user.password.encode("utf-8")):
                schema = UserSchema()
                user_id = schema.dump(user)["id"]

                token = jwt.encode({
                    "user_id": user_id,
                    "exp": date.datetime.now() + date.timedelta(hours=12)
                }, secret_key, algorithm="HS256")

                return {"code": 200, "res": token}
            else:
                return {"code": 401, "res": ""}
