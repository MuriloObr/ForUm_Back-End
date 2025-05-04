from datetime import datetime, timezone

from sqlmodel import Field, Relationship, SQLModel

from .comment import Comment
from .many_to_many import PostLikeLink, PostViewLink
from .user import User


class Post(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", nullable=False)
    title: str = Field(nullable=False)
    content: str = Field(nullable=False)
    views: list["User"] = Relationship(
        link_model=PostViewLink, back_populates="post_views"
    )
    likes: list["User"] = Relationship(
        link_model=PostLikeLink, back_populates="post_likes"
    )
    is_closed: bool = Field(default=False, nullable=False)
    answer_id: int | None = Field(default=None)
    comments: list["Comment"] = Relationship(back_populates="post")
    created_at: datetime = Field(default=datetime.now(timezone.utc), nullable=False)
    updated_at: datetime = Field(default=datetime.now(timezone.utc), nullable=False)
