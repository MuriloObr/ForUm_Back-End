from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

from .many_to_many import CommentLikeLink, PostLikeLink, PostViewLink

if TYPE_CHECKING:
    from .comment import Comment
    from .post import Post


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: int | None = Field(default=None, primary_key=True)
    nickname: str
    username: str = Field(nullable=False)
    password: str = Field(nullable=False)
    email: str = Field(nullable=False)
    posts: list["Post"] = Relationship(back_populates="user")
    comments: list["Comment"] = Relationship(back_populates="user")
    post_views: list["Post"] = Relationship(
        back_populates="views", link_model=PostViewLink
    )
    post_likes: list["Post"] = Relationship(
        back_populates="likes", link_model=PostLikeLink
    )
    comment_likes: list["Comment"] = Relationship(
        back_populates="likes", link_model=CommentLikeLink
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
