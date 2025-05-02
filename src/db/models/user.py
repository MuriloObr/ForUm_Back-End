from datetime import datetime
from sqlmodel import Field, SQLModel, Relationship, DateTime
from .many_to_many import PostLikeLink, PostViewLink, CommentLikeLink


class User(SQLModel, table=True):
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
    created_at: datetime = Field(DateTime(timezone=True), server_default=func.now())
    updated_at: datetime = Field(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.current_timestamp(),
    )

    def __repr__(self):
        return f"(ID: {self.id} Username: {self.username} Email: {self.email})"
