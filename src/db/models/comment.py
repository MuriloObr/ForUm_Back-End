from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

from .many_to_many import CommentLikeLink

if TYPE_CHECKING:
    from .post import Post
    from .user import User


class Comment(SQLModel, table=True):
    __tablename__ = "comments"

    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", nullable=False)
    post_id: int = Field(foreign_key="posts.id", nullable=False)
    content: str = Field(nullable=False)
    likes: list[User] = Relationship(
        link_model=CommentLikeLink, back_populates="comment_likes"
    )
    user: User = Relationship(back_populates="comments")
    post: Post = Relationship(back_populates="comments")
    created_at: datetime = Field(
        sa_column_kwargs={"server_default": "now()"}
    )
    updated_at: datetime = Field(
        sa_column_kwargs={"server_default": "now()", "onupdate": "now()"}
    )
