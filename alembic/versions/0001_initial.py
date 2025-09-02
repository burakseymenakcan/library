"""Initial schema: users, books, loans

Revision ID: 0001_initial
Revises: 
Create Date: 2025-09-02 00:00:00

"""
from alembic import op  # type: ignore
import sqlalchemy as sa  # type: ignore

# revision identifiers, used by Alembic.
revision = '0001_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('username', sa.String(length=255), nullable=False, unique=True),
        sa.Column('email', sa.String(length=255), nullable=False, unique=True),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('is_staff', sa.Boolean(), server_default=sa.text('FALSE')),
        sa.Column('is_superuser', sa.Boolean(), server_default=sa.text('FALSE')),
        sa.Column('is_banned', sa.Boolean(), server_default=sa.text('FALSE')),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP')),
    )

    op.create_table(
        'books',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('author', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text()),
        sa.Column('published_year', sa.Integer()),
        sa.Column('isbn', sa.String(length=50)),
        sa.Column('category', sa.String(length=100)),
        sa.Column('cover_url', sa.Text()),
        sa.Column('total_copies', sa.Integer(), server_default=sa.text('1')),
        sa.Column('available_copies', sa.Integer(), server_default=sa.text('1')),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP')),
    )

    op.create_table(
        'loans',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('book_id', sa.Integer(), nullable=False),
        sa.Column('borrowed_at', sa.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('due_date', sa.Date()),
        sa.Column('returned_at', sa.TIMESTAMP()),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.ForeignKeyConstraint(['book_id'], ['books.id']),
    )


def downgrade() -> None:
    op.drop_table('loans')
    op.drop_table('books')
    op.drop_table('users')
