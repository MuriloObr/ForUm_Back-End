from database.models import User, Post, Comment
from database.schemas import UserSchema, PostSchema, CommentSchema
from src.user_actions import get_user_by_id
from utils.api_types import NewPost
from utils.error_decorators import errorHandler
from sqlalchemy.orm import Session

@errorHandler("get")
def get_post_by_id(session: Session, id: int):
    schema = PostSchema()
    data = session.query(Post).filter_by(id=id).first()

    if data is None:
        return None

    jsonData = schema.dump(data)
    jsonData["user"] = get_user_by_id(jsonData["user"])["res"]

    return jsonData


@errorHandler("get")
def get_all_posts(session: Session):
    schema = PostSchema()
    data = session.query(Post).all()

    if data is None:
        return None
    
    jsonData = []
    for post in data:
        jsonPost = schema.dump(post)
        jsonPost["user"] = get_user_by_id(jsonPost["user"])["res"]
        jsonData.append(jsonPost)

    return jsonData


@errorHandler("get")
def get_all_posts_from_user(session: Session, id):
    schema = PostSchema()
    data = session.query(Post).filter_by(user_id=id).all()

    print(f"\033[31m {data}")
    if data == []:
        print("here")
        return False
    
    jsonData = []
    for post in data:
        jsonPost = schema.dump(post)
        jsonPost["user"] = get_user_by_id(jsonPost["user"])["res"]
        jsonData.append(jsonPost)

    return jsonData


@errorHandler("post")
def create_new_post(session: Session, post: NewPost, currentUser):
    schema = PostSchema()
    user = session.query(User).get(currentUser)

    if not user:
        return None

    data = Post(
        tittle=post.tittle,
        content=post.content,
        closed=False,
        user=user,
    )

    session.add(data)

    return schema.dump(data)


@errorHandler("post")
def delete_post(session: Session, post_id, currentUser):
    schemas = [PostSchema(), UserSchema()]
    post = session.query(Post).get(post_id)
    user = session.query(User).get(currentUser)

    jsonPost = schemas[0].dump(post)
    jsonUser = schemas[1].dump(user)
    
    session.delete(post)

    return f"Post: {jsonPost['tittle']} Deleted by User: {jsonUser['username']}"



@errorHandler("post")
def like_post(session: Session, post_id, currentUser):
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


@errorHandler("post")
def rm_like_post(session: Session, post_id, currentUser):
    schemas = [PostSchema(), UserSchema()]
    post = session.query(Post).get(post_id)
    user = session.query(User).get(currentUser)

    jsonPost = schemas[0].dump(post)
    jsonUser = schemas[1].dump(user)

    post.likes.remove(user)

    return f"Post: {jsonPost['tittle']} Like Removed by User: {jsonUser['username']}"



@errorHandler("post")
def choose_answer(session: Session, post_id, comment_id, currentUser):
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


@errorHandler("post")
def close_or_open_post(session: Session, post_id, currentUser):
    schemas = [PostSchema(), UserSchema()]
    post = session.query(Post).get(post_id)
    user = session.query(User).get(currentUser)

    jsonPost = schemas[0].dump(post)
    jsonUser = schemas[1].dump(user)

    if jsonPost["id"] not in jsonUser["posts"]:
        return None

    post.closed = not jsonPost["closed"]

    return f"Post: {jsonPost['id']} is now {not jsonPost['closed']}"


@errorHandler("post")
def view_post(session: Session, post_id, currentUser):
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
