"""rename tittle to title, closed to is_closed, add answer_id

Revision ID: c677445c41bb
Revises: c51476d1633e
Create Date: 2026-07-26 18:50:21.767565

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'c677445c41bb'
down_revision: Union[str, Sequence[str], None] = 'c51476d1633e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('posts', sa.Column('title', sa.String(), nullable=False))
    op.add_column('posts', sa.Column('is_closed', sa.Boolean(), nullable=False))
    op.add_column('posts', sa.Column('answer_id', sa.Integer(), nullable=True))

    op.execute("""
        UPDATE posts SET title = tittle
    """)
    op.execute("""
        UPDATE posts SET is_closed = closed
    """)
    op.execute("""
        UPDATE posts p SET answer_id = c.id
        FROM comments c
        WHERE c.post_id = p.id AND c.answer = true
    """)

    op.drop_column('posts', 'tittle')
    op.drop_column('posts', 'closed')
    op.drop_column('comments', 'answer')


def downgrade() -> None:
    """Downgrade schema."""
    op.add_column('comments', sa.Column('answer', sa.Boolean(), nullable=False, server_default='false'))

    op.execute("""
        UPDATE comments c SET answer = true
        FROM posts p
        WHERE p.answer_id = c.id
    """)

    op.add_column('posts', sa.Column('tittle', sa.String(), nullable=False))
    op.add_column('posts', sa.Column('closed', sa.Boolean(), nullable=False, server_default='false'))

    op.execute("""
        UPDATE posts SET tittle = title
    """)
    op.execute("""
        UPDATE posts SET closed = is_closed
    """)

    op.drop_column('posts', 'answer_id')
    op.drop_column('posts', 'is_closed')
    op.drop_column('posts', 'title')
