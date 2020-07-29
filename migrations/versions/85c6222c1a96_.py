"""empty message

Revision ID: 85c6222c1a96
Revises: 
Create Date: 2020-07-26 20:25:42.752544

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '85c6222c1a96'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('articles', 'author',
               existing_type=sa.VARCHAR(length=64),
               nullable=True)
    op.alter_column('articles', 'content',
               existing_type=sa.TEXT(length=2048),
               nullable=True)
    op.alter_column('articles', 'time',
               existing_type=sa.VARCHAR(length=64),
               nullable=True)
    op.alter_column('articles', 'title',
               existing_type=sa.VARCHAR(length=64),
               nullable=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('articles', 'title',
               existing_type=sa.VARCHAR(length=64),
               nullable=False)
    op.alter_column('articles', 'time',
               existing_type=sa.VARCHAR(length=64),
               nullable=False)
    op.alter_column('articles', 'content',
               existing_type=sa.TEXT(length=2048),
               nullable=False)
    op.alter_column('articles', 'author',
               existing_type=sa.VARCHAR(length=64),
               nullable=False)
    # ### end Alembic commands ###
