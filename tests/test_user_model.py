from datetime import datetime, timezone, timedelta

import pytest
from sqlmodel import Session, select
from sqlalchemy.exc import IntegrityError

from src.db.models.user import User
from src.db.models.post import Post
from src.db.models.comment import Comment
from src.db.models.many_to_many import (
    CommentLikeLink,
    PostLikeLink,
    PostViewLink,
)


class TestUserRegistrationFlow:
    def test_create_user_with_all_fields(self, db_session):
        user = User(
            username="johndoe",
            nickname="John",
            email="john@example.com",
            password="hashed_pw_123",
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        assert user.id is not None
        assert user.username == "johndoe"
        assert user.nickname == "John"
        assert user.email == "john@example.com"
        assert user.password == "hashed_pw_123"
        assert isinstance(user.created_at, datetime)
        assert isinstance(user.updated_at, datetime)

    def test_id_auto_increments(self, db_session):
        user1 = User(
            username="user1", nickname="U1",
            email="u1@example.com", password="pw",
        )
        user2 = User(
            username="user2", nickname="U2",
            email="u2@example.com", password="pw",
        )
        db_session.add_all([user1, user2])
        db_session.commit()
        db_session.refresh(user1)
        db_session.refresh(user2)

        assert user2.id == user1.id + 1

    def test_password_stored_as_raw_string(self, db_session):
        raw_pw = "my_plain_password"
        user = User(
            username="rawpw", nickname="RP",
            email="rp@example.com", password=raw_pw,
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        assert user.password == raw_pw

    def test_read_back_from_db(self, db_session):
        user = User(
            username="readback", nickname="RB",
            email="rb@example.com", password="pw",
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        user_id = user.id

        fetched = db_session.get(User, user_id)
        assert fetched is not None
        assert fetched.username == "readback"
        assert fetched.email == "rb@example.com"


class TestUserCreatesPost:
    def test_user_post_relationship(self, db_session):
        user = User(
            username="author", nickname="Author",
            email="author@example.com", password="pw",
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        post = Post(
            user_id=user.id, title="First Post",
            content="Hello world",
        )
        db_session.add(post)
        db_session.commit()
        db_session.refresh(post)
        db_session.refresh(user)

        assert post.user_id == user.id
        assert post.user.username == "author"
        assert len(user.posts) == 1
        assert user.posts[0].title == "First Post"

    def test_user_creates_multiple_posts(self, db_session):
        user = User(
            username="prolific", nickname="P",
            email="p@example.com", password="pw",
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        for i in range(3):
            db_session.add(Post(
                user_id=user.id, title=f"Post {i}",
                content=f"Content {i}",
            ))
        db_session.commit()
        db_session.refresh(user)

        assert len(user.posts) == 3
        titles = {p.title for p in user.posts}
        assert titles == {"Post 0", "Post 1", "Post 2"}


class TestUserCommentsOnPost:
    def test_comment_relationships(self, db_session):
        author = User(
            username="postauthor", nickname="PA",
            email="pa@example.com", password="pw",
        )
        commenter = User(
            username="commenter", nickname="C",
            email="c@example.com", password="pw",
        )
        db_session.add_all([author, commenter])
        db_session.commit()
        db_session.refresh(author)
        db_session.refresh(commenter)

        post = Post(
            user_id=author.id, title="My Post",
            content="Discussion",
        )
        db_session.add(post)
        db_session.commit()
        db_session.refresh(post)

        comment = Comment(
            user_id=commenter.id, post_id=post.id,
            content="Great post!",
        )
        db_session.add(comment)
        db_session.commit()
        db_session.refresh(comment)
        db_session.refresh(post)
        db_session.refresh(commenter)

        assert comment.user_id == commenter.id
        assert comment.post_id == post.id
        assert comment.user.username == "commenter"
        assert comment.post.title == "My Post"
        assert len(post.comments) == 1
        assert post.comments[0].content == "Great post!"
        assert len(commenter.comments) == 1

    def test_multiple_users_comment_on_post(self, db_session):
        author = User(
            username="op", nickname="OP",
            email="op@example.com", password="pw",
        )
        db_session.add(author)
        db_session.commit()
        db_session.refresh(author)

        post = Post(
            user_id=author.id, title="Hot Topic",
            content="Debate time",
        )
        db_session.add(post)
        db_session.commit()
        db_session.refresh(post)

        commenters = []
        for i in range(3):
            u = User(
                username=f"critic{i}", nickname=f"C{i}",
                email=f"c{i}@example.com", password="pw",
            )
            db_session.add(u)
            db_session.commit()
            db_session.refresh(u)
            commenters.append(u)

            c = Comment(
                user_id=u.id, post_id=post.id,
                content=f"Opinion #{i}",
            )
            db_session.add(c)

        db_session.commit()
        db_session.refresh(post)

        assert len(post.comments) == 3


class TestUserLikesPost:
    def test_user_likes_and_unlikes_post(self, db_session):
        user = User(
            username="liker", nickname="L",
            email="l@example.com", password="pw",
        )
        post = Post(
            user_id=1, title="Likeable",
            content="Like me",
        )
        db_session.add_all([user, post])
        db_session.commit()
        db_session.refresh(user)
        db_session.refresh(post)

        link = PostLikeLink(user_id=user.id, post_id=post.id)
        db_session.add(link)
        db_session.commit()
        db_session.refresh(post)
        db_session.refresh(user)

        assert len(post.likes) == 1
        assert post.likes[0].username == "liker"
        assert len(user.post_likes) == 1
        assert user.post_likes[0].title == "Likeable"

        db_session.delete(link)
        db_session.commit()
        db_session.refresh(post)
        db_session.refresh(user)

        assert len(post.likes) == 0
        assert len(user.post_likes) == 0

    def test_multiple_users_like_post(self, db_session):
        post = Post(
            user_id=1, title="Popular",
            content="Everyone likes this",
        )
        db_session.add(post)
        db_session.commit()
        db_session.refresh(post)

        users = []
        for i in range(5):
            u = User(
                username=f"fan{i}", nickname=f"F{i}",
                email=f"f{i}@example.com", password="pw",
            )
            db_session.add(u)
            db_session.commit()
            db_session.refresh(u)
            users.append(u)

            db_session.add(PostLikeLink(user_id=u.id, post_id=post.id))

        db_session.commit()
        db_session.refresh(post)

        assert len(post.likes) == 5
        fan_names = {u.username for u in post.likes}
        assert fan_names == {f"fan{i}" for i in range(5)}


class TestUserViewsPost:
    def test_user_views_post(self, db_session):
        user = User(
            username="viewer", nickname="V",
            email="v@example.com", password="pw",
        )
        post = Post(
            user_id=1, title="Interesting",
            content="Read me",
        )
        db_session.add_all([user, post])
        db_session.commit()
        db_session.refresh(user)
        db_session.refresh(post)

        link = PostViewLink(user_id=user.id, post_id=post.id)
        db_session.add(link)
        db_session.commit()
        db_session.refresh(post)
        db_session.refresh(user)

        assert len(post.views) == 1
        assert post.views[0].username == "viewer"
        assert len(user.post_views) == 1

    def test_same_user_cannot_view_twice(self, db_session):
        user = User(
            username="reloader", nickname="R",
            email="r@example.com", password="pw",
        )
        post = Post(
            user_id=1, title="Page",
            content="Content",
        )
        db_session.add_all([user, post])
        db_session.commit()
        db_session.refresh(user)
        db_session.refresh(post)

        db_session.add(PostViewLink(user_id=user.id, post_id=post.id))
        db_session.commit()

        db_session.add(PostViewLink(user_id=user.id, post_id=post.id))
        with pytest.raises(IntegrityError):
            db_session.commit()


class TestUserLikesComment:
    def test_user_likes_comment(self, db_session):
        user = User(
            username="cliker", nickname="CL",
            email="cl@example.com", password="pw",
        )
        post = Post(
            user_id=1, title="Post",
            content="Content",
        )
        db_session.add_all([user, post])
        db_session.commit()
        db_session.refresh(user)
        db_session.refresh(post)

        comment = Comment(
            user_id=1, post_id=post.id,
            content="Wise words",
        )
        db_session.add(comment)
        db_session.commit()
        db_session.refresh(comment)

        link = CommentLikeLink(user_id=user.id, comment_id=comment.id)
        db_session.add(link)
        db_session.commit()
        db_session.refresh(comment)
        db_session.refresh(user)

        assert len(comment.likes) == 1
        assert comment.likes[0].username == "cliker"
        assert len(user.comment_likes) == 1

    def test_multiple_users_like_comment(self, db_session):
        post = Post(
            user_id=1, title="Post",
            content="Content",
        )
        db_session.add(post)
        db_session.commit()
        db_session.refresh(post)

        comment = Comment(
            user_id=1, post_id=post.id,
            content="Brilliant insight",
        )
        db_session.add(comment)
        db_session.commit()
        db_session.refresh(comment)

        for i in range(3):
            u = User(
                username=f"fan{i}", nickname=f"F{i}",
                email=f"f{i}@example.com", password="pw",
            )
            db_session.add(u)
            db_session.commit()
            db_session.refresh(u)
            db_session.add(CommentLikeLink(user_id=u.id, comment_id=comment.id))

        db_session.commit()
        db_session.refresh(comment)

        assert len(comment.likes) == 3


class TestPostAnswerMarking:
    def test_mark_answer_on_post(self, db_session):
        author = User(
            username="questioner", nickname="Q",
            email="q@example.com", password="pw",
        )
        solver = User(
            username="answerer", nickname="A",
            email="a@example.com", password="pw",
        )
        db_session.add_all([author, solver])
        db_session.commit()
        db_session.refresh(author)
        db_session.refresh(solver)

        post = Post(
            user_id=author.id, title="How to?",
            content="I need help",
        )
        db_session.add(post)
        db_session.commit()
        db_session.refresh(post)

        comment = Comment(
            user_id=solver.id, post_id=post.id,
            content="Do this",
        )
        db_session.add(comment)
        db_session.commit()
        db_session.refresh(comment)

        post.answer_id = comment.id
        db_session.commit()
        db_session.refresh(post)

        assert post.answer_id == comment.id

    def test_clear_answer_on_post(self, db_session):
        author = User(
            username="op", nickname="OP",
            email="op@example.com", password="pw",
        )
        db_session.add(author)
        db_session.commit()
        db_session.refresh(author)

        post = Post(
            user_id=author.id, title="Question",
            content="Help",
        )
        db_session.add(post)
        db_session.commit()
        db_session.refresh(post)

        comment = Comment(
            user_id=author.id, post_id=post.id,
            content="Self-answer",
        )
        db_session.add(comment)
        db_session.commit()
        db_session.refresh(comment)

        post.answer_id = comment.id
        db_session.commit()
        db_session.refresh(post)
        assert post.answer_id == comment.id

        post.answer_id = None
        db_session.commit()
        db_session.refresh(post)
        assert post.answer_id is None


class TestUserTimestampsBehavior:
    def test_timestamps_set_on_creation(self, db_session):
        before = datetime.now(timezone.utc)
        user = User(
            username="timed", nickname="T",
            email="t@example.com", password="pw",
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        after = datetime.now(timezone.utc)

        created = user.created_at.replace(tzinfo=timezone.utc) if user.created_at.tzinfo is None else user.created_at
        assert before <= created <= after

    def test_updated_at_does_not_auto_update(self, db_session):
        user = User(
            username="stale", nickname="S",
            email="s@example.com", password="pw",
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        original_updated = user.updated_at

        user.nickname = "Updated Nick"
        db_session.commit()
        db_session.refresh(user)

        assert user.nickname == "Updated Nick"
        assert user.updated_at == original_updated
