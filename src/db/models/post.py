from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

from .many_to_many import PostLikeLink, PostViewLink

if TYPE_CHECKING:
    from .comment import Comment
    from .user import User


class Post(SQLModel, table=True):
    __tablename__ = "posts"

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
    user: "User" = Relationship(back_populates="posts")
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
