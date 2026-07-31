from sqlmodel import Field, SQLModel


class PostLikeLink(SQLModel, table=True):
    __tablename__ = "posts_likes"

    post_id: int | None = Field(default=None, foreign_key="posts.id", primary_key=True)
    user_id: int | None = Field(default=None, foreign_key="users.id", primary_key=True)


class PostViewLink(SQLModel, table=True):
    __tablename__ = "posts_views"

    post_id: int | None = Field(default=None, foreign_key="posts.id", primary_key=True)
    user_id: int | None = Field(default=None, foreign_key="users.id", primary_key=True)


class CommentLikeLink(SQLModel, table=True):
    __tablename__ = "comments_likes"

    comment_id: int | None = Field(
        default=None, foreign_key="comments.id", primary_key=True
    )
    user_id: int | None = Field(default=None, foreign_key="users.id", primary_key=True)
