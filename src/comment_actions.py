from database.models import User, Post, Comment
from database.schemas import UserSchema, CommentSchema
from src.user_actions import get_user_by_id
from utils.api_types import NewComment
from utils.error_decorators import errorHandler
from sqlalchemy.orm import Session

@errorHandler("get")
def get_all_comments_from_post(session, id):
    schema = CommentSchema()
    data = session.query(Comment).filter_by(post_id=id).all()

    if data is None:
        return None
    
    jsonData = []
    for comment in data:
        jsonComment = schema.dump(comment)
        jsonComment["user"] = get_user_by_id(jsonComment["user"])["res"]
        jsonData.append(jsonComment)

    return jsonData


@errorHandler("post")
def create_new_comment(session: Session, comment: NewComment, currentUser):
    schema = CommentSchema()
    user = session.query(User).get(currentUser)
    post = session.query(Post).get(comment.post_id)

    data = Comment(
        content=comment.content,
        answer=False,
        user=user,
        post=post
    )

    session.add(data)

    return schema.dump(data)


@errorHandler("post")
def like_comment(session: Session, comment_id, currentUser):
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


@errorHandler("post")
def rm_like_comment(session, comment_id, currentUser):
    schemas = [CommentSchema(), UserSchema()]
    comment = session.query(Comment).get(comment_id)
    user = session.query(User).get(currentUser)

    jsonComment = schemas[0].dump(comment)
    jsonUser = schemas[1].dump(user)

    comment.likes.remove(user)

    return f"Comment: {jsonComment['id']} Like Removed by User: {jsonUser['username']}"