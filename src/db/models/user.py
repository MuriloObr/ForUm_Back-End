from sqlmodel import Field, SQLModel, Relationship

class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    nickname: str
    username: str = Field(nullable=False)
    password: str = Field(nullable=False)
    email: str = Field(nullable=False)
    posts: list["Post"] = Relationship(back_populates="user")
    comments: list["Comment"] = Relationship(back_populates="user")
    post_views: list["Post"] = Relationship(
        secondary=posts_views, back_populates="views"
    )
    post_likes: list["Post"] = Relationship(
        secondary=posts_likes, back_populates="likes"
    )
    comment_likes: list["Comment"] = Relationship(
        secondary=comments_likes, back_populates="likes"
    )
    created_at: [datetime.datetime] = Field(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: [datetime.datetime] = Field(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.current_timestamp(),
    )

    def __repr__(self):
        return f"(ID: {self.id} Username: {self.username} Email: {self.email})"
