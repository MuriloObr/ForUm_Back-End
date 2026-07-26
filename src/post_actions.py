from sqlmodel import Session, select
from src.db.models.user import User
from src.db.models.post import Post
from src.db.models.comment import Comment
from src.user_actions import _get_user_data
from utils.api_types import NewPost
from utils.error_decorators import errorHandler


@errorHandler("get")
def get_post_by_id(session: Session, id: int):
    data = session.get(Post, id)

    if data is None:
        return False

    jsonData = data.model_dump()
    jsonData["user"] = _get_user_data(session, jsonData["user_id"])

    return jsonData


@errorHandler("get")
def get_all_posts(session: Session):
    data = session.exec(select(Post)).all()

    if not data:
        return False

    jsonData = []
    for post in data:
        jsonPost = post.model_dump()
        jsonPost["user"] = _get_user_data(session, jsonPost["user_id"])
        jsonData.append(jsonPost)

    return jsonData


@errorHandler("get")
def get_all_posts_from_user(session: Session, id):
    data = session.exec(select(Post).where(Post.user_id == id)).all()

    if not data:
        return False

    jsonData = []
    for post in data:
        jsonPost = post.model_dump()
        jsonPost["user"] = _get_user_data(session, jsonPost["user_id"])
        jsonData.append(jsonPost)

    return jsonData


@errorHandler("post")
def create_new_post(session: Session, post: NewPost, currentUser):
    user = session.get(User, currentUser)

    if user is None:
        return False

    data = Post(
        title=post.title,
        content=post.content,
        is_closed=False,
        user=user,
    )

    session.add(data)
    session.flush()

    jsonData = data.model_dump()
    jsonData["user"] = _get_user_data(session, jsonData["user_id"])

    return jsonData


@errorHandler("post")
def delete_post(session: Session, post_id, currentUser):
    post = session.get(Post, post_id)
    user = session.get(User, currentUser)

    jsonPost = post.model_dump()
    jsonUser = user.model_dump()

    session.delete(post)

    return f"Post: {jsonPost['title']} Deleted by User: {jsonUser['username']}"


@errorHandler("post")
def like_post(session: Session, post_id, currentUser):
    post = session.get(Post, post_id)
    user = session.get(User, currentUser)

    jsonPost = post.model_dump()
    jsonUser = user.model_dump()

    for like in post.likes:
        if like.id == jsonUser["id"]:
            return False

    post.likes.append(user)

    return f"Post: {jsonPost['title']} Liked by User: {jsonUser['username']}"


@errorHandler("post")
def rm_like_post(session: Session, post_id, currentUser):
    post = session.get(Post, post_id)
    user = session.get(User, currentUser)

    jsonPost = post.model_dump()
    jsonUser = user.model_dump()

    post.likes.remove(user)

    return f"Post: {jsonPost['title']} Like Removed by User: {jsonUser['username']}"


@errorHandler("post")
def choose_answer(session: Session, post_id, comment_id, currentUser):
    post = session.get(Post, post_id)
    comment = session.get(Comment, comment_id)
    user = session.get(User, currentUser)

    if post is None or comment is None or user is None:
        return False

    jsonPost = post.model_dump()
    jsonUser = user.model_dump()

    if jsonPost["user_id"] != jsonUser["id"]:
        return False

    if comment.post_id != post.id:
        return False

    post.answer_id = comment.id

    return f"Post: {post.id} answer set to Comment: {comment.id}"


@errorHandler("post")
def close_or_open_post(session: Session, post_id, currentUser):
    post = session.get(Post, post_id)
    user = session.get(User, currentUser)

    jsonPost = post.model_dump()
    jsonUser = user.model_dump()

    if jsonPost["user_id"] != jsonUser["id"]:
        return False

    post.is_closed = not jsonPost["is_closed"]

    return f"Post: {jsonPost['id']} is now {not jsonPost['is_closed']}"


@errorHandler("post")
def view_post(session: Session, post_id, currentUser):
    post = session.get(Post, post_id)
    user = session.get(User, currentUser)

    jsonPost = post.model_dump()
    jsonUser = user.model_dump()

    for view in post.views:
        if view.id == jsonUser["id"]:
            return False

    post.views.append(user)

    return f"Post: {jsonPost['title']} Viewed by User: {jsonUser['username']}"
