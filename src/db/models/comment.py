from sqlmodel import SQLModel, Relationship, Field


class Comment(SQLModel, table=True):
    id: int = Field(primary_key=True)
    user_id: int = Field(ForeignKey("users.id"), nullable=False)
    post_id: int = Field(ForeignKey("posts.id"), nullable=False)
    content: str = Field(nullable=False)
    likes: list["User"] = Relationship(
        secondary=comments_likes, back_populates="comment_likes"
    )
    answer: bool = Field(nullable=False)
    user: ["User"] = Relationship(back_populates="comments")
    post: ["Post"] = Relationship(back_populates="comments")
    created_at: datetime.datetime = Field(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: datetime.datetime = Field(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.current_timestamp(),
    )

    def __repr__(self):
        return f"<ID: {self.id} User: {self.user} Post:{self.post}>"
