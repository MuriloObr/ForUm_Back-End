from sqlmodel import Session, select
from src.db.models.user import User
from src.db.models.post import Post
from src.db.models.comment import Comment
from src.user_actions import _get_user_data
from utils.api_types import NewComment
from utils.error_decorators import errorHandler


@errorHandler("get")
def get_all_comments_from_post(session: Session, id):
    data = session.exec(select(Comment).where(Comment.post_id == id)).all()

    if not data:
        return False

    jsonData = []
    for comment in data:
        jsonComment = comment.model_dump()
        jsonComment["user"] = _get_user_data(session, jsonComment["user_id"])
        jsonData.append(jsonComment)

    return jsonData


@errorHandler("post")
def create_new_comment(session: Session, comment: NewComment, currentUser):
    user = session.get(User, currentUser)
    post = session.get(Post, comment.post_id)

    data = Comment(
        content=comment.content,
        user=user,
        post=post
    )

    session.add(data)
    session.flush()

    return data.model_dump()


@errorHandler("post")
def like_comment(session: Session, comment_id, currentUser):
    comment = session.get(Comment, comment_id)
    user = session.get(User, currentUser)

    jsonComment = comment.model_dump()
    jsonUser = user.model_dump()

    for like in comment.likes:
        if like.id == jsonUser["id"]:
            return False

    comment.likes.append(user)

    return f"Comment: {jsonComment['id']} Liked by User: {jsonUser['username']}"


@errorHandler("post")
def rm_like_comment(session: Session, comment_id, currentUser):
    comment = session.get(Comment, comment_id)
    user = session.get(User, currentUser)

    jsonComment = comment.model_dump()
    jsonUser = user.model_dump()

    comment.likes.remove(user)

    return f"Comment: {jsonComment['id']} Like Removed by User: {jsonUser['username']}"
