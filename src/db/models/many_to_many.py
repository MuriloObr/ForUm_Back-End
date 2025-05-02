from sqlmodel import SQLModel, Field


class HeroTeamLink(SQLModel, table=True):
    team_id: int | None = Field(default=None, foreign_key="team.id", primary_key=True)
    hero_id: int | None = Field(default=None, foreign_key="hero.id", primary_key=True)


class PostLikeLink(SQLModel, table=True):
    post_id: int | None = Field(default=None, foreign_key="posts.id", primary_key=True)
    user_id: int | None = Field(default=None, foreign_key="users.id", primary_key=True)


class PostViewLink(SQLModel, table=True):
    post_id: int | None = Field(default=None, foreign_key="posts.id", primary_key=True) 
    user_id: int | None = Field(default=None, foreign_key="users.id", primary_key=True)


class CommentLikeLink(SQLModel, table=True):
    comment_id: int | None = Field(default=None, foreign_key="comments.id", primary_key=True) 
    user_id: int | None = Field(default=None, foreign_key="users.id", primary_key=True)
