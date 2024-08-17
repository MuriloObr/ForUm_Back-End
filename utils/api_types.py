from pydantic import BaseModel


class UIDToken(BaseModel):
    user_id: int
    exp: int

class PostRef(BaseModel):
    post_id: int

class NewPost(BaseModel):
    tittle: str
    content: str

class CommentRef(BaseModel):
    comment_id: int

class NewComment(BaseModel):
    post_id: int
    content: str

class BestCommentRef(BaseModel):
    post_id: int
    comment_id: int

class NewUser(BaseModel):
    username: str
    nickname: str
    email: str
    password: str

class UserPayload(BaseModel):
    user: str
    password: str