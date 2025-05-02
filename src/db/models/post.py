from datetime import datetime
from sqlmodel import Field, SQLModel, Relationship, DateTime


class Post(SQLModel, table=True):
    id: int = Field(primary_key=True)
    user_id: int = Field(ForeignKey("users.id"), nullable=False)
    tittle: str = Field(nullable=False)
    content: str = Field(nullable=False)
    views: list["User"] = Relationship(
        secondary=posts_views, back_populates="post_views"
    )
    likes: list["User"] = Relationship(
        secondary=posts_likes, back_populates="post_likes"
    )
    closed: bool = Field(nullable=False)
    user: ["User"] = Relationship(back_populates="posts")
    comments: list["Comment"] = Relationship(back_populates="post")
    created_at: datetime.datetime = Field(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: datetime.datetime = Field(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.current_timestamp(),
    )

    def __repr__(self):
        return f"[ID: {self.id} Tittle: {self.tittle} User: {self.user}  Closed: {self.closed}]"
