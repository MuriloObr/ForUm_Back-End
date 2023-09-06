from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from database.models import User, Post, Comment


class UserSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = User
        include_relationships = True


class PostSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Post
        include_relationships = True


class CommentSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Comment
        include_relationships = True
