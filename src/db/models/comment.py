from datetime import datetime, timezone

from sqlmodel import Field, Relationship, SQLModel

from src.db.models.many_to_many import CommentLikeLink

from .user import User


class Comment(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", nullable=False)
    post_id: int = Field(foreign_key="posts.id", nullable=False)
    content: str = Field(nullable=False)
    likes: list["User"] = Relationship(
        link_model=CommentLikeLink, back_populates="comment_likes"
    )
    created_at: datetime = Field(default=datetime.now(timezone.utc), nullable=False)
    updated_at: datetime = Field(default=datetime.now(timezone.utc), nullable=False)
