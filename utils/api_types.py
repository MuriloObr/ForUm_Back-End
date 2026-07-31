from datetime import datetime
from pydantic import BaseModel


class UIDToken(BaseModel):
    user_id: int
    exp: int

class PostRef(BaseModel):
    post_id: int

class NewPost(BaseModel):
    title: str
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


# --- Response models ---

class UserResponse(BaseModel):
    id: int
    nickname: str
    username: str
    email: str
    created_at: datetime
    updated_at: datetime

class PostResponse(BaseModel):
    id: int
    title: str
    content: str
    is_closed: bool
    answer_id: int | None
    created_at: datetime
    updated_at: datetime
    user_id: int
    user: UserResponse

class CommentResponse(BaseModel):
    id: int
    content: str
    post_id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    user: UserResponse | None = None

class MessageResponse(BaseModel):
    message: str

class LoggedResponse(BaseModel):
    res: str
