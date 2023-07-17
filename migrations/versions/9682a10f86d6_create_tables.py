"""create tables

Revision ID: 9682a10f86d6
Revises: 
Create Date: 2023-07-17 01:26:55.266345

"""
import sqlalchemy_utils
from alembic import op
import sqlalchemy as sa
from app_database.models import User

# revision identifiers, used by Alembic.
revision = '9682a10f86d6'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('category',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('title', sa.String(length=25), nullable=False),
                    sa.PrimaryKeyConstraint('id'),
                    sa.UniqueConstraint('title')
                    )
    op.create_table('user',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('username', sa.String(length=30), nullable=False),
                    sa.Column('password', sa.Text(), nullable=False),
                    sa.Column('email', sa.String(length=120), nullable=False),
                    sa.Column('active', sa.Boolean(), nullable=True),
                    sa.Column('group', sqlalchemy_utils.types.choice.ChoiceType(User.GROUP_USERS), nullable=True),
                    sa.PrimaryKeyConstraint('id'),
                    sa.UniqueConstraint('email'),
                    sa.UniqueConstraint('username')
                    )
    op.create_table('post',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('title', sa.String(length=40), nullable=False),
                    sa.Column('content', sa.Text(), nullable=False),
                    sa.Column('date_create', sa.TIMESTAMP(), nullable=True),
                    sa.Column('publish', sa.Boolean(), nullable=True),
                    sa.Column('author_id', sa.Integer(), nullable=True),
                    sa.Column('category_id', sa.Integer(), nullable=True),
                    sa.ForeignKeyConstraint(['author_id'], ['user.id'], ),
                    sa.ForeignKeyConstraint(['category_id'], ['category.id'], ),
                    sa.PrimaryKeyConstraint('id')
                    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('post')
    op.drop_table('user')
    op.drop_table('category')
    # ### end Alembic commands ###