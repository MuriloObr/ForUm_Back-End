import datetime
from sqlalchemy.sql import func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, DateTime, Table, Column
from typing import List


class Base(DeclarativeBase):
    pass


posts_likes = Table(
    "posts_likes",
    Base.metadata,
    Column("post_id", ForeignKey("posts.id"), primary_key=True),
    Column("user_id", ForeignKey("users.id"), primary_key=True)
)

posts_views = Table(
    "posts_views",
    Base.metadata,
    Column("post_id", ForeignKey("posts.id"), primary_key=True),
    Column("user_id", ForeignKey("users.id"), primary_key=True)
)

comments_likes = Table(
    "comments_likes",
    Base.metadata,
    Column("comment_id", ForeignKey("comments.id"), primary_key=True),
    Column("user_id", ForeignKey("users.id"), primary_key=True)
)


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    nickname: Mapped[str]
    username: Mapped[str] = mapped_column(nullable=False)
    password: Mapped[str] = mapped_column(nullable=False)
    email: Mapped[str] = mapped_column(nullable=False)
    posts: Mapped[List["Post"]] = relationship(back_populates="user")
    comments: Mapped[List["Comment"]] = relationship(back_populates="user")
    post_views: Mapped[List["Post"]] = relationship(
        secondary=posts_views, back_populates="views")
    post_likes: Mapped[List["Post"]] = relationship(
        secondary=posts_likes, back_populates="likes")
    comment_likes: Mapped[List["Comment"]] = relationship(
        secondary=comments_likes, back_populates="likes")
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.current_timestamp()
    )

    def __repr__(self):
        return f"(ID: {self.id} Username: {self.username} Email: {self.email})"


class Post(Base):
    __tablename__ = "posts"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), nullable=False)
    tittle: Mapped[str] = mapped_column(nullable=False)
    content: Mapped[str] = mapped_column(nullable=False)
    views: Mapped[List["User"]] = relationship(
        secondary=posts_views, back_populates="post_views")
    likes: Mapped[List["User"]] = relationship(
        secondary=posts_likes, back_populates="post_likes")
    closed: Mapped[bool] = mapped_column(nullable=False)
    user: Mapped["User"] = relationship(back_populates="posts")
    comments: Mapped[List["Comment"]] = relationship(back_populates="post")
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.current_timestamp()
    )

    def __repr__(self):
        return f"[ID: {self.id} Name: {self.name} User: {self.user}  Closed: {self.closed}]"


class Comment(Base):
    __tablename__ = "comments"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), nullable=False)
    post_id: Mapped[int] = mapped_column(
        ForeignKey("posts.id"), nullable=False)
    content: Mapped[str] = mapped_column(nullable=False)
    likes: Mapped[List["User"]] = relationship(
        secondary=comments_likes, back_populates="comment_likes")
    answer: Mapped[bool] = mapped_column(nullable=False)
    user: Mapped["User"] = relationship(back_populates="comments")
    post: Mapped["Post"] = relationship(back_populates="comments")
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.current_timestamp()
    )

    def __repr__(self):
        return f"<ID: {self.id} User: {self.user} Post:{self.post}>"
